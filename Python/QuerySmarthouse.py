import MySQLdb


#Return an array containing all results of the given SQL query 
def query4(cmd, arg1, arg2, arg3):
    result = []

    db = MySQLdb.connect(host="127.0.0.1", # your host
                         user="admin", # your username
                         passwd="admin", # your password
                         db="smarthouse") # name of the data base

    cur = db.cursor() 

    #Execute the sql command
    cur.execute(cmd, arg1, arg2, arg3)

    for row in cur.fetchall() :
        #print row[:]
        result.append(row)

    return result

def query3(cmd, arg1, arg2):
    result = []

    db = MySQLdb.connect(host="127.0.0.1", # your host
                         user="admin", # your username
                         passwd="admin", # your password
                         db="smarthouse") # name of the data base

    cur = db.cursor() 

    #Execute the sql command
    cur.execute(cmd, arg1, arg2)

    for row in cur.fetchall() :
        #print row[:]
        result.append(row)

    return result


def query2(cmd, arg1):
    result = []

    db = MySQLdb.connect(host="127.0.0.1", # your host
                         user="admin", # your username
                         passwd="admin", # your password
                         db="smarthouse") # name of the data base

    cur = db.cursor() 

    #Execute the sql command
    cur.execute(cmd, arg1)

    for row in cur.fetchall() :
        #print row[:]
        result.append(row)

    return result

def query1(cmd):
    result = []

    db = MySQLdb.connect(host="127.0.0.1", # your host
                         user="admin", # your username
                         passwd="admin", # your password
                         db="smarthouse") # name of the data base

    cur = db.cursor() 

    #Execute the sql command
    cur.execute(cmd)

    for row in cur.fetchall() :
        #print row[:]
        result.append(row)

    return result
