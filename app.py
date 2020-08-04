import werkzeug 
werkzeug.cached_property = werkzeug.utils.cached_property
from flask import Flask, request
from flask_restplus import Api, Resource, fields
import datetime

flask_app = Flask(__name__)
app = Api(app = flask_app,
		  version = "1.0", 
		  title = "To-do-list Rest API", 
		  description = "APIs for to-do-list application")

model = app.model('ListItem Model', 
		  {'title': fields.String(required = True, 
					 description="Title of list item", 
					 help="Name cannot be blank."),
		  'content': fields.String(required=False,
		  			 description="Content of list item"),
		  'timestamp': fields.DateTime(required=True,
		  			 description="Time of creation"),
		  'deadline': fields.DateTime(required=False,
		  			 description="Deadline for completion of task"),
		  'completed': fields.Boolean(default=False,
		  			 required=True),
		  })

list_namespace = app.namespace('to-do-list', description='APIs to create and read to-do-list items')

@list_namespace.route("/")
class To_do_list(Resource):

	@app.doc(responses={ 200: 'OK', 500: 'Could not resolve' })
	def get(self):
		return {
			"status": "Got new data"
		}
	def post(self):
		return {
			"status": "Posted new data"
		}

@list_namespace.route("/<int:id>")
class To_do_list_item(Resource):

	@app.doc(responses={ 200: 'OK', 400: 'Invalid Argument', 500: 'Mapping Key Error' }, 
			 params={ 'id': 'Specify the Id associated with the item' })
	def get(self, id):
		try:
			name = list_of_names[id]
			return {
				"status": "List item retrieved",
				"name" : list_of_names[id]
			}
		except KeyError as e:
			name_space.abort(500, e.__doc__, status = "Could not retrieve information", statusCode = "500")
		except Exception as e:
			name_space.abort(400, e.__doc__, status = "Could not retrieve information", statusCode = "400")

	@app.doc(responses={ 200: 'OK', 400: 'Invalid Argument', 500: 'Mapping Key Error' }, 
			 params={ 'id': 'Specify the Id associated with the person' })
	@app.expect(model)		
	def post(self, id):
		try:
			list_of_names[id] = request.json['name']
			return {
				"status": "List item added",
				"name": list_of_names[id]
			}
		except KeyError as e:
			name_space.abort(500, e.__doc__, status = "Could not save information", statusCode = "500")
		except Exception as e:
			name_space.abort(400, e.__doc__, status = "Could not save information", statusCode = "400")


if __name__ == "__main__" :
	flask_app.run(debug=True)