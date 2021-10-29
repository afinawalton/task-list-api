from flask import Blueprint, json, jsonify, request
from app.models.goal import Goal
from app import db
from datetime import datetime
# from dotenv import load_dotenv
# import os
# import requests

goals_bp = Blueprint("goals", __name__, url_prefix="/goals")

@goals_bp.route("", methods=["GET"])
def get_goals():
    # Query into db to get goal
    goals = Goal.query.all()

    goals_response = []

    if not goals:
        return goals_response, 200

    for goal in goals:
        pass
