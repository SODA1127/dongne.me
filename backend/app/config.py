from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str
    gemini_api_key: str
    resend_api_key: str
    from_email: str = "briefing@dongne.me"
    weather_api_key: str
    naver_client_id: str
    naver_client_secret: str
    localdata_api_key: str
    kakao_channel_id: str = ""
    app_url: str = "https://dongne.me"
    admin_secret: str
    tz: str = "Asia/Seoul"


settings = Settings()
