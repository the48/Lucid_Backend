from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

from database import get_db
from schemas.user_schemas import (
    UserSignup, UserLogin, PostCreate, PostDelete,
    TokenResponse, PostResponse, PostCreateResponse, PostsListResponse, ErrorResponse, UserCreatedResponse
)
from services.user_service import UserService
from services.auth_service import AuthService
from dependencies.auth_dependencies import get_current_user, verify_token_dependency, get_current_user1
from models.user import User
from utilities.validators import PayloadValidator

router = APIRouter(prefix="/api", tags=["users"])

@router.post("/signup", response_model=UserCreatedResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserSignup,
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        PayloadValidator.validate_payload_size(await request.body(), max_size_mb = 1.0)
        
        post = UserService.create_user(db, user_data)
        
        return UserCreatedResponse(
            message = f"User {user_data.email} successfully"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while creating post"
        )

@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    try:
        user = UserService.authenticate_user(db, login_data.email, login_data.password)
        if not user:
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Invalid email or password"
            )

        access_token = AuthService.create_access_token(data={"sub": user.email})

        return TokenResponse(
            access_token=access_token,
            token_type="bearer"
        )

    except HTTPException:
        raise
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error occurred during login"
        )

@router.post("/posts", response_model=PostCreateResponse, status_code=status.HTTP_201_CREATED)
async def add_post(
    post_data: PostCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user1)
):
    try:
        PayloadValidator.validate_payload_size(await request.body(), max_size_mb=1.0)

        post = UserService.create_post(db, current_user.id, post_data.text)

        return PostCreateResponse(
            postID=post.id,
            message="Post created successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error occurred while creating post"
        )


@router.get("/posts", response_model=PostsListResponse)
async def get_posts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user1)
):
    try:
        posts = UserService.get_user_posts(db, current_user.id)
        
        post_responses = [
            PostResponse(
                id=post.id,
                text=post.text,
                created_on=post.created_on,
                user_id=post.user_id
            )
            for post in posts
        ]
        
        return PostsListResponse(
            posts=post_responses,
            total_count = len(post_responses)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error occurred while retrieving posts"
        )

@router.delete("/posts", status_code=status.HTTP_200_OK)
async def delete_post(
    post_data: PostDelete,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user1)
):
    try:
        PayloadValidator.validate_payload_size(await request.body(), max_size_mb=1.0)
        
        deleted = UserService.delete_post(db, current_user.id, post_data.postID)
        
        if not deleted:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "Post not found or you don't have permission to delete it"
            )
        
        return {"message": "Post deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error occurred while deleting post"
        )