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


        for r in p['junto_con']:
            if r not in self.recurs.clauses:
                no_tengo.append(r)


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

        for p in p['plan']:
            kb_de_trabajo.clauses.append(p)

        if inferencia.inferir(kb_de_trabajo,self.objetivo):
            return ('ok',[],self)
        else:
            return ('error',[],self)

    def responderConsulta(self,ob):
        return filter(lambda x: str(ob) in str(x),self.conoc.clauses)


class Nodo:
    def __init__(self,nivel,objetivo,plan,recursos,disponibles):
         self.nivel = nivel
         self.objetivo = objetivo
         self.plan = plan
         self.recursos = recursos
         self.hijos = []
         self.disponibles = disponibles

    def insertarHijos(self,nivel,objetivo,ns):

        if nivel == 1:
            assert(self.nivel==0)
            listNodos= []
            for n in ns:
                disp = map(expr,self.disponibles[:])
                flag = 0
                for r in n["recursos"]:
                    if r not in disp:
                        #print "no esta: "+r
                        flag = 1
                    else:
                        disp.remove(r)
                if flag == 0:
                    nod = Nodo(nivel,objetivo,n["planes"],n["recursos"],disp)
                    listNodos.append(nod)
            self.hijos = listNodos


        if nivel > (self.nivel)+1:
            for ab in self.hijos:
                ab.insertarHijos(nivel,objetivo,ns)

        if (nivel > 1) and (nivel == self.nivel+1):
            listNodos = []
            for n in ns:
                disp = map(expr,self.disponibles[:])
                #print disp
                flag = 0
                for r in n["recursos"]:
                    if r not in disp:
                        #print "no esta: "+r
                        flag = 1
                    else:
                        disp.remove(r)

                if flag == 0:
                    nod = Nodo(nivel,objetivo,n["planes"],n["recursos"],disp)
                    listNodos.append(nod)
            self.hijos= listNodos


    def __str__(self):
            salida=''
            for ns in self.hijos:
                espacios = ''
                for i in range(1,ns.nivel):
                    espacios += ' - '
                salida = salida+'\n '+ espacios +ns.__str__()
            return ','.join(map(str,self.recursos))+'('+','.join(map(str,self.plan))+')'+salida


class Mediador2:
    def __init__(self,agentes):
        self.tab_propuestas = {}
        self.tab_creencias = {}
        for a in agentes:
            self.tab_propuestas[a.num] = {'y':[],'x':[],'arg':[],'his':[]}
            self.tab_creencias[a.num] = {'br':[],'bg':[],'bnr':[]}
        self.conocimiento = PropKB()

    def insertarConocimiento(self,expresiones):
            for e in expresiones:
                 self.conocimiento.tell(e)

    def revisarCreencias(self,a,y,x,arg):
        for r in y:
            self.tab_creencias[a.num]['br'].append(r)
        for r in x:
            if r in self.tab_creencias[a.num]['br']:
                self.tab_creencias[a.num]['br'].remove(r)
            self.tab_creencias[a.num]['bnr'].append(r)

        self.tab_creencias[a.num]['bg']=[a.objetivo]

        for ex in arg:
            if "Goal" in str(ex):
                self.conocimiento.tell(ex)

    def armarArbol(self,re):

        arbol = Nodo(0,"Raiz",[],[],re)

        lista_objetivos = []
        resultados=[]

        for fila in self.tab_creencias:
            lista_objetivos += self.tab_creencias[fila]['bg']

        nivel = 1
        #print lista_objetivos
        for ob in lista_objetivos:
            #print "A"
            res=[]
            conoc_de_trabajo = PropKB()
            conoc_de_trabajo.clauses = filter(lambda x: str(ob) in str(x),self.conocimiento.clauses)
            rs = inferencia.calcular_inf(conoc_de_trabajo,ob)
            #print "B"
            for (pl,re1,re2) in rs:
                recursos = soloRec(re1+re2)
                if len(recursos) == 0:
                    continue
                sol={"planes":pl, "recursos":recursos}
                def estaEn(s,ss):
                    for i in ss:
                        if s["planes"] == i["planes"]:
                            return True
                    return False

                if not(estaEn(sol,res)):
                    res.append(sol)
            resultados.append({"nivel":nivel,"ob":ob, "res": res})
            nivel +=1

            for r in resultados:
                arbol.insertarHijos(r['nivel'],r['ob'],r["res"])


        return arbol

    def ponderar(self,soluciones):

        sol_pond=[]

        for sol in soluciones:
            suma = 0
            rec_pos = {}
            for s in sol:
                for fila in self.tab_creencias:
                    if s["objetivo"] in self.tab_creencias[fila]["bg"]:
                        for r in s["recursos"]:
                            if r in self.tab_creencias[fila]["br"]:
                                suma +=10
                                rec_pos[r]=(fila,"tiene")
                                continue
                            for f in self.tab_propuestas:
                                if f != fila:
                                    if r in self.tab_propuestas[f]["y"]:
                                        suma +=5
                                        rec_pos[r]=(f,"ofrece")
                                        break
                                    if r in self.tab_creencias[f]["br"]:
                                        suma += 3
                                        rec_pos[r]=(f,"pedir")
                                        break

                        break
            sol_pond.append({"solucion":sol,"valor":suma,"rec_pos":rec_pos})

        return sol_pond


    def armarPropuestas(self,sol_elegida,agentes):

        prop={}
        for a in agentes:
            prop[a.num]={'pido' : [],'doy' : [],'junto_con' : [], 'plan' : []}
            #Te pido .... y a cambio te doy .... porque junto_con .... y los planes .... podes alcanzar tu Objetivo


        for fila in self.tab_propuestas:
            obj = self.tab_creencias[fila]["bg"][:]
            for o in obj:
                for s in sol_elegida["solucion"]:
                    if o == s["objetivo"]:
                        for r in s["recursos"]:
                            if r in sol_elegida["rec_pos"]:
                                if sol_elegida["rec_pos"][r][0] == fila:
                                    continue
                                else:
                                    prop[sol_elegida["rec_pos"][r][0]]["pido"].append(r)
                            else:
                                if r in self.tab_creencias[fila]["bnr"]:
                                    band = 0
                                    for f in self.tab_creencias:
                                        if f == fila:
                                            continue
                                        if r in self.tab_creencias[f]["bnr"]:
                                            continue
                                        prop[f]["pido"].append(r)
                                        band = 1
                                        break
                                    if band == 0:
                                        return 0
                            prop[fila]["doy"].append(r)

                        prop[fila]["junto_con"]= [x for x in s["recursos"] if x not in prop[fila]["doy"]]
                        prop[fila]["plan"] += s["plan"][:]


        return prop


    def consultarPorPlanes(self,agentes):
            lista_objetivos = []

            for fila in self.tab_creencias:
                lista_objetivos += self.tab_creencias[fila]['bg']

            for ob in lista_objetivos:
                for a in agentes:
                    pl = a.responderConsulta(ob)
                    self.insertarConocimiento(pl)


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

def creencias_ini_med2(m,recursos_util,planes,subObj):
    rec=[]
    for r in recursos_util:
        rec.append(r[0])

    conj= gen_conjuntos_disjuntos(rec,len(m.tab_creencias))

    for fila in m.tab_creencias:
        cant = random.randrange(len(conj[fila-1])+1)
        seleccionados = random.sample(conj[fila-1], cant)

        for s in seleccionados:
            m.tab_creencias[fila]['br'].append(expr(s))

    lista_de_planes=planes[:]+subObj[:]
    cant = random.randrange(len(lista_de_planes))
    seleccionados = random.sample(lista_de_planes, cant)

    m.insertarConocimiento(map(expr,seleccionados))

def nivelesArbol(arbol):
    if arbol.hijos == []:
        return 0
    else:
        return max(map(lambda x: 1+nivelesArbol(x),arbol.hijos))


def arbolCompleto(arbol,agentes):
    lista_objetivos = []

    for a in agentes:
        lista_objetivos += [a.objetivo]

    if len(lista_objetivos) == nivelesArbol(arbol):
        return True
    else:
        return False


def extraerSoluciones(arbol):
    solucionesP = []

    solLocal= {"objetivo":arbol.objetivo, "plan":arbol.plan, "recursos":arbol.recursos}

    for h in arbol.hijos:
        for s in extraerSoluciones(h):
            solucionesP.append(s)

    if arbol.hijos == []:
            return [[solLocal]]

    if arbol.nivel == 0:
        return solucionesP
    else:
        return map(lambda x: [solLocal]+x, solucionesP)






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
    med2 = Mediador2(agentes)

    #Asignarle creencias al mediador
    creencias_ini_med2(med2,utiliz,regl,sub)

    conteo=0
    acuerdo = False


    for a in agentes:
        if agente_infiere(a,ob):
            return ("CASO DE PRUEBA NO VALIDO",agentes,regl+sub)
            #Porque es un caso en donde el agente puede alcanzar su objetivo con sus propios recursos, no necesita negociar
            #sys.exit(0)
        #print a.objetivo
        #print a.recurs.clauses

    consulta_de_planes = 0


    while acuerdo == False:
        #Propuestas iniciales de los agentes
        for a in agentes:

            (plans,tien,falt)=calcular_necesidad(a,ob,re)
            y = agente_ofrece(a,tien)
            x = soloRec(falt)
            arg = tien+falt+plans+[str(a.objetivo)]

            med2.tab_propuestas[a.num]['y']=y
            med2.tab_propuestas[a.num]['x']=x
            med2.tab_propuestas[a.num]['arg']=arg
            med2.tab_propuestas[a.num]['his']+=[(y,x)]

            med2.revisarCreencias(a,y,x,arg)



        arbol = med2.armarArbol(re)




        if not(arbolCompleto(arbol,agentes)):
            print "arbol no completo"
            med2.consultarPorPlanes(agentes)
            consulta_de_planes = 1
            arbol = med2.armarArbol(re)
            if not(arbolCompleto(arbol,agentes)):
                print ("EL MEDIADOR 2 NO PUEDE RESOLVER ESTE PROBLEMA v1",agentes,regl+sub)




        soluciones = filter(lambda x: len(x) == nivelesArbol(arbol), extraerSoluciones(arbol))
        soluciones_ponderadas = med2.ponderar(soluciones)

        soluciones_ponderadas.sort(key=lambda x: x["valor"], reverse=True)

        for i in range(0,len(soluciones_ponderadas)):

            sol_elegida = soluciones_ponderadas[i]

            propRealizadas = []
            while True:
                propuestasDelMed = med2.armarPropuestas(sol_elegida,agentes)
                if (propuestasDelMed == 0) or (propuestasDelMed in propRealizadas) :
                    break

                propRealizadas.append(propuestasDelMed)

                respuestasAg={}

                for a in agentes:
                    respuestasAg[a.num]=a.evaluar(propuestasDelMed[a.num],ob)


                acuerdo = True
                for resp in respuestasAg:
                    #print respuestasAg[resp]
                    if respuestasAg[resp][0] == 'ok':
                        continue
                    else:
                        med2.interpretarCritica(respuestasAg[resp])
                        acuerdo = False


                if acuerdo == True:
                    #print propuestasDelMed
                    return ("OK",agentes,regl+sub,propuestasDelMed)

        if consulta_de_planes == 0:
            med2.consultarPorPlanes(agentes)
            consulta_de_planes = 1
        else:
            return ("EL MEDIADOR 2 NO PUEDE RESOLVER ESTE PROBLEMA v2",agentes,regl+sub)




result=[]
i=0
contador=1
cant_casos_validos=20




while i<cant_casos_validos:
    print "Prueba Nº: "+str(contador)
    r = simular(6,40,15)
    result.append(r)
    if r[0] != "CASO DE PRUEBA NO VALIDO":
        i+=1
    #print r[0]
    for l in r:
        print l
    for a in r[1]:
        print a.recurs.clauses
    contador+=1
    print "Casos de exito: " + str(len(filter(lambda x: x[0] == "OK",result)))
    print "Fracasos: " + str(len(filter(lambda x: (x[0] == "EL MEDIADOR 2 NO PUEDE RESOLVER ESTE PROBLEMA v1") or (x[0] == "EL MEDIADOR 2 NO PUEDE RESOLVER ESTE PROBLEMA v2"),result)))
print "\n \nSobre "+str(cant_casos_validos)+" casos de prueba validos \n"
print "Casos de exito: " + str(len(filter(lambda x: x[0] == "OK",result)))
print "Fracasos: " + str(len(filter(lambda x: (x[0] == "EL MEDIADOR 2 NO PUEDE RESOLVER ESTE PROBLEMA v1") or (x[0] == "EL MEDIADOR 2 NO PUEDE RESOLVER ESTE PROBLEMA v2"),result)))
