from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://cortex:cortex_dev@localhost:5432/cortex_dev"
    redis_url: str = "redis://localhost:6379/0"
    clerk_secret_key: str = ""
    clerk_jwks_url: str = "https://api.clerk.com/v1/jwks"

    class Config:
        env_file = ".env"


def get_settings() -> Settings:
    return Settings()
