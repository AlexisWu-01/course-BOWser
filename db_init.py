import bowser_sqlite3 as dbi

def setupConn():
    # sets up the connection to database
    conn = dbi.connect('bowserdb.db')
    curs = dbi.dict_cursor(conn)
    return conn,curs

conn,curs = setupConn()

sql_file = open("course.sql")
sql_as_string = sql_file.read()
curs.executescript(sql_as_string)
conn.commit()
conn.close()


