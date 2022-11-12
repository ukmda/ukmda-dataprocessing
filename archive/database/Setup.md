# Installing MariaDB

## Create /etc/yum.repos.d/MariaDB.repo

[mariadb]
name = MariaDB
baseurl = http://yum.mariadb.org/10.3/centos7-amd64
gpgkey=https://yum.mariadb.org/RPM-GPG-KEY-MariaDB
gpgcheck=1

## Install packages

yum update
yum install mariadb-server mariadb-client mariadb-devel mariadb-shared mariadb-common

## Create Databases and Tables

mysql -u root -p -h localhost 
execute contents of create_dbs_and_users.sql
execute contents of create_tables.sql

## Connecting from Python

pip install mysql-connector-python  
pip install pymysql  


    import pymysql.cursors  
    connection = pymysql.connect(host='localhost',  
        user='batch',  
        password='xxxxxxx',  
        db='test',  
        cursorclass=pymysql.cursors.DictCursor)  
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO books VALUES ({},'{}', {}, {})".format(sys.argv[1],'foo',34,56)
            cursor.execute(sql)
            connection.commit()
            sql = "SELECT * from `books` "
            cursor.execute(sql)
            result = cursor.fetchall()
            print(result)
    finally:
        connection.close()
