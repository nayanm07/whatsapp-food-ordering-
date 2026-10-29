from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    WHATSAPP_VERIFY_TOKEN: str
    OPENAI_API_KEY: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440  # 24 hours

    class Config:
        env_file = ".env"


settings = Settings()
