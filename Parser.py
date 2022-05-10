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

    precedence = (
        ('right', 'ASSIGN'),
        ('right', 'NOT'),
        ('nonassoc', 'LE', '<', '='),
        ('left', '+', '-'),
        ('right', '~'),
        ('left', '*', '/'),
        ('left', 'ISVOID'),
        ('right', 'UMINUS'),
        ('right', '@'),
        ('right', '.'),
    )

    # Programa

    @_("programa clase ';'")
    def programa(self, p):
        return Programa(p.lineno, p.programa.secuencia + [p.clase])

    @_("clase ';'")
    def programa(self, p):
        return Programa(p.lineno, [p.clase])

    # Clase

    @_('CLASS TYPEID INHERITS TYPEID "{" optional_feature "}"')
    def clase(self, p):
        return Clase(p.lineno, p.TYPEID0, p.TYPEID1, self.nombre_fichero, p.optional_feature)

    @_('CLASS TYPEID INHERITS TYPEID "{" "}"')
    def clase(self, p):
        return Clase(p.lineno, p.TYPEID0, p.TYPEID1, self.nombre_fichero, [])

    @_('CLASS TYPEID "{" optional_feature "}"')
    def clase(self, p):
        return Clase(p.lineno, p.TYPEID, "Object", self.nombre_fichero, p.optional_feature)

    @_('CLASS TYPEID "{" "}"')
    def clase(self, p):
        return Clase(p.lineno, p.TYPEID, "Object", self.nombre_fichero, [])

    @_('feature ";"')
    def optional_feature(self, p):
        return [p.feature]

    @_('optional_feature feature ";"')
    def optional_feature(self, p):
        return p.optional_feature + [p.feature]

    # Feature

    @_('OBJECTID ":" TYPEID ASSIGN expr')
    def feature(self, p):
        return Atributo(p.lineno, p.OBJECTID, p.TYPEID, p.expr)

    @_('OBJECTID ":" TYPEID')
    def feature(self, p):
        return Atributo(p.lineno, p.OBJECTID, p.TYPEID, NoExpr(p.lineno))

    @_('OBJECTID "(" formal optional_formal ")" ":" TYPEID "{" expr "}"')
    def feature(self, p):
        return Metodo(p.lineno, p.OBJECTID, p.TYPEID, p.expr, [p.formal] + p.optional_formal)

    @_('OBJECTID "(" formal ")" ":" TYPEID "{" expr "}"')
    def feature(self, p):
        return Metodo(p.lineno, p.OBJECTID, p.TYPEID, p.expr, [p.formal])

    @_('OBJECTID "(" ")" ":" TYPEID "{" expr "}"')
    def feature(self, p):
        return Metodo(p.lineno, p.OBJECTID, p.TYPEID, p.expr, [])

    @_('"," formal')
    def optional_formal(self, p):
        return [p.formal]

    @_('"," formal optional_formal')
    def optional_formal(self, p):
        return [p.formal] + p.optional_formal

    # Formal

    @_('OBJECTID ":" TYPEID')
    def formal(self, p):
        return Formal(p.lineno, p.OBJECTID, p.TYPEID)

    # Expr

    @_('"-" expr %prec UMINUS')
    def expr(self, p):
        return Entero(p.lineno, -int(p.expr))

    @_('BOOL_CONST')
    def expr(self, p):
        return Booleano(p.lineno, (bool)(p.BOOL_CONST))

    @_('STR_CONST')
    def expr(self, p):
        return String(p.lineno, p.STR_CONST)

    @_('INT_CONST')
    def expr(self, p):
        return Entero(p.lineno, int(p.INT_CONST))

    @_('OBJECTID')
    def expr(self, p):
        return Objeto(p.lineno, p.OBJECTID)

    @_('"(" expr ")"')
    def expr(self, p):
        return p.expr

    @_('NOT expr')
    def expr(self, p):
        return Not(p.lineno, p.expr)

    @_('expr "=" expr')
    def expr(self, p):
        return Igual(p.lineno, p.expr0, p.expr1)

    @_('expr LE expr')
    def expr(self, p):
        return LeIgual(p.lineno, p.expr0, p.expr1)

    @_('expr "<" expr')
    def expr(self, p):
        return Menor(p.lineno, p.expr0, p.expr1)

    @_('"~" expr')
    def expr(self, p):
        return Neg(p.lineno, p.expr)

    @_('expr "/" expr')
    def expr(self, p):
        return Division(p.lineno, p.expr0, p.expr1)

    @_('expr "*" expr')
    def expr(self, p):
        return Multiplicacion(p.lineno, p.expr0, p.expr1)

    @_('expr "-" expr')
    def expr(self, p):
        return Resta(p.lineno, p.expr0, p.expr1)

    @_('expr "+" expr')
    def expr(self, p):
        return Suma(p.lineno, p.expr0, p.expr1)

    @_('ISVOID expr')
    def expr(self, p):
        return EsNulo(p.lineno, p.expr)

    @_('NEW TYPEID')
    def expr(self, p):
        return Nueva(p.lineno, p.TYPEID)

    @_('CASE expr OF lista_asig ESAC')
    def expr(self, p):
        return [RamaCase(p.lineno, p.expr, p.lista_asig)]

    @_('OBJECTID ":" TYPEID DARROW expr ";"')
    def lista_asig(self, p):
        return [RamaCase(p.lineno, p.OBJECTID, p.TYPEID, p.expr)]

    @_('OBJECTID ":" TYPEID DARROW expr ";" lista_asig')
    def lista_asig(self, p):
        return [RamaCase(p.lineno, p.OBJECTID, p.TYPEID, p.expr)] + p.lista_asig

    # let
    @_('LET OBJECTID ":" TYPEID ASSIGN expr IN expr')
    def expr(self, p):
        return Let(p.lineno, p.OBJECTID, p.TYPEID, p.expr0, p.expr1)

    @_('LET OBJECTID ":" TYPEID IN expr')
    def expr(self, p):
        return Let(p.lineno, p.OBJECTID, p.TYPEID, NoExpr(p.lineno), p.expr)

    @_('LET OBJECTID ":" TYPEID ASSIGN expr optional_assigns IN expr')
    def expr(self, p):
        cuerpo = p.expr1
        for i in reversed([p.expr0] + p.optional_assigns):
            cuerpo = Let(p.lineno, p.OBJECTID, p.TYPEID, i, cuerpo)
        return cuerpo

    @_('LET OBJECTID ":" TYPEID optional_assigns IN expr')
    def expr(self, p):
        cuerpo = p.expr
        for i in reversed(p.optional_assigns):
            cuerpo = Let(p.lineno, p.OBJECTID, p.TYPEID, i, cuerpo)
        return cuerpo

    @_('"," OBJECTID ":" TYPEID ASSIGN expr optional_assigns')
    def optional_assigns(self, p):
        return [p.OBJECTID, p.TYPEID, p.expr] + p.optional_assigns

    @_('"," OBJECTID ":" TYPEID optional_assigns')
    def optional_assigns(self, p):
        return [p.OBJECTID, p.TYPEID, NoExpr(p.lineno)] + p.optional_assigns

    @_('"," OBJECTID ":" TYPEID ASSIGN expr')
    def optional_assigns(self, p):
        return [p.OBJECTID, p.TYPEID, p.expr]

    @_('"," OBJECTID ":" TYPEID')
    def optional_assigns(self, p):
        return [p.OBJECTID, p.TYPEID, NoExpr(p.lineno)]

    # {[expr;]+}
    @_('"{" lista_expr "}"')
    def expr(self, p):
        return Bloque(p.lineno, p.lista_expr)

    @_('expr ";"')
    def lista_expr(self, p):
        return [p.expr]

    @_('lista_expr expr ";"')
    def lista_expr(self, p):
        return p.lista_expr + [p.expr]

    # while
    @_('WHILE expr LOOP expr POOL')
    def expr(self, p):
        return Bucle(p.lineno, p.expr0, p.expr1)
    # if
    @_('IF expr THEN expr ELSE expr FI')
    def expr(self, p):
        return Condicional(p.lineno, p.expr0, p.expr1, p.expr2)

    # ID([expr[,expr]*])
    @_('OBJECTID "(" expr ")"')
    def expr(self, p):
        return LlamadaMetodo(p.lineno, Objeto(p.lineno, "self"), p.OBJECTID, [p.expr])

    @_('OBJECTID "(" expr optional_expressions ")"')
    def expr(self, p):
        return LlamadaMetodo(p.lineno, Objeto(p.lineno, "self"), p.OBJECTID, [p.expr] + p.optional_expressions)

    @_('OBJECTID "(" ")"')
    def expr(self, p):
        return LlamadaMetodo(p.lineno, Objeto(p.lineno, "self"), p.OBJECTID, [])

    @_('"," expr')
    def optional_expressions(self, p):
        return [p.expr]

    @_('"," expr optional_expressions')
    def optional_expressions(self, p):
        return [p.expr] + p.optional_expressions

    @_('expr "@" TYPEID "." OBJECTID "(" ")"')
    def expr(self, p):
        return LlamadaMetodoEstatico(p.lineno, p.expr, p.TYPEID, p.OBJECTID, [])

    @_('expr "@" TYPEID "." OBJECTID "(" expr ")"')
    def expr(self, p):
        return LlamadaMetodoEstatico(p.lineno, p.expr0, p.TYPEID, p.OBJECTID, [p.expr1])

    @_('expr "@" TYPEID "." OBJECTID "(" expr optional_expressions ")"')
    def expr(self, p):
        return LlamadaMetodoEstatico(p.lineno, p.expr0, p.TYPEID, p.OBJECTID, [p.expr1] + p.optional_expressions)

    @_('expr "." OBJECTID "(" ")"')
    def expr(self, p):
        return LlamadaMetodo(linea=p.lineno, cuerpo=p.expr, nombre_metodo=p.OBJECTID, argumentos=[])

    @_('expr "." OBJECTID "(" expr ")"')
    def expr(self, p):
        return LlamadaMetodo(p.lineno, p.expr0, p.OBJECTID, [p.expr1])

    @_('expr "." OBJECTID "(" expr optional_expressions ")"')
    def expr(self, p):
        return LlamadaMetodo(p.lineno, p.expr0, p.OBJECTID, [p.expr1] + p.optional_expressions)

    # ID <- expr
    @_('OBJECTID ASSIGN expr')
    def expr(self, p):
        return Asignacion(p.lineno, p.OBJECTID, p.expr)

    #Errores

    @_('CLASS TYPEID "{" error "}"')
    def clase(self, p):
        return []

    @_('IF expr THEN error FI')
    def expr(self, p):
        return []

    @_('IF expr THEN expr ELSE expr error')
    def expr(self, p):
        return []

    @_('OBJECTID "(" ")" ":" TYPEID "{" error "}"')
    def feature(self, p):
        return []

    @_('OBJECTID "(" optional_formal ")" ":" TYPEID "{" error "}" ')
    def feature(self, p):
        return []

    @_('error ";"')
    def optional_feature(self, p):
        return []

    @_('error ";"')
    def lista_expr(self, p):
        return []

    def error(self, p):
        # print(p)
        if p is None:
            self.errores.append(f'"{self.nombre_fichero}", line 0: syntax error at or near EOF')
        elif p.type in ['TYPEID', 'OBJECTID', 'INT_CONST']:
            self.errores.append(
                f'"{self.nombre_fichero}", line {p.lineno}: syntax error at or near {p.type} = {p.value}')
        elif p.type in ['OF', 'DARROW', 'ESAC', 'FI', 'ELSE', 'LOOP', 'POOL']:
            self.errores.append(f'"{self.nombre_fichero}", line {p.lineno}: syntax error at or near {p.type}')
        else:
            self.errores.append(f'"{self.nombre_fichero}", line {p.lineno}: syntax error at or near \'{p.value}\'')
