from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Global settings configuration using environment variables"""

    INPUT_DIR: str = "/input"
    OUTPUT_DIR: str = "/output"
    REFINEMENT_ENCRYPTION_KEY: str
    SCHEMA_VERSION: str = "0.0.1"
    SCHEMA_NAME: str = "Test Schema 20250727"
    SCHEMA_DESCRIPTION: str = "Test Schema Description"
    SCHEMA_DIALECT: str = "sqlite"
    STORJ_ACCESS_KEY: str
    STORJ_SECRET_KEY: str
    STORJ_BUCKET_NAME: str = "my-bucket"
    STORJ_GATEWAY_URL: str = "https://gateway.storjshare.io/"

    class Config:
        env_file = ".env"


settings = Settings()  # type: ignore
