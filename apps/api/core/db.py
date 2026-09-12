from supabase import create_client, Client

from apps.api.core.config import settings

try:
    supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
except Exception:
    supabase = None


def get_supabase() -> Client:
    if supabase is not None:
        return supabase
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)

