from apps.api.core.config import settings
from supabase import Client, create_client

api_key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_ANON_KEY

try:
    supabase: Client = create_client(settings.SUPABASE_URL, api_key)
except Exception:
    supabase = None


def get_supabase() -> Client:
    if supabase is not None:
        return supabase
    key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_ANON_KEY
    return create_client(settings.SUPABASE_URL, key)
