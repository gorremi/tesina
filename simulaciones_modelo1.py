#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, 'logica/')
import pdb

from logic import *

import string
import random

import inferencia

class Agente:
    def __init__(self,num,objetivo):
         self.num = num
         self.conoc = PropKB()
         self.recurs = PropKB()
         self.objetivo = objetivo

    def __repr__(self):
        return "Agente "+str(self.num)

    def insertarConocimiento(self,expresiones):
            for e in expresiones:
                 self.conoc.tell(e)

    def insertarRecursos(self,recursos):
            for r in recursos:
                self.recurs.tell(r)

    def evaluar(self,p,ob):
        kb_de_trabajo = PropKB()
        kb_de_trabajo.clauses = self.recurs.clauses[:]

        no_tengo=[]
        for r in p['pido']:
            if r not in self.recurs.clauses:
                no_tengo.append(r)
            else:
                kb_de_trabajo.retract(r)


        if len(no_tengo) > 0:
            return ('critica',no_tengo,self)

        for r in self.conoc.clauses:
            if (str(self.objetivo) in str(r)):
                kb_de_trabajo.clauses.append(r)
            for o in ob:
                if ("~"+o in str(r)):
                    kb_de_trabajo.clauses.append(r)

        for r in p['doy']:
            kb_de_trabajo.clauses.append(r)

        if inferencia.inferir(kb_de_trabajo,self.objetivo):
            return ('ok',[],self)
        else:
            return ('error',[],self)





class Arista:
    def __init__(self,origen,destino,etiqueta,fortaleza):
        self.origen=origen
        self.destino=destino
        self.etiqueta=etiqueta
        self.fortaleza=fortaleza

    def __repr__(self):
        return "{"+str(self.origen)+'->'+str(self.destino)+' , ag: '+str(self.etiqueta)+' , '+str(self.fortaleza)+'}'


class Mediador1:
    def __init__(self,agentes):
        self.tab_propuestas = {}
        self.tab_creencias = {}
        for a in agentes:
            self.tab_propuestas[a.num] = {'y':[],'x':[],'arg':[],'his':[]}
            self.tab_creencias[a.num] = {'br':[],'bg':[],'bnr':[]}

    def revisarCreencias(self,a,y,x):
        for r in y:
            self.tab_creencias[a.num]['br'].append(r)
        for r in x:
            if r in self.tab_creencias[a.num]['br']:
                self.tab_creencias[a.num]['br'].remove(r)
            self.tab_creencias[a.num]['bnr'].append(r)

        self.tab_creencias[a.num]['bg']=[a.objetivo]

    def generarGrafo(self):

        recursosSolicitados = []
        for fila in self.tab_propuestas:
            for r in self.tab_propuestas[fila]['x']:
                if r in recursosSolicitados:
                    #El mismo recurso lo solicitan dos agentes distintos, este mediador no puede resolver el problema
                    return 0
                recursosSolicitados.append(r)

        nodos = recursosSolicitados[:]
        aristasGrafo=[]

        #depurar
        #pdb.set_trace()

        #Genera las aristas fuertes
        para_elim=[]
        for r in nodos:
            for fila in self.tab_propuestas:
                if r in self.tab_propuestas[fila]['y']:
                    for rs in self.tab_propuestas[fila]['x']:
                        aristasGrafo.append(Arista(rs,r,fila,'f'))
                    para_elim.append(r)
                    break

        for r in para_elim:
            nodos.remove(r)

        para_elim=[]

        #Genera las aristas debiles
        for r in nodos:
            for fila in self.tab_creencias:
                if (r in self.tab_creencias[fila]['br']) and (r not in  self.tab_propuestas[fila]['arg']) :
                    for rs in self.tab_propuestas[fila]['x']:
                        aristasGrafo.append(Arista(rs,r,fila,'d'))
                    para_elim.append(r)

                    break

        for r in para_elim:
            nodos.remove(r)

        band=0
        #Verificar si quedaron nodos sin grado de entrada
        if len(nodos) > 0:
            for r in nodos:
                i=0
                while ((i<len(self.tab_creencias)*3)) and (band == 0):
                    fila=random.sample(self.tab_creencias,1)[0]

                    if (r not in self.tab_creencias[fila]['bnr']) and (r not in self.tab_propuestas[fila]['arg']):
                        for rs in self.tab_propuestas[fila]['x']:
                            aristasGrafo.append(Arista(rs,r,fila,'r'))
                        band= 1
                    i+=1

        if band==0:

            return 0

        return aristasGrafo

    def generarPropuestas(self,aristas,agentes):
        prop={}
        for a in agentes:
            prop[a.num]={'doy' : [], 'pido' : []}
            for ar in aristas:
                if ar.etiqueta == a.num:
                    prop[a.num]['doy'].append(ar.origen)
                    prop[a.num]['pido'].append(ar.destino)

            if a.num not in [ar.etiqueta for ar in aristas]:
                prop[a.num]['doy']=self.tab_propuestas[a.num]['x'][:]



        for p in prop:
            prop[p]['doy'] = list(set(prop[p]['doy']))
            prop[p]['pido'] = list(set(prop[p]['pido']))
        return prop

    def interpretarCritica(self,crit):

        for r in crit[1]:
            self.tab_creencias[crit[2].num]['bnr'].append(r)
            if r in self.tab_creencias[crit[2].num]['br']:
                self.tab_creencias[crit[2].num]['br'].remove(r)

def genRecursosStr(cant):
     xs=[]
     rond = cant/26
     if rond < 1:
         for c in string.ascii_uppercase[0:cant]:
             xs.append(c)
     if rond >= 1:
         for c in string.ascii_uppercase[0:26]:
             xs.append(c)

         i=1
         for j in range(i,rond):
             for c in string.ascii_uppercase[0:26]:
                 xs.append(c+str(j))

         i=rond
         resto = cant - 26*rond
         for c in string.ascii_uppercase[0:resto]:
             xs.append(c+str(i))

     return xs


def genObjetivosStr(cant):
    xs=[]
    for i in range(1,cant+1):
        xs.append('Goal'+str(i))
    return xs


def genExpresionesStr(cant,objetivos,recursos,n):
    #cant: cantidad de reglas mas alla de las necesarias para que cada objetivo tenga una forma de ser alcanzado
    #n: cantidad máxima de recursos implicados en una regla
    reglas = []
    rec_utilizados = []

    for o in objetivos:
        largo = random.randrange(n)+1
        reg= '('
        rec = random.sample(recursos, largo)
        for re in rec:
            rec_utilizados.append(re)
        reg+=rec[0]
        if largo > 1:
            for r in rec[1:]:
                reg+="&"+r

        reg+=')==>'+o
        reglas.append(reg)

    for i in range(0,cant):
        largo = random.randrange(n)+1
        reg= '('
        rec = random.sample(recursos, largo)
        for re in rec:
            rec_utilizados.append(re)
        reg+=rec[0]
        if largo > 1:
            for r in rec[1:]:
                reg+="&"+r

        reg+=')==>'+random.choice(objetivos)
        reglas.append(reg)

    #se generan reglas en las cuales subobjetivos implican otros objetivos:
    planes_con_subjetivos = []
    for i in range(0,cant/2):
        lar = random.randrange(2)+2
        rec = random.sample(objetivos, lar)
        ult = rec.pop()
        reg= '('+'&'.join(rec)+')==>'+ult
        planes_con_subjetivos.append(reg)


    return (reglas,list(set(rec_utilizados)),planes_con_subjetivos)

def genAgentes(cant,objetivos,recursos):
    lisAg=[]
    for i in range(0,cant):
        lisAg.append(Agente(i+1,expr(objetivos[i])))

    return lisAg


def gen_conjuntos_disjuntos(xs,cant):
    lista_de_trabajo = xs[:]
    conjuntos_salida=[]

    for c in range(0,cant):
        conjuntos_salida.append([])

    while len(lista_de_trabajo) > 0:
        elem=lista_de_trabajo[0]
        i = random.randrange(cant)
        conjuntos_salida[i].append(elem)
        lista_de_trabajo.remove(elem)

    return conjuntos_salida


def dividir_recursos(ags,utiliz):
    lista_de_rec=utiliz[:]
    for a in ags:
        indice = random.randrange(len(lista_de_rec))
        a.insertarRecursos([expr(lista_de_rec.pop(indice))])

    while len(lista_de_rec) > 0:
        ind = random.randrange(len(ags))
        indice = random.randrange(len(lista_de_rec))
        ags[ind].insertarRecursos([expr(lista_de_rec.pop(indice))])


def dividir_conocimiento(ags,planes,subObj):
    lista_de_planes=planes[:]+subObj[:]
    pl_utilizados=[]
    for a in ags:
        filtrados = filter(lambda x: str(a.objetivo) not in x,lista_de_planes )
        cant = random.randrange(len(filtrados)+1/2)
        seleccionados = random.sample(filtrados, cant)


        #seleccionados = random.sample(lista_de_planes, cant)


        for p in planes:
            if (str(a.objetivo) in p):
                seleccionados.append(p)
                break


        a.insertarConocimiento(map(expr,seleccionados))
        pl_utilizados += list(set(seleccionados))

    return pl_utilizados


def hayRec(rs,rss):
    for r in rs:
        if r in rss:
            return True
    return False

def soloRec(ss):
    sol=[]
    for s in ss:
        if "Goal" not in str(s):
            sol.append(s)
    return sol



#El agente puede alcanzar su objetivo o no
def agente_infiere(ag,ob):
    kbDeTrabajo = PropKB()

    for r in ag.conoc.clauses:
        if (str(ag.objetivo) in str(r)):
            kbDeTrabajo.clauses.append(r)
        for o in ob:
            if ("~"+o in str(r)):
                kbDeTrabajo.clauses.append(r)

    kbDeTrabajo.clauses +=(ag.recurs.clauses)

    return inferencia.inferir(kbDeTrabajo,ag.objetivo)


#El agente calcula que recursos le faltan par alograr su objetivo
def calcular_necesidad(ag,ob,re):
    kbDeTrabajo = PropKB()

    for r in ag.conoc.clauses:
        if (str(ag.objetivo) in str(r)):
            kbDeTrabajo.clauses.append(r)
        for o in ob:
            if ("~"+o in str(r)):
                kbDeTrabajo.clauses.append(r)

    kbDeTrabajo.clauses +=(ag.recurs.clauses)

    res = inferencia.calcular_inf(kbDeTrabajo,ag.objetivo)

    vistos = []

    #res = filter(lambda (y,x,z): hayRec(z,re),res)
    sol_elegida=res[0]

    for (pl,tie,fal) in res:
        if (len((filter(lambda x: x in ob,fal))) == 0) and (set(fal) not in vistos) and (len(soloRec(fal))>0):
            vistos.append(set(fal))
            if len(tie) >= len(sol_elegida[1]):
                sol_elegida = (pl,tie,fal)

    return sol_elegida


def agente_ofrece(a,t):
    l_trabajo = a.recurs.clauses[:]
    l_trabajo = filter(lambda x: x not in t,l_trabajo)

    if len(l_trabajo) == 0:
        return []
    cant = random.randrange(len(l_trabajo))
    if cant == 0:
        return []
    return random.sample(l_trabajo, cant)

def creencias_ini_med1(m,recursos_util):
    rec=[]
    for r in recursos_util:
        rec.append(r[0])

    conj= gen_conjuntos_disjuntos(rec,len(m.tab_creencias))

    for fila in m.tab_creencias:
        cant = random.randrange(len(conj[fila-1])+1)
        seleccionados = random.sample(conj[fila-1], cant)

        for s in seleccionados:
            m.tab_creencias[fila]['br'].append(expr(s))


def simular(cant_ag, cant_recursos, cant_expresiones):

    #Cantidad de agentes
    cant_agentes = cant_ag

    #Generacion de recursos, objetivos y panes
    re = genRecursosStr(cant_recursos)
    ob = genObjetivosStr(cant_agentes)
    (regl,utiliz,sub) = genExpresionesStr(cant_expresiones,ob,re,3)

    #Generacion de agentes
    agentes = genAgentes(cant_agentes,ob,re)

    #Dividir los recursos y el conocimiento entre los agentes
    dividir_recursos(agentes,utiliz)
    pl_utilizados=dividir_conocimiento(agentes,regl,sub)

    #Crear mediador
    med1 = Mediador1(agentes)

    #Asignarle creencias al mediador
    creencias_ini_med1(med1,utiliz)

    conteo=0
    acuerdo = False

    for a in agentes:
        if agente_infiere(a,ob):
            return "CASO DE PRUEBA NO VALIDO"
            #Porque es un caso en donde el agente puede alcanzar su objetivo con sus propios recursos, no necesita negociar
            #sys.exit(0)


    while acuerdo == False:
        #Propuestas iniciales de los agentes
        for a in agentes:

            (plans,tien,falt)=calcular_necesidad(a,ob,re)
            y = agente_ofrece(a,tien)
            x = soloRec(falt)
            arg = tien+falt+plans+[str(a.objetivo)]

            med1.tab_propuestas[a.num]['y']=y
            med1.tab_propuestas[a.num]['x']=x
            med1.tab_propuestas[a.num]['arg']=arg
            med1.tab_propuestas[a.num]['his']+=[(y,x)]

            med1.revisarCreencias(a,y,x)


        aristas = med1.generarGrafo()

        if aristas == 0:
            return "EL MEDIADOR 1 NO PUEDE RESOLVER ESTE PROBLEMA"
            #sys.exit(0)


        prop = med1.generarPropuestas(aristas,agentes)

        respuestasAg={}

        for a in agentes:
            respuestasAg[a.num]=a.evaluar(prop[a.num],ob)

        acuerdo = True
        for resp in respuestasAg:
            #print respuestasAg[resp]
            if respuestasAg[resp][0] == 'ok':
                continue
            else:
                med1.interpretarCritica(respuestasAg[resp])
                acuerdo = False

        #print "-----------"
        conteo +=1

    return "OK"
result=[]
i=0
contador=1
cant_casos_validos=100
while i<cant_casos_validos:
    print "Prueba Nº: "+str(contador)
    r = simular(6,30,10)
    result.append(r)
    if r != "CASO DE PRUEBA NO VALIDO":
        i+=1
    print r
    contador+=1
print "\n \nSobre "+str(cant_casos_validos)+" casos de prueba validos \n"
print "Casos de exito: " + str(len(filter(lambda x: x == "OK",result)))
print "Fracasos: " + str(len(filter(lambda x: x == "EL MEDIADOR 1 NO PUEDE RESOLVER ESTE PROBLEMA",result)))
