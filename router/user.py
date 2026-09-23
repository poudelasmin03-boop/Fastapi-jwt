from fastapi import APIRouter,FastAPI,Depends,HTTPException,status
from sqlalchemy.orm import Session
from models.user import User
from sechma.user import UserIn,UserOut
from database.db import Base,get_db
from typing import List
app = FastAPI()

router = APIRouter(
  prefix="/user",
  tags=["User"]
)




@router.get("/",response_model=List[UserIn])
async def get_all(db:Session=Depends(get_db)):
  users = db.query(User).all()
  return users


@router.get("/{user_id}")
async def get_user(user_id:int,db:Session=Depends(get_db)):
  user = db.query(User).filter(User.id == user_id).first()
  if not user:
    raise HTTPException(
      status_code=400,
      detail="Not found..."
    )
  return user



@router.post("/",response_model=UserIn)
async def create_user(user:UserIn,db:Session=Depends(get_db)):
  existing_user = db.query(User).filter(User.email == user.email).first()

  if existing_user:
    raise HTTPException(
      status_code=400,
      detail="Email is already exits"

    )

  new_user = User(
    name =user.name,
    email = user.email,
    is_avaliable=True,
    address = user.address
  )

  db.add(new_user)
  db.commit()
  db.refresh(new_user)
  return new_user




@router.delete("/{user_id}")
async def delete_user(user_id:int,db:Session=Depends(get_db)):
  user = db.query(User).filter(User.id==user_id).first()

  if not user:
        raise HTTPException(
          status_code=400,
          detail="user not extis."    
        )
  db.delete(user)
  db.commit()
 
####update the user

@router.put("/{user_id}")
async def update_user(user_id:int,user_data:UserIn,db:Session=Depends(get_db)):
   user = db.query(User).filter(User.id == user_id).first()

   if not user:
           raise HTTPException(
             status_code=400,
             detail="user not extis."    
           )

   user.name = user_data.name
   user.address = user_data.address
   user.email = user_data.email

   db.commit()
   db.refresh(user)

   return{
      "user":user
   }



#### searching by name


@router.get("/")
async def search(user_name:str,db:Session=Depends(get_db)):
   user = db.query(User).filter(User.name == user_name).first()
   if not user:
       raise HTTPException(
                status_code=400,
                detail="User doesn't exists.."    
              )

   return{
      "username":user.name,
      "email":user.email,
      "status":user.is_avaliable,
      "address":user.address,
      "message":"User found.."
   }