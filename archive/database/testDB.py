import pymysql.cursors  
import sys
import os


def testDB(id):
    user = 'batch'
    pwdfile = os.path.expanduser(f'~/.ssh/db_{user}.passwd')
    with open(pwdfile, 'r') as inf:
        pwd = inf.readline().strip()
    connection = pymysql.connect(host='ukmonhelper',  
        user=user,  
        password=pwd,  
        db='test',  
        cursorclass=pymysql.cursors.DictCursor)  
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO books VALUES ({},'{}', {}, {})".format(id,'foo',34,56)
            cursor.execute(sql)
            connection.commit()
            sql = "SELECT * from `books` "
            cursor.execute(sql)
            result = cursor.fetchall()
            print(result)
    finally:
        connection.close()


if __name__ == '__main__':
    testDB(sys.argv[1])
