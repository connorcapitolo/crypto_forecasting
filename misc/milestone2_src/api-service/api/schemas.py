from typing import Optional
from pydantic import BaseModel, Field
from fastapi import Query


class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class Profile(BaseModel):
    username: str
    full_name: Optional[str] = None
    github_username: Optional[str] = None
    twitter_handle: Optional[str] = None
    research_interests: Optional[str] = None
    account_type: Optional[str] = None


class Account(BaseModel):
    username: str
    email: Optional[str] = None


class AccountUpdate(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None


class ResetPassword(BaseModel):
    email: str


class Token(BaseModel):
    access_token: str = Field(..., description="The access token")
    token_type: str = Field("bearer", description="Type type of access token")
    expires_in: int = Field(
        30 * 24 * 60 * 60, description="The amount of seconds the token remains valid")
    refresh_token: str = Field(..., description="The refresh token")


class TokenData(BaseModel):
    username: Optional[str] = None


class Pagination:
    page_number: int
    page_size: int

    def __init__(self, page_num: int = Query(0, ge=0, description="Page number"), page_size: int = Query(20, gt=0, le=100, description="Number of results per page")):
        self.page_number = page_num
        self.page_size = page_size
