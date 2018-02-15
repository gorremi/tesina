from logic import *



recursos = ['A', 'B', 'C','D','E','F','H','I','J','K','L','M','N','O','P','Q','R']

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


def buscar_laterales(x,xs):
        for (l,c,r) in xs:
            
            if x == c:
                if (l == "leaf") & (r == "leaf"):
                    
                    return [c]
                else:
                    return buscar_laterales(l,xs)+buscar_laterales(r,xs)




def armar_arbol_ok(xs):
    
    print buscar_laterales(Expr('FALSE'),xs)
    #print xs


def es_padre(o,xs):
    for (l,c,r) in xs:
        if o == l:
            return True
        if o == r:
            return True
    
    return False        


def descartar_padres(xs):
        lista_final=[]
        for (l,c,r) in xs:
            if not es_padre(c,xs):
                lista_final.append((l,c,r))
    
        for (l,c,r) in lista_final:
            if 'G7' in str(c):
                print c
   
        




kb = PropKB()    

for r in reglas:
    kb.tell (expr(r))


    



#print tt_entails(expr('(((P | Q) ==> R) & Q)'), expr('~R'))

#print tt_entails(P & Q -> R , Q)


#print tt_entails(expr('~R & R'), expr('~R'))


#print prop_symbols(expr('(((P | Q) ==> R) & Q)'))

#print tt_true(expr("(P >> Q) <=> (~P | Q)"))
#print tt_true(expr("(P & ~P) ==> TRUE"))




#kb.tell(expr('(((((L & Q) & B) | H) | (((I & D) & K) & N)) >> G7)'))
#kb.tell(expr('H'))
#kb.tell(expr(' (T & Y) ==> P & Q & ~L '))


#print kb.clauses

setkb = set()

setkb.update(set(kb.clauses))


posee_recursos = []
for i in range(0,5):
    posee_recursos.append(recursos[random.randrange(len(recursos))])

for r in posee_recursos:
    kb.tell(expr(r))
    
for r in reglas:
    print r
print posee_recursos



(resultado,arbol) = pl_resolution(kb, expr('G7'))





print resultado
if resultado:
    armar_arbol_ok (arbol)
else:
    descartar_padres(arbol)

#print setkb

#print prop_symbols(expr('(((P & Q) ==> R) & ( (T & Y) ==> P ) & T)'))

#for k in setkb:
 #   print prop_symbols(k)
 
 