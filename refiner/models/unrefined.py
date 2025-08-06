from pydantic import BaseModel, Field


class User(BaseModel):
    wallet_address: str
    birth_year: int = Field(ge=1900)
    birth_month: str
    occupation: str = Field(max_length=30)
    country: str
    region: str


class Audio(BaseModel):
    language_code: str = Field(max_length=10)
    audio_length: int
    audio_source: str = Field(max_length=10)
    audio_type: str = Field(max_length=10)
    user: User
    raw_data: bytes
