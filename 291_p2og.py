import sqlite3
import itertools


DBname= raw_input("Please provide name of database to be normalized\n")

conn = sqlite3.connect(DBname+'.db')
c = conn.cursor()
conn.text_factory = str

tableList=[]
coverTable=[]

    
def permutingLHS(i):
    combin=[]    
    
    for x in range(len(i)+1):
        combin= combin+ list( itertools.combinations(i,x))
        
    return(combin)

def findClosure(string,checked,dependencies):
    string = set(string)
    string =''.join(string)
    checking = checked
    permutations = permutingLHS(string)
    
    for i in permutations:
        for j in dependencies:
            if len(j[0].replace(',','')) == len(''.join(i).replace(',','')):
                           
                if (j in checking):
                    continue
                
                if set(i)==set(j[0].replace(',','')):
                    checking.append(j)
                    string = findClosure(string+j[1].replace(',','')+j[0].replace(',',''),checking,dependencies)
                
    return string
    
    
'''
if v in somethingElse:
    #then x is redundent
    print("HI!")
    print(set(u,v))
    print('\n')
    #aList.remove(dep)
    #aList.append(set(u,v))
'''

    
def computeMinCov(dependencies):
    resolved=False
    aList = []
    track=0
    for i in dependencies:
        if len(i[1]) > 1:
            RHS = ''.join(i[1]).replace(',','')
            
            rep1 = (i[0], RHS[0])
            rep2 = (i[0], RHS[1])
            
            dependencies.remove(i)
            
            dependencies.append(rep1)
            dependencies.append(rep2)
        
    
    for j in dependencies:
        aList.append(j)
    #checks individual components of RHS for redundancy    
    while (resolved ==False):
        entered=False        
        sw=[]
        
        #covSet=set()
        #covSet.clear()
        
        for dep in aList:
            modDep=[]            
            for j in aList:
                modDep.append(j)
            modDep.remove(dep)
            for x in dep[0].replace(',',''):
                sw=[]                
                u = dep[0].replace(x,'').replace(',','')
                v = dep[1].replace(',','')
                somethingElse = findClosure(u,sw,modDep)
              
                if (x in somethingElse) or ( v in somethingElse):
                    # We check both for when x(RHS) or v(LHS) is in the closure.
                    # As we removed the tested dependancy from the modDep, if it occurs still
                    # x would be redundant.
                    sw=[]
                    sw.append(dep[0].replace(x,'').replace(',,',',').strip(','))
                    sw.append(dep[1].replace(',',''))

                    aList[track]=tuple(sw)
                    entered = True
            track=track+1     
        
        if entered==False:
            resolved=True
            
    resolved = False
    

    #checks an entire LHS block for redundancy
    while resolved == False:
        entered=False        
        sw=[]
        
        for dep in aList:
            modDep=[]            
            for j in aList:
                modDep.append(j)
                
            modDep.remove(dep)
            
            sw=[]
            u = dep[0].replace(',','')
            v = dep[1].replace(',','')
            somethingElse = findClosure(u,sw,modDep)
 
            
            if (v in somethingElse):
                # Then x is redundent
                # Since we are removing dependencies all together, we cannot use x as a search
                # because we may find that the RHS occurs multiple times, but they may not be redundant.
                
                aList.remove(dep)
                entered = True
                
        if entered==False:
            resolved=True                    
    
   
    return (aList)


def CreateTable(tableList):
    tableDict={}
    build=[]
    temp=[]
    for x in tableList:
        u =x[0].replace(',','')
        v = x[1].replace(',','')
        if u in tableDict:
            tableDict[u]+=v
        else:
            tableDict.update({u:u+v})
    for f, v in  tableDict.iteritems():
        build.append(v)
    print build
    
    for x in build:
        tbName="Output_R1_"+x
        print (tbName)
        for y in range(len(x)):
            if y == 0:
                query = 'create table ' +tbName+ '('+x[0]+');'
                c.execute(query)
            else:
                query ='alter table '+tbName+' add column '+x[y]+';'
                c.execute(query)

                



def main():
    dependencies=[] 
    rs = c.execute('SELECT * FROM Input_R1 WHERE 1=0');
    dir(rs)
    for x in rs.description:
        tableList.append(x[0])
        
    #print tableList
        
    
    c.execute("Select * from Input_FDs_R1")
    FD=c.fetchone()
    
    while FD != None:
        dependencies.append(FD)
        FD=c.fetchone()
    
    
    for i in dependencies:
        #print i
        dw=[]
        coverageSet=set()
        coverageSet.clear()
        
        coverageSet.update(i[0])
        coverageSet.update(i[1])
        CoverStr=(','.join(coverageSet)).replace(',','')
        permuteList = permutingLHS(CoverStr)
        
        
        something = set(findClosure(CoverStr,dw,dependencies))
        
        itemSet = set(tableList)
        if something == itemSet:
            print something, "Super Key = ", i[0]
        #else:
            #print something
        #print("I'M OUT")
    
    coverList =computeMinCov(dependencies)
    print coverList
    CreateTable(coverList)
    
    
    
    
        
main()