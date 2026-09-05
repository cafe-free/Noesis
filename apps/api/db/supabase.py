from supabase import create_client, Client
from apps.api.core.config import get_settings

settings = get_settings()

def get_supabase() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
