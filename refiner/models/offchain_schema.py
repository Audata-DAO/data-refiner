from pydantic import BaseModel, Field


class OffChainSchema(BaseModel):
    name: str
    version: str
    description: str
    dialect: str
    # Call it data_schema in order not to override anything
    data_schema: str = Field(alias="schema")
