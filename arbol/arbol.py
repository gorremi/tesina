#!/usr/bin/env python

class Nodo:
    def __init__(self,agente,nivel,objetivo,plan):
         self.agente = agente
         self.nivel = nivel
         self.objetivo = objetivo
         self.plan = plan
         self.hijos = []
         self.costo = calcular_costo(plan)

    def insertarHijos(self,ns,nivel):

        if nivel == 1:
            assert(self.nivel==0)
            listNodos= []
            for n in ns:
                nod = Nodo(str(nivel),nivel,str(nivel),n)
                listNodos.append(nod)
            self.hijos = listNodos


        if nivel > (self.nivel)+1:
            for ab in self.hijos:
                ab.insertarHijos(ns,nivel)

        if nivel == self.nivel+1:
            listNodos= []
            for n in ns:
                nod = Nodo(str(nivel),nivel,str(nivel),n)
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



solu = {'G1':['H^M','O^L'],'G2':['I^A','N'],'G3':['N','F^L'],'G4':['O^C','N']}

#print solu.items()

arbol = Nodo("raiz",0,"","")


i=1

for k in solu:
    arbol.insertarHijos(solu[k],i)
    i +=1

print arbol


#nodoTest = Nodo("ag","obj","")

#print nodoTest.plan
