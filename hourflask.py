from flask import Flask

from hourflaskView import HourflaskView, CreateAccount, Login, CreateProject, DeleteProject, GetProjects, AddTime

# Create the app
app = Flask(__name__)

# Routes
app.add_url_rule('/', view_func=HourflaskView.as_view('hourflask_view'), methods=['GET'])
app.add_url_rule('/createAccount', view_func=CreateAccount.as_view('create_new_account'), methods=['POST'])
app.add_url_rule('/login', view_func=Login.as_view('login'), methods=['POST'])
app.add_url_rule('/createProject', view_func=CreateProject.as_view('create_new_project'), methods=['POST'])
app.add_url_rule('/getProjects', view_func=GetProjects.as_view('get_projects'), methods=['POST'])
app.add_url_rule('/addTime', view_func=AddTime.as_view('add_time'), methods=['POST'])
app.add_url_rule('/deleteProject', view_func=DeleteProject.as_view('delete_project'), methods=['POST'])
# route for login
# route for adding a project
# route for adding time to a project
# route for deleting a project

# Run the app
if __name__ == '__main__':
	app.run(debug=True)