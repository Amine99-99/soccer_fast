from ..models import User,UserRegister ,UserCreate,UserField,FieldRegister,UserRegisterPlayer
from fastapi import APIRouter,HTTPException
from ..core.debs import session_db
from ..helper_1 import create_user_player, get_user_by_email,create_user,get_active_user,create_token,create_user_field,get_field_by_email,get_active_field
from ..helper_2 import generate_token_verification_token,send_email_of_verification,verify_token
from datetime import timedelta
from ..helper_stat import notify

from ..core.config import settings 


time_veri = settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES


auth=APIRouter()


 
 

@auth.post('/register_player',status_code=201)
def register_player(session:session_db,user_register:UserRegisterPlayer):
     user_db = create_user_player(session=session,user_reg=user_register)
     return user_db
     
 
@auth.post('/register',response_model=User,status_code=201)
def register(session:session_db,user_register:UserRegister):
     user = get_user_by_email(session=session,email=user_register.email)
    
     if user:
          print("User already registred")
          raise HTTPException(
            status_code=400,
            detail='User Already Registred'
        )
     user_create = UserCreate.model_validate(user_register)
     user= create_user(session=session,user_create=user_create)
     return user
@auth.post('/register_field',response_model=UserField,status_code=201)
def register_field(session:session_db,user_field:FieldRegister):
    user = get_field_by_email(session=session,email=user_field.email)
    if user:
          print("User already registred")
          raise HTTPException(
            status_code=400,
            detail='User Already Registred'
        )
    user=create_user_field(session=session,field_create=user_field)
   
    return user


