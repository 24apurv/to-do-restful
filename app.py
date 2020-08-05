# Import required libraries
import werkzeug 
werkzeug.cached_property = werkzeug.utils.cached_property
from flask import Flask, request, jsonify
from flask_restplus import Api, Resource, fields
from flask_sqlalchemy import SQLAlchemy 
from datetime import date, datetime
import json
import dateutil.parser

# Initialize app
flask_app = Flask(__name__)
# Database for SQLAlchemy
flask_app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///to-do-list.db'
flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True 
# Initialize Database
db = SQLAlchemy(flask_app)
# Initialize restplus api
app = Api(app = flask_app,
		  version = "1.0", 
		  title = "To-do-list Rest API", 
		  description = "APIs for to-do-list application")

def json_serial(obj):
    """ JSON serializer for datetime objects """
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

# Database Model
class ToDo(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(50), nullable=False)
	content = db.Column(db.String(200), nullable=True)
	timestamp = db.Column(db.DateTime, default=datetime.now)
	deadline = db.Column(db.DateTime, nullable=True)
	completed = db.Column(db.Boolean, default=False)

	# Readable format for debugging using print function
	def __str__(self):
		return str(self.id) + " " + self.title

# Swagger Model
model = app.model('ListItem Model', 
		  {'id': fields.Integer(required=False,
		  			 description="Id of list item"),
		  'title': fields.String(required = True, 
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

# API namespace for Swagger UI
list_namespace = app.namespace('to-do-list', description='APIs to create and read to-do-list items')

# Class defining API's for route "to-do-list/"
@list_namespace.route("/")
class To_do_list(Resource):

	@app.doc(responses={ 200: 'OK', 500: 'Could not resolve' })
	def get(self):
		""" API for GET request at "to-do-list/" 
			Returns all to-do-list items
		"""

		# List of dictionaries to unpack queryset
		lst = []
		for item in ToDo.query.all():
			itemDict = {}
			itemDict['id'] = item.id
			itemDict['title'] = item.title
			itemDict['content'] = item.content
			itemDict['timestamp'] = json_serial(item.timestamp)
			itemDict['deadline'] = json_serial(item.deadline)
			itemDict['completed'] = item.completed
			lst.append(itemDict)
		# Return jsonified list of dictionaries as array of json objects
		return jsonify(lst)


	@app.doc(responses={ 200: 'OK', 400: 'Invalid Argument', 500: 'Mapping Key Error' })
	@app.expect(model)
	def post(self):
		""" API for POST request at "to-do-list/" 
			Creates a new item and returns the same
		"""
		try:
			data = request.json

			# Create model object and inject json data 
			toDoItem = ToDo()
			toDoItem.title =  data['title']
			toDoItem.content = data['content']
			toDoItem.timestamp = dateutil.parser.parse(data['timestamp'], ignoretz=True)
			toDoItem.deadline = dateutil.parser.parse(data['deadline'], ignoretz=True)
			toDoItem.completed = data['completed']

			# Add model object to database
			db.session.add(toDoItem)
			db.session.commit()
			return request.json

		# Handle any exceptions
		except Exception as e:
			list_namespace.abort(400, e.__doc__, status = "Could not save item", statusCode = "400")


@list_namespace.route("/<int:id>")
class To_do_list_item(Resource):

	@app.doc(responses={ 200: 'OK', 400: 'Invalid Argument', 500: 'Mapping Key Error' }, 
			 params={ 'id': 'Specify the Id associated with the item' })
	def get(self, id):
		""" API for GET request at "to-do-list/<id>" 
			Returns item with specified id
		"""
		try:

			# Retrieve item from database
			item = ToDo.query.get(id)
			if item == None:
				raise KeyError

			# Add data from query to dictionary to serialize 
			itemDict = {}
			itemDict['id'] = item.id
			itemDict['title'] = item.title
			itemDict['content'] = item.content
			itemDict['timestamp'] = json_serial(item.timestamp)
			itemDict['deadline'] = json_serial(item.deadline)
			itemDict['completed'] = item.completed

			# Return jsonified dictionary
			return jsonify(itemDict)

		# Handle exceptions, especially KeyError for wrong id
		except KeyError as e:
			list_namespace.abort(500, e.__doc__, status = "Item does not exist", statusCode = "500")
		except Exception as e:
			list_namespace.abort(400, e.__doc__, status = "Could not fetch item", statusCode = "400")


	@app.doc(responses={ 200: 'OK', 400: 'Invalid Argument', 500: 'Mapping Key Error' }, 
			 params={ 'id': 'Specify the Id associated with the person' })
	@app.expect(model)		
	def put(self, id):
		""" API for PUT request at "to-do-list/<id>"
			Updates item with specified id
		"""
		try:

			# Retrieve item from database
			item = ToDo.query.get(id)
			if item == None:
				raise KeyError
			data = request.json
			item.title =  data['title']
			item.content = data['content']
			item.timestamp = dateutil.parser.parse(data['timestamp'], ignoretz=True)
			item.deadline = dateutil.parser.parse(data['deadline'], ignoretz=True)
			item.completed = data['completed']

			# Save updated object in database
			db.session.commit()

			# Return same object
			return request.json

		# Handle exceptions, especially KeyError for wrong id
		except KeyError as e:
			list_namespace.abort(500, e.__doc__, status = "Item does not exist", statusCode = "500")
		except Exception as e:
			list_namespace.abort(400, e.__doc__, status = "Could not update item", statusCode = "400")


	@app.doc(responses={ 200: 'OK', 400: 'Invalid Argument', 500: 'Mapping Key Error' }, 
			 params={ 'id': 'Specify the Id associated with the person' })
	@app.expect(model)		
	def delete(self, id):
		""" API for DELETE request at "to-do-list/<id>"
			Deletes item with specified id
		"""
		try:
			# Retrieve item from database
			item = ToDo.query.get(id)
			if item == None:
				raise KeyError

			# Delete object from database
			db.session.delete(item)
			db.session.commit()
			return request.json

		# Handle exceptions, especially KeyError for wrong id
		except KeyError as e:
			list_namespace.abort(500, e.__doc__, status = "Item does not exist", statusCode = "500")
		except Exception as e:
			list_namespace.abort(400, e.__doc__, status = "Could not delete item", statusCode = "400")

# Initialize Flask app
if __name__ == "__main__" :
	flask_app.run(debug=True)