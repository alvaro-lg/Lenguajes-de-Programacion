# coding: utf-8
__author__ = "Alvaro Lopez, Jairo Gonzalez, Jorge Piris"

from dataclasses import dataclass, field
from typing import List

# coding: utf-8
from dataclasses import dataclass, field
from typing import List
from copy import copy


class Ambito:

    def __init__(self):
        self.local_variables = dict()
        self.atributes = dict()
        self.clases = {'Object', 'Int', 'String', 'Bool', 'IO'}
        self.basic_clases = {'Object', 'Int', 'String', 'Bool'}
        self.features = {('Object', 'abort'): ([], "Object"),
                         ('Object', 'copy'): ([], "Object"),
                         ('Int', 'copy'): ([], "Int"),
                         ('String', 'copy'): ([], "String"),
                         ('Bool', 'copy'): ([], "Bool"),
                         ('String', 'length'): ([], "Int"),
                         ('String', 'substr'): (['Int', 'Int'], "String"),
                         ('String', 'concat'): (['String'], "String"),
                         ('IO', 'out_string'): (["String"], 'SELF_TYPE'),
                         ('IO', 'out_int'): (["Int"], 'SELF_TYPE'),
                         ('IO', 'in_string'): ([], "String"),
                         ('IO', 'in_int'): ([], "Int")}
        self.inheritance = {'Object': None,
                            'Int': 'Object',
                            'String': 'Object',
                            'Bool': 'Object',
                            'IO' : 'Object'}
        self.error = 'Compilation halted due to static semantic errors.'
        self.current_class : Clase

    def new_class(self, clase):
        self.atributes[(clase.nombre, 'self')] = 'SELF_TYPE'
        self.current_class = clase
        self.clases.add(clase.nombre)

    def new_method(self):
        self.local_variables = dict()

    def new_child(self, child, parent):
        self.inheritance[child] = parent

        keys = copy(list(self.atributes.keys()))
        for (clase, attr) in keys:
            if clase == parent:
                self.atributes[(child, attr)] = self.atributes[(clase, attr)]

        keys = copy(list(self.features.keys()))
        for (clase, method) in keys:
            if clase == parent:
                self.features[(child, method)] = self.features[(clase, method)]

    def is_child(self, child, parent):
        try:
            if self.inheritance[child] == parent:
                return True
        except:
            return False

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
        resultado = ''

        if self.nombre == 'self':
            return f":{self.cuerpo.linea}: Cannot assign to 'self'.\n"

        # Comprobacion de que la variable existe como variable local
        try:
            tipo = ambito.local_variables[self.nombre]
        except:
            tipo = None

        # Comprobacion de que la variable existe como atributo
        if tipo is None:
            try:
                tipo = ambito.atributes[(ambito.current_class.nombre, self.nombre)]
            except:
                tipo = None

        resultado += self.cuerpo.Tipo()

        # Caso de que los tipos no matcheen
        if tipo is not None and tipo != self.cuerpo.cast and tipo != ambito.inheritance[self.cuerpo.cast]:
            return f":{self.cuerpo.linea}: Type {self.cuerpo.cast} of assigned expression does not conform to declared" \
                   f" type {tipo} of identifier {self.nombre}.\n"
        elif tipo is None: # Caso de que no exista la variable
            pass
            # TODO: No existe la variable

        self.cast = self.cuerpo.cast
        return resultado

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
        resultado = self.cuerpo.Tipo()
        try:
            args, return_type = ambito.features[(self.clase, self.nombre_metodo)]
        except:
            return f":{self.linea}: Dispatch to undefined method {self.nombre_metodo}.\n"
        for pos, a in enumerate(self.argumentos):
            resultado += a.Tipo()
            if a.cast != args[pos]:
                return f":{self.linea}: Expression type {self.nombre_metodo}, type Object of parameter a does not conform to declared static dispatch type {args[pos]}.\n"
        self.cast = return_type
        return resultado


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
        if self.cuerpo.cast == '_no_type':
            try:
                args, return_type = ambito.features[(ambito.current_class.nombre, self.nombre_metodo)]
                for pos, a in enumerate(self.argumentos):
                    resultado += a.Tipo()
                    if a.cast != args[pos]:
                        return f":{self.linea}: In call of method {self.nombre_metodo}, type Object of parameter a does not conform to declared type {args[pos]}.\n"
                self.cast = return_type
            except:
                return f":{self.linea}: Dispatch to undefined method {self.nombre_metodo}.\n"
        else:
            try:
                tipo = self.cuerpo.cast
                if tipo == 'SELF_TYPE':
                    tipo = ambito.current_class.nombre
                args, return_type = ambito.features[(tipo, self.nombre_metodo)]
                for pos, a in enumerate(self.argumentos):
                    resultado += a.Tipo()
                    tipo = a.cast
                    if a.cast == 'SELF_TYPE':
                        tipo = ambito.current_class.nombre
                    if tipo != args[pos]:
                        return f":{self.linea}: In call of method {self.nombre_metodo}, type Object of parameter a does not conform to declared type {args[pos]}.\n"
                self.cast = return_type
            except:
                return f":{self.linea}: Dispatch to undefined method {self.nombre_metodo}.\n"
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
        resultado = self.verdadero.Tipo()
        resultado += self.falso.Tipo()
        resultado += self.condicion.Tipo()

        node_falso = self.falso.cast
        path_falso = []
        node_verdadero = self.verdadero.cast
        path_verdadero = []

        while node_falso is not None :
            path_falso.insert(0, node_falso)
            node_falso = ambito.inheritance[node_falso]

        while node_verdadero is not None:
            path_verdadero.insert(0, node_verdadero)
            node_verdadero = ambito.inheritance[node_verdadero]

        common_parent = 'Object'
        for i, j in zip(path_verdadero, path_falso):
            if i == j:
                common_parent = i
            else:
                break

        self.cast = common_parent
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
        resultado = self.condicion.Tipo()

        if self.condicion.cast != 'Bool':
            return f":{self.linea}: Loop condition does not have type Bool.\n"

        resultado += self.cuerpo.Tipo()
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

        global ambito

        if self.nombre == 'self':
            return f":{self.linea}: '{self.nombre}' cannot be bound in a 'let' expression.\n"

        backup = copy(ambito)

        # Creamos la entrada de la variable
        ambito.local_variables[self.nombre] = self.tipo
        resultado = self.inicializacion.Tipo()

        if self.inicializacion.cast != self.tipo and not isinstance(self.inicializacion, NoExpr):
            return f":{self.linea}: Inferred type {self.inicializacion.cast} of initialization of" \
                   f" {self.nombre} does not conform to identifier's declared type {self.tipo}.\n"

        resultado += self.cuerpo.Tipo()
        self.cast = self.cuerpo.cast
        ambito = backup
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
        resultado = self.expr.Tipo()
        tipos = set()
        for c in self.casos:
            if c.tipo not in tipos:
                tipos.add(c.tipo)
                resultado += c.Tipo()
            else:
                return f":{self.linea}: Duplicate branch {c.tipo} in case statement.\n"
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
            return resultado + f':{str(self.linea)}: non-Int arguments: {self.izquierda.cast} + {self.derecha.cast}\n'


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
        resultado = self.izquierda.Tipo()
        resultado += self.derecha.Tipo()
        if self.izquierda.cast == 'Int' and self.derecha.cast == 'Int':
            self.cast = 'Int'
            return resultado
        else:
            return resultado + 'Error - mult'


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
        self.cast = 'Bool'
        self.izquierda.Tipo()
        self.derecha.Tipo()
        if self.izquierda.cast == 'Int' and self.derecha.cast == 'Int':
            return ""
        elif self.izquierda.cast != 'Int' and self.derecha.cast != 'Int':
            return ""
        else:
            return f":{self.linea}: Illegal comparison with a basic type.\n"


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
        self.cast = 'Bool'
        self.izquierda.Tipo()
        self.derecha.Tipo()
        if self.izquierda.cast == 'Int' and self.derecha.cast == 'Int':
            return ""
        elif self.izquierda.cast != 'Int' and self.derecha.cast != 'Int':
            return ""
        else:
            return f":{self.linea}: Illegal comparison with a basic type.\n"


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
        self.cast = 'Bool'
        self.izquierda.Tipo()
        self.derecha.Tipo()
        if self.izquierda.cast == 'Int' and self.derecha.cast == 'Int':
            return ""
        elif self.izquierda.cast != 'Int' and self.derecha.cast != 'Int':
            return ""
        else:
            return f":{self.linea}: Illegal comparison with a basic type.\n"

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
        resultado = self.expr.Tipo()
        self.cast = self.expr.cast
        return resultado


@dataclass
class Not(Expresion):
    expr: Expresion = None
    operador: str = 'not'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n) * " "}_comp\n'
        resultado += self.expr.str(n + 2)
        resultado += f'{(n) * " "}: {self.cast}\n'
        return resultado

    def Tipo(self):
        self.cast = 'Bool'
        self.expr.Tipo()
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
        resultado = self.expr.Tipo()
        self.cast = self.expr.cast
        return resultado


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
        # Comprobacion de que la variable existe como variable local
        try:
            tipo = ambito.local_variables[self.nombre]
        except:
            tipo = None

        # Comprobacion de que la variable existe como atributo
        if tipo is None:
            try:
                tipo = ambito.atributes[(ambito.current_class.nombre, self.nombre)]
            except:
                tipo = None

        if tipo is None:
            self.cast = "Object"
            return f":{str(self.linea)}: Undeclared identifier {self.nombre}.\n"
        else:
            self.cast = tipo
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
        return ''


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
        self.cast = 'Bool'
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
        resultado = ""

        # Explorando todos los metodos
        for c in self.secuencia:
            if c.nombre in ambito.clases and c.nombre not in ambito.basic_clases:
                return f"{c.nombre_fichero}:{c.linea}: Class {c.nombre} was previously defined.\n" + ambito.error
            ambito.new_class(c)
            ambito.new_child(c.nombre, c.padre)
            for car in c.caracteristicas:
                if isinstance(car, Metodo):
                    args = []
                    for f in car.formales:
                        if f.nombre_variable == 'self':
                            return f"{c.nombre_fichero}:{car.linea}: '{f.nombre_variable}' cannot be the name of a formal parameter.\n" + ambito.error
                        if f.tipo == 'SELF_TYPE':
                            return f"{c.nombre_fichero}:{car.linea}: Formal parameter {f.nombre_variable} cannot have type {f.tipo}.\n" + ambito.error
                        args.append(f.tipo)
                    ambito.features[(c.nombre, car.nombre)] = (args, car.tipo)

        # Check overriding
        for c in self.secuencia:
            parent = ambito.inheritance[c.nombre]
            for car in c.caracteristicas:
                if isinstance(car, Metodo):
                    try:
                        original = ambito.features[(parent, car.nombre)]
                        overrided = ambito.features[(c.nombre, car.nombre)]
                        if original != overrided:
                            for i, j in zip(original, overrided):
                                if i != j:
                                    break
                            return f"{c.nombre_fichero}:{car.linea}: In redefined method {car.nombre}, parameter " \
                                   f"type {j[0]} is different from original type {i[0]}\n" + ambito.error
                    except:
                        pass


        if 'Main' not in ambito.clases:
            return "Class Main is not defined.\n" + ambito.error

        for c in self.secuencia:
            if c.nombre == 'SELF_TYPE':
                return c.nombre_fichero + f':{str(self.linea)}: Redefinition of basic class SELF_TYPE.\n {ambito.error}'
            ambito.new_class(c)
            resultado += c.Tipo()
        if resultado != "":
            resultado += ambito.error
        return "" + resultado


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

        # Errores
        # TODO: Comprobar orden
        if self.padre != 'Object' and self.padre in ambito.basic_clases.union({'SELF_TYPE'}):
            return f"{self.nombre_fichero}:{self.linea+1}: Class {self.nombre} cannot inherit class {self.padre}.\n"

        if self.padre != '_no_set':
            if self.padre not in ambito.clases:
                return f"{self.nombre_fichero}:{self.linea+1}: Class {self.nombre} inherits from an undefined class {self.padre}.\n"
            ambito.new_child(self.nombre, self.padre)
        else:
            ambito.new_child(self.nombre, 'Object')

        if self.nombre in ambito.basic_clases:
            return f"{self.nombre_fichero}:{self.linea+1}: Redefinition of basic class {self.nombre}.\n"

        for c in self.caracteristicas:
            ambito.new_method()
            s += c.Tipo()

        # TODO: +1 da error en inheritsselftype.test y missingclass.test
        if s != "":
            s = f"{self.nombre_fichero}"+ s
        return s


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

        resultado = ''
        types = []
        for f in self.formales:
            types.append(f.tipo)
            ambito.local_variables[f.nombre_variable] = f.tipo
        resultado += self.cuerpo.Tipo()

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
        s = self.cuerpo.Tipo()
        if self.nombre == 'self':
            s += f":{str(self.linea)}: 'self' cannot be the name of an attribute.\n"
        try:
            if ambito.atributes[(ambito.inheritance[ambito.current_class.nombre], self.nombre)] is not self.tipo:
                return f":{self.linea}: Attribute {self.nombre} is an attribute of an inherited class.\n"
        except:
            pass
        ambito.atributes[(ambito.current_class.nombre, self.nombre)] = self.tipo
        return s
