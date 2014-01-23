from flask import request, jsonify, render_template
from hourflaskModel import HourflaskModel
from passlib.hash import sha256_crypt
import flask.views
import json

class HourflaskView(flask.views.MethodView):
	def get(self):
		return render_template('index.html')

class CreateAccount(flask.views.MethodView):
	def post(self):
		args = json.loads(request.data)
		user_exists = HourflaskModel.user_exists(args['username'])
		if not user_exists:
			enc_password = sha256_crypt.encrypt(args['password'])
			user_id = HourflaskModel.create_account(args['username'], enc_password)
			example_project = {
						'user_id': user_id,
						'title': "Example Project", 
						'description': "An example Project. Feel free to delete it.", 
						'start_time': 16080.78, 
						'total_hours': 100,
						'completed_hours': 5.0, 
						'time_limit': 15 
			}
			HourflaskModel.create_project(example_project)
			return jsonify({ 'success': True, 'user_id': user_id })
		return jsonify({ 'success': False, 'error': 'Username is taken'})

class Login(flask.views.MethodView):
	def post(self):
		args = json.loads(request.data)
		result = HourflaskModel.login(args['username'])
		if (len(result) == 0):
			return jsonify({ 'success': False, 'error': 'Username not found'})
		user = result[0]
		if not sha256_crypt.verify(args['password'], user['password']):
			return jsonify({ 'success': False, 'error': 'Incorrect password'})
		return jsonify({ 'success': True, 'user_id': user['id']})

class CreateProject(flask.views.MethodView):
	def post(self):
		args = json.loads(request.data)
		project_id = HourflaskModel.create_project(args)
		return jsonify({ 'success': True, 'id': project_id})

class DeleteProject(flask.views.MethodView):
	def post(self):
		args = json.loads(request.data)
		HourflaskModel.delete_project(args['id'])
		return jsonify({ 'success': True })

class GetProjects(flask.views.MethodView):
	def post(self):
		args = json.loads(request.data)
		projects = HourflaskModel.get_projects(args['user_id'])
		return jsonify({
			'success': True,
			'projects': [{ 
				'id': p['id'],
				'title': p['title'], 
				'description': p['description'], 
				'start_time': p['start_time'], 
				'total_hours': p['total_hours'], 
				'completed_hours': p['completed_hours'], 
				'time_limit': p['time_limit'],
				'visible': False
			} for p in projects]
		})

class AddTime(flask.views.MethodView):
	def post(self):
		args = json.loads(request.data)
		HourflaskModel.add_time(args)
		return jsonify( {'success': True } )

class EditTitle(flask.views.MethodView):
	def post(self):
		args = json.loads(request.data)
		HourflaskModel.edit_title(args)
		return jsonify( {'success': True } )
