from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    redis_url: str = "redis://redis:6379"
    option_symbols: str = "AAPL240920C00175000,MSFT240920P00300000"
    poll_sec: int = 30
    risk_free: float = 0.05

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()