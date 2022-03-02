######################################
# author ben lawson <balawson@bu.edu>
# Edited by: Craig Einstein <einstein@bu.edu>
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
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
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
	pwd = str(data[0][0] )
	user.is_authenticated = request.form['password'] == pwd
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
		first_name=request.form.get('first_name')
		last_name=request.form.get('last_name')
		email=request.form.get('email')
		password=request.form.get('password')
		date_of_birth=request.form.get('date_of_birth')
		gender=request.form.get('gender')
		hometown=request.form.get('hometown')
	except:
		print("couldn't find all tokens") #this prints to shell, end users will not see this (all print statements go to shell)
		return flask.redirect(flask.url_for('register'))
	cursor = conn.cursor()
	test =  isEmailUnique(email)
	
	# pass: first_name, last_name, email, password, date_of_birth
	passed =  test and first_name and last_name and password and date_of_birth

	if passed: # if email is unique
		print(cursor.execute("INSERT INTO Users (first_name, last_name, email, password, date_of_birth, gender, hometown) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}')".format(first_name, last_name, email, password, date_of_birth, gender, hometown)))
		conn.commit()
		#log user in
		user = User()
		user.id = email
		flask_login.login_user(user)
		return render_template('profile.html', name=email, message='Account Created!')
	else:
		print("couldn't find all tokens")
		return flask.redirect(flask.url_for('register'))

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
	if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)):
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
							albums = getUsersAlbums(uid), photos = getUsersPhotos(uid), base64=base64)

#---------------------begin album creating code---------------------
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
								albums = getUsersAlbums(uid), photos=getUsersPhotos(uid), base64=base64)
	else:
		return render_template('newalbum.html')

#----------------------------My Content----------------------------
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
									albums = getUsersAlbums(uid), photos = getUsersPhotos(uid), base64=base64)
	except:
		return render_template('hello.html', name = flask_login.current_user.id, message='Tag was not added', 
									albums = getUsersAlbums(uid), photos = getUsersPhotos(uid), base64=base64)

#delete stuff
@app.route('/mycontent', methods=['POST'])
@flask_login.login_required
def show_content():
	uid = getUserIdFromEmail(flask_login.current_user.id)
		#delete photo
	if(request.form.get('deletepic')):
		pid = request.form.get('deletepic')
		cursor = conn.cursor()
		cursor.execute('''DELETE FROM Pictures WHERE picture_id = %s;''', pid)
		conn.commit()
		return render_template('hello.html', name = flask_login.current_user.id, message='Photo Deleted!', 
								albums = getUsersAlbums(uid), photos = getUsersPhotos(uid), base64=base64)
	#delete Album
	if(request.form.get('deletealb')):
		aid = request.form.get('deletealb')
		cursor = conn.cursor()
		cursor.execute('''DELETE FROM Albums WHERE album_id = %s;''', aid)
		conn.commit()
		return render_template('hello.html', name = flask_login.current_user.id, message='Album Deleted!', 
								albums = getUsersAlbums(uid), photos = getUsersPhotos(uid), base64=base64)
	return render_template('hello.html', name = flask_login.current_user.id, message='Here is your content', 
								albums = getUsersAlbums(uid), photos = getUsersPhotos(uid), base64=base64)
	
#-----------------------------upload-----------------------------

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
									photos=getUsersPhotos(uid), base64=base64)
		except:
			return render_template('upload.html', albums=getUsersAlbums(uid))
	#The method is GET so we return a  HTML form to upload the a photo.
	else:
		return render_template('upload.html', albums=getUsersAlbums(uid))
#end photo uploading code

#------------------------------Search------------------------------
def getAllAlbums():
	cursor = conn.cursor()
	cursor.execute('''SELECT * FROM Albums''')
	return cursor.fetchall() #NOTE return a list of tuples, [(album_id, album_name, user_id, doc), ...]

def getAllPhotos():
	cursor = conn.cursor()
	cursor.execute('''SELECT * FROM Pictures''')
	return cursor.fetchall() #NOTE return a list of tuples, [(picture_id, user_id, imgdata, caption, loc, album_id), ...]

def getPhotos_byAlbum(aid):
	cursor = conn.cursor()
	cursor.execute('''SELECT * FROM Pictures WHERE album_id = %s''', aid)
	return cursor.fetchall() #NOTE return a list of tuples, [(picture_id, user_id, imgdata, caption, loc, album_id), ...]

def getPhotos_byTag(tag, onlyusers):
	if onlyusers==0:
		cursor = conn.cursor()
		cursor.execute('''SELECT P.picture_id, P.user_id, P.imgdata, P.caption, P.loc, P.album_id FROM Pictures P, Tag T 
						WHERE T.word = %s AND T.picture_id = P.picture_id''', tag)
		return cursor.fetchall() #NOTE return a list of tuples, [(picture_id, user_id, imgdata, caption, loc, album_id), ...]
	else:
		uid=getUserIdFromEmail(flask_login.current_user.id)
		cursor = conn.cursor() 
		cursor.execute("SELECT P.picture_id, P.user_id, P.imgdata, P.caption, P.loc, P.album_id FROM Pictures P, Tag T \
						WHERE P.user_id = '{0}' AND T.picture_id = P.picture_id AND T.word = '{1}'".format(uid, tag))
		return cursor.fetchall() #NOTE return a list of tuples, [(picture_id, user_id, imgdata, caption, loc, album_id), ...]
	

#default page/home page
@app.route("/", methods=['GET', 'POST'])
def hello(): #hello()
	allphotos = getAllPhotos()
	allalbums = getAllAlbums()
	try:
		userid=getUserIdFromEmail(flask_login.current_user.id)
	except:
		userid = None
	if request.method=='POST':
		#Get photos in Album
		if(request.form.get('aid')):
			aid = request.form.get('aid')
			photos = getPhotos_byAlbum(aid)
			return render_template('searchall.html', uid=userid, photos = photos, base64=base64) 
		#get All photos from tag
		if(request.form.get('tag')):
			tag=request.form.get('tag')
			photos = getPhotos_byTag(tag,0)
			return render_template('searchall.html', uid=userid, photos = photos, base64=base64)
		#get User photos from tag
		if(request.form.get('mytagsearch')):
			mytag = request.form.get('mytagsearch')
			photos = getPhotos_byTag(mytag,1)
			return render_template('searchall.html', uid=userid, photos = photos, base64=base64)
		else:
			return render_template('searchall.html', message = "Nothing was found for that search", uid=userid, albums = allalbums, photos = allphotos, base64=base64)
	return render_template('searchall.html', uid=userid, albums = allalbums, photos = allphotos, base64=base64)
	



if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)