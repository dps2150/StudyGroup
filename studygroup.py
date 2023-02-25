#!/usr/bin/env python2.7

"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver

To run locally:

    python server.py

Go to http://localhost:8111 in your browser.

A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response
import random

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@104.196.18.7/w4111
#
# For example, if you had username biliris and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://biliris:foobar@104.196.18.7/w4111"
#

DATABASEURI = "postgresql://dps2150:4918@35.196.158.126/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#

#engine.execute("""CREATE TABLE IF NOT EXISTS test (
#  id serial,
#  name text
#);""")
#engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")

engine.execute("""SELECT * FROM students;""")


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print ("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print (request.args)


  #
  # example of a database query
  #
  cursor = g.conn.execute("SELECT name FROM test")
  names = []
  for result in cursor:
    names.append(result['name'])  # can also be accessed using result[0]
  cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = dict(data = names)



  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#





@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/logout')
def logout():
    global useremail
    useremail = ''
    return redirect('/')



# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    cursor = g.conn.execute('SELECT COUNT(*)+1 AS idcount FROM test')
    newid = []
    for result in cursor:
      newid.append(result['idcount'])
    cursor.close()

    g.conn.execute('INSERT INTO test VALUES ({}, \'{}\')'.format(newid[0], name))

    return redirect('/')

@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()

def timeconvert(x):
    i = 0
    temp = x
    while i < len(temp):
        if isinstance(temp[i], int):
            if temp[i] == 0:
                temp[i] = '-'
            elif temp[i] > 0:
                s = str(temp[i])
                if temp[i] < 1000:
                    time = s[:1] + ':' + s[1:] + 'am'
                    temp[i] = time
                elif temp[i] < 1200:
                    time = s[:2] + ':' + s[2:] + 'am'
                    temp[i] = time
                elif temp[i] < 1300:
                    time = s[:2] + ':' + s[2:] + 'pm'
                    temp[i] = time
                elif temp[i] < 2200:
                    s = str(temp[i] - 1200)
                    time = s[:1] + ':' + s[1:] + 'pm'
                    temp[i] = time
                elif temp[i] < 2200:
                    s = str(temp[i] - 1200)
                    time = s[:1] + ':' + s[1:] + 'pm'
                    temp[i] = time
                elif temp[i] < 2400:
                    s = str(temp[i] - 1200)
                    time = s[:2] + ':' + s[2:] + 'pm'
                    temp[i] = time
                elif temp[i] == 2400:
                    s = str(temp[i] - 1200)
                    time = s[:2] + ':' + s[2:] + 'am+'
                    temp[i] = time
        i += 1
    x = temp
    return x
#______________________________________________________________________________________________________


#login
useremail = ''
@app.route('/userlogin', methods=['POST'])
def userlogin():
    global useremail
    email = request.form['email']
    password = request.form['password']
    cursor = g.conn.execute("SELECT email, password FROM students")
    login = []
    for result in cursor:
      login.append(result['email'])
    cursor.close()

    if email in login:
      cursor = g.conn.execute('SELECT password FROM students WHERE email=\'{}\''.format(email))
      loginpassword = []
      for result in cursor:
        loginpassword.append(result['password'])
      cursor.close()
      if password in loginpassword:
        useremail = email
        return render_template('login.html')
      else:
        return render_template('index.html', error='wrong password')
    else:
      return render_template('index.html', error='email not found')



email = ''
@app.route('/testemail', methods=['POST'])
def testemail():
    global email
    email = request.form['email']
    cursor = g.conn.execute("SELECT email FROM students")
    login = []
    for result in cursor:
      login.append(result['email'])
    cursor.close()
    if email in login:
        return render_template("register.html", error='Email already exists')
    else:
        return render_template("register2.html", email=email)



@app.route('/userinfo', methods=['POST'])
def userinfo():
    global email
    password = request.form['password']
    name = request.form['name']
    phone = request.form['phone']
    major = request.form['major']

    g.conn.execute('INSERT INTO students VALUES (\'{}\', \'{}\', \'{}\', \'{}\', \'{}\')'.format(email, password, name, phone, major))

    return render_template("inputstudytime.html")



@app.route('/inputstudytime', methods=['POST'])
def inputstudytime():
    global email
    global useremail
    mstart = request.form['mstart']
    mend = request.form['mend']
    tstart = request.form['tstart']
    tend = request.form['tend']
    wstart = request.form['wstart']
    wend = request.form['wend']
    thstart = request.form['thstart']
    thend = request.form['thend']
    fstart = request.form['fstart']
    fend = request.form['fend']
    sastart = request.form['sastart']
    saend = request.form['saend']
    sustart = request.form['sustart']
    suend = request.form['suend']
    cursor = g.conn.execute('SELECT MAX(stid)+1 AS idcount FROM stfors')
    newid = []
    for result in cursor:
      newid.append(result['idcount'])
    cursor.close()
    sid = newid[0]
    g.conn.execute(
        'INSERT INTO stfors VALUES (\'{}\', {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, \'{}\')'.format(
            sid, mstart, mend, tstart, tend, wstart, wend, thstart, thend, fstart, fend, sastart, saend, sustart, suend, email))

    useremail = email
    cursor = g.conn.execute('SELECT * FROM university')
    u = []
    uid = []
    u.append('University ID')
    u.append('University')
    u.append('City')
    u.append(' ')
    for result in cursor:
        u.append(result['uid'])
        u.append(result['name'])
        u.append(result['city'])
        u.append(' ')
        uid.append(result['uid'])
    cursor.close()
    return render_template("register3.html", uid=uid, u=u)

@app.route('/studytime')
def studytime():
    global useremail
    cursor = g.conn.execute('SELECT * FROM stfors WHERE email=\'{}\''.format(useremail))
    studytimes = []
    for result in cursor:
        studytimes.append(result['mstart'])
        studytimes.append(result['mend'])
        studytimes.append(result['tstart'])
        studytimes.append(result['tend'])
        studytimes.append(result['wstart'])
        studytimes.append(result['wend'])
        studytimes.append(result['thstart'])
        studytimes.append(result['thend'])
        studytimes.append(result['fstart'])
        studytimes.append(result['fend'])
        studytimes.append(result['sastart'])
        studytimes.append(result['saend'])
        studytimes.append(result['sustart'])
        studytimes.append(result['suend'])
    cursor.close()

    studytimes = timeconvert(studytimes)

    mstart = studytimes[0]
    mend = studytimes[1]
    tstart = studytimes[2]
    tend = studytimes[3]
    wstart = studytimes[4]
    wend = studytimes[5]
    thstart = studytimes[6]
    thend = studytimes[7]
    fstart = studytimes[8]
    fend = studytimes[9]
    sastart = studytimes[10]
    saend = studytimes[11]
    sustart = studytimes[12]
    suend = studytimes[13]
    return render_template('studytime.html', mstart=mstart, mend=mend, tstart=tstart, tend=tend, wstart=wstart,
                           wend=wend, thstart=thstart, thend=thend, fstart=fstart, fend=fend, sastart=sastart,
                           saend=saend, sustart=sustart, suend=suend)


@app.route('/register3')
def register3():
    global useremail
    cursor = g.conn.execute('SELECT * FROM university')
    u = []
    uids = []
    u.append('University ID')
    u.append('University')
    u.append('City')
    u.append(' ')
    for result in cursor:
        u.append(result['uid'])
        u.append(result['name'])
        u.append(result['city'])
        u.append(' ')
        uids.append(result['uid'])
    cursor.close()

    return render_template('register3.html', u=u, uid=uids)

uid = ''
@app.route('/register4', methods=['POST'])
def register4():
    global useremail
    global uid
    uid = request.form['uid']
    cursor = g.conn.execute('WITH courses AS(SELECT cid FROM catu EXCEPT SELECT cid FROM sinc WHERE email=\'{}\') '
                            'SELECT * FROM catu NATURAL JOIN courses WHERE uid={};'.format(useremail, uid))
    c = []
    cid = []
    c.append('Course ID')
    c.append('Department')
    c.append('Course')
    c.append('Section')
    c.append('Name')
    c.append('Professor')
    c.append(' ')
    for result in cursor:
        c.append(result['cid'])
        c.append(result['dpt'])
        c.append(result['course'])
        c.append(result['section'])
        c.append(result['cname'])
        c.append(result['professor'])
        c.append(' ')
        cid.append(result['cid'])
    cursor.close()

    return render_template('register4.html', c=c, cid=cid)


@app.route('/register5', methods=['POST'])
def register5():
    global useremail
    global uid
    cid = request.form['cid']
    g.conn.execute('INSERT INTO sinc VALUES ({}, \'{}\')'.format(cid, useremail))
    cursor = g.conn.execute('WITH courses AS(SELECT cid FROM catu EXCEPT SELECT cid FROM sinc WHERE email=\'{}\') '
                            'SELECT * FROM catu NATURAL JOIN courses WHERE uid={};'.format(useremail, uid))
    c = []
    cid = []
    c.append('Course ID')
    c.append('Department')
    c.append('Course')
    c.append('Section')
    c.append('Name')
    c.append('Professor')
    c.append(' ')
    for result in cursor:
        c.append(result['cid'])
        c.append(result['dpt'])
        c.append(result['course'])
        c.append(result['section'])
        c.append(result['cname'])
        c.append(result['professor'])
        c.append(' ')
        cid.append(result['cid'])
    cursor.close()

    done = "FINISH"
    return render_template('register4.html', c=c, cid=cid, done=done)



@app.route('/home')
def home():
    global useremail
    cursor = g.conn.execute('WITH usergroups AS(SELECT * FROM sginc NATURAL JOIN member WHERE email=\'{}\'), '
                            'groups AS (SELECT member.email, usergroups.gname, usergroups.cid FROM member JOIN '
                            'usergroups ON member.sgid=usergroups.sgid), groups2 AS (SELECT catu.cname, '
                            'groups.gname, groups.email FROM catu JOIN groups ON groups.cid=catu.cid)SELECT * FROM '
                            'groups2 NATURAL JOIN students'.format(useremail))
    usergroups = []
    for result in cursor:
        usergroups.append(result['cname'])
        usergroups.append(result['gname'])
        usergroups.append(result['name'])
        usergroups.append(result['email'])
        usergroups.append(result['phone'])
        usergroups.append(result['major'])
        usergroups.append(' ')

    cursor.close()
    cursor = g.conn.execute('WITH usergroups AS(SELECT * FROM sginc NATURAL JOIN member WHERE email=\'{}\')SELECT '
                            ' * FROM mforsg NATURAL JOIN usergroups'.format(useremail))
    groupinfo = []
    for result in cursor:
        groupinfo.append(result['gname'])
        groupinfo.append(result['location'])
        groupinfo.append(result['mstart'])
        groupinfo.append(result['mend'])
        groupinfo.append(result['tstart'])
        groupinfo.append(result['tend'])
        groupinfo.append(result['wstart'])
        groupinfo.append(result['wend'])
        groupinfo.append(result['thstart'])
        groupinfo.append(result['thend'])
        groupinfo.append(result['fstart'])
        groupinfo.append(result['fend'])
        groupinfo.append(result['sastart'])
        groupinfo.append(result['saend'])
        groupinfo.append(result['sustart'])
        groupinfo.append(result['suend'])
        groupinfo.append(' ')
    cursor.close()
    if len(usergroups) < 2:
        usergroups.append('You')
        usergroups.append('Are')
        usergroups.append('Not')
        usergroups.append('In')
        usergroups.append('Any')
        usergroups.append('Groups')

    groupinfo = timeconvert(groupinfo)

    #GROUP POSTS
    cursor = g.conn.execute('WITH usergroups AS(SELECT * FROM sginc NATURAL JOIN member WHERE email=\'{}\'), '
                            'groups AS(SELECT sginc.gname, sginc.sgid FROM sginc JOIN usergroups ON '
                            'sginc.sgid=usergroups.sgid) SELECT * FROM groups JOIN pinsg ON '
                            'groups.sgid=pinsg.sgid'.format(useremail))
    posts = []
    for result in cursor:
        posts.append(result['post'])
        posts.append(result['date'])
        posts.append(result['gname'])
        posts.append(' ')

    cursor.close()
    rposts = reversed(posts)

    return render_template("home.html", useremail=useremail, groups=usergroups, groupinfo=groupinfo, posts=rposts)



@app.route('/post')
def post():
    cursor = g.conn.execute('WITH usergroups AS(SELECT * FROM sginc NATURAL JOIN member WHERE email=\'{}\') SELECT '
                            'sginc.gname, sginc.sgid FROM sginc JOIN usergroups ON '
                            'sginc.sgid=usergroups.sgid'.format(useremail))
    gnames = []
    for result in cursor:
        gnames.append(result['sgid'])
        gnames.append(result['gname'])

    cursor.close()
    return render_template('post.html', gnames=gnames)

@app.route('/posting', methods=['POST'])
def posting():
    cursor = g.conn.execute('WITH usergroups AS(SELECT * FROM sginc NATURAL JOIN member WHERE email=\'{}\') SELECT '
                            'sginc.gname, sginc.sgid FROM sginc JOIN usergroups ON '
                            'sginc.sgid=usergroups.sgid'.format(useremail))
    gnames = []
    for result in cursor:
        gnames.append(result['sgid'])
        gnames.append(result['gname'])

    post = request.form['post']
    sgid = request.form['sgid']

    posted = 'your message has been posted'
    cursor = g.conn.execute('SELECT MAX(postnum)+1 AS idcount FROM pinsg')
    newid = []
    for result in cursor:
      newid.append(result['idcount'])
    cursor.close()
    postnum = newid[0]
    g.conn.execute('INSERT INTO pinsg VALUES ({}, NOW(), \'{}\', {})'.format(postnum, post, sgid))
    return render_template('post.html', posted=posted, gnames=gnames)



@app.route('/test')
def tester():
    global useremail
    useremail = 'dps2150@columbia.edu'
    return render_template('login.html')


@app.route('/groups')
def groups():
    global useremail
    #TOP SUGGESTED MEETING TIMES
    cursor = g.conn.execute('WITH usergroups AS(SELECT * FROM sginc NATURAL JOIN member WHERE email=\'{}\'), '
                            'groups AS(SELECT member.email, usergroups.gname FROM member JOIN usergroups ON '
                            'member.sgid=usergroups.sgid) SELECT groups.gname, MAX(mstart)AS mstart, MIN(mend)AS mend,'
                            ' MAX(tstart)AS tstart, MIN(tend)AS tend, MAX(wstart)AS wstart, MIN(wend)AS wend, '
                            'MAX(thstart)AS thstart, MIN(thend)AS thend, MAX(fstart)AS fstart, MIN(fend)AS fend, '
                            'MAX(sastart)AS sastart, MIN(saend)AS saend, MAX(sustart)AS sustart, MIN(suend)AS suend '
                            'FROM groups NATURAL JOIN stfors GROUP BY gname'.format(useremail))

    stimes = []
    for result in cursor:
        stimes.append(result['gname'])
        stimes.append(result['mstart'])
        stimes.append(result['mend'])
        stimes.append(result['tstart'])
        stimes.append(result['tend'])
        stimes.append(result['wstart'])
        stimes.append(result['wend'])
        stimes.append(result['thstart'])
        stimes.append(result['thend'])
        stimes.append(result['fstart'])
        stimes.append(result['fend'])
        stimes.append(result['sastart'])
        stimes.append(result['saend'])
        stimes.append(result['sustart'])
        stimes.append(result['suend'])
        stimes.append(' ')
    cursor.close()

    i = 1
    while i < len(stimes) -2:
        if i % 15 == 0:
            i = i+2
        elif stimes[i] > stimes[i+1]:
            stimes[i] = 0
            stimes[i+1] = 0
        i = i + 2
    stimes = timeconvert(stimes)

    #SUGGEST PEOPLE TO START GROUP WITH
    days = ['MONDAYS', 'TUESDAYS', 'WEDNESDAYS', 'THURSDAYS', 'FRIDAYS', 'SATURDAYS', 'SUNDAYS']
    day = random.choice(days)
    daytimes = ['MONDAYS', 'mstart', 'mend', 'TUESDAYS', 'tstart', 'tend', 'WEDNESDAYS', 'wstart', 'wend', 'THURSDAYS',
                'thstart', 'thend', 'FRIDAYS', 'fstart', 'fend', 'SATURDAYS', 'sastart', 'saend', 'SUNDAYS', 'sustart',
                'suend']
    index = daytimes.index(day)
    daystart = daytimes[index + 1]
    dayend = daytimes[index + 2]

    cursor = g.conn.execute('WITH sschedule AS(SELECT * FROM students NATURAL JOIN stfors), me AS(SELECT * FROM '
                            'sschedule WHERE email=\'{}\') SELECT sschedule.name, sschedule.email, sschedule.{}, '
                            'sschedule.{} FROM sschedule JOIN me ON sschedule.{} < me.{}  AND sschedule.{} > '
                            'me.{} AND sschedule.email <> \'{}\''.format(useremail, daystart, dayend, daystart,
                                                                         dayend, dayend, daystart, useremail))
    people = []
    for result in cursor:
        people.append(result['name'])
        people.append(result['email'])
        people.append(result[daystart])
        people.append(result[dayend])
        people.append(' ')

    cursor.close()
    people = timeconvert(people)
    if len(people) < 1:
        people.append('No person overlaps your schedule on ' + day)


    #GROUPS TO JOIN
    cursor = g.conn.execute('WITH userc AS(SELECT cid FROM sinc NATURAL JOIN catu WHERE email=\'{}\'), '
                            'userc2 AS(SELECT * FROM sginc NATURAL JOIN userc EXCEPT SELECT cid, sgid, gname FROM '
                            'member NATURAL JOIN sginc WHERE email=\'{}\') SELECT cname, gname FROM userc2 NATURAL JOIN '
                            'catu'.format(useremail, useremail))
    jgroups = []
    for result in cursor:
        jgroups.append(result['cname'])
        jgroups.append(result['gname'])
        jgroups.append(' ')

    cursor.close()

    return render_template("groups.html", people=people, day=day, daystart=daystart, dayend=dayend, stimes=stimes,
                           jgroups=jgroups)


@app.route('/creategroup')
def creategroup():
    global useremail
    cursor = g.conn.execute('SELECT * FROM sinc NATURAL JOIN catu WHERE email=\'{}\';'.format(useremail))
    courses = []
    for result in cursor:
        courses.append(result['cid'])
        courses.append(result['cname'])

    cursor.close()
    return render_template("creategroup.html", courses=courses)

@app.route('/creategroup2', methods=['POST'])
def creategroup2():
    global useremail

    cid = request.form['cid']
    gname = request.form['gname']

    cursor = g.conn.execute('SELECT MAX(sgid)+1 AS idcount FROM sginc')
    newid = []
    for result in cursor:
        newid.append(result['idcount'])
    cursor.close()
    sgid = newid[0]
    g.conn.execute('INSERT INTO sginc VALUES ({}, \'{}\', {})'.format(sgid, gname, cid))

    location = request.form['location']
    mstart = request.form['mstart']
    mend = request.form['mend']
    tstart = request.form['tstart']
    tend = request.form['tend']
    wstart = request.form['wstart']
    wend = request.form['wend']
    thstart = request.form['thstart']
    thend = request.form['thend']
    fstart = request.form['fstart']
    fend = request.form['fend']
    sastart = request.form['sastart']
    saend = request.form['saend']
    sustart = request.form['sustart']
    suend = request.form['suend']
    cursor = g.conn.execute('SELECT MAX(meetingnum)+1 AS idcount FROM mforsg')
    newid = []
    for result in cursor:
        newid.append(result['idcount'])
    cursor.close()
    mnum = newid[0]
    g.conn.execute('INSERT INTO mforsg VALUES ({}, \'{}\', {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {})'
                   .format(mnum, location, sgid, mstart, mend, tstart, tend, wstart, wend, thstart, thend, fstart, fend,
                           sastart, saend, sustart, suend, email))
    note = 'Group Created!'
    cursor = g.conn.execute('SELECT * FROM sinc NATURAL JOIN catu WHERE email=\'{}\';'.format(useremail))
    courses = []
    for result in cursor:
        courses.append(result['cid'])
        courses.append(result['cname'])

    cursor.close()
    g.conn.execute('INSERT INTO member VALUES (\'{}\', {})'.format(useremail, sgid))

    return render_template("creategroup.html", note=note, courses=courses)

@app.route('/joingroup')
def joingroup():
    global useremail

    cursor = g.conn.execute('WITH userc AS(SELECT cid FROM sinc NATURAL JOIN catu WHERE email=\'{}\'), userc2 AS(SELECT'
                            ' * FROM sginc NATURAL JOIN userc EXCEPT SELECT cid, sgid, gname FROM member NATURAL JOIN '
                            'sginc WHERE email=\'{}\'), userc3 AS(SELECT * FROM userc2 NATURAL JOIN mforsg), userc4 '
                            'AS(SELECT * FROM userc3 NATURAL JOIN catu), usert AS(SELECT mstart, mend, tstart, tend, '
                            'wstart, wend, thstart, thend, fstart, fend, sastart, saend, sustart, suend FROM stfors '
                            'WHERE email=\'{}\') SELECT userc4.cname, userc4.sgid, userc4.gname, userc4.location, '
                            'userc4.mstart, userc4.mend, userc4.tstart, userc4.tend, userc4.wstart, userc4.wend, '
                            'userc4.thstart, userc4.thstart, userc4.thend, userc4.fstart, userc4.fend, userc4.sastart, '
                            'userc4.saend, userc4.sustart, userc4.suend FROM userc4 JOIN usert ON '
                            '(userc4.mstart<usert.mend AND userc4.mend>usert.mstart) OR (userc4.tstart<usert.tend AND '
                            'userc4.tend>usert.tstart) OR (userc4.wstart<usert.wend AND userc4.wend>usert.wstart) OR '
                            '(userc4.thstart<usert.thend AND userc4.thend>usert.thstart) OR (userc4.fstart<usert.fend '
                            'AND userc4.fend>usert.fstart) OR (userc4.sastart<usert.saend AND '
                            'userc4.saend>usert.sastart) OR (userc4.sustart<usert.suend AND userc4.suend>usert.sustart)'
                            .format(useremail, useremail, useremail))
    jgroups = []
    jgroup = []
    for result in cursor:
        jgroups.append(result['cname'])
        jgroups.append(result['gname'])
        jgroups.append(result['location'])
        jgroups.append(result['mstart'])
        jgroups.append(result['mend'])
        jgroups.append(result['tstart'])
        jgroups.append(result['tend'])
        jgroups.append(result['wstart'])
        jgroups.append(result['wend'])
        jgroups.append(result['thstart'])
        jgroups.append(result['thend'])
        jgroups.append(result['fstart'])
        jgroups.append(result['fend'])
        jgroups.append(result['sastart'])
        jgroups.append(result['saend'])
        jgroups.append(result['sustart'])
        jgroups.append(result['suend'])
        jgroups.append(' ')
        jgroup.append(result['sgid'])
        jgroup.append(result['gname'])
    cursor.close()
    jgroups = timeconvert(jgroups)


    return render_template("joingroup.html", jgroups=jgroups, jgroup=jgroup)

@app.route('/joingroup2', methods=['POST'])
def joingroup2():
    global useremail
    sgid = request.form['sgid']
    joined = 'Group Joined!'
    g.conn.execute('INSERT INTO member VALUES (\'{}\', {})'.format(useremail, sgid))

    cursor = g.conn.execute('WITH userc AS(SELECT cid FROM sinc NATURAL JOIN catu WHERE email=\'{}\'), userc2 AS(SELECT'
                            ' * FROM sginc NATURAL JOIN userc EXCEPT SELECT cid, sgid, gname FROM member NATURAL JOIN '
                            'sginc WHERE email=\'{}\'), userc3 AS(SELECT * FROM userc2 NATURAL JOIN mforsg), userc4 '
                            'AS(SELECT * FROM userc3 NATURAL JOIN catu), usert AS(SELECT mstart, mend, tstart, tend, '
                            'wstart, wend, thstart, thend, fstart, fend, sastart, saend, sustart, suend FROM stfors '
                            'WHERE email=\'{}\') SELECT userc4.cname, userc4.sgid, userc4.gname, userc4.location, '
                            'userc4.mstart, userc4.mend, userc4.tstart, userc4.tend, userc4.wstart, userc4.wend, '
                            'userc4.thstart, userc4.thstart, userc4.thend, userc4.fstart, userc4.fend, userc4.sastart, '
                            'userc4.saend, userc4.sustart, userc4.suend FROM userc4 JOIN usert ON '
                            '(userc4.mstart<usert.mend AND userc4.mend>usert.mstart) OR (userc4.tstart<usert.tend AND '
                            'userc4.tend>usert.tstart) OR (userc4.wstart<usert.wend AND userc4.wend>usert.wstart) OR '
                            '(userc4.thstart<usert.thend AND userc4.thend>usert.thstart) OR (userc4.fstart<usert.fend '
                            'AND userc4.fend>usert.fstart) OR (userc4.sastart<usert.saend AND '
                            'userc4.saend>usert.sastart) OR (userc4.sustart<usert.suend AND userc4.suend>usert.sustart)'
                            .format(useremail, useremail, useremail))
    jgroups = []
    jgroup = []
    for result in cursor:
        jgroups.append(result['cname'])
        jgroups.append(result['gname'])
        jgroups.append(result['location'])
        jgroups.append(result['mstart'])
        jgroups.append(result['mend'])
        jgroups.append(result['tstart'])
        jgroups.append(result['tend'])
        jgroups.append(result['wstart'])
        jgroups.append(result['wend'])
        jgroups.append(result['thstart'])
        jgroups.append(result['thend'])
        jgroups.append(result['fstart'])
        jgroups.append(result['fend'])
        jgroups.append(result['sastart'])
        jgroups.append(result['saend'])
        jgroups.append(result['sustart'])
        jgroups.append(result['suend'])
        jgroups.append(' ')
        jgroup.append(result['sgid'])
        jgroup.append(result['gname'])
    cursor.close()
    jgroups = timeconvert(jgroups)

    return render_template("joingroup.html", joined=joined, jgroups=jgroups, jgroup=jgroup)



@app.route('/deleteuser')
def deleteuser():
    global useremail
    g.conn.execute('DELETE FROM sinc WHERE email=\'{}\''.format(useremail))
    g.conn.execute('DELETE FROM member WHERE email=\'{}\''.format(useremail))
    g.conn.execute('DELETE FROM students WHERE email=\'{}\''.format(useremail))
    useremail = ''
    return redirect('/')


#______________________________________________________________________________________________________

if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port
    print ("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
