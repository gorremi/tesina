#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, 'logica/')

from logic import *


def buscar_laterales(x,xs):
        for (l,c,r) in xs:

            if x == c:
                if (l == "leaf") & (r == "leaf"):

                    return [c]
                else:
                    return buscar_laterales(l,xs)+buscar_laterales(r,xs)
        return []

def armar_arbol_ok(xs):

    lista_de_resultado = []
    #cant_de_sol = xs.count(("leaf",Expr('FALSE'),"leaf"))

    #for i in range(0,cant_de_sol):
    #    result = buscar_laterales(Expr('FALSE'),xs)
    #    lista_de_resultado.append(result)
    #    xs.remove(("leaf",Expr('FALSE'),"leaf"))

    #return lista_de_resultado
    return buscar_laterales(Expr('FALSE'),xs)



def es_padre(o,xs):
    for (l,c,r) in xs:
        if o == l:
            return True
        if o == r:
            return True

    return False

def esplan(ex):
    if ('|' in str(ex)) or ('&' in str(ex)):
        return True
    else:
        return False

def descartar_padres(xs,expre):
        lista_final=[]
        for (l,c,r) in xs:
            if (not es_padre(c,xs) or not esplan(c)) and (str(expre) not in str(c)):
                #lista_final.append((l,c,r))
                lista_final.append(c)

        #for (l,c,r) in lista_final:
        #    if 'G7' not in str(c):
                #print l,c,r
        #        print c
            #print l,c,r
        return lista_final


def calcular_inf(kb,expresion):


    (resultado,arbol) = pl_resolution(kb, expresion)

    result=[]


    while resultado:
        res = armar_arbol_ok(arbol)
        for r in res:
            if not(esplan(r)):
                kb.retract(r)
        (resultado,arbol) = pl_resolution(kb, expresion)




    alternativas = descartar_padres(arbol,expresion)
    for a in alternativas:
        kbn = PropKB()
        kbn.clauses=kb.clauses[:]
        kbn.tell(to_cnf(expr(~a)))
        (res,a2) = pl_resolution(kbn, expresion)
        ret = armar_arbol_ok(a2)
        if to_cnf(expr(~expresion)) in ret:
            conj = set(map(expr,ret))
            #conjunto de soluciones:
            planes_que_se_utilizan = []
            recursos_que_tiene = []
            recursos_que_le_faltan = []
            for c in conj:
                if '(' in str(c):
                    planes_que_se_utilizan.append(c)
                else:
                    if c in kb.clauses:
                        recursos_que_tiene.append(c)
                    else:
                        recursos_que_le_faltan.append(c)
            result.append((planes_que_se_utilizan,recursos_que_tiene,recursos_que_le_faltan))

        kbn.retract(to_cnf(expr(~a)))

    return result



def inferir(kb,expresion):
    return pl_resolution_sin_Arbol(kb, expresion)
