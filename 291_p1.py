import hashlib
import re
import sqlite3
import random
import datetime



conn = sqlite3.connect("hospital.db")
c = conn.cursor()
conn.text_factory = str
doctor="D"

#Login returns role of user
def login():
    u = raw_input("Enter username: ")
    p = raw_input("Enter password: ")
    if re.match("^[\w.-]*$", u) and re.match("^[\w.-]*$", p):
        ep = hashlib.sha224(p).hexdigest()
        c.execute('SELECT password FROM staff WHERE login = ?', (u,))
        buff = c.fetchone()
        if buff!= None:
            edp = buff[0]
            while edp != None:
                if edp == ep:
                    print ("Login Successful")
                    c.execute('SELECT role FROM staff WHERE login = ? AND password = ?;', (u, ep,))
                    return c.fetchone()[0], u
                else:
                    buff = c.fetchone()
                    if buff!= None:
                        edp = buff[0] 
                    else:
                        edp= None
    else:
        print("Invalid username or password.")

#Add user to database 
def add_user(): 
    un = raw_input("Enter new username: ")
    pw = raw_input("Enter new password: ")
    na = raw_input("Enter name: ")
    ro = raw_input("Enter role: ").upper()
    sid = input("Enter staff id: ")
    
    epw = hashlib.sha224(pw).hexdigest()
    
    c.execute('INSERT INTO staff VALUES (?,?,?,?,?);', (sid,ro,na,un,epw))
    
    conn.commit()
    print("User %s created successfully" %(un))

#------NURSE STUFF------

#Closes a chart with given chart ID 
def closeChart(chartId):
    c.execute('SELECT hcno FROM charts c WHERE c.chart_id = ? and c.edate is NULL;',(chartId,))
    test = c.fetchone()
    if test == None:
        print "No chart to close"
    else:
        now = datetime.datetime.now()
        edate = now.strftime("%Y-%m-%d %H/%M/%S")
        c.execute('UPDATE charts SET edate=? WHERE chart_id =?;',(edate,chartId))
        conn.commit()
        print "Chart updated"


#Opens a chart with a new HCNO, requires role and name to properly return
def openChart(newHcno, role, name):
     #Getting chart ID
    c.execute('SELECT chart_id FROM charts WHERE hcno = ? AND edate is NULL;',(newHcno,))
    test = c.fetchone()
    if test == None:
        print "No open charts for this patient - Creating new chart"
        now = datetime.datetime.now()
        adate = now.strftime("%Y-%m-%d %H/%M/%S")
        exists = True
        while exists:
            newChartId = raw_input("Enter a new chart ID: ")
            c.execute('SELECT hcno FROM charts WHERE chart_id = ?;',(newChartId,))
            if c.fetchone() == None:
                exists = False
            else:
                print "That chart ID already exits."
        print "Chart Id: "+newChartId
        print "HCNO: "+newHcno
        print "Date: "+adate
        correct = raw_input("Is this correct? (Y/N) ")
        edate = None
        if correct == 'y' or correct == 'Y':
            c.execute('INSERT INTO charts VALUES (?,?,?,?);',(newChartId,newHcno,adate,edate))
            conn.commit()
            print "Chart created"
            return
        else:
            print "Returning to main menu"
            NurseFunction(role, name)
    else:
        print "Chart "+test[0]+" for this patient already exists"
        choice = raw_input("1.Close this chart 2.Leave chart open ")
        if choice == '1':
            closeChart(test[0])
        else:
            return
                
    
#Nurse main menu
def NurseFunction(role, name):
    print "-----NURSE-----"
    logon = True
    while logon == True:
        task = raw_input("1:New chart 2:Close chart 3:List current chart 4:Add symptom 5:Logout ")
        if re.match("^[1-5]{1}$",task):
            task = int(task)            
            if task == 1:
                #Open chart
                newHcno = raw_input("Enter patient HCNO: ")
                openChart(newHcno,role, name)                                             
            elif task == 2:
                #Closing chart
                chartId = raw_input("Enter chart ID: ")
                closeChart(chartId)                  
            elif task == 3:
                #List charts
                print "Getting charts"
                get_chart() 
            elif task == 4:
                #Add symptom
                print "Adding new symptom under "+name
                rec_symp(role, name)    
            else:
                logon = False
        else:
            print "Invalid input"
    return "logout"
    


#------DOCTOR STUFF------

#Record a symptom with under a name and role
def rec_symp(role, name):

    if role == 'D':
        patient = raw_input("Enter the hcno of the patient: ")
        c.execute('SELECT chart_id FROM charts WHERE hcno = ? AND edate is NULL;', (patient,))

        chart =c.fetchone()
        if chart is None: #or == None?
            print "Patient already discharged."
        else:
            chart = chart[0]
            symp = raw_input("Symptom: ")
            date = str(datetime.datetime.now())
            c.execute('SELECT staff_id FROM staff WHERE login = ?;', (name,));

            sid=c.fetchone()
            if sid is not None:
                staff_id = sid[0]
                c.execute('INSERT INTO symptoms VALUES (?,?,?,?,?);', (patient,chart,staff_id,date,symp,))
                conn.commit()
                print("Symptom added successfully")
            

#Record a diagnosis under a name
def rec_diag(name):
    #assume we've already validated the user as a doctor.
    patient = raw_input("Patient (hcno): ")
    c.execute('SELECT chart_id FROM charts WHERE hcno = ? AND edate is NULL;', 
              (patient,))
    chart = c.fetchone()
    c.execute('SELECT staff_id FROM staff WHERE login = ?;', (name,))
    staff_id = c.fetchone()
    if chart is None:
        print "The patient has been discharged or some other problem has occurred."
    else:
        chart=chart[0]
        staff_id=staff_id[0]
        diag = raw_input("Diagnosis: ")
        date = str(datetime.datetime.now())
        c.execute('INSERT INTO diagnoses VALUES (?,?,?,?,?);', (patient,chart,
                                                                staff_id,date,diag))
        conn.commit()
        print "Diagnosis successfully added."
        

#Prescribe under a name
def prescribe(name):
    loop=True
    patient = raw_input("Patient (hcno): ")
    c.execute('SELECT chart_id FROM charts WHERE hcno = ? AND edate is NULL;', 
              (patient,))
    chart = c.fetchone()
    c.execute('SELECT staff_id FROM staff WHERE login = ?;', (name,))
    staff = c.fetchone()
    if chart is None:
        print "The patient has been discharged or some other problem has occurred."
    else:
        med = raw_input("Enter the drug you would like to prescribe: ")
        c.execute('SELECT drug_name FROM drugs WHERE drug_name = ?;', (med,))
        if c.fetchone() is None:
            print "This drug is not in our system."
        else:
            check = check_allergy(patient,med)
            if check == "Good":
            # check_allergy(med) will be defined later.
                amount = input("Enter the amount: ")
                c.execute('SELECT sug_amount FROM dosage WHERE drug_name = ?;', 
                          (med,))
                suggested = int(c.fetchone()[0])
                while loop:
                
                    if amount > suggested:
                        print "The suggested amount for this drug is %s. Would you like to proceed (Y/N/(C)hange)?" %str(suggested)
                        response = raw_input().lower()
                        if response == 'y':
                            start = raw_input("Start date YYYY-MM-DD: ")
                            end = raw_input("End date YYYY-MM-DD: ")
                            date = str(datetime.datetime.now())
                            c.execute('INSERT INTO medications VALUES (?,?,?,?,?,?,?,?);', (patient,'' .join(chart),'' .join(staff),date,start,end,amount,med))
                            loop=False
                        if response == 'n':
                            return
                        if response =='c':
                            amount = input("Please enter new amount\n")      
                                
                    else:
                        start = raw_input("Start date YYYY-MM-DD: ")
                        end = raw_input("End date YYYY-MM-DD: ")
                        date = str(datetime.datetime.now())
                        c.execute('INSERT INTO medications VALUES (?,?,?,?,?,?,?,?);', 
                                  (patient,'' .join(chart),'' .join(staff),date,start,end,amount,med))
                        loop = False
                       
    conn.commit()

                

#Check the allergy of a patient with the medication
def check_allergy(patient,med):
    c.execute('SELECT drug_name FROM reportedallergies WHERE hcno = ? AND drug_name=?;', (patient,med,))
    algs = c.fetchone()
    while algs is not None:
        if ''.join(algs)==med:
            print( "Cannot prescribe this drug. Patient is allergic to %s." %(med))
            return "NG"
        algs = c.fetchone()
    
    c.execute('SELECT alg FROM inferredallergies WHERE canbe_alg = ?;', (med,))
    is_alg = c.fetchone()
    if is_alg is None:
        return "Good"        
    while is_alg is not None:
        print "WARNING: patient is allergic to %s. Could be allergic to %s." %(is_alg,med)
        is_alg = c.fetchone()
        
    return "NG"
        

#Get a chart
def get_chart():
    loop=True
    patient = raw_input("Enter hcno of patient: ")
    c.execute('SELECT chart_id, adate,edate FROM charts WHERE hcno = ? ORDER BY adate;', (patient,))
    i = c.fetchone()
    if i ==None:
        print("Patient not found")
        return
    while i != None:         
        if None in i:
            print ("{0}  OPEN" .format(i))
        else:
            print ("{0}   CLOSED" .format(i))
        i = c.fetchone()
      
            
    display = raw_input("Of the charts displayed, would you like to select one (Y/N)?\n ").lower()
 
    while loop==True:
         
        if display == 'y':
            chart = raw_input("Enter the chart you would like to see (chart_id): ")
            c.execute('SELECT * FROM symptoms s, diagnoses d, medications m WHERE s.chart_id = ? AND d.chart_id=s.chart_id AND s.chart_id=m.chart_id ORDER BY mdate DESC, ddate DESC, obs_date DESC;', (chart,))
            results = c.fetchone()
            while results!=None:
                print results
                results = c.fetchone()
            loop=False
                
        elif display == 'n':
            loop=False            
            return
        else:
            display= raw_input("Please enter Y or N\n")
        

#Main menu for doctor
def DoctorFunction(role, name):
    if role =='D':
            a = raw_input("What would you like to do? 1:List patient chart; 2:Add symptom; 3:Add diagnosis; 4:Add medication; 5:logout\n").lower()  
            if a == '1':
                get_chart() 
            elif a =='2':
                rec_symp(role, name)
            elif a =='3':     
                rec_diag(name)
            elif a =='4':
                prescribe(name)
            elif a =='5':
                return 'logout'
            else:
                print("No such function exists")




#------ADMIN STUFF------

def AdminFunction(role):
    if role =='A':
        a = raw_input("What would you like to do? 1:Create report; 2:List prescribed for category;\n 3:List medication for diagnosis; 4:List diagnoses for drug; 5:logout\n").lower()
        
        if (a == '1'):
            d=raw_input("Please specify date to start from in form YYYY-MM-DD\n")
            f= datetime.datetime.strptime(d,'%Y-%m-%d')
            
            c.execute ('SELECT name, drug_name, sum(amount)  FROM staff, medications WHERE role = ? AND staff.staff_id =medications.staff_id AND medications.mdate>=? GROUP BY name, drug_name;', (doctor, f,))
            Report= c.fetchone()
            print ('Doctor DrugName Amount')
            while Report != None:
                print (Report)
                Report = c.fetchone()
            
                
        elif (a == '2'):
            d=raw_input("Please specify date to start from in form YYYY-MM-DD\n")
            f= datetime.datetime.strptime(d,'%Y-%m-%d')
            
            c.execute ('SELECT category, medications.drug_name, sum(amount) FROM drugs, medications WHERE medications.drug_name=drugs.drug_name AND medications.mdate>=? GROUP BY category, medications.drug_name;', (f,))
            ReportD= c.fetchone()
            
            print ('Category DrugName Amount')
            while ReportD is not None:
                print (ReportD)
                ReportD = c.fetchone()
                
            c.execute ('SELECT category, sum(amount) FROM drugs, medications WHERE medications.drug_name=drugs.drug_name AND medications.mdate>=? GROUP BY category;', (f,))
            ReportT= c.fetchone()
            print ('Category Total Amount')        
            while ReportT is not None:
                print (ReportT)
                ReportT = c.fetchone()              
                
        elif (a == '3'):
            c.execute ('SELECT diagnosis FROM diagnoses;')
            dia=c.fetchone()
            while dia is not None:
                print(dia)
                dia=c.fetchone()
            d=raw_input("Please specify diagnosis.\n")
            c.execute('SELECT drug_name FROM medications, diagnoses WHERE diagnosis =? and mdate>=ddate and diagnoses.chart_id=medications.chart_id GROUP BY drug_name ORDER BY count(drug_name) ASC;', (d,))
            drug=c.fetchone()
            print("Drugs given after %s in ascending order." %(d))
            while drug is not None:
                print(drug)
                drug=c.fetchone()
            
        
        elif (a == '4'):
            c.execute ('SELECT drug_name FROM drugs;')
            dia=c.fetchone()
            while dia is not None:
                print(dia)
                dia=c.fetchone()
            d=raw_input("Please specify the drug.\n")
            c.execute('SELECT diagnosis FROM medications, diagnoses WHERE drug_name =? and ddate<=mdate and diagnoses.chart_id=medications.chart_id GROUP BY diagnosis ORDER BY avg(amount) ASC;', (d,))
            drug=c.fetchone()
            print("Diagnosis given before %s in ascending order of average drug amount." %(d))
            while drug is not None:
                print(drug)
                drug=c.fetchone()
            
        elif (a == '5'):
            return 'logout'
        
        else:
            print("No such function exists")


#Read a file and execute the commands in it
def readSQL(filename):
    fd = open(filename,'r')
    sqlFile = fd.read()
    fd.close()
    commands = sqlFile.split(";")
    for com in commands:
        try:
            c.execute(com+';')
        except:
            print "error in command "+com

        
    
#------MAIN------

def main():
    #Load SQL files
    #readSQL("CreateTable.sql")
    #readSQL("Data.sql")
    action=''  
    while action is not "quit":
        s =''
        action = raw_input("Would you like to 1:login, 2:create a new user or (quit)?\n")
        if action == '1':
            log=login()
            if log != None:
                role, name=log
                if role =='A' or role== 'D' or role =='N':
                    while s is not "logout":
                        if role=='A':
                            print "-----ADMIN-----"
                            s=AdminFunction(role)
                        if role == 'D':
                            print "-----DOCTOR-----"
                            s= DoctorFunction(role, name)
                        if role =='N':
                            s= NurseFunction(role,name)
                    print("Logging you out.")
                                
                        
            else:
                print("Name and password not found, please try again.");
                
        elif action == '2':
            add_user()
        elif action== 'quit':
            return
        else:
            print("Invalid command %s" %(action))
        

if __name__ == "__main__":
    main()
