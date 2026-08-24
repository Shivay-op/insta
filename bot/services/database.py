import json
import os

from config import DATA_DIR

FILE = os.path.join(DATA_DIR, "users.json")


def load_users():

    if not os.path.exists(FILE):
        return []

    with open(
        FILE,
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)



def save_users(users):

    with open(
        FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            users,
            f,
            indent=4,
            ensure_ascii=False
        )



def add_user(user):

    users = load_users()

    for u in users:
        if u["id"] == user.id:
            return len(users)


    users.append({
        "id": user.id,
        "name": user.first_name or "Unknown",
        "username": user.username or "No Username"
    })


    save_users(users)


    return len(users)
