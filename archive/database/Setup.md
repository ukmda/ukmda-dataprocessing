# Installing MariaDB

## Installing and Migrating
For installation and migration instructions see `migratingBatchServer.md` in the `server_setup` folder

## Connecting from Python

These packages are installed as part of the ukmda tooling. 
``` bash
pip install mysql-connector-python  
pip install pymysql  
```
``` python 

    import pymysql.cursors  
    connection = pymysql.connect(host='localhost',  
        user='batch',  
        password='xxxxxxx',  
        db='test',  
        cursorclass=pymysql.cursors.DictCursor)  
    try:
        with connection.cursor() as cursor:
            #sql = "INSERT INTO books VALUES ({},'{}', {}, {})".format(sys.argv[1],'foo',34,56)
            cursor.execute(sql)
            connection.commit()
            sql = "SELECT * from matches limit 10 "
            cursor.execute(sql)
            result = cursor.fetchall()
            print(result)
    finally:
        connection.close()
```