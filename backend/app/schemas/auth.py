from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field


class Token(BaseModel):
    access_token: Annotated[str, Field(min_length=1)]
    token_type: Annotated[str, Field(min_length=1)]

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                }
            ]
        }
    )


class TokenData(BaseModel):
    username: Optional[Annotated[str, Field(min_length=3, max_length=30)]] = None

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "username": "john_doe",
                }
            ]
        }
    )
