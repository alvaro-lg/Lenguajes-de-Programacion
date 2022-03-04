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
    literals = {}

    ELSE = r'\b[eE][lL][sS][eE]\b'
    OBJECTID = r'\b[a-z][a-zA-Z0-9]*\b'
    INT_CONST = r'\b[0-9]+\b'
    BOOL_CONST = r'\b([tT][Rr][uU][eE])|([Ff][Aa][Ll][sS][Ee])\b'
    TYPEID = r'\b[tT][yY][pP][eE][iI][dD]\b'
    ELSE = r'\b[eE][lL][sS][eE]\b'
    IF = r'\b[iI][fF]\b'
    FI = r'\b[fF][iI]\b'
    THEN = r'\b[tT][hH][eE][nN]\b'
    NOT = r'\b[nN][oO][tT]\b'
    IN = r'\b[iI][nN]\b'
    CASE = r'\b[cC][aA][sS][eE]\b'
    ESAC = r'\[eE][sS][aA][cC]\b'
    CLASS = r'\b[A-Z][a-zA-Z]*\b'
    INHERITS = r'\b[iI][nN][hH][eE][rR][iI][tT][sS]\b'
    ISVOID = r'\b[iI][sS][vV][oO][iI][dD]\b'
    LET = r'\b[lL][eE][tT]\b'
    LOOP = r'\b[lL][oO][oO][pP]\b'
    NEW = r'\b[nN][eE][wW]\b'
    OF = r'\b[oO][fF]\b'
    POOL = r'\b[pP][oO][oO][lL]\b'
    THEN = r'\b[tT][hH][eE][nN]\b'
    WHILE = r'\b[wW][hH][iI][lL][eE]\b'
    NUMBER = r'\d+'
    STR_CONST = r'\b"\d*"\b'
    LE = r'\b[<lL][eE]\b'
    DARROW = r'\b->\b'
    ASSIGN = r'\b<-\b'



    @_('[Tt][Rr][Uu][Ee]')
    def BOOL_CONST(self, t):
        t.value = True
        return t

    @_('[Ff][Aa][Ll][Ss][Ee]')
    def BOOL_CONST(self, t):
        t.value = False
        return t

    @_('\d')
    def NUMBER(self, t):
        t.value = int(t)
        return t

    CARACTERES_CONTROL = [bytes.fromhex(i+hex(j)[-1]).decode('ascii')
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