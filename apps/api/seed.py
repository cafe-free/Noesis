from data import users
from core.db import supabase

def insert_users():
    try:
        for user in users:
            supabase.table("users").insert(user).select().execute()
    except Exception as e:
        print(e)
        return False
    return True

if __name__ == "__main__":
    insert_users()