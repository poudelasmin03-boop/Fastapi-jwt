from database.db import Base
from sqlalchemy import Column,String,Integer,Boolean,Float
 
class User(Base):
  __tablename__ = "Userdetails"

  id =Column(Integer,primary_key=True,autoincrement=True)

  username = Column(String(100),nullable=False)

  email =Column(String(200),nullable=False)

  password = Column(String(100),nullable=False)
  
