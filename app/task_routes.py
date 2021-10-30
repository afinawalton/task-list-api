from flask import Blueprint, json, jsonify, request
from app.models.task import Task
from app import db
from datetime import datetime
from dotenv import load_dotenv
import os
import requests

load_dotenv()
SLACK_API_KEY = os.environ.get('SLACK_API_KEY')

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["GET"])
def get_tasks():
    tasks = Task.query.all()
    tasks_response = []

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
def get_or_update_one_task(task_id):
    task = Task.query.get(task_id)

    if not task:
        return "", 404

    if not task.goal_id:
        return {"task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": task.is_complete
        }
        }, 200 

    return {
        "task": {
            "id": task.task_id,
            "goal_id": task.goal_id,
            "title": task.title,
            "description": task.description,
            "is_complete": task.is_complete
        }
        }, 200        

@tasks_bp.route("/<task_id>", methods=["PUT"])
def update_one_task(task_id):
    task = Task.query.get(task_id)
    request_body = request.get_json()

    if not task:
        return "", 404

    if 'title' in request_body:
        task.title = request_body['title']
        
    if request_body['description']:
        task.description = request_body['description']

    if 'completed_at' in request_body:
        task.completed_at = request_body['completed_at']
        task.is_complete = True
        
    db.session.commit()

    return {"task": task.to_dict()}, 200


@tasks_bp.route("/<task_id>/mark_complete", methods=["POST", "PATCH"])
def update_task_complete(task_id):
    task = Task.query.get(task_id)

    if not task:
        return "", 404

    task.is_complete = True
    task.completed_at = datetime.now()

    db.session.commit()

    if request.method == "PATCH":
        requests.post(
            'https://slack.com/api/chat.postMessage',
            params={
                'channel': 'task-notifications',
                'text': f"Someone just completed the task {task.title}"},
            headers={'Authorization': f'Bearer {SLACK_API_KEY}'}
        )

    task_response = task.to_dict()

    return {"task": task_response}, 200

@tasks_bp.route("/<task_id>/mark_incomplete", methods=["POST", "PATCH"])
def update_task_incomplete(task_id):
    task = Task.query.get(task_id)

    if not task:
        return "", 404

    task.is_complete = False
    task.completed_at = None
    db.session.commit()

    task_response = task.to_dict()

    return {"task": task_response}, 200

@tasks_bp.route("", methods=["POST"])
def create_task():
    request_body = request.get_json()

    if 'title' not in request_body or 'description' not in request_body \
    or 'completed_at' not in request_body:
        return {"details": "Invalid data"}, 400

    new_task = Task(
        title=request_body['title'],
        description=request_body['description'],
        completed_at=request_body['completed_at']
    )

    if request_body['completed_at']:
        new_task.is_complete = True

    db.session.add(new_task)
    db.session.commit()

    task_response = new_task.to_dict()

    return jsonify({"task": task_response}), 201

@tasks_bp.route("/<task_id>", methods=["PUT"])
def update_task(task_id):
    task = Task.query.get(task_id)

    if not task:
        return "", 404

    request_body = request.get_json()

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