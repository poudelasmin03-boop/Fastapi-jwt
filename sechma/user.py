from sqlalchemy import create_engine
from pydantic import Field,BaseModel,EmailStr

class  Create_user(BaseModel):
  username:str
  email:EmailStr
  password:str
 

