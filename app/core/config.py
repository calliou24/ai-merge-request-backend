from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "ai-merge-request"
    ENV: str = "env"
    DSN: str = "postgresql+asyncpg://postgres:password@localhost:4406/mydb"

    OPEN_ROUTER_API_KEY: str = ""
    CEREBRAS_API_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf_8",
        case_sensitive=False,
    )

    @property
    def alembic_url(self) -> str:
        # Prefer explicit sync DSN; otherwise convert async -> psycopg

        return self.DSN.replace("+asyncpg", "+psycopg").replace("+aiopg", "+psycopg")


settings = Settings()
