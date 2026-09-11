from .core.debs import session_db 
from .models import User,UserCreate,Token,TokenBase,UserField,FieldRegister,PictureProfileDB,PictureProfile,Player,UserRegisterPlayer
from sqlmodel import select
from .core.security import hash_password,hash_token,verify_password
import uuid

from datetime import time
from enum import Enum
import json
from fastapi import HTTPException,UploadFile
from .models import ParentRegister
import os
from .helper_stat import notify






def get_user_by_email(*,session:session_db,email:str)->User:
    statement = select(User).where(User.email == email )

    user_db = session.exec(statement).first()
    return user_db

def get_user_by_username(*,session:session_db,username:str)->User|UserField:
    statement = select(User).where((User.username == username))
    statement_1= select(UserField).where(UserField.username==username)
    user_db = session.exec(statement).first()
    if user_db:
        print('name',user_db.username)
    user_field = session.exec(statement_1).first()
    if user_field:
        print('name_f',user_field.username)
    if user_db:
        return user_db
    elif user_field:
        return user_field

def get_active_user(*,session:session_db,email:str)->User:
    statement = select(User).where((User.email == email)& (User.is_active==False) )
    user_db = session.exec(statement).first()
    return user_db
    

def create_user(*,session:session_db,user_create:UserCreate)->User:
    
    user_db = User.model_validate(user_create,update={'hashed_password':hash_password(user_create.password),'is_active':True})
    
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return user_db 
def create_user_player(session:session_db,user_reg:UserRegisterPlayer)->User:
    print(user_reg.username)
    user_registred =get_active_user(session=session,email=user_reg.email)
    if user_registred:
          print("User already registred")
          raise HTTPException(
            status_code=400,
            detail='User Already Registred'
        )
    user_create = UserCreate.model_validate(user_reg)
    user_db = User.model_validate(user_create,update={'hashed_password':hash_password(user_create.password),'is_active':True})
    
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    if user_db is not None and user_db.id:
         print('user_id',user_db.id)
         player= Player(player_status='non_active',name=user_db.username,phone=user_db.phone,position=user_reg.position,user_id=user_db.id)
         session.add(player)
         session.commit()
         session.refresh(player)
         print(player.id,'player_id')

    return user_db

   


def get_field_by_email(*,session:session_db,email:str)->UserField:
    statement = select(UserField).where(UserField.email==email) 
    user_db = session.exec(statement).first()
    return user_db
def get_active_field(*,session:session_db,email:str)->UserField:
    statement = select(UserField).where((UserField.email==email) & (UserField.is_active==False))
    user_db = session.exec(statement).first()
    return user_db


def create_user_field(*, session: session_db, field_create: FieldRegister) -> UserField:
    user_admin = session.exec(select(User).where(User.register_as=='admin')).first()
    passw= field_create.password
    print(passw,'password')
    hashy = hash_password(passw)
    print('hhh',hashy)
    

    user_db = UserField.model_validate(field_create,update={
        "hashed_password":hashy,'is_active':True
    })
    session.add(user_db)
    session.flush()
    notify(session=session,user_id=str(user_admin.id),sender_id=str(user_db.id),type=f'Field owner registring his user account',ref_id=str(user_db.id),read=False)
    session.commit()
    
    return user_db


def authenticate_user(*,session:session_db,username:str,password:str)->User|UserField:
    password=password
    print('pass',password)
    username=username
    print('usern',username)
    user = get_user_by_username(session=session,username=username) 
    if isinstance(user,UserField):
        print(user.status,'status')
        if not user.status =='approved account':
                raise HTTPException(
                        status_code=401,
                        detail='Your Account not active'
            
                    )
    print(user.username,'auth')
    print('verify',verify_password(password,user.hashed_password))
    if not user:
        raise HTTPException(
            status_code=401,
            detail='username'

        )
    
     
    if not verify_password(password,user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail='Invalid password'
        )
    return user

def  create_token(*,session:session_db,user:User|UserField,token:Token)->TokenBase:
    if isinstance(user,User):
        
        token_db = TokenBase.model_validate(token,update={
       'user_field_id':None,
         
        'user_id':user.id,
       'hashed_token':hash_token(token.token_access)

    })
    elif isinstance(user,UserField):
          token_db = TokenBase.model_validate(token,update={
        'user_field_id':user.id,
        'user_id':None,
         
      
       'hashed_token':hash_token(token.token_access)

    })
  
    session.add(token_db)
    session.commit()
    session.refresh(token_db)
    return token_db

async def create_picture_profile(image:UploadFile,session:session_db,user:UserField|User)->PictureProfileDB:
    filename=f"{uuid.uuid4()}_{image.filename}"
    file_path=f"./uploads/{filename}"
    os.makedirs('./uploads',exist_ok=True)
    with open(file_path,'wb') as f:
        f.write(await image.read())
        if isinstance(user,User):
            pic_db = PictureProfileDB(file=file_path, user_id=user.id, user_field_id=None)
      
        elif isinstance(user,UserField):
            pic_db = PictureProfileDB(file=file_path, user_id=None, user_field_id=user.id)
       
    
    session.add(pic_db)
    session.commit()
    session.refresh(pic_db)
    return pic_db



def register_parent(session:session_db,parent:ParentRegister):
    parent_exist = get_user_by_email(session=session,email=parent.email)
    if parent_exist:
        raise HTTPException(
            status_code=400,
            detail='Parent Already Registered'
        )
    new_parent = User(username=parent.username,email=parent.email,phone=parent.phone,city=parent.city,country=parent.country,
                      post_code=parent.post_code,register_as=parent.register_as,
                      hashed_password=hash_password(parent.password),address=parent.address,is_active=True)
    
    
  
    return new_parent










    
