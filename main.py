from fastapi import FastAPI,HTTPException,Depends,Header

from jose import jwt
##jose is stands javascripys objects signature encrpition

from datetime import datetime,timedelta,timezone
from models.user import User
from database.db import  get_db,Base,engine
from sqlalchemy.orm import Session

from passlib.context import CryptContext
app = FastAPI()


Base.metadata.create_all(bind=engine)
SECRET_KEY ="my_secret" 

ALGORITHM = "HS256" 


pwd_context =CryptContext(
  schemes = ["argon2"],
  deprecated ="auto"
)
def create_token(data:dict):
  to_encode =data.copy()
  ###expire date
  expire = datetime.now(
    timezone.utc) + timedelta(days=2)

  to_encode.update({
    "exp":expire}
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
### token   
@app.post("/login")
async def login(
  username:str,
  password:str,
  db:Session = Depends(get_db)
):
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

  token = create_token({
   "user_id":user.id,
   "username":user.username
  })

  return{
    "access_token":token,
    "token_type":"bearer"
  }
  

####  =======verify token========
def verify_token(token:str=Header(None)):
  try:
     payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])

     return payload
  
  except:
    raise HTTPException(
      status_code=401,
      detail="Invalid or expired token"
    )



###protect route

@app.get("/dashboard")
def dashboard  (user =Depends(verify_token)):
  return (
    {
      "message":"welcome to our page",
      "user":user["username"]
    }
  )

    
