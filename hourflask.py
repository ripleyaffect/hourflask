# Import statements
import sqlite3, time
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from contextlib import closing
from passlib.hash import sha256_crypt

DATABASE = '/tmp/hourflask.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'user'
PASSWORD = 'pass'

# Initialize the app
app = Flask(__name__)

# Configuration. Should be changed to imprort from a config file.
app.config.from_object(__name__)

# Connect to database
def connect_db():
	return sqlite3.connect(app.config['DATABASE'])

def init_db():
	with closing(connect_db()) as db:
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()

@app.before_request
def before_request():
	g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
	db = getattr(g, 'db', None)
	if db is not None:
		db.close()

# Helper methods
def get_time_in_hours():
	return time.time() / 3600

# Display projects if logged in, login page otherwise
@app.route('/')
def root():
	if session.get('logged_in'):
		return redirect(url_for('show_projects'))
	else:
		return redirect(url_for('login'))

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		# Lookup user in the users table.
		cur = g.db.execute('select id, password from users where username=?', [request.form['username']])
		# flash error if user does not exist or password is incorrect, else set the session ID
		result = cur.fetchall()
		flash(result)
		if len(result) == 0:
			error = "Invalid username"
		elif not sha256_crypt.verify(request.form['password'], result[0][1]):
			error = "Invalid password"
		else:
			session['user_id'] = result[0][0]
			session['logged_in'] = True
			flash('You were logged in with user ID ' + str(session.get('user_id')))
			return redirect(url_for('show_projects'))
	return render_template('login.html', error=error)

@app.route('/createuser', methods=['GET', 'POST'])
def create_user():
	error = None
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		cur = g.db.execute('select id from users where username=?', [username])
		results = cur.fetchall()
		if len(username) < 5:
			error = "Username must be 5 or more characters long"
		elif len(password) < 6:
			error = "password must be 6 or more characters long"
		elif len(results) > 0:
			error = "Username taken"
		elif password != request.form['password2']:
			error = "Passwords don't match"
		else:
			g.db.execute('insert into users (username, password) values (?, ?)',
					 [username, sha256_crypt.encrypt(password)])
			g.db.commit()
			flash('Account created!')
			return redirect(url_for('login'))
	return render_template('new_user.html', error=error)

@app.route('/projects')
def show_projects():
	cur = g.db.execute('select title, description, start_time, total_hours, completed_hours, time_limit from projects where user_id= (?) order by id', 
					[session.get('user_id')])
	projects = [dict(title=row[0], 
									description=row[1], 
									start_time=row[2], 
									total_hours=row[3], 
									completed_hours=row[4],
									time_limit=row[5]
									) for row in cur.fetchall()]
	return render_template('show_projects.html', projects=projects)

@app.route('/addproject', methods=['POST'])
def add_project():
	error = None
	if not session.get('logged_in'):
		abort(401)
	title = request.form['title']
	description = request.form['description']
	time_limit = request.form['time_limit']
	if len(title) < 1:
		error = "Must enter a title name"
	elif time_limit == '':
		error = "Enter a time limit for your project. enter -1 for unlimited time"
	else:
		if float(time_limit) < 0:
			time_limit = 99999999999
		g.db.execute('insert into projects (user_id, title, description, start_time, total_hours, completed_hours, time_limit) values (?, ?, ?, ?, ?, ?, ?)',
					 [session.get('user_id'), title, description, get_time_in_hours(), 100.0, 0.0, float(time_limit)])
		g.db.commit()
		flash('New project was created!')
		return redirect(url_for('show_projects'))
	return render_template('show_projects.html', error=error)

@app.route('/time', methods=['POST'])
def add_time():
	return redirect(url_for('show_projects'))

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	session.pop('user_id', None)
	flash('You were logged out')
	return redirect(url_for('login'))

if __name__ == '__main__':
	app.run()