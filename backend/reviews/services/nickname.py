import hashlib

ADJECTIVES = ["Anonymous", "Mysterious", "Clever", "Swift", "Silent", "Brave", "Curious", "Happy"]
ANIMALS = ["Fox", "Panda", "Bunny", "Tiger", "Owl", "Dolphin", "Eagle", "Wolf", "Koala", "Otter"]

def generate_nickname(visitor_id: str) -> str:
    """
    Deterministically generates a nickname from a visitor ID.
    The same ID will always get the same nickname.
    """
    if not visitor_id:
        return "Anonymous Ghost"

    # Create a hash of the visitor ID
    hash_hex = hashlib.md5(visitor_id.encode('utf-8')).hexdigest()
    
    # Use the hash to pick an adjective and an animal
    adj_index = int(hash_hex[:8], 16) % len(ADJECTIVES)
    animal_index = int(hash_hex[8:16], 16) % len(ANIMALS)
    
    return f"{ADJECTIVES[adj_index]} {ANIMALS[animal_index]}"

def get_initials(nickname: str) -> str:
    """Extracts initials from a nickname (e.g., 'Anonymous Panda' -> 'AP')"""
    parts = nickname.split()
    if len(parts) >= 2:
        return f"{parts[0][0]}{parts[1][0]}".upper()
    return nickname[:2].upper()