from flask import Blueprint, json, jsonify, request
from app.models.task import Task
from app import db

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

# If no tasks exist, return [] and 200
@tasks_bp.route("", methods=["GET"])
def get_tasks():
    # Query the database to get all tasks
    # If none exist, return [] 200
    tasks = Task.query.all()
    tasks_response = []

    if not tasks:
        return jsonify(tasks_response), 200

    for task in tasks:
        task = task.to_dict()
        tasks_response.append(task)

    return jsonify(tasks_response), 200

@tasks_bp.route("", methods=["POST"])
def create_task():
    # Get some input from user -> request body
    # Map the key value pairs to our Task
    # Add that info to our database
    request_body = request.get_json()
    # {"title": "fido", "key": "value"}

    new_task = Task(
        title=request_body['title'],
        description=request_body['description']
    )

    db.session.add(new_task)
    db.session.commit()

    task_response = new_task.to_dict()

    return jsonify(task_response), 200