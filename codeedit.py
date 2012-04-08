# -*- coding: utf-8 -*-

import sys
from PyQt4.QtGui import QWidget,QBrush,QPlainTextEdit,QTextEdit,QPalette,QTextOption,QTextCursor,QResizeEvent,QPainter,QPen,QTextCharFormat,QTextFormat,QColor,QFont,QApplication
from PyQt4.QtCore import QSize, Qt,QPoint,SIGNAL,QRegExp,QRect


class LineNumberArea(QWidget):

	def __init__(self,editor):
		self.codeEditor=editor
		self.markers=[]
		QWidget.__init__(self, editor)
        

	def sizeHint(self):
		return QSize(self.codeEditor.lineNumberAreaWidth(),0)

	def drawMarker(self,painter,region):
		painter.setBrush(QBrush(Qt.red))
		painter.drawEllipse(QPoint(region.x()+region.width()/2,region.y()+region.height()/2),5,5)
	def drawFoldingItem(self,painter,region,expanded):
		painter.setBrush(QBrush(Qt.white))
		painter.drawRect(region.x() + region.width() / 2 - 5, region.y() + region.height() / 2 - 5, 10, 10)
		painter.drawLine(region.x() + region.width() / 2 - 3, region.y() + region.height() / 2, region.x() + region.width() / 2 + 3, region.y() + region.height() / 2)
		if not expanded:
			painter.drawLine(region.x() + region.width() / 2, region.y() + region.height() / 2 - 3, region.x() + region.width() / 2, region.y() + region.height() / 2 + 3)
		else:
			painter.drawLine(region.x() + region.width() / 2 , region.y() + region.height() / 2 + 5, region.x() + region.width() / 2 , region.bottom()+1)

	def paintEvent(self, event):
		self.codeEditor.lineNumberAreaPaintEvent(event)
		#~ print "wep"
	def mousePressEvent(self,event):
		if event.button()==Qt.LeftButton:
			line = self.codeEditor.cursorForPosition(QPoint(self.width() + 1, event.pos().y())).block().blockNumber()
			#~ print line
			if event.pos().x() < self.codeEditor.lineNumberAreaWidthPrimar():
				self.codeEditor.gotoLine(line,True)
			elif event.pos().x() >= self.codeEditor.lineNumberAreaWidthPrimar() and event.pos().x() < self.codeEditor.lineNumberAreaWidthPrimar()+15:
				if line in self.markers:
					self.markers.remove(line)
				else:
					self.markers.append(line)
			else:
				if self.codeEditor.foldableLines.has_key(line):
					if self.codeEditor.foldedLines.has_key(line):
						self.codeEditor.unfold(line,self.codeEditor.foldableLines[line])
					else:
						self.codeEditor.fold(line,self.codeEditor.foldableLines[line])
		self.update()

class CodeEditor(QPlainTextEdit):
    
    def __init__(self,parent=None):
		
        self.lang= None
        self.prevBlockNum=0
        #~ self.
        self.foldableLines={}
        self.foldedLines={}
        QPlainTextEdit.__init__(self,parent)
        self.palette= QPalette()
        self.palette.setColor(QPalette.Base, Qt.white)
        self.palette.setColor(QPalette.Text, Qt.black)
        self.setPalette(self.palette)
        self.lineNumberArea = LineNumberArea (self)
        #~ self.connect(self, SIGNAL("textChanged()"), 
                     #~ self.findFoldableLines)
        self.connect(self, SIGNAL("blockCountChanged(int)"), 
                     self.updateLineNumberAreaWidth)
            
        self.connect(self, SIGNAL("updateRequest(const QRect &, int)"), 
                     self.updateLineNumberArea)
        
                #~ 
        self.connect(self, SIGNAL("cursorPositionChanged()"), 
                     self.highlightCurrentLine)

        self.updateLineNumberAreaWidth(0)
        self.errorPos=None
        self.highlightCurrentLine()
        
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setWordWrapMode(QTextOption.NoWrap)
        self.findFoldableLines()
    
    def setLanguage(self,lang):
		self.lang = lang
		#~ print lang
		self.lang.setDocument(self.document())
		#~ print self.lang.initialized
		if not self.lang.initialized:
			self.lang.initialize()
		#~ print "que onda"
		self.setFont(self.lang.font)
		self.setTabStopWidth(self.fontMetrics().width("    "))
		self.update()
    def keyPressEvent(self, e):
		
		if e.key() in (Qt.Key_Return,Qt.Key_Enter):
			#~ print self.textCursor().block().blockNumber(),self.foldableLines
			line=self.textCursor().block().blockNumber()
			#~ print self.foldableLines,line
			if line in self.foldedLines:
				self.unfold(line,self.foldableLines[line])
			QPlainTextEdit.keyPressEvent(self, e)	
			self.indent()
			return
		
		QPlainTextEdit.keyPressEvent(self, e)
		if e.key() == Qt.Key_BraceLeft:
			self.findFoldableLines()
		if e.key() == Qt.Key_BraceRight:
			self.findFoldableLines()
			cursor = self.textCursor()
			start = cursor.position()
			next = self.check_brackets(True)
			if next is not None:
				cursor.setPosition(next)
				indent=self.getIndent(cursor.block().text())
				#~ spaces= QRegExp("^(\\s*).*$")
				#~ if spaces.indexIn(cursor.block().text()) == -1:
					#~ indent=""
				#~ else:
					#~ indent=spaces.cap(1)
				self.moveCursor(QTextCursor.Left)
				self.moveCursor(QTextCursor.StartOfLine,QTextCursor.KeepAnchor)
				text = self.textCursor().selectedText()
				
				for a in range(len(text)):
			
					if text[a] != '	':
						cursor.setPosition(start)
						self.setTextCursor(cursor)
						return
			
				self.textCursor().removeSelectedText()
				self.textCursor().insertText(indent)
				self.moveCursor(QTextCursor.EndOfLine)
			
    def getIndent(self,text):
		spaces= QRegExp("^(\\s*).*$")
		#~ indentation=""
		#~ if len(text) > 0 and text[-1] in [':', '{', '(', '[']:
				#~ indentation="	"
		if spaces.indexIn(text) == -1:
			return ""
		return spaces.cap(1)

    def indent(self):
		if not self.textCursor().block().previous().isValid():
			return
		text = self.textCursor().block().previous().text()
		indent= self.getIndent(text)
		if len(text) > 0 and text[-1] in [':', '{', '(', '[']:
				indent+="	"
		self.textCursor().movePosition(QTextCursor.StartOfLine)
		self.textCursor().insertText(indent)
		self.textCursor().movePosition(QTextCursor.EndOfLine)
		
    def gotoLine(self,l,select):
		tc = self.textCursor()
		#~ currentLine = tc.block().blockNumber()
		tc.setPosition(self.document().findBlockByLineNumber(l).position())
		#~ offset = currentLine - l
		#~ if offset > 0:
			#~ for i in range(offset):
				#~ tc.movePosition(QtGui.QTextCursor.Down,QtGui.QTextCursor.MoveAnchor)
		#~ else:
			#~ for i in range(-offset):
				#~ tc.movePosition(QtGui.QTextCursor.Down,QtGui.QTextCursor.MoveAnchor)
		if select:
			tc.select(QTextCursor.LineUnderCursor)
		self.setTextCursor(tc)
		
    def fold(self,start,end):
		self.foldedLines[start]=end
		block= self.document().findBlockByNumber(start)
		#~ block.userData().folded=True
		endblock=self.document().findBlockByNumber(end)
		#~ block=block.next()
		while block.isValid() and block != endblock:
			#~ self.document().findBlockByNumber(i+start+1).setVisible(False)
			block=block.next()
			block.setVisible(False)
			block.setLineCount(0)
			self.update()
			
		#~ self.update()
		#~ self.document().markContentsDirty(start, end)
		self.resizeEvent(QResizeEvent(QSize(0,0),self.size()))

    def unfold(self,start,end):
		if not self.foldedLines.has_key(start):
			return
		block= self.document().findBlockByNumber(start)
		#~ block.userData().folded=False
		endblock=self.document().findBlockByNumber(end+1)
		block=block.next()
		while block.isValid() and block != endblock:
			block.setVisible(True)
			block.setLineCount(block.layout().lineCount())
			#~ if block.blockNumber() in self.foldedLines:
			if self.foldedLines.has_key(block.blockNumber()):
				#~ print block.blockNumber()
				block=self.document().findBlockByNumber(self.foldedLines[block.blockNumber()]).next()
			else:
				block=block.next()
		#~ for i in range(end-start):
			#~ if (i+start+1) in self.foldedLines:
				#~ j = self.foldedLines[i]
			#~ print i
			#~ self.document().findBlockByNumber(j+start+1).setVisible(True)
			self.update()
			#~ j+=1
		self.foldedLines.pop(start)
		self.update()
		self.resizeEvent(QResizeEvent(QSize(0,0),self.size()))	

    def findFoldableLines(self):
		#~ print "find"
		if self.lang == None:
			#~ print self.lang
			return
		#~ print self.lang
		#~ print "hola"
		#~ self.foldedLines.clear()
		self.foldableLines.clear()
		lines = self.toPlainText().split('\n')
		#~ print "hola",lines.count()
		for i in range(lines.count()):
			line = lines[i]
			for b in self.lang.blocks:
				sr = QRegExp(b.start)
				
				er = QRegExp(b.end)
				#~ print sr,er
				if sr.indexIn(line) != -1:
					#~ print sr.indexIn(line)
					start = i
					j = start
					encast = 0
					if er.indexIn(line) != -1:
						#~ print er.indexIn(line)
						continue
					while ( not (er.indexIn(line) != -1 and encast == 0) and (j < lines.count())):
						#~ print (not ((er.indexIn(line) != -1) and (encast == 0)) and (j < lines.count()))
						#~ print lines.count(),j
						
						line = lines[j]
						#~ print "hola"
						if sr.indexIn(line) !=-1:
							encast += 1
						if er.indexIn(line) != -1:
							encast -= 1
						j += 1
					self.foldableLines[start]=j-1
					#~ print self.foldableLines
		self.update()
    def lineNumberAreaWidth(self):
        space=self.lineNumberAreaWidthPrimar()+35
        return space
    def lineNumberAreaWidthPrimar(self):
		digits=1
		_max = max(1,self.blockCount())
		while _max >= 10:
			_max = _max/10
			digits+=1
		space=10 + self.fontMetrics().width('9') * digits
		return space
    def updateFoldedLines(self):
		#~ self.foldedLines.clear()
		#~ for aaa in self.foldableLines:
			#~ block= self.document().findBlockByNumber(aaa)
			#~ data=block.userData()
			#~ print data.folded,aaa
			#~ if data.isFolded():
				#~ self.foldedLines[aaa]=self.foldableLines[aaa]
			#~ if not block.isVisible():
				#~ self.foldedLines[aaa]=self.foldableLines[aaa]
		#~ print "folded:",self.foldedLines
		#~ print "foldables:",self.foldableLines		
		#~ return
		
		it = {}
		#~ self.findFoldableLines()
		#~ print "folded"
		for aaa in self.foldedLines:
			#~ print aaa,it,self.foldableLines
			if self.foldableLines.has_key(aaa) and self.foldableLines[aaa] == self.foldedLines[aaa]:
				#~ print "todo bien"
				it[aaa]=self.foldableLines[aaa]
				#~ self.foldedLines.pop(aaa)
			elif self.foldableLines.has_key(aaa+1) and self.foldableLines[aaa+1] == self.foldedLines[aaa]+1:
					#~ aaa+=1
					it[aaa+1]=self.foldableLines[aaa+1]
			elif self.foldableLines.has_key(aaa-1) and self.foldableLines[aaa-1] == self.foldedLines[aaa]-1:
					#~ aaa-=1
					it[aaa-1]=self.foldableLines[aaa-1]
				#~ return
			#~ else:
				#~ it[aaa]=self.foldableLines[aaa]
				#~ print aaa,it,self.foldableLines
		#~ self.update()
		#~ self.foldedLines.clear()
		self.foldedLines=it
		#~ print "folded:",self.foldedLines,it
		#~ print "foldables:",self.foldableLines
    def updateLineNumberAreaWidth(self, newBlockCount):
		self.findFoldableLines()
		self.updateFoldedLines()
		self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)


    def updateLineNumberArea(self, rect, dy):
		#~ 
        #~ print "aca tmb",rect,dy
        
        #~ return
        #~ self.findFoldableLines()
        if dy:
            self.lineNumberArea.scroll(0, dy);
        else:
            self.lineNumberArea.update(0, rect.y(), 
                self.lineNumberArea.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)
        self.update()
    def paintEvent(self,event):
		QPlainTextEdit.paintEvent(self,event)
		for aaa in self.foldedLines:
			tmp=True
			for bbb in self.foldedLines:
				if bbb != aaa and bbb < aaa and self.foldedLines[bbb]>self.foldedLines[aaa]:
					tmp=False
			if tmp:
				bottom = int(self.blockBoundingGeometry(self.document().findBlockByNumber(aaa+1)).top()+self.blockBoundingGeometry(self.document().findBlockByNumber(self.foldedLines[aaa]).next()).height())
				paint = QPainter()
				paint.begin(self.viewport())
				paint.setPen(QPen(Qt.black, 1, Qt.DashLine))
				paint.drawLine(0,bottom,self.width(),bottom)
				paint.end()
			
		
    def resizeEvent(self, e):
        QPlainTextEdit.resizeEvent(self,e)
        self.cr = self.contentsRect()
        self.lineNumberArea.setGeometry(self.cr.left(), 
                                        self.cr.top(), 
                                        self.lineNumberAreaWidth(), 
                                        self.cr.height())

    def match_left(self, block, character, start, found):
        map = {'{': '}', '(': ')', '[': ']'}
        #~ block_jump = 0

        while block.isValid():
            data = block.userData()
            if data is not None:
                braces = data.braces
                N = len(braces)

                for k in range(start, N):
                    if braces[k].character == character:
                        found += 1

                    if braces[k].character == map[character]:
                        if not found:
                            return braces[k].position + block.position()
                        else:
                            found -= 1

                block = block.next()
                #~ block_jump += 1
                start = 0
    
    def match_right(self, block, character, start, found):
        map = {'}': '{', ')': '(', ']': '['}
        #~ block_jump = 0

        while block.isValid():
            data = block.userData()
            #~ print data.valid
            if data is not None:
                braces = data.braces
                #~ print braces

                if start is None:
                    start = len(braces)
                for k in range(start - 1, -1, -1):
                    if braces[k].character == character:
                        found += 1
                    if braces[k].character == map[character]:
                        if found == 0:
                            #~ print "que onda:",braces[k].position,block.position()
                            return braces[k].position + block.position()
                        else:
                            found -= 1
            block = block.previous()
            #~ block_jump += 1
            start = None

    def check_brackets(self,nada):
        left, right = QTextEdit.ExtraSelection(),\
                      QTextEdit.ExtraSelection()

        cursor = self.textCursor()
        block = cursor.block()
        data = block.userData()
        #~ print data
        previous, next = None, None

        if data is not None:
            position = cursor.position()
            block_position = cursor.block().position()
            braces = data.braces
            N = len(braces)
            #~ print N

            for k in range(0, N):
                if braces[k].position == position - block_position or\
                   braces[k].position == position - block_position - 1:
                    previous = braces[k].position + block_position
                    #~ print previous
                    if braces[k].character in ['{', '(', '[']:
                        next = self.match_left(block, braces[k].character, k + 1, 0)
                        
                        #~ print next
                    elif braces[k].character in ['}', ')', ']']:
                        next = self.match_right(block,braces[k].character,k, 0)
                        if nada == True:
							return next
                        #~ print block,braces[k].character,k,next
#                    if next is None:
#                        next = -1
		#~ print previous,next
        if (next is not None and next > 0) \
            and (previous is not None and previous > 0):

            format = QTextCharFormat()

            cursor.setPosition(previous)
            cursor.movePosition(QTextCursor.NextCharacter,
                                QTextCursor.KeepAnchor)
			
            format.setForeground(QColor('blue'))
            format.setBackground(QColor('white'))
            #~ format.setFontWeight(QFont.Bold)
            #~ self.mergeCurrentCharFormat(format)
            #~ cursor.mergeCharFormat(format)
            left.format = format
            left.cursor = cursor

            cursor.setPosition(next)
            cursor.movePosition(QTextCursor.NextCharacter,
                                QTextCursor.KeepAnchor)
            #~ cf=self.textCursor().charFormat()
            #~ cf.setFontWeight(QFont.Bold)
            #~ cursor.setCharFormat(cf);
            format.setForeground(QColor('blue'))
            format.setBackground(QColor('white'))
            #~ format.setFont(QFont("Courier"))
            #~ cursor.mergeCharFormat(format)
            right.format = format
            right.cursor = cursor

            return left, right

        elif previous is not None:
            format = QTextCharFormat()

            cursor.setPosition(previous)
            cursor.movePosition(QTextCursor.NextCharacter,
                                QTextCursor.KeepAnchor)

            format.setForeground(QColor('red'))
            format.setBackground(QColor('white'))
            left.format = format
            left.cursor = cursor
            return (left,)
        elif next is not None:
            format = QTextCharFormat()

            cursor.setPosition(next)
            cursor.movePosition(QTextCursor.NextCharacter,
                                QTextCursor.KeepAnchor)

            format.setForeground(QColor('red'))
            format.setBackground(QColor('white'))
            left.format = format
            left.cursor = cursor
            return (left,)

    def highlightCurrentLine(self):         
        extraSelections=[]
        if not self.isReadOnly():             
            selection = QTextEdit.ExtraSelection()
            lineColor = QColor(169, 169, 169,50)
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        extras = self.check_brackets(False)
        if extras:
            extraSelections.extend(extras)
        #~ cursor = self.textCursor()
        #~ cursor.movePosition(QtGui.QTextCursor.NextCharacter,
                             #~ QtGui.QTextCursor.KeepAnchor)
        #~ text=cursor.selectedText()
        #~ pos1=cursor.position()
        #~ if text in (')', ']', '}'):
            #~ selection=QtGui.QTextEdit.ExtraSelection()
            #~ selection.format.setForeground(QtGui.QColor(QtCore.Qt.blue))
            #~ selection.format.setBackground(QtGui.QColor(169, 169, 255, 0))
            #~ selection.format.setFontWeight(QtGui.QFont.Bold)
            #~ selection.cursor = cursor
            #~ extraSelections.append(selection)
        #~ cursor = self.textCursor()
        #~ cursor.movePosition(QtGui.QTextCursor.PreviousCharacter,
                             #~ QtGui.QTextCursor.KeepAnchor)
        #~ text=cursor.selectedText()
        #~ if text in (')', ']', '}'):
            #~ selection=QtGui.QTextEdit.ExtraSelection()
  #~ 
            #~ selection.format.setForeground(QtGui.QColor(QtCore.Qt.blue))
            #~ selection.format.setBackground(QtGui.QColor(169, 169, 255, 0))
#~ 
            #~ selection.cursor = cursor                              
            #~ extraSelections.append(selection)
       
       
       
       
        #~ elif text in ('(', '[', '{'):
            #~ pos2 = self._match_braces(pos1, text, forward=True)
        #~ else:
            #~ self.setExtraSelections(extraSelections)
            #~ return
        #~ if pos2 is not None:
            #~ self._braces = (pos1, pos2)
            #~ selection = QTextEdit.ExtraSelection()
            #~ selection.format.setForeground(QColor(Qt.blue))
            #~ selection.format.setBackground(QColor(Qt.white))
            #~ selection.cursor = cursor
            #~ extraSelections.append(selection)
            #~ selection = QTextEdit.ExtraSelection()
            #~ selection.format.setForeground(QColor(
                #~ resources.CUSTOM_SCHEME.get('brace-foreground',
                #~ resources.COLOR_SCHEME.get('brace-foreground'))))
            #~ selection.format.setBackground(QColor(
                #~ resources.CUSTOM_SCHEME.get('brace-background',
                #~ resources.COLOR_SCHEME.get('brace-background'))))
            #~ selection.cursor = self.textCursor()
            #~ selection.cursor.setPosition(pos2)
            #~ selection.cursor.movePosition(QTextCursor.NextCharacter,
                             #~ QTextCursor.KeepAnchor)
            #~ extraSelections.append(selection)
        #~ else:
            #~ self._braces = (pos1,)
            #~ selection = QTextEdit.ExtraSelection()
            #~ selection.format.setBackground(QColor(
                #~ resources.CUSTOM_SCHEME.get('brace-background',
                #~ resources.COLOR_SCHEME.get('brace-background'))))
            #~ selection.format.setForeground(QColor(
                #~ resources.CUSTOM_SCHEME.get('brace-foreground',
                #~ resources.COLOR_SCHEME.get('brace-foreground'))))
            #~ selection.cursor = cursor
            #~ extraSelections.append(selection)
        #~ self.setExtraSelections(extraSelections)
        
        #~ if self.errorPos is not None:
                #~ errorSel = QtGui.QTextEdit.ExtraSelection()
                #~ lineColor = QtGui.QColor(QtCore.Qt.red).lighter(160)
                #~ errorSel.format.setBackground(lineColor)
                #~ errorSel.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
                #~ errorSel.cursor = QtGui.QTextCursor(self.document())
                #~ errorSel.cursor.setPosition(self.errorPos)
                #~ errorSel.cursor.clearSelection()
                #~ extraSelections.append(errorSel)

        self.setExtraSelections(extraSelections)                                        			
    def lineNumberAreaPaintEvent(self, event):
		
		#~ QtGui.QPlainTextEdit.paintEvent(self,event)
        painter=QPainter(self.lineNumberArea)
        #~ print "entro aca el joputa"	
        #~ painter.begin(self.lineNumberArea)
        painter.fillRect(event.rect(), Qt.lightGray)
        painter.setPen(QPen(QColor(243, 243, 243)))
        painter.setBrush(QColor(243, 243, 243))
        painter.drawRect(self.lineNumberArea.width()-15,event.rect().top(),self.lineNumberArea.width(),event.rect().bottom())
        
        initialFont = painter.font()
        font = QFont(initialFont)
        font.setWeight(QFont.Bold)
        
        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber();
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())
        
        markers = self.lineNumberArea.markers
        folding = []
        for a in range(blockNumber):
			if self.foldableLines.has_key(a) and blockNumber <= self.foldableLines[a]:
				folding.append(a)
        #~ print "entro",blockNumber,folding
        while block.isValid() and top <= event.rect().bottom():
            
            if block.isVisible() and bottom >= event.rect().top():
				number = blockNumber
				if self.textCursor().blockNumber() == number:
					painter.setFont(font)
				painter.setPen(Qt.black)
				painter.drawText(0, top, self.lineNumberArea.width()-35, 
                    self.fontMetrics().height(),
                    Qt.AlignRight, str(blockNumber+1))
				if self.textCursor().block().blockNumber() == number:
					painter.setFont(initialFont)
				if number in markers:
					self.lineNumberArea.drawMarker(painter,QRect(self.lineNumberArea.width()-30,top,15,self.fontMetrics().height()))
				painter.setPen(Qt.black)
				#~ print folding
				if folding and (number in self.foldableLines.values()):
					painter.drawLine(self.lineNumberArea.width()-7.5,top+(bottom-top)/2,self.lineNumberArea.width(),top+(bottom-top)/2)
					#~ painter.setPen(QtCore.Qt.red)

					painter.drawLine(self.lineNumberArea.width()-7.5,top+(bottom-top)/2,self.lineNumberArea.width()-7.5,top)
					folding.pop()
				if folding and (number > folding[-1]) and (number < self.foldableLines[folding[-1]]):
					#~ painter.setPen(Qt.red)
					painter.drawLine(self.lineNumberArea.width() - 7.5, top, self.lineNumberArea.width() - 7.5, bottom)
					#~ print  number in self.foldableLines.keys()
				if number in self.foldableLines.keys():
					#~ self.updateFoldedLines()
					#~ print self.foldedLines
					if number in self.foldedLines.keys():
						self.lineNumberArea.drawFoldingItem(painter,QRect(self.lineNumberArea.width()-15,self.blockBoundingGeometry(block).translated(self.contentOffset()).top(),15,self.fontMetrics().height()),False)
					else:
						self.lineNumberArea.drawFoldingItem(painter,QRect(self.lineNumberArea.width()-15,self.blockBoundingGeometry(block).translated(self.contentOffset()).top(),15,self.fontMetrics().height()),True)
						folding.append(number)
						#~ print "folding:",folding

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            
            blockNumber+=1

                                        
    #~ def highlightError(self,pos):
        #~ self.errorPos=pos
        #~ self.highlightCurrentLine()

             


if __name__ == "__main__":
    
    #~ import simplejson as json
    #~ from highlighter import Highlighter
    from cpplexer import CppLexer
    #~ from lexer import Lexer
    
    app = QApplication(sys.argv)

    js = CodeEditor()
    #~ js.setStyleSheet("background-color: rgb(255, 255, 255)")
    js.setWindowTitle('pilili')
    hl=CppLexer(js.document())
    js.setLanguage(hl)
    #~ print "hola"
    js.show()

    #~ def validateJSON():
        #~ style=unicode(js.toPlainText())
        #~ if not style.strip(): #no point in validating an empty string
            #~ return
        #~ pos=None
        #~ try:
            #~ json.loads(style)
        #~ except ValueError, e:
            #~ s=str(e)
            #~ print s
            #~ if s == 'No JSON object could be decoded':
                #~ pos=0
            #~ elif s.startswith('Expecting '):
                #~ pos=int(s.split(' ')[-1][:-1])
            #~ elif s.startswith('Extra data'):
                #~ pos=int(s.split(' ')[-3])
            #~ else:
                #~ print 'UNKNOWN ERROR'
                #~ 
        #~ # This makes a red bar appear in the line
        #~ # containing position pos
        #~ js.highlightError(pos)
#~ 
    #~ # Run validateJSON on every keypress
    #~ js.connect(js,QtCore.SIGNAL('textChanged()'),validateJSON)

    sys.exit(app.exec_())
