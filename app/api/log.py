from ..helper_1 import authenticate_user,create_token,create_picture_profile
from ..models import User ,UserRegister,Token,UserPublic,TokenBase,UserField,UserFieldPublic,PictureProfile,PictureProfileDB
from ..core.debs import session_db,create_access_token ,get_current_active_user
from fastapi import APIRouter ,Depends,HTTPException,UploadFile,File
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from datetime import datetime,timedelta,timezone
from ..core.config import settings 
import uuid 
from sqlmodel import select
from fastapi.staticfiles import StaticFiles
from ..profile_service import MyProfile




auth = APIRouter()
time_set = settings.ACCESS_TOKEN_EXPIRE_MINUTES




my_profile =MyProfile()




@auth.post('/token')
def log(session:session_db,form_data:Annotated[ OAuth2PasswordRequestForm,Depends()])->Token:
    password= form_data.password
    print('pa',password)
    username=form_data.username 
    print('username',username)
    user = authenticate_user(session=session,username=username,password=password)

    print('user_log',user,'user_hashed in db')
    
    if not user :
        raise HTTPException(
            status_code=404,
            detail='Invalid credentials'
        )
    if isinstance(user,User):
        user_type='regular'
        session.query(TokenBase).filter(TokenBase.user_id==user.id).delete()
    elif isinstance(user,UserField):
        user_type='field'
        session.query(TokenBase).filter(TokenBase.user_field_id==user.id).delete()
   
   
    session.commit()
    time_expire_token = timedelta(minutes=time_set) 
    token_access = create_access_token(data={'sub':str(user.id)},user_type=user_type,time_expire=time_expire_token)
    print('id',user.id)
    print('token_access',token_access)
    
    create_token(session=session,token=Token(token_access=token_access,token_type='bearer'),user=user)
    return Token(token_access=token_access,token_type='bearer')

@auth.get('/user_me',response_model=UserPublic|UserFieldPublic,status_code=200)
def get_current_user(current_profile:Annotated[User|UserField,Depends(get_current_active_user)]):
    return my_profile.get_my_profile(current_profile=current_profile)
@auth.get('/authenticate',status_code=200)
def authenticate_me(user:Annotated[User|UserField,Depends(get_current_active_user)]):
    if user:
        return {
            'is_authenticated':True
        }
    return {
        'is_authenticated':False
    }

@auth.post('/logout',status_code=200)
def log_out(user:Annotated[User|UserField,Depends(get_current_active_user)],session:session_db):
    if isinstance(user,User):
       print(user.register_as,user)
       token_db =session.exec(select(TokenBase).where(TokenBase.user_id==user.id)).first()
       print('token_1',token_db)
       if token_db:
           session.delete(token_db)
           session.commit()
           token_check = session.exec(select(TokenBase).where(TokenBase.user_id== user.id)).first()
          
           print('deleted_1',token_check)
           print("Returning success message for User", user.register_as)
           return {
            'message':'Successfully Logged out'
           }
    elif isinstance(user,UserField):
         print(user.register_as,user)
         token_db =session.exec(select(TokenBase).where(TokenBase.user_field_id==user.id)).first()
         print('token_2',token_db)
         if token_db:
           session.delete(token_db)
           session.commit()
           token_check = session.exec(select(TokenBase).where(TokenBase.user_field_id== user.id)).first()
           print('deleted_2',token_check)
           print("Returning success message for UserField", user.register_as)
           return {
            'message':'Successfully Logged out'
           }


@auth.post('/upload_pic',status_code=201)
async def upload_photo(image:Annotated[UploadFile,File()],session:session_db,user:Annotated[User|UserField,Depends(get_current_active_user)]):
    if isinstance(user,User):
        session.query(PictureProfileDB).filter(PictureProfileDB.user_id==user.id).delete()
    if isinstance(user,UserField):
        session.query(PictureProfileDB).filter(PictureProfileDB.user_field_id==user.id).delete()
    session.commit()
    
    picture_db = await create_picture_profile(image=image,session=session,user=user)
    if not picture_db:
        raise HTTPException(
            status_code=401,
            detail='picture invalid'
        )
    return picture_db
@auth.get('/pic',status_code=200)
def get_pic(session:session_db,user:Annotated[User|UserField,Depends(get_current_active_user)]):
    print('user',user)
    result={}
    base_url='http://localhost:8000'
    if isinstance(user,User):
        statement = select(PictureProfileDB).where(PictureProfileDB.user_id==user.id)
        pic_profile = session.exec(statement).first()
        
    elif isinstance(user,UserField):
         statement = select(PictureProfileDB).where(PictureProfileDB.user_field_id==user.id)
         pic_profile = session.exec(statement).first()
    print('pict',pic_profile)
    print('user',user)
    if not pic_profile:
        return None
    id= pic_profile.id
    file_name = pic_profile.file.split('/')[-1]
    full_url = f"{base_url}/uploads/{file_name}"
    result.update({'file':full_url,'id':id})

    return result




    




    
    