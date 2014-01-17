# Import statements
import sqlite3, time
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from contextlib import closing

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

# Display projects if logged in, login page otherwise
@app.route('/')
def root():
	if session.get('logged_in'):
		redirect(url_for('show_projects'))
	else:
		redirect(url_for('login'))


# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		if request.form['username'] != app.config['USERNAME']:
			error = 'Invalid username'
		elif request.form['password'] != app.config['PASSWORD']:
			error = 'Invalid password'
		else:
			session['logged_in'] = True
			flash('You were logged in')
			return redirect(url_for('show_projects'))
	return render_template('login.html', error=error)

@app.route('/projects')
def show_projects():
	cur = g.db.execute('select title, description, start_time, total_hours, hours_completed from projects order by id')
	projects = [dict(title=row[0], 
									description=row[1], 
									start_time=row[2], 
									total_hours=row[3], 
									completed_hours=row[4]
									) for row in cur.fetchall()]
	return render_template('show_projects.html', projects=projects)

@app.route('/add', methods=['POST'])
def add_project():
	if not session.get('logged_in'):
		abort(401)
	g.db.execute('insert into projects (title, description, start_time, total_hours, hours_completed) values (?, ?, ?, ?, ?)',
				 [request.form['title'], request.form['description'], time.time() / 60 / 60, 100.0, 1.0])
	g.db.commit()
	flash('New entry was successfully posted')
	return redirect(url_for('show_projects'))

@app.route('/time', methods=['POST'])
def add_time():
	return redirect(url_for('show_projects'))

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You were logged out')
	return redirect(url_for('login'))

if __name__ == '__main__':
	app.run()