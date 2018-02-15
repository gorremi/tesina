from logic import *



recursos = ['A', 'B', 'C','D','E','F','H','I','J','K','L','M','N','O','P','Q','R']

objetivos = ['G1','G2','G3','G4','G5','G6','G7','G8','G9']

conectores = ['&','|','(',')']

reglas = []

"""
for i in range(0,5):
    obje = objetivos
    rec = recursos
    op_parentesis = 0
    reg = '(##    '
    for j in range(0,random.randrange(5)+2):
        #reg+="     $   "
        if len(rec) < 2:
            break
        simbolo = rec[random.randrange(len(rec))]
        reg+= simbolo
        rec.remove(simbolo)
        conec = conectores[random.randrange(len(conectores))]
        
        if conec == '(':
            op_parentesis +=1
            reg+=conectores[random.randrange(2)]
            reg+=conec
            break
        if (conec == ')') & (op_parentesis > 0):
            op_parentesis -=1
            reg+=conec
            reg+=conectores[random.randrange(2)]
            break
        if (conec != ')') & (conec != '('):
            reg+=conec
        
        
    ult = reg[len(reg)-1]
    if (ult != '(') | (ult != ')'):
        simbolo = rec[random.randrange(len(rec))]
        reg+=simbolo
    if ult == '(':
        reg = reg[0:len(reg)-1]
        
    for k in range(0,op_parentesis):
        reg += ')'
    reg+='  ##)'
    
    reg+= '==>'
    
    goal = obje[random.randrange(len(obje))]
    obje.remove(goal)
    
    reg+=goal
    
    reglas.append(reg)
    
"""


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
    

for r in reglas:
    print expr(r)


    



#print tt_entails(expr('(((P | Q) ==> R) & Q)'), expr('~R'))

#print tt_entails(P & Q -> R , Q)


#print tt_entails(expr('~R & R'), expr('~R'))


#print prop_symbols(expr('(((P | Q) ==> R) & Q)'))

#print tt_true(expr("(P >> Q) <=> (~P | Q)"))
#print tt_true(expr("(P & ~P) ==> TRUE"))


kb = PropKB()

kb.tell(expr('(((((L & Q) & B) | H) | (((I & D) & K) & N)) >> G7)'))
kb.tell(expr('H'))
#kb.tell(expr(' (T & Y) ==> P & Q & ~L '))


#print kb.clauses

setkb = set()

setkb.update(set(kb.clauses))


print pl_resolution(kb, expr('G7'))

#print setkb

#print prop_symbols(expr('(((P & Q) ==> R) & ( (T & Y) ==> P ) & T)'))

#for k in setkb:
 #   print prop_symbols(k)
 
 