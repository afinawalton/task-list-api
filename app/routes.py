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

    # If user has given us a query param
    # Get queries to sort by ascending order
    # Store that query in a variable
    # It will be a list of instances
    # Each instance has methods and attributes
    # Return items in ascending order
    # As a list of dictionaries
    # Need to use jsonify on the list
    # Loop through each query, turning into dictionary
    # Then appending to list

    sort_by = request.args.get("sort") # If user has requested a sort param, get the value
    if sort_by:
        if sort_by == "asc":
            # Query into the db to get objects by ascending
            sorted_tasks = Task.query.order_by(Task.title.asc())
            for task in sorted_tasks:
                task = task.to_dict()
                tasks_response.append(task)

            return jsonify(tasks_response)
        elif sort_by == "desc":
            sorted_tasks = Task.query.order_by(Task.title.desc())
            for task in sorted_tasks:
                task = task.to_dict()
                tasks_response.append(task)

            return jsonify(tasks_response)

    if not tasks:
        return jsonify(tasks_response), 200

    if not sort_by: # If no query param given
        for task in tasks:
            task = task.to_dict()
            tasks_response.append(task)

        return jsonify(tasks_response), 200

@tasks_bp.route("/<task_id>", methods=["GET"])
def get_one_task(task_id):
    task = Task.query.get(task_id)

    if not task:
        return "", 404

    return {"task": task.to_dict()}, 200

@tasks_bp.route("", methods=["POST"])
def create_task():
    # Get some input from user -> request body
    # Map the key value pairs to our Task
    # Add that info to our database
    request_body = request.get_json()
    # {"title": "fido", "key": "value"}

    if 'title' not in request_body or 'description' not in request_body \
    or 'completed_at' not in request_body:
        return {"details": "Invalid data"}, 400

    new_task = Task(
        title=request_body['title'],
        description=request_body['description']
    )

    db.session.add(new_task)
    db.session.commit()

    task_response = new_task.to_dict()

    return jsonify({"task": task_response}), 201

@tasks_bp.route("/<task_id>", methods=["PUT"])
def update_task(task_id):
    # Get the selected task
    task = Task.query.get(task_id)

    if not task:
        return "", 404

    request_body = request.get_json()

    # Take values from request body and apply to task
    if "title" in request_body:
        task.title = request_body['title']
    if "description" in request_body:
        task.description = request_body['description']

    db.session.commit()

    task_response = task.to_dict()
    
    return {"task": task_response}, 200

@tasks_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = Task.query.get(task_id)

    if not task:
        return "", 404

    db.session.delete(task)
    db.session.commit()

    return {"details": f'Task {task_id} "{task.title}" successfully deleted'}, 200