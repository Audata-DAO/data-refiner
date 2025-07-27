from pydantic import BaseModel, Field


class User(BaseModel):
    user_id: str
    age: int = Field(ge=0)
    country_code: str = Field(max_length=2)
    occupation: str = Field(max_length=30)
    language_code: str = Field(max_length=10)
    region: str = Field(max_length=100)


class Audio(BaseModel):
    audio_length: int
    audio_source: str = Field(max_length=10)
    audio_type: str = Field(max_length=10)
    user: User
