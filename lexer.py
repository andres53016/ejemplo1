#! /usr/bin/python
#-*- coding: utf-8 -*- 
#
# This file is part of the Pililí project
#
# Copyright © 2012 by Pablo Andrés Smola
#
# Pililí is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# Pililí is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pililí. If not, see <http://www.gnu.org/licenses/>.

from PyQt4.QtCore import QRegExp, QString,QVariant,QStringList
from PyQt4.QtGui import QSyntaxHighlighter,QTextCharFormat,QTextDocument,QFont,QTextBlockUserData
class Lexer(QSyntaxHighlighter):
	def __init__(self,name,document):
		self.init= False
		self.name = name
		self.entities=[]
		self.initialized=False
		self.styles=[]
		self.blocks=[]
		self.braces = QRegExp('(\{|\}|\(|\)|\[|\])')
		self.font=QFont()
		self.Default=0
		QSyntaxHighlighter.__init__(self,document)
	def highlightBlock(self,text):
		braces = self.braces
		block_data = TextBlockData()

		# Brackets
		index = braces.indexIn(text, 0)

		while index >= 0:
			matched_brace = str(braces.capturedTexts()[0])
			info = BracketsInfo(matched_brace, index)
			block_data.insert_brackets_info(info)
			index = braces.indexIn(text, index + 1)

		self.setCurrentBlockUserData(block_data)
		for en in self.entities:
			self.highlightEntity(text,en)
		for b in self.blocks:
			self.highlightRegion(text,b)
	def highlightRegion(self,text,block):
		if block.style == self.Default:
			return
		startId=0
		self.setCurrentBlockState(0)
		start=QRegExp(block.start)
		end=QRegExp(block.end)
		if self.previousBlockState() != 1:
			startId= start.indexIn(text)
		while startId >= 0:
			endId=end.indexIn(text,startId)
			if endId == -1:
				self.setCurrentBlockState(1)
				length=text.length()-startId
			else:
				length=endId - startId +end.matchedLength()
			self.setFormat(startId,length,self.style(block.style))
			startId=start.indexIn(text,startId+length)
	def highlightEntity(self,text,entity):
		if entity.style == self.Default:
			return
		expression=QRegExp(entity.pattern)
		index=expression.indexIn(text)
		while index>=0:
			length =expression.matchedLength()
			self.setFormat(index,length,self.style(entity.style))
			index=expression.indexIn(text,index+length)
	def makeEntities(self,keywords,style,autoBound=True,autoReplace=True):
		out=[]
		specKws=QStringList([ "\\" , "+" ,"?","*","^","$","!" ,"[","]", "(" ,")" ,"{" ,"}", "." , "|"])
		for s in keywords:
			b = Entity("",0)
			if autoReplace:
				for exp in specKws:
					if exp in s:
						s.replace(exp,"\\"+exp)
			if autoBound:
				b.pattern=QRegExp("\\b"+s+"\\b")
			else:
				b.pattern=QRegExp(s)
			b.style=style
			out.append(b)
		return out
	def setFont(self,f):
		self.font=f

		
class Block():
	def __init__( self, start,end,style):
		self.start = start
		self.end = end
		self.style= style
class Entity():
	def __init__( self, pattern,style):
		self.pattern=pattern
		self.style=style

class BracketsInfo:
	def __init__(self, character, position):
		self.character = character
		self.position  = position

class TextBlockData(QTextBlockUserData):
	def __init__(self, parent = None):
		super(TextBlockData, self).__init__()
		self.braces = []
		self.valid = False
		#~ self.folded=False

	def insert_brackets_info(self, info):
		self.valid = True
		self.braces.append(info)
		#~ self.folded=True

	def isValid(self):
		return self.valid
	#~ def isFolded(self):
		#~ return self.folded
