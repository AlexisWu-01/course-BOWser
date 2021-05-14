import bowser_sqlite3 as dbi

def setupConn():
    # sets up the connection to database
    conn = dbi.connect('bowserdb.db')
    curs = dbi.dict_cursor(conn)
    return conn,curs

def recent_entries(cid,pid,limit=100):
    '''Returns the most recent 'limit' entries from the blog'''
    conn,curs = setupConn()
    curs.execute('''SELECT entered as time,username,entry
                    FROM blog_entry
                    WHERE (cid=? AND pid=?)
                    ORDER BY entered DESC
                    LIMIT ?''',[cid,pid,limit])
    return curs.fetchall()
