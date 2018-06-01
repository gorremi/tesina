from logic import *



recursos = ['A', 'B', 'C','D','E','F','H','I','J','K','L','M','N','O','P','Q','R','~A', '~B', '~C','~D','~E','~F','~H','~I','~J','~K','~L','~M','~N','~O','~P','~Q','~R']

recursosSINneg = ['A', 'B', 'C','D','E','F','H','I','J','K','L','M','N','O','P','Q','R']

recursos = recursosSINneg[:]

objetivos = ['G1','G2','G3','G4','G5','G6','G7','G8','G9']

conectores = ['&','|','(',')']

reglas = []


def generar_expr (n, xs):
    expresion = ''
    for i in range(0,n+1):
        simbolo = recursos[random.randrange(len(recursos))]
        while simbolo in xs:
            simbolo = recursos[random.randrange(len(recursos))]
        expresion += simbolo

        conec = conectores[random.randrange(2)]
        expresion += conec

        xs+=expresion

    simbolo = recursos[random.randrange(len(recursos))]
    while simbolo in xs:
        simbolo = recursos[random.randrange(len(recursos))]
    expresion += simbolo

    return expresion


for i in range(0,5):
    cantidad_de_exps = random.randrange(2)+1
    reg = '('

    for ce in range(0,cantidad_de_exps):
        if ce != 0 :
            conec = conectores[random.randrange(2)]
            reg+=conec
        reg+='('
        r = generar_expr(random.randrange(3),reg)
        reg+=r
        reg+=')'
    reg+=')'
    reg+= '==>'
    goal = objetivos[random.randrange(len(objetivos))]
    reg+=goal

    reglas.append(reg)

for i in range(0,3):
    cantidad_de_exps = random.randrange(2)+1
    reg = '('

    for ce in range(0,cantidad_de_exps):
        if ce != 0 :
            conec = conectores[random.randrange(2)]
            reg+=conec
        reg+='('
        r = generar_expr(random.randrange(3),reg)
        reg+=r
        reg+=')'
    reg+=')'
    reg+= '==>'
    goal = recursos[random.randrange(len(recursos))]
    reg+=goal

    reglas.append(reg)




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





kb = PropKB()


debug= True


if debug:
    #reglas=["((F&H&A&I))==>G1","((J&N)|(L&I|P))==>G9","((L|A&H)&(R&Q&O))==>G7","((J&I)|(H&C))==>G9","((M&C&H|B))==>O"]
    #reglas=["((L|A&H)&(R&Q&O))==>G7","((M&C&H|B))==>O"]
    reglas = ["((E|K&L&P)|(I|Q|J|N))==>G7","A ==> J","R ==> J"]

for r in reglas:
    kb.tell (expr(r))


setkb = set()

setkb.update(set(kb.clauses))


posee_recursos = []
for i in range(0,5):
    posee_recursos.append(recursosSINneg[random.randrange(len(recursosSINneg))])

if debug:
    #posee_recursos = ['D','E','R', 'C']
    posee_recursos = ['H', 'O', 'L', 'B', 'N']


for r in posee_recursos:
    kb.tell(expr(r))

for r in reglas:
    print r
print posee_recursos

expresion = expr('G7')

(resultado,arbol) = pl_resolution(kb, expresion)


print resultado

while resultado:
    res = armar_arbol_ok(arbol)
    print res
    for r in res:
        if not(esplan(r)):
            kb.retract(r)
    (resultado,arbol) = pl_resolution(kb, expresion)



alternativas = descartar_padres(arbol,expresion)
for a in alternativas:
    kbn = PropKB()
    kbn.clauses=kb.clauses[:]
    #tiene = posee_recursos[:]
    #nuevos=obtener_rec(a)
    #tiene += nuevos
    #tiene.append(obtener_rec(a))
    kbn.tell(to_cnf(expr(~a)))
    #print tiene
    #print kbn
    (res,a2) = pl_resolution(kbn, expresion)
    print res
    ret = armar_arbol_ok(a2)
    if to_cnf(expr(~expresion)) in ret:
        #for r in ret:
            #print to_cnf(r)
        conj = set(map(expr,ret))
        #conj.difference(kb.clauses)
        print "conjunto de soluciones:"
        for c in conj:
            if c in kb.clauses:
                print c
                print "   esta"
            else:
                print c
                print " no esta"

        #print "\n base kb inicial:"
        #for c in kb.clauses:
            #print c

    kbn.retract(to_cnf(expr(~a)))


#print setkb

#print prop_symbols(expr('(((P & Q) ==> R) & ( (T & Y) ==> P ) & T)'))

#for k in setkb:
 #   print prop_symbols(k)
