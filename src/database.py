from __future__ import annotations
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship, sessionmaker, declarative_base, scoped_session
from datetime import datetime
from typing import List, Optional, Dict, Literal
import numpy as np
from pydantic import BaseModel, constr
import json
import os
from copy import copy

Base = declarative_base()

# SQLAlchemy models
class UserModel(Base):
    
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    
    # Relationship with GameModel
    games = relationship("GameModel", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self) -> None:
        return (
            f"User: {self.name}\n"
            f"\tNr. of games played: {len(self.games)}\n"
        )

class GameModel(Base):
    
    __tablename__ = 'games'
    
    id = Column(Integer, primary_key=True, index=True)
    
    timestamp = Column(DateTime)
    time_axis = Column(String)  # Stored as JSON string in SQLite
    left_force = Column(String)  # Stored as JSON string in SQLite
    right_force = Column(String)  # Stored as JSON string in SQLite
    left_force_target = Column(String)  # Stored as JSON string in SQLite
    right_force_target = Column(String)  # Stored as JSON string in SQLite
    left_error = Column(Float)
    right_error = Column(Float)
    left_instability = Column(Float)
    right_instability = Column(Float)
    
    # Relationship with UserModel
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("UserModel", back_populates="games")
    
    def __init__(self, 
        time_axis: np.ndarray,
        left_force: np.ndarray, 
        right_force: np.ndarray,
        left_force_target: np.ndarray, 
        right_force_target: np.ndarray,
        left_error: float,
        right_error: float,
        left_instability: float,
        right_instability: float,
        user_id: int
    ):

        self.timestamp = datetime.now()
        self.time_axis = json.dumps(time_axis.tolist())
        self.left_force = json.dumps(left_force.tolist())
        self.right_force = json.dumps(right_force.tolist())
        self.left_force_target = json.dumps(left_force_target.tolist())
        self.right_force_target = json.dumps(right_force_target.tolist())
        self.left_error = left_error
        self.right_error = right_error
        self.left_instability = left_instability
        self.right_instability = right_instability
        self.user_id = user_id
    
    def __repr__(self) -> str:
        return (
            f"Game played {self.timestamp.strftime('%H:%M:%S - %d.%m.%y')}\n"
        )
    
# Pydantic models for type checking and validation
class User(BaseModel):

    name: str

    class Config:
        from_attributes = True

class Game(BaseModel):

    time_axis: np.ndarray
    left_force: np.ndarray
    right_force: np.ndarray
    left_force_target: np.ndarray
    right_force_target: np.ndarray
    left_error: float
    right_error: float
    left_instability: float
    right_instability: float

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True



class DatabaseHandler:
    def __init__(self, database_name: str) -> None:
        
        self.engine = create_engine(f'sqlite:///database/{database_name}.db')
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)
        
        self.sessions = {
            "add_user" : self.Session(),
            "add_game" : self.Session(),
            "fetch_users" : self.Session(),
            "fetch_user_games" : self.Session(),
            "search" : self.Session(),
            "delete_user" : self.Session(),
            "fetch_all_games" : self.Session()
        }
                
        if not os.path.exists(f"database/{database_name}.db"):
            Base.metadata.create_all(self.engine)

    def add_user(self, name: str):
        session = self.sessions["add_user"]
        new_user = UserModel(
            name = name,
            games = []
        )
        session.add(new_user)
        session.commit()

    def fetch_users(self) -> List[UserModel]:
        session = self.sessions["fetch_users"]
        users = session.query(UserModel).all()
        return users

    def add_game_to_user(self, 
        user_id: int, 
        game: Game.dict
        ) -> None:
        
        session = self.sessions["add_game"]
        
        # Retrieve the user from the database
        user = session.query(UserModel).filter(UserModel.id == user_id).first()

        if user:
            # Create a new GameModel instance
            new_game = GameModel(**game, user_id = user_id)

            # Add the game to the user's games list
            user.games.append(new_game)

            # Commit the changes to the database
            session.commit()

            return True
        else:
            # User with the given ID does not exist
            return False
    
    def fetch_user_games(self, user_id: int):
        
        session = self.sessions["fetch_user_games"]
        user = session.query(UserModel).filter(UserModel.id == user_id).first()
        
        if user:
            return user.games
        else:
            return None
    
    def fetch_all_games(self):
        
        session = self.sessions["fetch_all_games"]
        games = session.query(UserModel).all()
        
        return games

    def search_users(self, username: str = None) -> List[UserModel]:
        session = self.sessions["search"]
        query = session.query(UserModel).filter(UserModel.name.like(f'%{username}%'))

        if username:
            # Filter users whose username contains the provided string
            query = query.filter(UserModel.name.like(f'%{username}%'))

        users = query.all()
        return users

    def delete_user(self, user_id):
        
        session = self.sessions["delete_user"]
        # Retrieve the user object from the database
        user = session.query(UserModel).filter(UserModel.id == user_id).first()

        if user:
            # Delete the user object
            session.delete(user)
            
            # Commit the transaction to persist the changes to the database
            session.commit()