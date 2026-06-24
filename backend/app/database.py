from __future__ import annotations

from functools import lru_cache

from supabase import Client, create_client

from app.config import settings


@lru_cache(maxsize=1)
def get_client() -> Client:
    """Return a service-role Supabase client (backend-only, full access)."""
    return create_client(settings.supabase_url, settings.supabase_service_role_key)


@lru_cache(maxsize=1)
def get_anon_client() -> Client:
    """Return an anon-key Supabase client (public, RLS-restricted)."""
    return create_client(settings.supabase_url, settings.supabase_anon_key)
