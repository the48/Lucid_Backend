from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from datetime import datetime

from database import Base


class User(Base):
    __tablename__ = "Users"
    
    id = Column(Integer, primary_key = True, index = True, autoincrement = True) 
    email = Column(String(255), unique = True, index = True, nullable = False)
    password_hash = Column(String(255), nullable = False)
    created_on = Column(DateTime, default = datetime.utcnow, nullable = False)

    posts = relationship("Post", back_populates="owner", cascade="all, delete-orphan")



class Post(Base):
    __tablename__ = "Posts"
    id = Column(Integer, primary_key = True, index = True, autoincrement = True)
    text = Column(Text, nullable = False)
    user_id = Column(Integer, ForeignKey("Users.id"), nullable = False)
    created_on = Column(DateTime, default = datetime.utcnow, nullable = False)

    owner = relationship("User", back_populates="posts")