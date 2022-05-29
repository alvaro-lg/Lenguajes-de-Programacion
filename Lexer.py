# coding: utf-8

from sly import *
import os
import re
import sys

class CommentLexer(Lexer):
    tokens = {ERROR}
    _level = 0

    @_(r'\*\)\Z')
    def no_fin(self, t):
        if self._level == 0:
            self.begin(CoolLexer)
        else:
            self._level = 0
            t.type = 'ERROR'
            self.begin(CoolLexer)
            t.value = '"EOF in comment"'
            return t


    @_(r'\*\)')
    def cierraComentario(self, t):
        if self._level == 0:
            self.begin(CoolLexer)
        else:
            self._level -= 1

    @_(r'\(\*')
    def in_comment(self, t):
        self._level += 1

    @_(r'.\Z')
    def eof_in_comment(self, t):
        t.type = 'ERROR'
        self.begin(CoolLexer)
        t.value = '"EOF in comment"'
        return t

    @_(r'\n\Z')
    def eof_in_comment_2(self, t):
        t.type = 'ERROR'
        self.begin(CoolLexer)
        t.lineno += 1
        t.value = '"EOF in comment"'
        return t

    @_(r'.')
    def ignoreChar(self, t):
        pass

    @_(r'\n|\r')
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

class StringLexer(Lexer):

    tokens = {}

    _string = '"'
    _str_error = False
    _str_len = 0

    @_(r'"')
    def cierra_string(self, t):
        if self._str_len > 1024:
            t.type = 'ERROR'
            t.value = '"String constant too long"'
            self._string = '"'
            self._str_len = 0
            self.begin(CoolLexer)
            return t

        t.value = self._string + '"'
        t.type = 'STR_CONST'
        self._string = '"'
        self._str_len = 0
        if self._str_error:
            self._str_error = False
            self.begin(CoolLexer)
            return t
        self.begin(CoolLexer)
        return t

    @_(r'.\Z|.\\\n\Z|\\\"\Z')
    def eof_error(self, t):
        self._str_error = False
        t.type = "ERROR"
        t.lineno += t.value.count('\n')
        self._string = '"'
        self._str_len = 0
        self.begin(CoolLexer)
        t.value = '"EOF in string constant"'
        return t


    @_(r'\\\x00')
    def escaped_null(self, t):
        self._str_error = True
        self._str_len = 0
        t.type = "ERROR"
        t.value = '"String contains escaped null character."'
        return t

    @_(r'\x00')
    def error_null(self, t):
        self._str_len = 0
        self._str_error = True
        t.type = 'ERROR'
        t.value = '"String contains null character."'
        return t

    @_(r'\x0d')
    def carriage_return_0(self, t):
        self._string += r'\015'
        self._str_len += 1

    @_(r'\x1b')
    def carriage_return(self, t):
        self._string += r'\033'
        self._str_len += 1
        print(self._string)

    @_(r'\\[fbtn"\\]')
    def scpecialChar(self, t):
        self._string += t.value
        self._str_len += 1

    @_(r'\\\n')
    def ignore_newline(self, t):
        self._str_len += 1
        self.lineno += 1

    @_(r'\\\n')
    def backslash(self, t):
        self._str_len += 1
        self._string += '\\n'
        self.lineno += t.value.count('\n')


    @_(r'[^\\\n]\n|(\\\\)*\n')
    def unterminated_string(self, t):
        self._str_len = 0
        if self._str_error:
            self._str_error = False
            self.begin(CoolLexer)
            t.lineno += t.value.count('\n')
            self.lineno = t.lineno
            self._string = '"'
            return

        t.lineno += t.value.count('\n')
        self.lineno = t.lineno
        self._string = '"'
        t.type = "ERROR"
        self.begin(CoolLexer)
        t.value = '"Unterminated string constant"'
        return t

    @_(r'\\\w')
    def escaped_char(self, t):
        self._str_len += 1
        self._string += t.value

    @_(r'\\"')
    def inline_quotes(self, t):
        self._str_len += 1
        self._string += t.value

    @_(r'\t|\\\t')
    def tabulador(self, t):
        self._str_len += 1
        self._string += '\\t'

    @_(r'\\-')
    def guion(self, t):
        self._string += "-"
        self._str_len += 1

    @_(r'\n')
    def error(self, t):
        return t

    @_(r'\013')
    def error_013(self, t):
        self._string += '\\013'
        self._str_len += 1

    @_(r'\022')
    def error_022(self, t):
        self._string += '\\022'
        self._str_len += 1

    @_(r'\\\010')
    def backspace(self, t):
        self._str_len += 1
        self._string += '\\b'

    @_(r'\f|\\\f')
    def form_feed(self, t):
        self._str_len += 1
        self._string += "\\f"

    @_(r'\\[a-zA-Z0-9]')
    def escaped_char(self, t):
        self._str_len += 1
        self._string += t.value[1:]

    @_(r'.')
    def ignoreChar(self, t):
        self._str_len += 1
        self._string += t.value

    def addChar(self, t):
        self._str_len += 1
        self._string += t.value

class CoolLexer(Lexer):
    tokens = {OBJECTID, INT_CONST, BOOL_CONST, TYPEID,
              ELSE, IF, FI, THEN, NOT, IN, CASE, ESAC, CLASS,
              INHERITS, ISVOID, LET, LOOP, NEW, OF,
              POOL, THEN, WHILE, NUMBER, STR_CONST, LE, DARROW, ASSIGN}
    literals = {';', '=', '+', '-', '*', '/', '(', ')', '"', '\\', '$', '{', '<', '>', ':', '~', '}', '.', ',', '@'}
    ignore = '\t '



    ELSE = r'\b[eE][lL][sS][eE]\b'
    IF = r'[iI][fF]\b'
    FI = r'[fF][iI]\b'
    THEN = r'[tT][hH][eE][nN]\b'
    NOT = r'[nN][oO][tT]\b'
    IN = r'[iI][nN]\b'
    CASE = r'[cC][aA][sS][eE]\b'
    ESAC = r'[eE][sS][aA][cC]\b'
    CLASS = r'[cC][lL][aA][sS][sS]\b'
    INHERITS = r'[iI][nN][hH][eE][rR][iI][tT][sS]\b'
    ISVOID = r'[iI][sS][vV][oO][iI][dD]\b'
    LET = r'[lL][eE][tT]\b'
    LOOP = r'[lL][oO][oO][pP]\b'
    NEW = r'[nN][eE][wW]\b'
    OF = r'[oO][fF]\b'
    POOL = r'[pP][oO][oO][lL]\b'
    WHILE = r'[wW][hH][iI][lL][eE]\b'
    LE = r'\<='
    DARROW = r'\=>'
    ASSIGN = r'\<-'

    @_(r'\(\*')
    def blockComment(self, t):
        self.begin(CommentLexer)

    @_(r'"')
    def string(self, t):
        self.begin(StringLexer)

    @_(r'--.*')
    def lineComment(self, t):
        pass

    @_(r'\*\)')
    def unmatched_block_comment(self, t):
        t.type = "ERROR"
        t.value = '"Unmatched *)"'
        return t

    @_(r't[rR][uU][eE]\b|f[aA][lL][sS][eE]')
    def BOOL_CONST(self, t):
        t.value = t.value.lower() == 'true'
        return t

    @_(r'[0-9]+')
    def INT_CONST(self, t):
        return t

    @_(r'[A-Z][a-zA-Z0-9_]*')
    def TYPEID(self, t):
        t.value = str(t.value)
        return t

    @_(r'[a-z][a-zA-Z0-9_]*')
    def OBJECTID(self, t):
        return t


    @_(r'\n|\r')
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    @_(r'\d+')
    def NUMBER(self, t):
        t.value = int(t.value)
        return t

    @_(r'_|!|#|\$|\%|\^|\&|\>|\?|`|\[|\]|\|')
    def ERROR(self, t):
        t.type = 'ERROR'
        t.value = '"' + t.value + '"'
        return t

    @_(r'\\')
    def backslash_error(self, t):
        t.type = "ERROR"
        t.value = "\"" + "\\\\" + "\""

        return t

    @_(r'\000')
    def err_000(self, t):
        t.type = 'ERROR'
        t.value = '"\\000"'
        return t

    @_(r'\001')
    def err_001(self, t):
        t.type = 'ERROR'
        t.value = '"\\001"'
        return t

    @_(r'\002')
    def err_002(self, t):
        t.type = 'ERROR'
        t.value = '"\\002"'
        return t

    @_(r'\003')
    def err_003(self, t):
        t.type = 'ERROR'
        t.value = '"\\003"'
        return t

    @_(r'\004')
    def err_004(self, t):
        t.type = 'ERROR'
        t.value = '"\\004"'
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