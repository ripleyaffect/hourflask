app = angular.module('HourflaskApp', []);

app.factory('sessionData', function(){
  return { logged_in: false };
});

app.config(['$routeProvider', function($routeProvider) {
		$routeProvider
			.when('/', {
				templateUrl: '../static/login.html',
				controller: 'LoginController'
			})
			.when('/createNewAccount', {
				templateUrl: '../static/createNewAccount.html',
				controller: 'CreateAccountController'
			})
			.when('/projects' , {
				templateUrl: '../static/projects.html',
				controller: 'ProjectsController'
			})
			.otherwise({ redirectTo: '/' });
}]);

app.controller('LoginController', [
	'$scope',
	'$http',
	'$location',
	'sessionData',
	function($scope, $http, $location, sessionData) {
		$scope.user = {};
		$scope.session = sessionData;

		if($scope.session.logged_in == true) { $location.path('/projects') };

		$scope.login = function() {
			if($scope.user.username.length < 5) {
				window.alert('Username is too short');
			} 
			else if($scope.user.password.length < 5) {
				window.alert('Password is too short');
			}
			else {
				$http.post('/login', {
					username: $scope.user.username.toLowerCase(),
					password: $scope.user.password
				})
				.success(function(data, status, headers, config) {
					if (data.success) {
						$scope.session.user_id = data.user_id;
						$scope.session.logged_in = true;
						$location.path('/projects').replace();
					} else {
						window.alert('User was not not logged in: ' + data.error);
					}
				})
				.error(function(data, status, headers, config) {
					window.alert('There was an error');
				});
			}
		};
	}
]);

app.controller('CreateAccountController', [
	'$scope',
	'$http',
	'$location',
	'sessionData',
	function($scope, $http, $location, sessionData) {
		$scope.user = {};
		$scope.session = sessionData;
		// Add a user to the database and sign them in.
		$scope.create = function() {
			if($scope.user.username.length < 5) {
				window.alert('Username must be at least 5 characters long');
			} else if($scope.user.password.length < 5) {
				window.alert('Password must be at least 6 characters long');
			} else if($scope.user.password != $scope.user.password2) {
				window.alert('Passwords do not match');	
			}	else {
				$http.post('/createAccount', {
					username: $scope.user.username.toLowerCase(),
					password: $scope.user.password
				})
				.success(function(data, status, headers, config) {
					if (data.success) {
						$scope.session.user_id = data.user_id;
						$scope.session.logged_in = true;
						$location.path('/projects');
					} else {
						window.alert('User was not added');
					}
				})
				.error(function(data, status, headers, config) {
				});
			}
		};
	}
]);

app.controller('ProjectsController', [
	'$scope',
	'$http',
	'$location',
	'sessionData',
	function($scope, $http, $location, sessionData) {
		$scope.session = sessionData;
		$scope.projects = [];
		$scope.new_project = { title: "", description: "", time_limit: 20, total_hours: 100};
		$scope.add_time = { hours: 0.0, minutes: 0.0 };

		if($scope.session.logged_in == false) { $location.path('/login') };

		$scope.logout = function() {
			$scope.session.logged_in = false;
			$scope.session.user_id = null;
			$location.path('/login');
		}

		$scope.getProjects = function() {
			$http.post('/getProjects', {
				'user_id': $scope.session.user_id
			})
			.success(function(data, status, headers, config) {
				if (data.success) {
					$scope.projects = data.projects;
				} else {
					window.alert('Projects could not be retrieved');
				}
			})
			.error(function(data, status, headers, config) {
			});
		};

		$scope.createProject = function() {
			var time = (new Date().getTime()) / (1000 * 60 * 60 * 24)
			if($scope.new_project.title.length < 1){
				window.alert("Project name can't be blank");
			} else if($scope.new_project.time_limit < 4.17) {
				window.alert("That's too short a time frame");
			} else {
				$http.post('/createProject', {
					user_id: $scope.session.user_id,
					title: $scope.new_project.title,
					description: $scope.new_project.description,
					start_time: time,
					total_hours: 100.0,
					completed_hours: 0.0,
					time_limit: $scope.new_project.time_limit
				})
				.success(function(data, status, headers, config) {
					if (data.success) {
						$scope.projects.push({
							id: data.id,
							user_id: $scope.session.user_id,
							title: $scope.new_project.title,
							description: $scope.new_project.description,
							start_time: time,
							total_hours: $scope.new_project.total_hours,
							completed_hours: 0.0,
							time_limit: $scope.new_project.time_limit
						});
						$scope.new_project.title = "";
						$scope.new_project.description = "";
						$scope.new_project.time_limit = 20;
					} else {
						window.alert('Project could not be added');
					}
				})
				.error(function(data, status, headers, config) {
				});
			}
		};

		$scope.deleteProject = function(project) {
			$scope.r = confirm("Are you sure you want to delete '" + project.title + "'?");
			if($scope.r) {
				$http.post('/deleteProject', {
						id: project.id
					})
					.success(function(data, status, headers, config) {
						if (data.success) {
	        		$scope.projects.splice($scope.projects.indexOf(project), 1);
						} else {
							window.alert('Project could not be destroyed');
						}
					})
					.error(function(data, status, headers, config) {
						window.alert('An error occured');
					});
			}
		};

		$scope.addTime = function(project){
			if(project.completed_hours == project.total_hours) { return };
			$scope.new_time = project.completed_hours + $scope.add_time.hours + ($scope.add_time.minutes / 60);
			if($scope.new_time > project.total_hours) { $scope.new_time = project.total_hours };
			$http.post('/addTime', {
					id: project.id,
					completed_hours: $scope.new_time
				})
				.success(function(data, status, headers, config) {
					if (data.success) {
						project.completed_hours = $scope.new_time;
						if($scope.new_time / project.total_hours > 0.99) {
							project.border_radius = " border-bottom-right-radius: 5px; border-top-right-radius: 5px;";
						}
					} else {
						window.alert('Time could not be updated');
					}
				})
				.error(function(data, status, headers, config) {
					window.alert('An error occured');
				});
		};

		$scope.showEdit = function(project) {
			$scope.projects.forEach(function(p) {
				if(p != project) { p.visible = false; };
			});
			$scope.add_time.hours = 0.0;
			$scope.add_time.minutes = 0.0;
			project.visible = !project.visible;
		}

		if($scope.projects.length == 0) {
			$scope.getProjects();
		}
	}
]);