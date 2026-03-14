from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ==========================
    # APP
    # ==========================
    APP_NAME: str = "Life Signify NumAI SaaS"
    ENGINE_VERSION: str = "1.0.0"

    # ==========================
    # DATABASE
    # ==========================
    DATABASE_URL: str

    # ==========================
    # JWT
    # ==========================
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ==========================
    # AZURE OPENAI
    # ==========================
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_API_VERSION: str = "2024-02-15-preview"
    AZURE_OPENAI_DEPLOYMENT: str

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        extra="ignore",
    )


settings = Settings()
