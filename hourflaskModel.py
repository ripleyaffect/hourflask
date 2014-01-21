import sqlite3

_conn = sqlite3.connect('/tmp/hourflask.db', check_same_thread=False)
_conn.row_factory = sqlite3.Row
_cursor = _conn.cursor()

class HourflaskModel:
	def __init__(self):
		pass

	@classmethod
	def user_exists(cls, username):
		rows = _cursor.execute('SELECT id FROM users where username=?', [username])
		user = [r['id'] for r in rows]
		if len(user) > 0:
			return True
		return False

	@classmethod
	def create_account(cls, username, password):
		_cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
		_conn.commit()
		print [r for r in _cursor.execute('SELECT last_insert_rowid()')]
		rows = _cursor.execute('SELECT id FROM users where username=?', [username])
		user_id = [r['id'] for r in rows]
		return user_id[0]

	@classmethod
	def login(cls, username):
		rows = _cursor.execute('SELECT id, password FROM users where username=?', [username])
		return [{ 'id':r['id'], 'password': r['password'] } for r in rows]

	@classmethod
	def create_project(cls, args):
		_cursor.execute('INSERT INTO projects (user_id, title, description, start_time, total_hours, completed_hours, time_limit) values (?, ?, ?, ?, ?, ?, ?)',
					 (args['user_id'], args['title'], args['description'], args['start_time'], args['total_hours'], args['completed_hours'], args['time_limit']))
		_conn.commit()
		return [r for r in _cursor.execute('SELECT last_insert_rowid()')][0][0]

	@classmethod
	def delete_project(cls, id):
		_cursor.execute('DELETE FROM projects WHERE id=?', [id])
		_conn.commit()		

	@classmethod
	def get_projects(cls, user_id):
		rows = _cursor.execute('SELECT id, title, description, start_time, total_hours, completed_hours, time_limit FROM projects where user_id=?', [user_id])
		return [p for p in rows]

	@classmethod
	def add_time(cls, args):
		_cursor.execute('UPDATE projects SET completed_hours=? WHERE id=?', (args['completed_hours'], args['id']))
		_conn.commit()