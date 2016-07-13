import sys
import io
import hashlib
import loginer
import MySQLdb
import eventlet
import time
from eventlet.green.urllib import request, parse
from eventlet import tpool
from bs4 import BeautifulSoup

def getMemberInfo(classID = '1404052'):
    CLASSINFO_METHOD = 'ACTIONQUERYCLASSSTUDENT.APPPROCESS?mode=2&query=1'
    postData = parse.urlencode([('ClassNO', classID)]).encode('utf-8')
    reqData = request.Request(loginer.BASE_URL + CLASSINFO_METHOD, data = postData, headers = {'Cookie': cookie})
    response = request.urlopen(reqData).read().decode('GBK')
    page = BeautifulSoup(response, 'html.parser')
    studentList = []
    studentList.append(list(map(lambda x:str(x.string), page.find_all('table')[1].find_all('td', recursive = False)[1:4])))
    db = MySQLdb.connect(charset='utf8', host='localhost', user='root', passwd='NakatsuShizuru#2', db='sabrina')
    for row in page.find_all('table')[1].find_all('tr')[1:-1]:
        rowData = row.find_all('td', recursive = False)[1:4]
        rowList = list(map(lambda x:str(x.string), rowData))
        studentList.append(rowList)
        db.query('INSERT INTO student (id, name, sex) VALUES (\'%s\', \'%s\', \'%s\')' % tuple(rowList))
    db.commit()
    db.close()
    return studentList

def getResultInfo(studentID, termID):
    start = time.time()
    RESULTINFO_METHOD = 'ACTIONQUERYSTUDENTSCOREBYSTUDENTNO.APPPROCESS?mode=2'
    postData = parse.urlencode([('YearTermNO', termID), ('EndYearTermNO', termID), ('ByStudentNO', studentID)]).encode('utf-8')
    reqData = request.Request(loginer.BASE_URL + RESULTINFO_METHOD, data = postData, headers = {'Cookie': cookie})
    response = request.urlopen(reqData).read().decode('GBK')
    page = BeautifulSoup(response, 'html.parser')
    db = MySQLdb.connect(charset='utf8', host='localhost', user='root', passwd='NakatsuShizuru#2', db='sabrina')
    for row in page.find_all('table')[4].find_all('tr')[1:]:
        rowList = row.find_all('td')
        if rowList[0].string==None:
            break
        rowList = list(map(lambda x:str(x.string), rowList))
        dataList = []
        md5encoder = hashlib.md5()
        md5encoder.update((studentID + ''.join(rowList)).encode('utf-8'))
        dataList.append(md5encoder.hexdigest())
        dataList.append(studentID)
        dataList.append(str(termID))
        dataList+=rowList[1:7]+rowList[-2:]
        if dataList[-1] == 'None':
            dataList[-1] = 'NULL'
        print(dataList)
        db.query('''INSERT INTO result_data
                (hash_id, student_id, term, course_id, course_name, course_type, school_hour, credit, exam_type, result, point)
                VALUES
                ('%s', '%s', %s, '%s', '%s', '%s', %s, %s, '%s', '%s', %s)''' % tuple(dataList))
    db.commit()
    db.close()
    finish = time.time()
    print((finish - start))

classes = ['1404051', '1404052', '1404053']
cookie = loginer.Login()
db = MySQLdb.connect(charset='utf8', host='localhost', user='root', passwd='NakatsuShizuru#2', db='sabrina')

c = db.cursor()
c.execute('SELECT id FROM student')
IDList = c.fetchall()
print(IDList)
c.close()
db.close()

pool = eventlet.GreenPool()
start = time.time()
for i in pool.starmap(getResultInfo, [(student[0], term) for student in IDList for term in range(11, 14+1)]):
    pass

pool.waitall()
print('Time: %ss' % str(time.time()-start))
