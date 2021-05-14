from flask import Flask, render_template, make_response, request, redirect, url_for,flash,get_flashed_messages,session,send_file
import bowser_sqlite3 as dbi
import sys,os
from utils import setupConn,recent_entries
import random
import bcrypt
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads/'

app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

def delete(conn, tablename, colname, id):
    '''delete from given table, where colname equals id'''
    curs = dbi.cursor(conn)
    query = ('delete from {} where {} = {}'
             .format(tablename,colname,id))
    curs.execute(query)
    conn.commit()

@app.route('/delete/<table>/<col>/<id>')
def delete_item(table,col,id):
    conn = dbi.connect('bowserdb.db')
    delete(conn,table,col,id)
    return redirect(url_for('index'))

@app.route('/',methods=['GET','POST'])
def index():
    conn,curs = setupConn()
    curs.execute("SELECT * FROM course WHERE school_id=1")
    print(curs.fetchall())
    return render_template('main.html')

@app.route('/join/', methods=["POST"])
def join():
    try:
        username = request.form['username']
        passwd1 = request.form['password1']
        passwd2 = request.form['password2']
        if passwd1 != passwd2:
            flash('passwords do not match','warning')
            return redirect( url_for('index'))
        hashed = bcrypt.hashpw(passwd1.encode('utf-8'), bcrypt.gensalt())
        hashed_str = hashed.decode('utf-8')
        print(passwd1, type(passwd1), hashed, hashed_str)
        conn,curs = setupConn()
        try:
            curs.execute("""INSERT INTO userpass(uid,username,hashed) VALUES(null,\"{}\",\"{}\")""".format(username, hashed_str))
            conn.commit()
        except Exception as err:
                flash('That username is taken: {}'.format(repr(err)),'warning')
                return redirect(url_for('index'))

        uid = curs.lastrowid
        flash('Welcome,{}'.format(username),'success')
        flash('FYI, you were issued UID {}'.format(uid),'success')
        session['username'] = username
        session['uid'] = uid
        session['logged_in'] = True
        session['visits'] = 1
        return redirect( url_for('search'))
    except Exception as err:
        flash('form submission error '+str(err),'error')
        return redirect( url_for('index') )
        
@app.route('/login/', methods=["POST"])
def login():
    try:
        username = request.form['username']
        passwd = request.form['password']
        conn,curs = setupConn()
        curs.execute("""SELECT uid,hashed FROM userpass WHERE username = \"{}\"""".format(username))
        row = curs.fetchone()
        if row is None:
            # Same response as wrong password,
            # so no information about what went wrong
            flash('login incorrect. Try again or join','warning')
            return redirect( url_for('index'))
        hashed = row['hashed']
        print('database has hashed: {} {}'.format(hashed,type(hashed)))
        print('form supplied passwd: {} {}'.format(passwd,type(passwd)))
        hashed2 = bcrypt.hashpw(passwd.encode('utf-8'),hashed.encode('utf-8'))
        hashed2_str = hashed2.decode('utf-8')
        print('rehash is: {} {}'.format(hashed2_str,type(hashed2_str)))
        if hashed2_str == hashed:
            print('they match!')
            flash('successfully logged in as '+username,'success')
            session['username'] = username
            session['uid'] = row['uid']
            session['logged_in'] = True
            session['visits'] = 1
            return redirect( url_for('search') )
        else:
            flash('login incorrect. Try again or join')
            return redirect( url_for('index'))
    except Exception as err:
        flash('form submission error '+str(err))
        return redirect( url_for('index') )



@app.route('/logout/',methods=['POST','GET'])
def logout():
    print('logout button pressed')
    try:
        if 'username' in session:
            username = session['username']
            session.pop('username')
            session.pop('uid')
            session.pop('logged_in')
            flash('You are logged out','success')
            return redirect(url_for('index'))
        else:
            flash('Sorry, but you are not logged in.','warning')
            return redirect( url_for('index') )
    except Exception as err:
        flash('some kind of error '+str(err),'error')
        return redirect( url_for('index') )




@app.route('/search/',methods=['GET','POST'])
def search():
    if 'username' in session:
        if request.method == 'POST':
            school_id = request.form['school_id']
            department = request.form['department']
            new_dep = request.form['new_dep']
            tt = request.form['course_tt']
            if len(new_dep) > 0:
                department = new_dep
            conn,curs = setupConn()
            curs.execute("""SELECT cid FROM course WHERE school_id=\"{}\" AND department=\"{}\" AND course_number=\"{}\"""".format(school_id,department,tt))
            cid = curs.fetchone()
            conn.close()

            if cid:
                cid = cid['cid']
                return redirect(url_for('specify',cid=cid))
            else:
                conn,curs = setupConn()
                curs.execute("""SELECT school_name FROM school WHERE school_id = {}""".format(school_id))
                school = curs.fetchone()['school_name']
                conn.close()
                course_code = department+'-'+str(tt)
                flash('Sorry, we do not have this course in record.','error')
                conn,curs = setupConn()
                curs.execute("""SELECT MAX(cid) FROM course""")
                cid = str(int(curs.fetchone()['MAX(cid)']) +1)
                new_url = '/specify/'+cid
                return redirect(url_for('add_course'))
        else:
            conn,curs = setupConn()
            curs.execute("""SELECT DISTINCT department FROM course""")
            dep_lst = curs.fetchall()
            conn.close()
            dep_lst = [list(i.values())[0] for i in dep_lst]
            return render_template('search.html',department_lst=dep_lst)
    else:
        flash('sorry,but you are not logged in.','warning')
        return redirect(url_for('index'))

@app.route('/specify/<cid>',methods=['GET','POST'])
def specify(cid):
    if 'username' in session:
        if request.method=='GET':
            conn,curs = setupConn()
            curs.execute("""SELECT * FROM course WHERE cid=\"{}\"""".format(cid))
            dct = curs.fetchone()
            school = dct['school_id']
            
            course_number = dct['course_number']
            course_title = dct['course_title']
            dep = dct['department']
            course_code = dep+'-'+str(course_number)
            conn.close()
            conn,curs = setupConn()
            curs.execute("""SELECT school_name FROM school WHERE school_id=\"{}\"""".format(school))
            school_name = curs.fetchone()['school_name']
            conn.close()
            conn,curs = setupConn()
            curs.execute("""SELECT pid FROM taughtby WHERE cid=\"{}\"""".format(cid))
            pids = curs.fetchall()
            prof_lst = []
            if pids:
                pids = [list(i.values())[0] for i in pids]
                print(pids)
                for pid in pids:
                    conn,curs = setupConn()
                    curs.execute("""SELECT prof_name FROM prof WHERE pid=\"{}\"""".format(pid))
                    prof_lst.append(curs.fetchone()['prof_name'])
            return render_template('specify.html',course_title=course_title,course_code=course_code,school=school_name,pids=pids,prof_lst=prof_lst,url='/specify/'+str(cid))
        else:
            pid = request.form['prof']
            new_prof = request.form['new_prof']
            if len(new_prof) == 0 and len(pid) == 0:
                flash('You did not specify the instructor of this class','warning')
                return redirect(url_for('specify',cid=cid))
            if len(new_prof) == 0:
                return redirect(url_for('content',cid=cid,pid=pid))
            conn,curs = setupConn()
            curs.execute("""SELECT pid FROM prof WHERE prof_name=\"{}\"""".format(new_prof))
            pid = curs.fetchone()
            conn.close()
            conn,curs = setupConn()
            if pid:
                # add this prof to taught by
                pid = pid['pid']
                curs.execute("""INSERT INTO taughtby VALUES (\"{}\",\"{}\")""".format(cid,pid))
                conn.commit()
                conn.close()
            else:
                #add this to to prof and taught by
                curs.execute("""INSERT INTO prof (prof_name) VALUES (\"{}\")""".format(new_prof))
                conn.commit()
                curs.execute("""SELECT pid FROM prof WHERE prof_name= \"{}\"""".format(new_prof))
                pid = curs.fetchone()['pid']
                curs.execute("""INSERT INTO taughtby VALUES (\"{}\",\"{}\")""".format(cid,pid))
                conn.commit()
                conn.close()
            return redirect(url_for('content',cid=cid,pid=pid))            
    else:
        flash('Sorry,but you are not logged in.','warning')
        return redirect(url_for('index'))

@app.route('/content/<cid>/<pid>',methods=['GET','POST'])
def content(cid,pid):
    if 'username' not in session:
        flash('Sorry,but you are not logged in.','warning')
        return redirect(url_for('index'))
    conn,curs = setupConn()
    curs.execute("""SELECT * FROM course WHERE cid=\"{}\"""".format(cid))
    dct = curs.fetchone()
    dep = dct['department']
    school_id = dct['school_id']
    course_number = dct['course_number']
    course_title = dct['course_title']
    course_code = dep+'-'+course_number
    conn.close()
    conn,curs=setupConn()
    curs.execute("""SELECT school_name FROM school WHERE school_id=\"{}\"""".format(school_id))
    school = curs.fetchone()['school_name']
    conn.close()
    conn,curs = setupConn()
    curs.execute("""SELECT prof_name FROM prof WHERE pid=\"{}\"""".format(pid))
    prof = curs.fetchone()['prof_name']
    conn.close()
    if request.method == 'GET':
        entries = recent_entries(cid,pid)
        return render_template('content.html',school_name=school,course_code=course_code,course_title=course_title,prof=prof,bloguser=session['username'],rows=entries)
    else:
        if len(request.form['comment']) > 0:
            user = session['username']
            entry = request.form['comment']
            conn,curs = setupConn()
            curs.execute('''INSERT INTO blog_entry(entered,username,cid,pid,entry) VALUES
                        (CURRENT_TIMESTAMP,?,?,?,?)''',[user,cid,pid,entry])
            conn.commit()           # don't forget to commit!
            return redirect(url_for('content',cid=cid,pid=pid))
        else:
            return redirect(url_for('content',cid=cid,pid=pid))


    return redirect(url_for('index'))

@app.route('/add_course/',methods=['POST',"GET"])
def add_course():
    if 'username' not in session:
        flash('Sorry,but you are not logged in')
        return redirect(url_for('index'))
    else:
        if request.method == 'GET':
            conn,curs = setupConn()
            curs.execute("""SELECT DISTINCT department FROM course""")
            dep_lst = curs.fetchall()
            conn.close()
            dep_lst = [list(i.values())[0] for i in dep_lst] 
            return render_template('add_course.html',department_lst=dep_lst)
        else:
            school_id = request.form['school_id']
            department = request.form['department']
            new_dep = request.form['new_dep']
            course_tt = request.form['course_tt']
            title = request.form['title']
            if len(new_dep) > 0:
                department = new_dep
            conn,curs = setupConn()
            curs.execute("""SELECT cid FROM course WHERE (department=\"{}\" AND school_id= \"{}\" AND course_number=\"{}\")""".format(department,school_id,course_tt))
            tmp = curs.fetchone()
            if tmp:
                cid = tmp['cid']
                flash('Sorry, this course is already in our databasee.')
                return redirect(url_for('specify',cid=cid))
            conn,curs = setupConn()
            curs.execute("""INSERT INTO course (cid,department, school_id, course_number, course_title) VALUES (NULL,\"{}\",\"{}\",\"{}\",\"{}\")""".format(department,school_id,course_tt,title))
            conn.commit()
            cid = curs.lastrowid
            conn.close()
            print(cid)
            return redirect(url_for('specify',cid=cid))


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
@app.route('/uploadfile', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print('no file')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            print('no filename')
            return redirect(request.url)
        else:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print("saved file successfully")
      #send file name as parameter to downlad
            return redirect('/downloadfile/'+ filename)
    return render_template('content.html')



# Download API
@app.route("/downloadfile/<filename>", methods = ['GET'])
def download_file(filename):
    return render_template('download.html',value=filename)


@app.route('/return-files/<filename>')
def return_files_tut(filename):
    file_path = UPLOAD_FOLDER + filename
    return send_file(file_path, as_attachment=True, attachment_filename='')


if __name__ == '__main__':
    conn=dbi.connect('bowserdb.db')

    if len(sys.argv) > 1:
        # arg, if any, is the desired port number
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
    app.debug = True
    app.run('0.0.0.0',port)
