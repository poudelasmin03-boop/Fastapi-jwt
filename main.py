from fastapi import FastAPI,HTTPException,Depends,Header
import os
from jose import jwt,JWTError
##jose is stands javascripys objects signature encrpition

from datetime import datetime,timedelta,timezone
from models.user import User
from database.db import  get_db,Base,engine
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from passlib.context import CryptContext
import secrets
app = FastAPI()


Base.metadata.create_all(bind=engine)

###t Run     uv run python -c "import secrets; print(secrets.token_urlsafe(64))"


SECRET_KEY = ("uMsJmEtwdCqmRHBgjdPBIQEDox-c73vVtzBjHejDrDF7Lt-DKUpH_1_zNUrA-V56R-9erPYxvwOcLPL7s_8sMQ")
print("SECRET KEY LOADED:", SECRET_KEY is not None)
ALGORITHM = "HS256" 

ACCESS_TOKEN_EXPIRE_TIME_MINUTES = 15

REFRESH_TOKEN_EXPIRE_TIME_DAYS=7

oAuth_scheme = OAuth2PasswordBearer(
  tokenUrl="/login"
)

pwd_context =CryptContext(
  schemes = ["argon2"],
  deprecated ="auto"
)
def create_access_token(data:dict):
  to_encode =data.copy()
  ###expire date
  expire = datetime.now(
    timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_TIME_MINUTES)

  to_encode.update({
    "exp":expire,
    "type":"access"

    }
  )


  # jwt token is create
  token = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)

  return token

def create_refresh_token(data:dict):
  to_encode =data.copy()
  ###expire date
  expire = datetime.now(
    timezone.utc) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_TIME_DAYS)

   ### unique id for a refresh token
  uuid = secrets.token_urlsafe(32) 

  to_encode.update({
    "exp":expire,
    "type":"refresh"

    }
  )

  # jwt token is create
  token = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)

  return token



###  register api
@app.post("/register")
async def register(
  username:str,

  email:str,
  password:str,
  db:Session=Depends(get_db)
):
  existing_user =db.query(User).filter(User.username == username).first()

  if existing_user:
    raise HTTPException(
      status_code=400,
      detail="Username already exists..."
    )
  hashed_password =pwd_context.hash(password)


  user = User(
    username = username,
    email = email,
    password = hashed_password,
  )

  db.add(user)
  db.commit()
  db.refresh(user)

  return{
    "message":"User registered successfully..",
    "user_id":user.id,
    "username":user.username
  }


# login api/  
@app.post("/login")
async def login(
  form_data:OAuth2PasswordRequestForm=Depends(),
  db:Session = Depends(get_db)
):

  username = form_data.username
  password = form_data.password
  user = db.query(User).filter(User.username== username).first()

  if user is None:
    raise HTTPException(
      status_code=401,
      detail="Invalid username"
    )

  if not pwd_context.verify(password,user.password):
    raise HTTPException(
      status_code=401,
      detail = "Invalid password.."
    )

  access_token = create_access_token({
   "user_id":user.id,
   "username":user.username,
   "type":"access"
  })

  # refresh_token = create_refresh_token({
  #    "user_id":user.id,
  #     "username":user.username,
  #     "type":"refresh"
  # })

  return{
    "access_token":access_token,
    # "refresh_token":refresh_token,
    "token_type":"bearer"
  }
  


### bear means token proof authentication
def get_current_user(token:str=Depends(oAuth_scheme)):
  credentials = HTTPException(
    status_code=404,
    detail= "Could not valid credentail"
  )

  #simple server saying the user beerertoke
  header ={
    "WWW-Authenticate":"Bearer.."
    }

  try:
    payload = jwt.decode(
      token,
      SECRET_KEY,
      algorithms=[ALGORITHM]
   )
    username :str=payload.get("username")
    if username is None:
      raise credentials

    if token in blacklisted_token:
      raise HTTPException(
        status_code=401,
        details = "token has been failed"
      )

  except JWTError:
    raise credentials

  return  {
    "username":username,
  }


####  =======verify token========

###protect route

@app.get("/dashboard")
def dashboard  (current_user:dict =Depends(get_current_user)):
  return (
    {
      "message":"welcome to our page",
      "user":f"hello {current_user['username']}"
    }
  )


### server reject it even id someone still has a copy    
blacklisted_token = set()

###### loagout
@app.post("/logout")

def logout(token:str=Depends(oAuth_scheme)):
  blacklisted_token.add(token)
  return {"message": "Logged out successfully"}

