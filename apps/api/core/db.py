import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL", "https://placeholder.supabase.co")
supabase_anon_key = os.getenv("SUPABASE_ANON_KEY", "placeholder-anon-key")

try:
    supabase: Client = create_client(supabase_url, supabase_anon_key)
except Exception:
    supabase = None


def get_supabase() -> Client:
    if supabase is not None:
        return supabase
    url = os.getenv("SUPABASE_URL", "https://placeholder.supabase.co")
    key = os.getenv("SUPABASE_ANON_KEY", "placeholder-anon-key")
    return create_client(url, key)
