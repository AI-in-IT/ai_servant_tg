from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT_TOKEN: str
    BASE_URL_BACKEND: str
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
