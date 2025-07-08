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
    
    # Check if interest already exists (case-insensitive)
    interest_lower = interest.lower()
    for existing_interest in interests:
        if existing_interest.lower() == interest_lower:
            return  # Interest already exists, don't add duplicate
    
    # Add the interest with original capitalization
    interests.append(interest)
    with open(MEMORY_FILE, "w") as f:
        json.dump(interests, f)

def remove_interest(interest):
    interests = load_interests()
    
    # First try exact match (case-sensitive)
    if interest in interests:
        interests.remove(interest)
        with open(MEMORY_FILE, "w") as f:
            json.dump(interests, f)
        return True
    
    # If no exact match, try case-insensitive search
    interest_lower = interest.lower()
    for stored_interest in interests:
        if stored_interest.lower() == interest_lower:
            interests.remove(stored_interest)
            with open(MEMORY_FILE, "w") as f:
                json.dump(interests, f)
            return True
    
    return False