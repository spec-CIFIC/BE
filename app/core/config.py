from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DATABASE_URL: str
    SUPABASE_URL: str

    # SQLAlchemy가 실행 SQL·파라미터를 콘솔에 출력할지 여부.
    # 기본 False(조용). 쿼리 디버깅이 필요할 때만 .env에 SQL_ECHO=true.
    SQL_ECHO: bool = False


settings = Settings()
