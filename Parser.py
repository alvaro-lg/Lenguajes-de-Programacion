# coding: utf-8
__author__ = "Alvaro Lopez, Jairo Gonzalez, Jorge Piris"

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
        return Programa(linea=p.lineno, secuencia=p.programa.secuencia + [p.clase])

    @_("clase ';'")
    def programa(self, p):
        return Programa(linea=p.lineno, secuencia=[p.clase])

    # Clase

    @_('CLASS TYPEID INHERITS TYPEID "{" optional_feature "}"')
    def clase(self, p):
        return Clase(linea=p.lineno, nombre=p.TYPEID0, padre=p.TYPEID1, nombre_fichero=self.nombre_fichero, caracteristicas=p.optional_feature)

    @_('CLASS TYPEID INHERITS TYPEID "{" "}"')
    def clase(self, p):
        return Clase(linea=p.lineno, nombre=p.TYPEID0, padre=p.TYPEID1, nombre_fichero=self.nombre_fichero, caracteristicas=[])

    @_('CLASS TYPEID "{" optional_feature "}"')
    def clase(self, p):
        return Clase(linea=p.lineno, nombre=p.TYPEID, padre="Object", nombre_fichero=self.nombre_fichero, caracteristicas=p.optional_feature)

    @_('CLASS TYPEID "{" "}"')
    def clase(self, p):
        return Clase(linea=p.lineno, nombre=p.TYPEID, padre="Object", nombre_fichero=self.nombre_fichero, caracteristicas=[])

    @_('feature ";"')
    def optional_feature(self, p):
        return [p.feature]

    @_('optional_feature feature ";"')
    def optional_feature(self, p):
        return p.optional_feature + [p.feature]

    # Feature

    @_('OBJECTID ":" TYPEID ASSIGN expr')
    def feature(self, p):
        return Atributo(linea=p.lineno, nombre=p.OBJECTID, tipo=p.TYPEID, cuerpo=p.expr)

    @_('OBJECTID ":" TYPEID')
    def feature(self, p):
        return Atributo(linea=p.lineno, nombre=p.OBJECTID, tipo=p.TYPEID, cuerpo=NoExpr(p.lineno))

    @_('OBJECTID "(" formal optional_formal ")" ":" TYPEID "{" expr "}"')
    def feature(self, p):
        return Metodo(linea=p.lineno, nombre=p.OBJECTID, tipo=p.TYPEID, cuerpo=p.expr, formales=[p.formal] + p.optional_formal)

    @_('OBJECTID "(" formal ")" ":" TYPEID "{" expr "}"')
    def feature(self, p):
        return Metodo(linea=p.lineno, nombre=p.OBJECTID, tipo=p.TYPEID, cuerpo=p.expr, formales=[p.formal])

    @_('OBJECTID "(" ")" ":" TYPEID "{" expr "}"')
    def feature(self, p):
        return Metodo(linea=p.lineno, nombre=p.OBJECTID, tipo=p.TYPEID, cuerpo=p.expr, formales=[])

    @_('"," formal')
    def optional_formal(self, p):
        return [p.formal]

    @_('"," formal optional_formal')
    def optional_formal(self, p):
        return [p.formal] + p.optional_formal

    # Formal

    @_('error formal')
    def optional_formal(self, p):
        return []

    @_('OBJECTID ":" TYPEID')
    def formal(self, p):
        return Formal(linea=p.lineno, nombre_variable=p.OBJECTID, tipo=p.TYPEID)

    # Expr

    @_('"-" expr %prec UMINUS')
    def expr(self, p):
        return Entero(p.lineno, f'-{p.expr}')

    @_('BOOL_CONST')
    def expr(self, p):
        return Booleano(linea=p.lineno, valor=p.BOOL_CONST)

    @_('STR_CONST')
    def expr(self, p):
        return String(linea=p.lineno, valor=p.STR_CONST)

    @_('INT_CONST')
    def expr(self, p):
        return Entero(linea=p.lineno, valor=p.INT_CONST)

    @_('OBJECTID')
    def expr(self, p):
        return Objeto(linea=p.lineno, nombre=p.OBJECTID)

    @_('"(" expr ")"')
    def expr(self, p):
        return p.expr

    @_('NOT expr')
    def expr(self, p):
        return Not(linea=p.lineno, expr=p.expr)

    @_('expr "=" expr')
    def expr(self, p):
        return Igual(p.lineno, izquierda=p.expr0, derecha=p.expr1)

    @_('expr LE expr')
    def expr(self, p):
        return LeIgual(p.lineno, izquierda=p.expr0, derecha=p.expr1)

    @_('expr "<" expr')
    def expr(self, p):
        return Menor(p.lineno, izquierda=p.expr0, derecha=p.expr1)

    @_('"~" expr')
    def expr(self, p):
        return Neg(linea=p.lineno, expr=p.expr)

    @_('expr "/" expr')
    def expr(self, p):
        return Division(p.lineno, izquierda=p.expr0, derecha=p.expr1)

    @_('expr "*" expr')
    def expr(self, p):
        return Multiplicacion(p.lineno, izquierda=p.expr0, derecha=p.expr1)

    @_('expr "-" expr')
    def expr(self, p):
        return Resta(linea=p.lineno, izquierda=p.expr0, derecha=p.expr1)

    @_('expr "+" expr')
    def expr(self, p):
        return Suma(p.lineno, izquierda=p.expr0, derecha=p.expr1)

    @_('ISVOID expr')
    def expr(self, p):
        return EsNulo(linea=p.lineno, expr=p.expr)

    @_('NEW TYPEID')
    def expr(self, p):
        return Nueva(linea=p.lineno, tipo=p.TYPEID)

    @_('CASE expr OF lista_asig ESAC')
    def expr(self, p):
        return Swicht(linea=p.lineno, expr=p.expr, casos=p.lista_asig)

    @_('OBJECTID ":" TYPEID DARROW expr ";"')
    def lista_asig(self, p):
        return [RamaCase(linea=p.lineno, nombre_variable=p.OBJECTID, tipo=p.TYPEID, cuerpo=p.expr)]

    @_('OBJECTID ":" TYPEID DARROW expr ";" lista_asig')
    def lista_asig(self, p):
        return [RamaCase(linea=p.lineno, nombre_variable=p.OBJECTID, tipo=p.TYPEID, cuerpo=p.expr)] + p.lista_asig

    # let
    @_('LET OBJECTID ":" TYPEID ASSIGN expr IN expr')
    def expr(self, p):
        return Let(linea=p.lineno, nombre=p.OBJECTID, tipo=p.TYPEID, inicializacion=p.expr0, cuerpo=p.expr1)

    @_('LET OBJECTID ":" TYPEID IN expr')
    def expr(self, p):
        return Let(linea=p.lineno, nombre=p.OBJECTID, tipo=p.TYPEID, inicializacion=NoExpr(p.lineno), cuerpo=p.expr)

    @_('LET OBJECTID ":" TYPEID ASSIGN expr optional_assigns IN expr')
    def expr(self, p):
        cuerpo = p.expr1
        for i in reversed(p.optional_assigns):
            cuerpo = Let(linea=p.lineno, nombre=i[0], tipo=i[1], inicializacion=i[2], cuerpo=cuerpo)
        cuerpo = Let(linea=p.lineno, nombre=p.OBJECTID, tipo=p.TYPEID, inicializacion=p.expr0, cuerpo=cuerpo)
        return cuerpo

    @_('LET OBJECTID ":" TYPEID optional_assigns IN expr')
    def expr(self, p):
        cuerpo = p.expr
        for i in reversed(p.optional_assigns):
            cuerpo = Let(linea=p.lineno, nombre=i[0], tipo=i[1], inicializacion=i[2], cuerpo=cuerpo)

        cuerpo = Let(linea=p.lineno, nombre=p.OBJECTID, tipo=p.TYPEID, inicializacion=NoExpr(p.lineno), cuerpo=cuerpo)
        return cuerpo


    @_('"," OBJECTID ":" TYPEID ASSIGN expr optional_assigns')
    def optional_assigns(self, p):
        return [[p.OBJECTID, p.TYPEID, p.expr]] + p.optional_assigns

    @_('"," OBJECTID ":" TYPEID optional_assigns')
    def optional_assigns(self, p):
        return [[p.OBJECTID, p.TYPEID, NoExpr(p.lineno)]] + p.optional_assigns

    @_('"," OBJECTID ":" TYPEID ASSIGN expr')
    def optional_assigns(self, p):
        return [[p.OBJECTID, p.TYPEID, p.expr]]

    @_('"," OBJECTID ":" TYPEID')
    def optional_assigns(self, p):
        return [[p.OBJECTID, p.TYPEID, NoExpr(p.lineno)]]

    @_('"{" lista_expr "}"')
    def expr(self, p):
        return Bloque(linea=p.lineno, expresiones=p.lista_expr)

    @_('expr ";"')
    def lista_expr(self, p):
        return [p.expr]


    @_('lista_expr expr ";"')
    def lista_expr(self, p):
        return p.lista_expr + [p.expr]

    # while
    @_('WHILE expr LOOP expr POOL')
    def expr(self, p):
        return Bucle(p.lineno, condicion=p.expr0, cuerpo=p.expr1)
    # if
    @_('IF expr THEN expr ELSE expr FI')
    def expr(self, p):
        return Condicional(linea=p.lineno, condicion=p.expr0, verdadero=p.expr1, falso=p.expr2)

    # ID([expr[,expr]*])
    @_('OBJECTID "(" expr ")"')
    def expr(self, p):
        return LlamadaMetodo(linea=p.lineno, cuerpo=Objeto(linea=p.lineno, nombre="self"), nombre_metodo=p.OBJECTID, argumentos=[p.expr])

    @_('OBJECTID "(" expr optional_expressions ")"')
    def expr(self, p):
        return LlamadaMetodo(linea=p.lineno, cuerpo=Objeto(linea=p.lineno, nombre="self"), nombre_metodo=p.OBJECTID, argumentos=[p.expr] + p.optional_expressions)

    @_('OBJECTID "(" ")"')
    def expr(self, p):
        return LlamadaMetodo(linea=p.lineno, cuerpo=Objeto(linea=p.lineno, nombre="self"), nombre_metodo=p.OBJECTID, argumentos=[])

    @_('"," expr')
    def optional_expressions(self, p):
        return [p.expr]

    @_('"," expr optional_expressions')
    def optional_expressions(self, p):
        return [p.expr] + p.optional_expressions

    @_('expr "@" TYPEID "." OBJECTID "(" ")"')
    def expr(self, p):
        return LlamadaMetodoEstatico(linea=p.lineno, cuerpo=p.expr, clase=p.TYPEID, nombre_metodo=p.OBJECTID, argumentos=[])

    @_('expr "@" TYPEID "." OBJECTID "(" expr ")"')
    def expr(self, p):
        return LlamadaMetodoEstatico(linea=p.lineno, cuerpo=p.expr0, clase=p.TYPEID, nombre_metodo=p.OBJECTID, argumentos=[p.expr1])

    @_('expr "@" TYPEID "." OBJECTID "(" expr optional_expressions ")"')
    def expr(self, p):
        return LlamadaMetodoEstatico(linea=p.lineno, cuerpo=p.expr0, clase=p.TYPEID, nombre_metodo=p.OBJECTID, argumentos=[p.expr1] + p.optional_expressions)

    @_('expr "." OBJECTID "(" ")"')
    def expr(self, p):
        return LlamadaMetodo(linea=p.lineno, cuerpo=p.expr, nombre_metodo=p.OBJECTID, argumentos=[])

    @_('expr "." OBJECTID "(" expr ")"')
    def expr(self, p):
        return LlamadaMetodo(linea=p.lineno, cuerpo=p.expr0, nombre_metodo=p.OBJECTID, argumentos=[p.expr1])

    @_('expr "." OBJECTID "(" expr optional_expressions ")"')
    def expr(self, p):
        return LlamadaMetodo(linea=p.lineno, cuerpo=p.expr0, nombre_metodo=p.OBJECTID, argumentos=[p.expr1] + p.optional_expressions)

    # ID <- expr
    @_('OBJECTID ASSIGN expr')
    def expr(self, p):
        return Asignacion(linea=p.lineno, cast=p.OBJECTID, cuerpo=p.expr)

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

    @_('LET OBJECTID ":" TYPEID ASSIGN expr IN error')
    def expr(self, p):
        return NoExpr()

    def error(self, p):
        if p is None:
            self.errores.append(f'"{self.nombre_fichero}", line 0: syntax error at or near EOF')

        elif p.type in ['TYPEID', 'OBJECTID', 'INT_CONST']:
            self.errores.append(
                f'"{self.nombre_fichero}", line {p.lineno}: syntax error at or near {p.type} = {p.value}')

        elif p.type in ['OF', 'DARROW', 'ESAC', 'FI', 'ELSE', 'LOOP', 'POOL']:
            self.errores.append(f'"{self.nombre_fichero}", line {p.lineno}: syntax error at or near {p.type}')

        else:
            self.errores.append(f'"{self.nombre_fichero}", line {p.lineno}: syntax error at or near \'{p.value}\'')

