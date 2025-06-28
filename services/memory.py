import json
import os

MEMORY_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'user_interests.json')

def load_interests():
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def add_interest(interest):
    interests = load_interests()
    if interest not in interests:
        interests.append(interest)
        with open(MEMORY_FILE, "w") as f:
            json.dump(interests, f)
