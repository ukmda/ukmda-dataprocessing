import pymysql.cursors  
import sys
import os
import argparse


def testDB(id):
    user = 'batch'
    pwdfile = os.path.expanduser(f'~/.ssh/db_{user}.passwd')
    with open(pwdfile, 'r') as inf:
        pwd = inf.readline().strip()
    connection = pymysql.connect(host='ukmbatch',  
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
    arg_parser = argparse.ArgumentParser(description='Test the database')
    arg_parser.add_argument('action', metavar='ACTION', type=str, help='test string.')

    cml_args = arg_parser.parse_args()
    
    testDB(cml_args.action)
