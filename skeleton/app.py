######################################
# camille hall <camilhall@bu.edu>
# chiara lim <cclim@bu.edu>
######################################
# Some code adapted from
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask_login
import datetime

#for image uploading
import os, base64

#for getting current date
def getDate():
	return datetime.date.today()


mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'password'
app.config['MYSQL_DATABASE_DB'] = 'photoshare1' #NOTICE: I added 1 to the end of this. so youll need to change it back
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users")
users = cursor.fetchall()

def getUserList():
	cursor = conn.cursor()
	cursor.execute("SELECT email from Users")
	return cursor.fetchall()

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	users = getUserList()
	email = request.form.get('email')
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
	data = cursor.fetchall()
	pwd = str(data[0][0])
	user.is_authenticated = (request.form['password'] == pwd)
	return user

'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'GET':
		return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
	#The request method is POST (page is recieving data)
	email = flask.request.form['email']
	cursor = conn.cursor()
	#check if email is registered
	if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		pwd = str(data[0][0] )
		if flask.request.form['password'] == pwd:
			user = User()
			user.id = email
			flask_login.login_user(user) #okay login in user
			return flask.redirect(flask.url_for('protected')) #protected is a function defined in this file

	#information did not match
	return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"

@app.route('/logout')
def logout():
	flask_login.logout_user()
	return render_template('unauth.html')
#TODO: change this to a non-user dependent page where they an login, search ect.

@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html')

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
	return render_template('register.html', supress='True')

@app.route("/register", methods=['POST'])
def register_user():
	try:
		first_name=request.form.get('firstname')
		last_name=request.form.get('lastname')
		email=request.form.get('email')
		password=request.form.get('password')
		birth_date=request.form.get('birthday')
		gender=request.form.get('gender')
		hometown=request.form.get('hometown')
	except:
		print("couldn't find all tokens") #this prints to shell, end users will not see this (all print statements go to shell)
		return flask.redirect(flask.url_for('register'))
	cursor = conn.cursor()
	test =  isEmailUnique(email)
	
	# pass: first_name, last_name, email, password, date_of_birth
	passed =  test and first_name and last_name and password and birth_date

	if passed: # if email is unique
		print(cursor.execute("INSERT INTO Users (first_name, last_name, email, password, birth_date, gender, hometown) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}')".format(first_name, last_name, email, password, birth_date, gender, hometown)))
		conn.commit()
		#log user in
		user = User()
		user.id = email
		flask_login.login_user(user)
		return render_template('hello.html', name=first_name, message='Account Created!')
	else:
		print("couldn't find all tokens")
		return render_template('home.html', photos = getAllPhotos(), albums=getAllAlbums(), message='Could not create an account. Try again!', base64=base64)

def getUsersPhotos(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall() #NOTE return a list of tuples, [(imgdata, pid, caption), ...]

def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email FROM Users WHERE email = '{0}'".format(email)):
		#this means there are greater than zero entries with that email
		return False
	else:
		return True
#end login code

@app.route('/profile')
@flask_login.login_required
def protected():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	return render_template('hello.html', name=flask_login.current_user.id, message="Here's your profile", 
							albums = getUsersAlbums(uid), photos = getUsersPhotos(uid), friends=getFriends(uid), base64=base64)
 
# ------------------------------------ FRIENDS ------------------------------------
# search for friend using search bar
def getUser_byEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM Users U WHERE U.email = '{0}'".format(email))
	return cursor.fetchall() #NOTE return a list of tuples, [(user_id), ...]

def getUserFriendids(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Friends WHERE Friends.user_id1 = '{0}' OR Friends.user2_id = '{0}'".format(uid))
    user_friend_pairs = cursor.fetchall()
    friends_of_user = [users[0] if users[0] != uid else users[1] for users in user_friend_pairs]
    return friends_of_user

def addFriend(uid, pid):
	cursor = conn.cursor()
	cursor.execute('''INSERT INTO Likes (picture_id, user_id) VALUES (%s, %s)''', (pid, uid))
	conn.commit()
 
def getFriends(uid):
	#friendids = getUserFriendids(uid) #[(fid, uid), ...]
	cursor = conn.cursor()
	cursor.execute('''WITH friendids(uid, fid) AS (Select * FROM Friends WHERE user_id1 = %s) SELECT U.first_name, U.last_name, U.email FROM Users U, friendids F WHERE F.fid=U.user_id''', uid)
	# cursor.execute("SELECT F.name, F.email FROM (SELECT * FROM Friends WHERE Friends.user_id1 = '{0}') WHERE F.user_id = friend_ids.uid".format(uid))
	#cursor.execute('''SELECT U.name, U.email FROM F.Friends, U.Users WHERE F.user_id1 = %s''', uid)
	conn.commit()
	return cursor.fetchall() #returns [(firstname, lastname, email)...]

# adding a Friends relation
@app.route('/addfriend', methods=['POST'])
@flask_login.login_required
def add_friend():
	uid=request.form.get('uid')
	uid=uid.replace(',','')
	print(uid)
	fid=request.form.get('fid')
	fid=fid.replace(',','')
	print(fid)
	#insert into friends
	cursor = conn.cursor()
	cursor.execute("INSERT INTO Friends (user_id1, user_id2) VALUES ('{0}', '{1}')".format(uid, fid))
	conn.commit()
	return render_template('hello.html', name=flask_login.current_user.id, message='Friend Added!', 
 								albums=getUsersAlbums(uid), friends=getFriends(uid), photos=getUsersPhotos(uid), base64=base64)
#     uid = getUserIdFromEmail(flask_login.current_user.id)
#     cursor = conn.cursor()
#     cursor.execute("SELECT user_id FROM Users WHERE username = '{0}'".format(friend))
#     fid = cursor.fetchone()[0] #friend id
#     if uid and (uid != fid):
#         cursor.execute("INSERT INTO Friends (user1_id, user2_id) VALUES ('{0}', '{1}')".format(uid, fid))
#         conn.commit()
#     return render_template('hello.html', name=flask_login.current_user.id, message='Friend Added!', 
# 								albums=getUsersAlbums(uid), photos=getUsersPhotos(uid), base64=base64)

# ------------------------------------ LIKES ------------------------------------
def insertLike(uid, pid):
	cursor = conn.cursor()
	cursor.execute('''INSERT INTO Likes (picture_id, user_id) VALUES (%s, %s)''', (pid, uid))
	conn.commit()
 
#add like to photo
@app.route('/addlike', methods=['POST'])
@flask_login.login_required
def add_like():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	try:
		pid = request.form.get('pid').replace('/','')
		insertLike(uid, pid)
		return render_template('hello.html', name=flask_login.current_user.id, message='Like Added!', 
									albums=getUsersAlbums(uid), photos=getUsersPhotos(uid), friends=getFriends(uid), base64=base64)
	except:
		return render_template('hello.html', name=flask_login.current_user.id, message='Like was not added.', 
									albums=getUsersAlbums(uid), photos=getUsersPhotos(uid), friends=getFriends(uid), base64=base64)

# ------------------------------------ COMMENTS ------------------------------------
def insertComment(uid, comment, pid):
	cid = 0 #need to come up with a way to get id
	doc = getDate()
	cursor = conn.cursor()
	cursor.execute('''INSERT INTO Comments (cmmt_id, user_id, picture_id, cmmt, doc) VALUES (%s, %s, %s, %s, %s)''', (cid, uid, pid, comment, doc))
	conn.commit()
 
#add comment to photo
@app.route('/addcomment', methods=['POST'])
@flask_login.login_required
def add_comment():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	try:
		cmmt = request.form.get('comment')
		pid = request.form.get('pid').replace('/','')
		insertComment(uid, cmmt, pid)
		return render_template('hello.html', name=flask_login.current_user.id, message='Comment Added!', 
									albums=getUsersAlbums(uid), photos=getUsersPhotos(uid), friends=getFriends(uid), base64=base64)
	except:
		return render_template('hello.html', name=flask_login.current_user.id, message='Comment was not added.', 
									albums=getUsersAlbums(uid), photos=getUsersPhotos(uid), friends=getFriends(uid), base64=base64)

# ---------------------begin album creating code---------------------
@app.route('/newalbum', methods=['GET', 'POST'])
@flask_login.login_required
def create_album():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	if request.method == 'POST':
		time = getDate()
		aname = request.form.get('aname')
		cursor = conn.cursor()
		cursor.execute('''INSERT INTO Albums (album_name, user_id, doc) VALUES (%s, %s, %s )''', (aname, uid, time))
		conn.commit()
		return render_template('hello.html', name=flask_login.current_user.id, message='Album created!', 
								albums=getUsersAlbums(uid), photos=getUsersPhotos(uid), friends=getFriends(uid), base64=base64)
	else:
		return render_template('newalbum.html')

# --------------------------------------------------------
def insertTag(tag, pid):
	cursor = conn.cursor()
	cursor.execute('''INSERT INTO Tag (word, picture_id) VALUES (%s, %s)''', (tag, pid))
	conn.commit()

def getUsersAlbums(uid):
	cursor = conn.cursor()
	cursor.execute('''SELECT album_id, album_name, user_id, doc FROM Albums WHERE user_id = %s''', uid)
	return cursor.fetchall() #NOTE return a list of tuples, [(album_id, album_name, user_id, doc), ...]

#add tag to photo
@app.route('/addtag', methods=['POST'])
@flask_login.login_required
def add_tag():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	try:
		tags = request.form.get('tag')
		pid = request.form.get('pid').replace('/','')
		print(pid)
		print(tags)
		tags = tags.split(',')
		print(tags)
		for tag in tags:
			print(tag)
			insertTag(tag, pid)
		return render_template('hello.html', name = flask_login.current_user.id, message='Tag Added!', 
									albums = getUsersAlbums(uid), photos = getUsersPhotos(uid), friends=getFriends(uid), base64=base64)
	except:
		return render_template('hello.html', name = flask_login.current_user.id, message='Tag was not added', 
									albums = getUsersAlbums(uid), photos = getUsersPhotos(uid), friends=getFriends(uid), base64=base64)

# ----------------------------- DELETION ----------------------------------
@app.route('/mycontent', methods=['POST'])
@flask_login.login_required
def show_content():
	uid = getUserIdFromEmail(flask_login.current_user.id)
		# delete photo
	if(request.form.get('deletepic')):
		pid = request.form.get('deletepic')
		cursor = conn.cursor()
		cursor.execute('''DELETE FROM Pictures WHERE picture_id = %s;''', pid)
		conn.commit()
		return render_template('hello.html', name = flask_login.current_user.id, message='Photo Deleted!', 
								albums = getUsersAlbums(uid), photos = getUsersPhotos(uid), friends=getFriends(uid), base64=base64)
	# delete Album
	if(request.form.get('deletealb')):
		aid = request.form.get('deletealb')
		cursor = conn.cursor()
		cursor.execute('''DELETE FROM Albums WHERE album_id = %s;''', aid)
		conn.commit()
		return render_template('hello.html', name = flask_login.current_user.id, message='Album Deleted!', 
								albums = getUsersAlbums(uid), photos = getUsersPhotos(uid), friends=getFriends(uid), base64=base64)
	return render_template('hello.html', name = flask_login.current_user.id, message='Here is your content', 
								albums = getUsersAlbums(uid), photos = getUsersPhotos(uid), friends=getFriends(uid), base64=base64)
	
# ------------------------- UPLOAD PHOTOS -------------------------

# photos uploaded using base64 encoding so they can be directly embeded in HTML
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	if request.method == 'POST':
		try:
			imgfile = request.files['photo']
			caption = request.form.get('caption')
			aid = request.form.get('album')
			photo_data =imgfile.read()
			cursor = conn.cursor()
			cursor.execute('''INSERT INTO Pictures (imgdata, user_id, caption, album_id) VALUES (%s, %s, %s, %s )''', 
						(photo_data, uid, caption, aid))
			conn.commit()
			return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!', 
									photos=getUsersPhotos(uid), albums=getUsersAlbums(uid), friends=getFriends(uid), base64=base64)
		except:
			return render_template('upload.html', albums=getUsersAlbums(uid))
	#The method is GET so we return a  HTML form to upload the a photo.
	else:
		return render_template('upload.html', albums=getUsersAlbums(uid))
#end photo uploading code

# ---------------------------- SEARCH FUNCTIONALITY -----------------------------
def getAllAlbums():
	cursor = conn.cursor()
	cursor.execute('''SELECT * FROM Albums''')
	return cursor.fetchall() #NOTE return a list of tuples, [(album_id, album_name, user_id, doc), ...]

def getAllPhotos():
	cursor = conn.cursor()
	cursor.execute('''SELECT * FROM Pictures''')
	return cursor.fetchall() #NOTE return a list of tuples, [(picture_id, user_id, imgdata, caption, loc, album_id), ...]

def getAllUsers():
	cursor = conn.cursor()
	cursor.execute('''SELECT * FROM Users''')
	return cursor.fetchall() 

def getPhotos_byAlbum(aid):
	cursor = conn.cursor()
	cursor.execute('''SELECT * FROM Pictures WHERE album_id = %s''', aid)
	return cursor.fetchall() #NOTE return a list of tuples, [(picture_id, user_id, imgdata, caption, loc, album_id), ...]

def getTopTags():
	cursor = conn.cursor()
	cursor.execute('''
	WITH tophalf(wrd,cnt) AS 
		(WITH bycount(wrd,cnt) AS 
			(SELECT word, COUNT(word) FROM Tag GROUP BY word) 
		SELECT wrd, cnt FROM bycount 
    	WHERE cnt> (SELECT AVG(cnt) FROM bycount)) 
	SELECT wrd FROM tophalf WHERE cnt>(SELECT AVG(cnt) FROM tophalf)''')
	return cursor.fetchall()

# in a loop
#TODO: make a T_ string
#TODO make FROMTag string
#TODO: add a T_.word=<tag> string and T_.pic...
def getPhotos_byTags(tags,onlyusers):
	query  = '''SELECT P.picture_id, P.user_id, P.imgdata, P.caption, P.loc, P.album_id FROM Pictures P'''
	tagcnt = len(tags)
	for i in range(0,tagcnt):
		query+=(''', Tag T'''+ str(i))
	query+=''' WHERE '''
	for (i, tag) in enumerate(tags):
		Tstr = ('''T'''+ str(i))
		if(i>0):
			query+=''' AND '''
		condition = (Tstr+'''.word=\''''+tag+'''\' AND '''+Tstr+'''.picture_id=P.picture_id''')
		query += condition
	if onlyusers==1:
		uid = getUserIdFromEmail(flask_login.current_user.id)
		query += (''' AND P.user_id ='''+str(uid))
	cursor=conn.cursor()
	cursor.execute(query)
	return cursor.fetchall()#NOTE return a list of tuples, [(picture_id, user_id, imgdata, caption, loc, album_id), ...]

# def getPhotos_byTag(tag, onlyusers):
# 	if onlyusers==0:
# 		cursor = conn.cursor()
# 		cursor.execute('''SELECT P.picture_id, P.user_id, P.imgdata, P.caption, P.loc, P.album_id FROM Pictures P, Tag T 
# 						WHERE T.word = %s AND T.picture_id = P.picture_id''', tag)
# 		return cursor.fetchall() #NOTE return a list of tuples, [(picture_id, user_id, imgdata, caption, loc, album_id), ...]
# 	else:
# 		uid = getUserIdFromEmail(flask_login.current_user.id)
# 		cursor = conn.cursor() 
# 		cursor.execute("SELECT P.picture_id, P.user_id, P.imgdata, P.caption, P.loc, P.album_id FROM Pictures P, Tag T \
# 						WHERE P.user_id = '{0}' AND T.picture_id = P.picture_id AND T.word = '{1}'".format(uid, tag))
# 		return cursor.fetchall() #NOTE return a list of tuples, [(picture_id, user_id, imgdata, caption, loc, album_id), ...]

# ---------------------------------------------------------------------------------

#--------------------------------Top Tags -----------------------------------------
@app.route("/toptags", methods=['GET'])
def toptags():
	tags = getTopTags()
	print(tags)
	tags = [tag for (tag,) in tags]
	print(tags)
	if(tags):
		return render_template('toptags.html', message="Here are the top tags!", toptags=tags)
	else:
		return render_template('toptags.html', message="There are no tags yet")


#-------------------------------- Recomendations ----------------------------------
def getTop5_Tags(uid):
	cursor = conn.cursor()
	cursor.execute('''
	WITH tgcnt(cnt, wrd, pid) AS (
		SELECT COUNT(*), T.word, T.picture_id FROM Tag T GROUP BY T.word)
	SELECT tgcnt.wrd FROM tgcnt, Pictures P
	WHERE tgcnt.pid = P.picture_id AND P.user_id = %s
 	ORDER BY tgcnt.cnt DESC LIMIT 5;''', uid)
	return cursor.fetchall()#returns [word, ]

def getPhotos_fromTop5Tags(tags):
	cursor = conn.cursor()
	cursor.execute('''
	WITH piccnt(cnt, pid) AS (
		WITH picsintoptags(pid) AS (
			SELECT P.picture_id FROM Pictures P, Tag T
			WHERE  T.picture_id = P.picture_id
				AND (T.word=%s OR T.word=%s OR T.word=%s OR T.word=%s OR T.word=%s))
		SELECT COUNT(*), pid FROM picsintoptags GROUP BY pid)
	SELECT P.picture_id, P.user_id, P.imgdata, P.caption, P.loc, P.album_id
	FROM Pictures P, piccnt
	WHERE P.picture_id = piccnt.pid 
	ORDER BY piccnt.cnt desc;''', (str(tags[0]), str(tags[1]), str(tags[2]), str(tags[3]), str(tags[4])))
	return cursor.fetchall()


def search_fromTop5Tags(toptags, searchtags):
	cursor = conn.cursor()
	query = ('''
	WITH Pics(picture_id, user_id, imgdata, caption, loc, album_id) AS (
		WITH piccnt(cnt, pid) AS (
			WITH picsintoptags(pid) AS (
				SELECT P.picture_id FROM Pictures P, Tag Tg
				WHERE  Tg.picture_id = P.picture_id
					AND (Tg.word=\''''+str(toptags[0])+'''\' OR Tg.word=\''''+str(toptags[1])+'''\' OR Tg.word=\''''+str(toptags[2])+'''\' OR Tg.word=\''''+str(toptags[3])+'''\' OR Tg.word=\''''+str(toptags[4])+'''\'))
			SELECT COUNT(*), pid FROM picsintoptags GROUP BY pid)
		SELECT P.picture_id, P.user_id, P.imgdata, P.caption, P.loc, P.album_id
		FROM Pictures P, piccnt
		WHERE P.picture_id = piccnt.pid 
		ORDER BY piccnt.cnt desc)
	SELECT P.picture_id, P.user_id, P.imgdata, P.caption, P.loc, P.album_id FROM Pics P''')
	tagcnt = len(searchtags)
	for i in range(0,tagcnt):
		query+=(''', Tag T'''+ str(i))
	query+=''' WHERE '''
	for (i, tag) in enumerate(searchtags):
		Tstr = ('''T'''+ str(i))
		if(i>0):
			query+=''' AND '''
		condition = (Tstr+'''.word=\''''+tag+'''\' AND '''+Tstr+'''.picture_id=P.picture_id''')
		query += condition
	query += ';'
	cursor=conn.cursor()
	cursor.execute(query)
	return cursor.fetchall()

def get_FriendsofFriends(uid):
	cursor =conn.cursor()
	cursor.execute('''
	WITH fofcnt(ffid, cnt) AS 
		(WITH fof(ffid) AS
			(WITH myfriends(fid) AS 
				(SELECT user_id2 FROM Friends
				WHERE user_id1=%s)
			SELECT F.user_id2 FROM Friends F, myfriends 
			WHERE F.user_id1 = myfriends.fid AND F.user_id2 <> %s)
		SELECT fof.ffid, COUNT(ffid) FROM fof GROUP BY ffid)
	SELECT U.first_name, U.last_name, U.email FROM fofcnt, Users U WHERE fofcnt.ffid = U.user_id
	ORDER BY fofcnt.cnt DESC;''', (uid, uid))
	return cursor.fetchall()


@app.route('/recs', methods=['GET', 'POST'])
@flask_login.login_required
def recs():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	top5 = getTop5_Tags(uid)
	top5tags = [word for (word,) in top5]
	fofs = get_FriendsofFriends(uid)
	if request.method == 'POST':
		searchtags = request.form.get('searchtags')
		print(searchtags)
		searchtags=searchtags.split(' ')
		#searchtags = [tag for (tag,) in searchtags]
		print(searchtags)
		photos = search_fromTop5Tags(top5tags, searchtags)
	else:
		print("photos from top 5 tags")
		photos = getPhotos_fromTop5Tags(top5tags)
	return render_template('recs.html', tagrecs = top5tags, friendrecs=fofs, photos = photos, base64=base64)
	
# app.route("/searchrecs", methods=['Post'])
# @flask_login.login_required
# def searchrecomment():
# 	uid = getUserIdFromEmail(flask_login.current_user.id)


#---------------------------------- Home  -----------------------------------------
#default page/home page
@app.route("/", methods=['GET', 'POST'])
def hello(): 
	allphotos = getAllPhotos()
	allalbums = getAllAlbums()
	# allusers  = getAllUsers()
	try:
		userid=getUserIdFromEmail(flask_login.current_user.id)
	except:
		userid = None
	if request.method=='POST':
		# get photos in Album
		if(request.form.get('aid')):
			aid = request.form.get('aid')
			photos = getPhotos_byAlbum(aid)
			return render_template('home.html', uid=userid, photos=photos, base64=base64) 
		# get All photos from tag
		if(request.form.get('tag')):
			tag = request.form.get('tag')
			tag = tag.replace('/','')
			tag = tag.split(' ')
			print(tag)
			photos = getPhotos_byTags(tag, 0)
			return render_template('home.html', uid=userid, photos=photos, base64=base64)
		# get User photos from tag
		if(request.form.get('mytagsearch')):
			mytag = request.form.get('mytagsearch')
			mytag = mytag.replace('/','')
			mytag = mytag.split(' ')
			photos = getPhotos_byTags(mytag, 1)
			return render_template('home.html', uid=userid, photos=photos, base64=base64)
		# get User from email
		if(request.form.get('friendsearch')): #NOTE: I think we need to do a try except here to not get internal error when query returns nothing
			myemail = request.form.get('friendsearch')
   			#if user exists -> follow button
			fid= getUserIdFromEmail(myemail)
			if getUser_byEmail(myemail) and fid!=userid:
				#add friend page
				return render_template('addfriend.html', email=myemail, uid=userid, fid=fid)
			#if user not exists -> message "sorry!"
			return render_template('home.html', uid=userid, photos=allphotos, base64=base64, message='Friend does not exist!')
		else:
			return render_template('home.html', message = "Nothing was found for that search", uid=userid, albums = allalbums, photos = allphotos, base64=base64)
	return render_template('home.html', uid=userid, albums = allalbums, photos = allphotos, base64=base64)
	



if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)
