from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Global settings configuration using environment variables"""

    INPUT_DIR: str = "/input"
    OUTPUT_DIR: str = "/output"
    REFINEMENT_ENCRYPTION_KEY: str
    SCHEMA_VERSION: str = "0.0.1"
    SCHEMA_NAME: str = "Audata Schema"
    SCHEMA_DESCRIPTION: str = "Audata Schema"
    SCHEMA_DIALECT: str = "sqlite"
    PINATA_API_KEY: str
    PINATA_API_SECRET: str
    PINATA_GATEWAY: str

    class Config:
        env_file = ".env"


settings = Settings()  # type: ignore
