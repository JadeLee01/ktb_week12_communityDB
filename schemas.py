# schemas.py

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import List

class SignUpIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length = 8, max_length = 20)
    nickname: str = Field(min_length = 1, max_length = 10)

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    nickname: str
    createdAt: datetime

class UserUpdate(BaseModel):
    nickname: str = Field(min_length = 1, max_length = 10)

class PostCreate(BaseModel):
    title: str = Field(min_length = 1, max_length = 26)
    body: str  = Field(min_length = 5, max_length = 20_000)

class PostOut(BaseModel):
    id: int
    title: str
    body: str
    authorId: int
    createdAt: datetime
    updatedAt: datetime
    views: int = 0
    likesCount: int = 0
    commentsCount: int = 0

class CommentCreate(BaseModel):
    text: str = Field(min_length = 1, max_length = 1000)

class CommentOut(BaseModel):
    id: int
    postId: int
    authorId: int
    text: str
    createdAt: datetime
    updatedAt: datetime

class PasswordChangeIn(BaseModel):
    currentPassword: str
    newPassword: str = Field(min_length = 8, max_length = 20)