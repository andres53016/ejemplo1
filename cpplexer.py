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

from lexer import Lexer,Block,Entity
from PyQt4.QtGui import QSyntaxHighlighter,QTextCharFormat,QTextDocument,QFont,QBrush,QColor
from PyQt4.QtCore import QRegExp, QString,QVariant,QStringList,Qt

class CppLexer(Lexer):
	def __init__(self,doc):
		(self.Default,self.Keywords,self.Operators,self.Number,self.Comments,self.MComments,self.String,self.Character,self.Preprocessor)=range(9)
		Lexer.__init__(self,"C++",doc)

	def initialize(self):
		self.font=QFont("Mono")
		self.font.setKerning(True)
		self.font.setPointSize(12)
		self.styles=[self.Default,self.Keywords,self.Operators,self.Number,self.Comments,self.String,self.Character]
		block=Block("^[^{]*\\{.*$","^[^}]*\\}.*$",self.Default)
		self.blocks.append(block)
		comments=Block( "/\\*","\\*/",self.Comments)
		self.blocks.append(comments)
		self.entities+=self.makeEntities(QStringList(["and" , "and_eq" , "asm" , "auto"
                                    , "bitand" , "bitor" , "bool" , "break"
                                    , "case" , "catch" , "char" , "class" , "compl" , "const" , "const_cast" , "continue"
                                    , "default" , "delete" , "do" , "double" , "dynamic_cast"
                                    , "else" , "enum" , "explicit" , "export" , "extern"
                                    , "false" , "float" , "for" , "friend"
                                    , "goto"
                                    , "if" , "inline" , "int"
                                    , "long"
                                    , "mutable"
                                    , "namespace" , "new" , "not" , "not_eq"
                                    , "operator" , "or" , "or_eq"
                                    , "private" , "protected" , "public"
                                    , "register" , "reinterpret_cast" , "return"
                                    , "short" , "signed" , "sizeof" , "static" , "static_cast" , "struct" , "switch" , "size_t"
                                    , "template" , "this" , "throw" , "true" , "try" , "typedef" , "typeid" , "typename"
                                    , "union" , "unsigned" , "using"
                                    , "virtual" , "void" , "volatile"
                                    , "wchar_t" , "while"
                                    , "xor" , "xor_eq"]), self.Keywords,True,True)		
		num=Entity(QRegExp("[0-9][^\\s]*"),self.Number)
		self.entities.append(num)
		self.entities+=self.makeEntities(QStringList(["+" , "-" , "*" , "/" , "^" , "." , ">" , "<" , "(" , ")" , "[" , "]" , "%" , "!" , "=" , "{" , "}" , "&" , "," , "?" , ";" , ":" , "|"]), self.Operators, False,True)
		com=Entity(QRegExp("//.*"),self.Comments)
		self.entities.append(com)
		_str=Entity(QRegExp('\".*\"'),self.String)
		self.entities.append(_str)
		_chr=Entity(QRegExp("\'.\'"),self.Character)
		self.entities.append(_chr)
		preproc=Entity(QRegExp("^\\s*#.*(\\\\\\n.*)*$"),self.Preprocessor)
		self.entities.append(preproc)
		self.initialized=True
		
	def style(self,num):
		_format = QTextCharFormat()
		_format.setFont(self.font)
		if num == self.Keywords:
			_format.setFontWeight(QFont.Bold)
			_format.setForeground(QBrush(QColor(0, 0, 251)))
		elif num == self.Number:
			_format.setForeground(QBrush(QColor(0,128,0)))
		elif num == self.Operators:
			_format.setForeground(QBrush(Qt.black))
			#~ _format.setFontWeight(QFont.Bold)
		elif num == self.MComments or num == self.Comments:
			_format.setForeground(QBrush(QColor(0, 128, 0)))
		elif num == self.String or num == self.Character:
			_format.setForeground(QBrush(QColor(128, 128, 128)))
		else:
			_format.setForeground(QBrush(QColor(128, 64, 0)))
		return _format
