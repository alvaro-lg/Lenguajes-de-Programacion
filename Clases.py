# coding: utf-8
from dataclasses import dataclass, field
from typing import List

# coding: utf-8
from dataclasses import dataclass, field
from typing import List


class Ambito:

    def __init__(self):
        self.variables = {'self': 'SELF_TYPE'}
        self.features = {('Object', 'abort'): ([], "Object"),
                         ('Object', 'copy'): ([], "Object"),
                         ('Int', 'copy'): ([], "Int"),
                         ('String', 'copy'): ([], "String"),
                         ('Bool', 'copy'): ([], "Bool"),
                         ('String', 'length'): ([], "Int"),
                         ('String', 'substr'): (['Int', 'Int'], "String"),
                         ('String', 'concat'): (['String'], "String")}
        self.inherits_from = {}
        self.classes = {}
        self.error = 'Compilation halted due to static semantic errors.'

ambito = Ambito()

@dataclass
class Nodo:
    linea: int = 0

    def str(self, n):
        return f'{n * " "}#{self.linea}\n'


@dataclass
class Formal(Nodo):
    nombre_variable: str = '_no_set'
    tipo: str = '_no_type'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n) * " "}_formal\n'
        resultado += f'{(n + 2) * " "}{self.nombre_variable}\n'
        resultado += f'{(n + 2) * " "}{self.tipo}\n'
        return resultado


@dataclass
class Expresion(Nodo):
    cast: str = '_no_type'


@dataclass
class Asignacion(Expresion):
    nombre: str = '_no_set'
    cuerpo: Expresion = None

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n) * " "}_assign\n'
        resultado += f'{(n + 2) * " "}{self.nombre}\n'
        resultado += self.cuerpo.str(n + 2)
        resultado += f'{(n) * " "}: {self.cast}\n'
        return resultado

    def Tipo(self):
        if self.nombre == 'self':
            return f"{self.linea}: Cannot assign to 'self'."

        try:
            tipo = ambito.variables[self.nombre]
            self.cast = self.cuerpo.cast
            return self.cuerpo.Tipo()
        except:
            self.cast = 'Object'
            return f'{self.linea}: Undeclared identifier {self.nombre}.'



@dataclass
class LlamadaMetodoEstatico(Expresion):
    cuerpo: Expresion = None
    clase: str = '_no_type'
    nombre_metodo: str = '_no_set'
    argumentos: List[Expresion] = field(default_factory=list)

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n) * " "}_static_dispatch\n'
        resultado += self.cuerpo.str(n + 2)
        resultado += f'{(n + 2) * " "}{self.clase}\n'
        resultado += f'{(n + 2) * " "}{self.nombre_metodo}\n'
        resultado += f'{(n + 2) * " "}(\n'
        resultado += ''.join([c.str(n + 2) for c in self.argumentos])
        resultado += f'{(n + 2) * " "})\n'
        resultado += f'{(n) * " "}: _no_type\n'
        return resultado

    def Tipo(self):
        self.cast = ambito.features[(self.clase, self.nombre_metodo)][1]
        return ''


@dataclass
class LlamadaMetodo(Expresion):
    cuerpo: Expresion = None
    nombre_metodo: str = '_no_set'
    argumentos: List[Expresion] = field(default_factory=list)

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n) * " "}_dispatch\n'
        resultado += self.cuerpo.str(n + 2)
        resultado += f'{(n + 2) * " "}{self.nombre_metodo}\n'
        resultado += f'{(n + 2) * " "}(\n'
        resultado += ''.join([c.str(n + 2) for c in self.argumentos])
        resultado += f'{(n + 2) * " "})\n'
        resultado += f'{(n) * " "}: {self.cast}\n'
        return resultado

    def Tipo(self):
        resultado = self.cuerpo.Tipo()
        args, return_type = ambito.features[(self.cuerpo.cast, self.nombre_metodo)]
        pos = 0
        for a in self.argumentos:
            resultado += a.Tipo()
            if a.cast != args[pos]:
                return resultado + "error"
            pos += 1
        self.cast = return_type
        return resultado


@dataclass
class Condicional(Expresion):
    condicion: Expresion = None
    verdadero: Expresion = None
    falso: Expresion = None

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n) * " "}_cond\n'
        resultado += self.condicion.str(n + 2)
        resultado += self.verdadero.str(n + 2)
        resultado += self.falso.str(n + 2)
        resultado += f'{(n) * " "}: {self.cast}\n'
        return resultado

    def Tipo(self):
        resultado = self.condicion.Tipo()
        self.cast = self.verdadero.cast
        return resultado


@dataclass
class Bucle(Expresion):
    condicion: Expresion = None
    cuerpo: Expresion = None

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n) * " "}_loop\n'
        resultado += self.condicion.str(n + 2)
        resultado += self.cuerpo.str(n + 2)
        resultado += f'{(n) * " "}: {self.cast}\n'
        return resultado

    def Tipo(self):
        resultado = self.cuerpo.Tipo()
        self.cast = self.cuerpo.cast
        return resultado


@dataclass
class Let(Expresion):
    nombre: str = '_no_set'
    tipo: str = '_no_set'
    inicializacion: Expresion = None
    cuerpo: Expresion = None

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n) * " "}_let\n'
        resultado += f'{(n + 2) * " "}{self.nombre}\n'
        resultado += f'{(n + 2) * " "}{self.tipo}\n'
        resultado += self.inicializacion.str(n + 2)
        resultado += self.cuerpo.str(n + 2)
        resultado += f'{(n) * " "}: {self.cast}\n'
        return resultado

    def Tipo(self):
        resultado = self.cuerpo.Tipo()
        self.cast = self.cuerpo.cast
        return resultado


@dataclass
class Bloque(Expresion):
    expresiones: List[Expresion] = field(default_factory=list)

    def str(self, n):
        resultado = super().str(n)
        resultado = f'{n * " "}_block\n'
        resultado += ''.join([e.str(n + 2) for e in self.expresiones])
        resultado += f'{(n) * " "}: {self.cast}\n'
        resultado += '\n'
        return resultado

    def Tipo(self):
        resultado = ''
        for expr in self.expresiones:
            resultado += expr.Tipo()
        self.cast = self.expresiones[-1].cast
        return resultado


@dataclass
class RamaCase(Nodo):
    nombre_variable: str = '_no_set'
    tipo: str = '_no_set'
    cast: str = '_no_type'

    cuerpo: Expresion = None

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n) * " "}_branch\n'
        resultado += f'{(n + 2) * " "}{self.nombre_variable}\n'
        resultado += f'{(n + 2) * " "}{self.tipo}\n'
        resultado += self.cuerpo.str(n + 2)
        resultado += f'{(n) * " "}: {self.cast}\n'
        return resultado

    def Tipo(self):
        resultado = self.cuerpo.Tipo()
        return resultado


@dataclass
class Swicht(Nodo):
    expr: Expresion = None
    casos: List[RamaCase] = field(default_factory=list)
    cast: str = '_no_type'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n) * " "}_typcase\n'
        resultado += self.expr.str(n + 2)
        resultado += ''.join([c.str(n + 2) for c in self.casos])
        resultado += f'{(n) * " "}: {self.cast}\n'
        return resultado

    def Tipo(self):
        resultado = ''
        for c in self.casos:
            resultado += c.Tipo()
        return resultado


@dataclass
class Nueva(Nodo):
    tipo: str = '_no_set'
    cast: str = '_no_type'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n) * " "}_new\n'
        resultado += f'{(n + 2) * " "}{self.tipo}\n'
        resultado += f'{(n) * " "}: {self.cast}\n'
        return resultado

    def Tipo(self):
        self.cast = self.tipo
        return ''


@dataclass
class OperacionBinaria(Expresion):
    izquierda: Expresion = None
    derecha: Expresion = None


@dataclass
class Suma(OperacionBinaria):
    operando: str = '+'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n) * " "}_plus\n'
        resultado += self.izquierda.str(n + 2)
        resultado += self.derecha.str(n + 2)
        resultado += f'{(n) * " "}: {self.cast}\n'
        return resultado

    def Tipo(self):

        resultado = self.izquierda.Tipo()
        resultado += self.derecha.Tipo()
        if self.izquierda.cast == 'Int' and self.derecha.cast == 'Int':
            self.cast = 'Int'
            return resultado
        else:
            return resultado + f': {str(self.linea)}: non-Int arguments: {self.izquierda.cast} {self.derecha.cast}\n'


@dataclass
class Resta(OperacionBinaria):
    operando: str = '-'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n) * " "}_sub\n'
        resultado += self.izquierda.str(n + 2)
        resultado += self.derecha.str(n + 2)
        resultado += f'{(n) * " "}: {self.cast}\n'
        return resultado

    def Tipo(self):
        resultado = self.izquierda.Tipo()
        resultado += self.derecha.Tipo()
        if self.izquierda.cast == 'Int' and self.derecha.cast == 'Int':
            self.cast = 'Int'
            return resultado
        else:
            return resultado + 'Error - resta'


@dataclass
class Multiplicacion(OperacionBinaria):
    operando: str = '*'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n) * " "}_mul\n'
        resultado += self.izquierda.str(n + 2)
        resultado += self.derecha.str(n + 2)
        resultado += f'{(n) * " "}: {self.cast}\n'
        return resultado

    def Tipo(self):
        resultado = self.izquierda.Tipo()
        resultado += self.derecha.Tipo()
        if self.izquierda.cast == 'Int' and self.derecha.cast == 'Int':
            self.cast = 'Int'
            return resultado
        else:
            return resultado + 'Error - mult'


@dataclass
class Division(OperacionBinaria):
    operando: str = '/'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n) * " "}_divide\n'
        resultado += self.izquierda.str(n + 2)
        resultado += self.derecha.str(n + 2)
        resultado += f'{(n) * " "}: {self.cast}\n'
        return resultado

    def Tipo(self):
        if self.izquierda.cast == 'Int' and self.derecha.cast == 'Int':
            return ""
        else:
            return "error"


@dataclass
class Menor(OperacionBinaria):
    operando: str = '<'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n) * " "}_lt\n'
        resultado += self.izquierda.str(n + 2)
        resultado += self.derecha.str(n + 2)
        resultado += f'{(n) * " "}: {self.cast}\n'
        return resultado

    def Tipo(self):
        if self.izquierda.cast == 'Int' and self.derecha.cast == 'Int':
            return ""
        else:
            return "error"


@dataclass
class LeIgual(OperacionBinaria):
    operando: str = '<='

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n) * " "}_leq\n'
        resultado += self.izquierda.str(n + 2)
        resultado += self.derecha.str(n + 2)
        resultado += f'{(n) * " "}: {self.cast}\n'
        return resultado

    def Tipo(self):
        if self.izquierda.cast == 'Int' and self.derecha.cast == 'Int':
            return ""
        else:
            return "error"


@dataclass
class Igual(OperacionBinaria):
    operando: str = '='

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n) * " "}_eq\n'
        resultado += self.izquierda.str(n + 2)
        resultado += self.derecha.str(n + 2)
        resultado += f'{(n) * " "}: {self.cast}\n'
        return resultado

    def Tipo(self):
        if self.izquierda.cast == 'Int' and self.derecha.cast == 'Int':
            return ""
        else:
            return "error"


@dataclass
class Neg(Expresion):
    expr: Expresion = None
    operador: str = '~'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n) * " "}_neg\n'
        resultado += self.expr.str(n + 2)
        resultado += f'{(n) * " "}: {self.cast}\n'
        return resultado

    def Tipo(self):
        if self.expr.cast == 'Int':
            return ""
        else:
            return "error"


@dataclass
class Not(Expresion):
    expr: Expresion = None
    operador: str = 'NOT'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n) * " "}_comp\n'
        resultado += self.expr.str(n + 2)
        resultado += f'{(n) * " "}: {self.cast}\n'
        return resultado

    def Tipo(self):
        return ""


@dataclass
class EsNulo(Expresion):
    expr: Expresion = None

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n) * " "}_isvoid\n'
        resultado += self.expr.str(n + 2)
        resultado += f'{(n) * " "}: {self.cast}\n'
        return resultado

    def Tipo(self):
        self.expr.Tipo()
        self.cast = self.expr.cast
        return ""


@dataclass
class Objeto(Expresion):
    nombre: str = '_no_set'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n) * " "}_object\n'
        resultado += f'{(n + 2) * " "}{self.nombre}\n'
        resultado += f'{(n) * " "}: {self.cast}\n'
        return resultado

    def Tipo(self):
        if self.nombre not in ambito.variables.keys():
            self.cast = "Object"
            return "Undeclared identifier"
        else:
            self.cast = ambito.variables[self.nombre]
            return ""


@dataclass
class NoExpr(Expresion):
    nombre: str = ''

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n) * " "}_no_expr\n'
        resultado += f'{(n) * " "}: {self.cast}\n'
        return resultado

    def Tipo(self):
        self.cast = "_no_type"
        return ""


@dataclass
class Entero(Expresion):
    valor: int = 0

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n) * " "}_int\n'
        resultado += f'{(n + 2) * " "}{self.valor}\n'
        resultado += f'{(n) * " "}: {self.cast}\n'
        return resultado

    def Tipo(self):
        self.cast = 'Int'
        return ""


@dataclass
class String(Expresion):
    valor: str = '_no_set'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n) * " "}_string\n'
        resultado += f'{(n + 2) * " "}{self.valor}\n'
        resultado += f'{(n) * " "}: {self.cast}\n'
        return resultado

    def Tipo(self):
        self.cast = 'String'
        return ""


@dataclass
class Booleano(Expresion):
    valor: bool = False

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n) * " "}_bool\n'
        resultado += f'{(n + 2) * " "}{1 if self.valor else 0}\n'
        resultado += f'{(n) * " "}: {self.cast}\n'
        return resultado

    def Tipo(self):
        self.cast = "Bool"
        return ""


@dataclass
class IterableNodo(Nodo):
    secuencia: List = field(default_factory=List)


@dataclass
class Programa(IterableNodo):

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{" " * n}_program\n'
        resultado += ''.join([c.str(n + 2) for c in self.secuencia])
        return resultado

    def Tipo(self):
        global ambito
        ambito = Ambito()
        s = ""
        for c in self.secuencia:
            if c.nombre == 'SELF_TYPE':
                return c.nombre_fichero + f': {str(self.linea)} :  Redefinition of basic class SELF_TYPE.\n {ambito.error}'
            ambito.classes[c.nombre] = ""
            s += c.Tipo()
            # del scope['class'][c.nombre]
        if s != "":
            s += ambito.error
        return "" + s


@dataclass
class Caracteristica(Nodo):
    nombre: str = '_no_set'
    tipo: str = '_no_set'
    cuerpo: Expresion = None


@dataclass
class Clase(Nodo):
    nombre: str = '_no_set'
    padre: str = '_no_set'
    nombre_fichero: str = '_no_set'
    caracteristicas: List[Caracteristica] = field(default_factory=list)

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n) * " "}_class\n'
        resultado += f'{(n + 2) * " "}{self.nombre}\n'
        resultado += f'{(n + 2) * " "}{self.padre}\n'
        resultado += f'{(n + 2) * " "}"{self.nombre_fichero}"\n'
        resultado += f'{(n + 2) * " "}(\n'
        resultado += ''.join([c.str(n + 2) for c in self.caracteristicas])
        resultado += '\n'
        resultado += f'{(n + 2) * " "})\n'
        return resultado

    def Tipo(self):
        s = ""
        if self.padre != '_no_set':
            ambito.inherits_from[self.nombre] = self.padre
        else:
            ambito.inherits_from[self.nombre] = 'Object'

        for c in self.caracteristicas:
            if isinstance(c, Atributo):
                if c.nombre == 'self':
                    s += f":{str(c.linea)}: 'self' cannot be the name of an attribute.\n"
                ambito.variables[c.nombre] = c.tipo
            if isinstance(c, Metodo):
                types = []
                for f in c.formales:
                    types.append(f.tipo)
                ambito.features[(self.nombre, c.nombre)] = (types, c.tipo)

        if s != "":
            s = self.nombre_fichero + s
        return "" + s


@dataclass
class Metodo(Caracteristica):
    formales: List[Formal] = field(default_factory=list)

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n) * " "}_method\n'
        resultado += f'{(n + 2) * " "}{self.nombre}\n'
        resultado += ''.join([c.str(n + 2) for c in self.formales])
        resultado += f'{(n + 2) * " "}{self.tipo}\n'
        resultado += self.cuerpo.str(n + 2)

        return resultado

    def Tipo(self):
        resultado = self.cuerpo.Tipo()
        return resultado


class Atributo(Caracteristica):

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n) * " "}_attr\n'
        resultado += f'{(n + 2) * " "}{self.nombre}\n'
        resultado += f'{(n + 2) * " "}{self.tipo}\n'
        resultado += self.cuerpo.str(n + 2)
        return resultado

    def Tipo(self):
        resultado = self.cuerpo.Tipo()
        if self.cuerpo.cast == self.tipo:
            return resultado
        else:
            return resultado
