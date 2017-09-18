import sqlite3
import itertools
import re


DBname= raw_input("Please provide name of database to be normalized\n")

conn = sqlite3.connect(DBname+'.db')
#conn.execute('pragma foreign_keys=ON;')
c = conn.cursor()
conn.text_factory = str

tableList=[]
coverTable=[]

def userClosure():
    attributes = raw_input("Please enter the atributes (X1, X2, ..., Xn): ")
    depName = raw_input("Enter the FD table name (table name 1, 2, ...): ")
    
    depends = depName.split(',')
    
    
    
    dependencies=[] 
      
            
        #print tableList
            
    for i in depends:
        query = 'SELECT * FROM ' + i + ';'
        c.execute(query)
        FD = c.fetchone()
        
        while FD != None:
            dependencies.append(FD)
            FD=c.fetchone()
            
    for i in dependencies:
        #print i
        dw=[]
        coverageSet=set(attributes)
        #coverageSet.clear()
                    
        #coverageSet.update(i[0])
        #coverageSet.update(i[1])
        CoverStr=(','.join(coverageSet)).replace(',','')
        permuteList = permutingLHS(CoverStr)
                    
                    
        something = set(findClosure(CoverStr,dw,dependencies))
                    
    
def equivalence():
    inF1 = raw_input("Enter the tables for F1 (table 1, 2, ...): ")
    inF2 = raw_input("Enter the tables for F2 (table 1, 2, ...): ")
    
    
    depends1 = inF1.split(',')
    depends2 = inF2.split(',')    
        
        
    dependencies1=[]
    dependencies2=[]
          
                
            #print tableList
                
    for i in depends1:
        query1 = 'SELECT * FROM ' + i + ';'
        c.execute(query1)
        FD1 = c.fetchone()
            
        while FD1 != None:
            dependencies1.append(FD1)   
            FD1=c.fetchone()
                
    for i in dependencies1:
        #print i
        dw1=[]
        coverageSet1=set()
        coverageSet1.clear()
                        
        coverageSet1.update(i[0])
        coverageSet1.update(i[1])
        CoverStr1=(','.join(coverageSet1)).replace(',','')
        permuteList1 = permutingLHS(CoverStr1)
                        
                        
        something1 = set(findClosure(CoverStr1,dw1,dependencies1))
        
        
    for j in depends2:
        query2 = 'SELECT * FROM ' + j + ';'
        c.execute(query2)
        FD2 = c.fetchone()
                    
        while FD2 != None:
            dependencies2.append(FD2)   
            FD2=c.fetchone()
                        
    for j in dependencies2:
        #print i
        dw2=[]
        coverageSet2=set()
        
        coverageSet2.clear()
                                
        coverageSet2.update(j[0])
        coverageSet2.update(j[1])
        CoverStr2=(','.join(coverageSet2)).replace(',','')
        permuteList = permutingLHS(CoverStr2)
                                
                                
            
        something2 = set(findClosure(CoverStr2,dw2,dependencies2))    
    

    if something1 == something2:
        print "Equivalent"
    else:
        print "Not equivalent"
    

    
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

def CreateBCNFRelations(tableList,sk,fc):
    tnameList = []
    tableDict={}
    build=[]
    primary=[]
    changedcover=[]

    for x in tableList:
        u =x[0].replace(',','')
        v = x[1].replace(',','')
        
        
        
        if u in tableDict:
            tableDict[u]+=v
        else:
            tableDict.update({u:u+v})
    for f, v in  tableDict.iteritems():
        key = set(f)
        relation =set(v)
        once = False
        g=''
        h=''

        if key.intersection(fc):
            
            if f in v and once == False:
                for j in range (len(f)):
                    g= g+f[j]+','
                g= 'PRIMARY KEY ('+g.strip(',')+')'
                primary.append (g)
                once = True
                tup= (','.join(f),','.join(v.replace(f,'')))
                changedcover.append(tup)
                
            
            fc = fc-(relation-key)
            build.append(','.join(relation))
            
    build.append(','.join(fc))
    primary.append("PRIMARY KEY(" +','.join(fc)+")")
    tup= (','.join(fc),','.join(fc))
    
    changedcover.append(tup)
    
    count =0    
    
    for x in build:
        tbName="Output_R1_"+x.replace(',','').replace(' primary key ','')

        query = 'CREATE TABLE ' + tbName + '('+x+','+primary[count]+');'
        c.execute(query)
            
        count=count+1
    
    tbName="Output_R1_"+sk.replace(',','')
    tnameList.append(tbName)

    query = 'create table ' +tbName+ '('+sk+');'
    c.execute(query)

    build.append(sk.replace(',',''))
    createDependency(changedcover)
    
    return tnameList, build    


def Create3nFRelation(tableList,sk):
    tnameList = []
    tableDict={}
    build=[]
    primary=[]
  
    for x in tableList:
        u =x[0].replace(',','')
        v = x[1].replace(',','')
        if u==v and len(v) ==1:
            continue
        
        if u in tableDict:
            tableDict[u]+=v
        else:
            tableDict.update({u:u+v})

    
            
    for f, v in  tableDict.iteritems():
        once = False
        ct = 0
        g=''
        h=''
        while ct < len(v):
            if f in v and once == False:
                for j in range (len(f)):
                    g= g+f[j]+','
                g= 'PRIMARY KEY ('+g.strip(',')+')'
                primary.append (g)
                once = True
            
            h=h+v[ct]+','
            ct =ct+1
            
        build.append(h.strip(','))
        
    count =0    
    for x in build:
    
        tbName="Output_R1_"+x.replace(',','').replace(' primary key ','')
        tnameList.append(tbName)

        query = 'CREATE TABLE ' + tbName + '('+x+','+primary[count]+');'
        c.execute(query)
            
        count=count+1
    if len(sk)>0:
        tbName="Output_R1_"+sk.replace(',','')
        tnameList.append(tbName)
        query = 'create table ' +tbName+ '('+sk+');'
        c.execute(query)

        build.append(sk.replace(',',''))
    createDependency(tableList)
    
    return tnameList, build

def createDependency(tableList):
    tnameList = []
    tableDict={}
    build=[]
    primary=[]
    for x in tableList:
        u =x[0].replace(',','')
        v = x[1].replace(',','')
        if u==v and len(v) ==1:
            continue
        
        if u in tableDict:
            tableDict[u]+=v
        else:
            if u!=v:
                tableDict.update({u:u+v})
            else:
                tableDict.update({u:v})
                
    for f, v in  tableDict.iteritems():
        tbName="Output_FDS_R1_"+v
        query = "CREATE TABLE " + tbName+ " (LHS, RHS);"
        c.execute(query)
        query = "INSERT INTO " +tbName+" VALUES (?, ?);"
        if v!=f:
            c.execute(query, (f, v.replace(f,''),))
        else:
            c.execute(query, (f, f))
            
    

    

def populate(tnameList, build):
    for y in tnameList:
        
        for i in build:
            if i in y.strip('Output_R1_'):
                aString=''
                for x in i:
                    aString = aString+x+','
                aString=aString.strip(',')
                query = 'INSERT INTO ' +y+' SELECT '+aString+ ' FROM INPUT_R1;'
                '''
                query = 'UPDATE ' + y + ' SET ' + x + '=(SELECT A FROM INPUT_R1);'
                print(query)
                '''
                c.execute(query)
                
                conn.commit()
                    
    


def normBCNF():
    dependencies=[] 
    superkey=''    
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
            fullCover =something
            superkey=i[0]
        #else:
            #print something
        #print("I'M OUT")
    
    coverList =computeMinCov(dependencies)
    print coverList
    tList,bld =CreateBCNFRelations(coverList, superkey, fullCover)
    '''
    tList,bld = Create3nFRelation(coverList, superkey)
    '''
    pop = raw_input("Populate tables (y/n)? ")
    if pop == 'y' or pop == 'Y':
        populate(tList, bld)
    
def norm3NF():
    dependencies=[]
    superkey=''
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
        print(something)
        print(itemSet)
        if something == itemSet:
            print something, "Super Key = ", i[0]
            fullCover =something
            superkey=i[0]
           #else:
               #print something
           #print("I'M OUT")
    coverList =computeMinCov(dependencies)
    print coverList
    #tList,bld =CreateBCNFRelations(coverList, superkey, fullCover)
       
    tList,bld = Create3nFRelation(coverList, superkey)
    
    pop = raw_input("Populate tables (y/n)? ")
    if pop == 'y' or pop == 'Y':
        populate(tList, bld)
           
    
def main():
    contin = True
    while contin:
        intent = raw_input("What would you like to do? [1]:BCNF, [2]:3NF, [3]:compute closure, [4]:check equivalence, [quit] ")
        if intent == '1':
            normBCNF()
        if intent == '2':
            norm3NF()
        if intent == '3':
            userClosure()
        if intent == '4':
            equivalence()
        if intent == 'quit':
            conn.close()
            return
            
main()