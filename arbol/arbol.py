#!/usr/bin/env python

class Nodo:
    def __init__(self,agente,nivel,objetivo,plan,disponibles):
         self.agente = agente
         self.nivel = nivel
         self.objetivo = objetivo
         self.plan = plan
         self.hijos = []
         self.costo = calcular_costo(plan)
         self.disponibles = disponibles

    def insertarHijos(self,ns,nivel):

        if nivel == 1:
            assert(self.nivel==0)
            listNodos= []
            for n in ns:
                disp = self.disponibles
                for r in simbolos(n):
                    if r not in disp:
                        return
                    disp.remove(r)

                nod = Nodo(str(nivel),nivel,str(nivel),n,disp)
                listNodos.append(nod)
            self.hijos = listNodos


        if nivel > (self.nivel)+1:
            for ab in self.hijos:
                ab.insertarHijos(ns,nivel)

        if nivel == self.nivel+1:
            listNodos= []
            for n in ns:
                disp = self.disponibles
                for r in simbolos(n):
                    if r not in disp:
                        return
                    disp.remove(r)

                nod = Nodo(str(nivel),nivel,str(nivel),n,disp)
                listNodos.append(nod)
            self.hijos= listNodos

    def __str__(self):
            salida=''
            for ns in self.hijos:
                espacios = ''
                for i in range(1,ns.nivel):
                    espacios += ' - '
                salida = salida+'\n '+ espacios +ns.__str__()
            return self.plan+salida




def calcular_costo(p):
    return 0

def simbolos(xs):
    return xs.split('^')


solu = {'G1':['H^M','O^L'],'G2':['I^A','N'],'G3':['N','F^L'],'G4':['O^C','N']}

#print solu.items()
todosLosRecursos=[]
for k in solu:
    for p in solu[k]:
        for r in simbolos(p):
            todosLosRecursos.append(r)

todosLosRecursos = list(set(todosLosRecursos))


arbol = Nodo("raiz",0,"","",todosLosRecursos)


i=1

for k in solu:
    arbol.insertarHijos(solu[k],i)
    i +=1

print arbol


#nodoTest = Nodo("ag","obj","")

#print nodoTest.plan
