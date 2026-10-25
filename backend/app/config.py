from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    elexon_base_url: str = "https://data.elexon.co.uk/bmrs/api/v1"
    cors_origin: str = "*"
    request_timeout: float = 30.0
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
