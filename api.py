from flask import Blueprint, request
from flask.ext.restful import Api, Resource, fields, marshal_with
from models import Todo, db

api = Api(prefix='/api')
api_bp = Blueprint('api_bp', __name__)
api.init_app(api_bp)

todo_fields = {
    'id': fields.Integer,
    'task': fields.String,
    'date': fields.DateTime,
    'done': fields.Boolean
}


class TodoListResource(Resource):
    @marshal_with(todo_fields)
    def get(self):
        return Todo.query.all()

    @marshal_with(todo_fields)
    def post(self):
        new = Todo(request.json['task'], False)
        db.session.add(new)
        db.session.commit()
        return new, 201

    def put(self):
        tasks = Todo.query.all()
        for task in tasks:
            task.done = True
        db.session.commit()
        return '', 204

    def delete(self):
        # clear all done todos
        db.session.query(Todo).filter(Todo.done==True).delete(synchronize_session=False)
        db.session.commit()


class TodoResource(Resource):
    @marshal_with(todo_fields)
    def get(self, todo_id):
        res = Todo.query.get(todo_id)
        if res:
            return res
        return {'error': 'The specified id was not found in the DB'}, 400

    def put(self, todo_id):
        to_modify = Todo.query.get(todo_id)
        if to_modify and request.json:
            to_modify.task = request.json.get('task', to_modify.task)
            to_modify.done = request.json.get('done', to_modify.done)
            db.session.commit()
            return '', 204
        return {}, 400

    def delete(self, todo_id):
        to_delete = Todo.query.get(todo_id)
        if to_delete:
            print(to_delete.id)
            db.session.delete(to_delete)
            db.session.commit()
            return '', 204
        return {'error': 'The specified id was not found in the DB'}, 400

    @marshal_with(todo_fields)
    def post(self, todo_id):

        current_todo = Todo.query.get(todo_id)

        clone_todo = Todo(
            task=current_todo.task,
            done=current_todo.done
        )

        clone_todo.date = current_todo.date

        db.session.add(clone_todo)
        db.session.commit()

        return clone_todo, 201

api.add_resource(TodoListResource, '/todos')
api.add_resource(TodoResource, '/todos/<string:todo_id>')
api.add_resource(TodoResource, '/todos/clone/<string:todo_id>', endpoint='clone')
