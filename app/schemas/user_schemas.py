from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional
from datetime import datetime
import re

class UserSignup(BaseModel):
    email: EmailStr = Field(..., description = "Valid email address")
    password: str = Field(
        ..., 
        min_length = 8, 
        max_length = 48,
        description = "Password must be 8 to 48 characters long"
    )
    
    @validator('password')
    def validate_password(cls, v):
        """
        RegEx patterns that enforce the password policy
        """
        if not re.search(r"[A-Z]", v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r"[a-z]", v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r"\d", v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError('Password must contain at least one special character')
        return v


class UserLogin(BaseModel):
    email: EmailStr = Field(..., description = "Valid email address")
    password: str = Field(..., min_length=1, description = "User password")


class PostCreate(BaseModel):
    text: str = Field(
        ..., 
        min_length = 1, 
        max_length = 1000000,
        description = "Post text content"
    )
    
    @validator('text')
    def validate_text_size(cls, v):
        text_bytes = len(v.encode('utf-8'))
        if text_bytes > 1024 * 1024:
            raise ValueError('Post text cannot exceed 1MB')
        return v


class PostDelete(BaseModel):
    postID: int = Field(..., gt = 0, description = "Valid post ID greater than 0")


class TokenResponse(BaseModel):
    access_token: str = Field(..., description = "JWT access token")
    token_type: str = Field(default = "bearer", description = "Token type")


class PostResponse(BaseModel):
    id: int = Field(..., description = "Post ID")
    text: str = Field(..., description = "Post content")
    created_on: datetime = Field(..., description = "Post creation timestamp")
    user_id: int = Field(..., description = "User ID who created the post")
    
    class Config:
        from_attributes = True


class PostCreateResponse(BaseModel):
    postID: int = Field(..., description="ID of the created post")
    message: str = Field(default="Post created successfully", description="Success message")


class UserCreatedResponse(BaseModel):
    message: str = Field(default="User created successfully", description="Success message")


class PostsListResponse(BaseModel):
    posts: List[PostResponse] = Field(..., description="List of user posts")
    total_count: int = Field(..., description="Total number of posts")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")