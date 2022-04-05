# coding: utf-8

from Lexer import CoolLexer
from sly import Parser
import sys
import os
from Clases import *


class CoolParser(Parser):
    nombre_fichero = ''
    tokens = CoolLexer.tokens
    debugfile = "salida.out"
    errores = []

    @_("programa clase ';'")
    def programa(self, p):
        pass

    @_("clase ';'")
    def programa(self, p):
        pass

