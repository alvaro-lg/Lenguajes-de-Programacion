# coding: utf-8

from sly import Lexer
import os
import re
import sys


class CoolLexer(Lexer):
    tokens = {OBJECTID, INT_CONST, BOOL_CONST, TYPEID,
              ELSE, IF, FI, THEN, NOT, IN, CASE, ESAC, CLASS,
              INHERITS, ISVOID, LET, LOOP, NEW, OF,
              POOL, THEN, WHILE, NUMBER, STR_CONST, LE, DARROW, ASSIGN}
    ignore = '\t '
    literals = {'=', '+', '-', '*', '/', '(', ')', '"', '\\', '$', '{', '<', '>', ':', '~', ';', '}', '.', ',', '@'}

    ELSE = r'[eE][lL][sS][eE]\b'
    IF = r'[iI][fF]\b'
    FI = r'[fF][iI]\b'
    THEN = r'[tT][hH][eE][nN]\b'
    NOT = r'[nN][oO][tT]\b'
    IN = r'[iI][nN]\b'
    CASE = r'[cC][aA][sS][eE]\b'
    ESAC = r'\[eE][sS][aA][cC]\b'
    CLASS = r'[cC][lL][aA][sS][sS]\b'
    INHERITS = r'[iI][nN][hH][eE][rR][iI][tT][sS]\b'
    ISVOID = r'[iI][sS][vV][oO][iI][dD]\b'
    LET = r'[lL][eE][tT]\b'
    LOOP = r'[lL][oO][oO][pP]\b'
    NEW = r'[nN][eE][wW]\b'
    OF = r'[oO][fF]\b'
    POOL = r'[pP][oO][oO][lL]\b'
    WHILE = r'[wW][hH][iI][lL][eE]\b'
    # NUMBER = r'\d+'
    # TODO STRING_CONST y StringLexer
    LE = r'\<='
    DARROW = r'\=>'
    ASSIGN = r'\<-'

    @_(r't[rR][uU][eE]\b|f[aA][lL][sS][eE]\b')
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
    def lineBr(self, t):
        self.lineno += t.value.count('\n')

    @_(r'_|!|#|\$|\%|\^|\&|\>|\?|`|\[|\]|\|')
    def ERROR(self, t):
        t.value = '\"' + t.value + '\"'
        return t

    @_(r'\001|\002|\003|\004')
    def error_1(self, t):
        t.type = "ERROR"
        if t.value == '\001':
            t.value = "\"\\001\""
        if t.value == '\002':
            t.value = "\"\\002\""
        if t.value == '\003':
            t.value = "\"\\003\""
        if t.value == '\004':
            t.value = "\"\\004\""
        return t

    @_(r'\x00')
    def error_null_code(self, t):
        t.type = "ERROR"
        t.value = "\"" + "\\000" + "\""
        return t

    @_(r'\\')
    def error_barra(self, t):
        t.type = "ERROR"
        t.value = "\"" + "\\\\" + "\""
        return t

    @_(r'(\*\))')
    def error_fin_comment(self, t):
        t.type = "ERROR"
        t.value = "\"Unmatched " + t.value + "\""
        return t

    CARACTERES_CONTROL = [bytes.fromhex(i + hex(j)[-1]).decode('ascii')
                          for i in ['0', '1']
                          for j in range(16)] + [bytes.fromhex(hex(127)[-2:]).decode("ascii")]

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
                result = f'#{token.lineno} \'{token.type}\' '
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
