# coding: utf-8

from sly import Lexer
import os
import re
import sys

class CommentLexer(Lexer):
    tokens = {}

    @_(r'\*\)')
    def cierraComentario(self, t):
        self.begin(CoolLexer)

    @_(r'.')
    def ignoreChar(self, t):
        pass

    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

class StringLexer(Lexer):

    tokens = {}

    _string = '"'

    @_(r'"')
    def cierraString(self, t):
        t.value = self._string + '"'
        t.type = 'STR_CONST'
        self._string = '"'
        self.begin(CoolLexer)
        return t

    @_(r'\\\n')
    def ignore_newline(self, t):
        self.lineno += 1

    @_(r'\\\w')
    def escaped_char(self, t):
        self._string += t.value
        
    @_(r'\\"')
    def inline_quotes(self, t):
        self._string += t.value

    @_(r'\n')
    def error(self, t):
        return t

    @_(r'.')
    def ignoreChar(self, t):
        self._string += t.value

class CoolLexer(Lexer):
    tokens = {OBJECTID, INT_CONST, BOOL_CONST, TYPEID,
              ELSE, IF, FI, THEN, NOT, IN, CASE, ESAC, CLASS,
              INHERITS, ISVOID, LET, LOOP, NEW, OF,
              POOL, THEN, WHILE, NUMBER, STR_CONST, LE, DARROW, ASSIGN}
    ignore = '\t '

    literals = {'=', '+', '-', '*', '/', '(', ')', '"', '\\', '$', '{', '<', '>', ':', '~', ';', '}', '.', ',', '@'}

    ELSE = r'\b[eE][lL][sS][eE]\b'
    IF = r'[iI][fF]\b'
    FI = r'[fF][iI]\b'
    THEN = r'[tT][hH][eE][nN]\b'
    NOT = r'[nN][oO][tT]\b'
    IN = r'[iI][nN]\b'
    CASE = r'[cC][aA][sS][eE]\b'
    ESAC = r'[eE][sS][aA][cC]\b'
    CLASS = r'[cC][lL][aA][sS][sS]\b'
    INHERITS = r'[iI][nN][hH][eE][rR][iI][tT][sS]'
    ISVOID = r'[iI][sS][vV][oO][iI][dD]'
    LET = r'[lL][eE][tT]'
    LOOP = r'[lL][oO][oO][pP]'
    NEW = r'[nN][eE][wW]'
    OF = r'[oO][fF]'
    POOL = r'[pP][oO][oO][lL]'
    WHILE = r'[wW][hH][iI][lL][eE]'
    # TODO STRING_CONST y StringLexer
    LE = r'\<='
    DARROW = r'\=>'
    ASSIGN = r'\<-'

    @_(r'\(\*')
    def blockComment(self, t):
        self.begin(CommentLexer)

    @_(r'"')
    def string(self, t):
        self.begin(StringLexer)

    @_(r'--.*\n')
    def lineComment(self, t):
        self.lineno += 1
        pass

    @_(r't[rR][uU][eE]\b|f[aA][lL][sS][eE]')
    def BOOL_CONST(self, t):
        t.value = t.value.lower() == 'true'
        return t

    @_(r'[0-9]+')
    def INT_CONST(self, t):
        t.value = int(t.value)
        return t

    @_(r'[A-Z][a-zA-Z0-9_]*')
    def TYPEID(self, t):
        t.value = str(t.value)
        return t

    @_(r'[a-z][a-zA-Z0-9_]*')
    def OBJECTID(self, t):
        return t

    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    @_(r'\d+')
    def NUMBER(self, t):
        t.value = int(t.value)
        return t

    @_(r'_|\!|\?')
    def ERROR(self, t):
        return t

    def error(self, t):
        print('Line %d: Bad character %r' % (self.lineno, t.value[0]))
        self.index += 1

    def salida(self, texto):
        list_strings = []
        for token in lexer.tokenize(texto):
            result = f'#{token.lineno} {token.type} '
            if token.type == 'OBJECTID':
                result += f"{token.value}"
            elif token.type == 'BOOL_CONST':
                result += "true" if token.value else "false"
            elif token.type == 'TYPEID':
                result += f"{str(token.value)}"
            elif token.type in self.literals:
                result = f'#{token.lineno} \'{token.type}\''
            elif token.type == 'STR_CONST':
                result += token.value
            elif token.type == 'INT_CONST':
                result += str(token.value)
            elif token.type == 'ERROR':
                result = f'#{token.lineno} {token.type} {token.value}'
            else:
                result = f'#{token.lineno} {token.type}'
            list_strings.append(result)
        return list_strings


lexer = CoolLexer()
lexer.salida('Else')
