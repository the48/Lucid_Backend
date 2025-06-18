from sqlalchemy.orm import Session
from typing import Optional, List
from models.user import User, Post
from schemas.user_schemas import UserSignup, PostCreate
from services.auth_service import AuthService
from services.cache_service import cache_service

class UserService:
    @staticmethod
    def create_user(db: Session, user_data: UserSignup) -> User:
        # print(db)
        existing_user = db.query(User).filter(User.email == user_data.email).first()

        if existing_user:
            raise ValueError("Email already registered")
        
        # Hash password and create user
        hashed_password = AuthService.get_password_hash(user_data.password)

        try:
            db_user = User(
                email=user_data.email,
                password_hash = hashed_password
            )
        except Exception as e:
            print(e)
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        
        if not AuthService.verify_password(password, user.password_hash):
            return None
        
        return user
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()
    

    @staticmethod
    def create_post(db: Session, user_id: int, post_data: PostCreate) -> Post:
        try:
            db_post = Post(
                text=post_data,
                user_id=user_id
            )
        except Exception as e:
            print(e)
        
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        
        cache_key = f"user_posts_{user_id}"
        cache_service.delete(cache_key)
        
        return db_post
    
    @staticmethod
    def get_user_posts(db: Session, user_id: int) -> List[Post]:
        cache_key = f"user_posts_{user_id}"
        cached_posts = cache_service.get(cache_key)
        
        if cached_posts is not None:
            return cached_posts
        
        posts = db.query(Post).filter(Post.user_id == user_id).order_by(Post.created_on.desc()).all()
        cache_service.set(cache_key, posts, ttl_minutes=5)
        
        return posts
    

    @staticmethod
    def delete_post(db: Session, user_id: int, post_id: int) -> bool:      
        post = db.query(Post).filter(
            Post.id == post_id,
            Post.user_id == user_id
        ).first()
        
        if not post:
            return False
        
        db.delete(post)
        db.commit()
        
        cache_key = f"user_posts_{user_id}"
        cache_service.delete(cache_key)
        
        return True
    
    @staticmethod
    def get_post_by_id(db: Session, post_id: int, user_id: int) -> Optional[Post]:
        return db.query(Post).filter(
            Post.id == post_id,
            Post.user_id == user_id
        ).first()