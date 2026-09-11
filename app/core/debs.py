from sqlmodel import Session,select
from .db import engine
from typing import Annotated
from fastapi import Depends,HTTPException,status
import jwt
from datetime import datetime,timedelta,timezone
from .config import settings
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from ..models import User,TokenData,UserPublic,TokenBase,UserField
from uuid import UUID



time_set = settings.ACCESS_TOKEN_EXPIRE_MINUTES
secret_key = settings.SECRET_KEY
ALGORITHM = "HS256"


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
print('f',oauth2_scheme.__dict__)


def get_db():
    with Session(engine) as session:
        yield session


session_db = Annotated[Session,Depends(get_db)]


def create_access_token(data:dict,user_type:str,time_expire:timedelta|None=None):
    obj_token = data.copy()
    if time_expire:
        time_token = datetime.now(timezone.utc) + time_expire
    else:
        time_token = datetime.now(timezone.utc) + timedelta(minutes=60*12)
    obj_token.update({'exp':time_token.timestamp(),'user_type':user_type})
    tok = jwt.encode(obj_token,secret_key,algorithm=ALGORITHM)
    print('tok',tok)
    return tok 
def get_current_user(session:session_db,token:Annotated[str,Depends(oauth2_scheme)])->User|UserField:

    try:
        payload = jwt.decode(token,secret_key,algorithms=[ALGORITHM])
        print('dict',payload)
        print('token',token)

        user_id = payload.get('sub')
        user_type= payload.get('user_type')
        print(user_id,'id')
        if user_id is None:
            raise  HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
        token_data = TokenData(user_id=user_id)
    except InvalidTokenError:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if user_type=='regular':
        user = session.get(User,UUID(token_data.user_id))
        print('user',user)
    elif user_type=='field':
        user = session.get(UserField,UUID(token_data.user_id))
    if user is None  :
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    print('user deb',user)
    return user
   
def get_current_active_user(session:session_db,current_user:Annotated[User|UserField,Depends(get_current_user)])->User|UserField:
    if not current_user.is_active :
        raise HTTPException(
            status_code=403,
            detail='User Inactive'
        )
    if isinstance(current_user,User):
        token_db = session.exec(select(TokenBase).where(TokenBase.user_id==current_user.id)).first()
        print('active?',token_db.is_active)
        if not token_db or not token_db.is_active:
          raise HTTPException(
               status_code=408,
               detail='User is Logged out'

    )
        print('current_use is',current_user)
        return current_user
    elif isinstance(current_user,UserField):
        token_db_1 = session.exec(select(TokenBase).where(TokenBase.user_field_id==current_user.id)).first()
        print('active?',token_db_1.is_active)
        if not token_db_1 or not token_db_1.is_active:
          raise HTTPException(
               status_code=408,
               detail='User is Logged out')
   

      
        return current_user 
    
def get_courts_registred(session:session_db,user:Annotated[UserField,Depends(get_current_active_user)])->UserField:
    if not isinstance(user,UserField):
           raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Unauthorized user'

        )
    print('user.id',user.id)
    user_ = session.get(UserField,user.id)
    print('user_',user_)
    if not user_:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Unauthorized user'

        )
   
        
    return user_

def get_admin_registered(session:session_db,user:Annotated[User,Depends(get_current_active_user)])->User:
    if not isinstance(user,User):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Unauthorized user'

        )
    user = session.get(User,user.id) 
    if not user and not user.register_as =='admin':
          raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Unauthorized user'

        )
    return user


def get_provider(session:session_db,user:Annotated[User,Depends(get_current_active_user)])->User:
    if not isinstance(user,User):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Unauthorized user'

        )
    user = session.get(User,user.id) 
     
    if not user and not user.register_as =='provider':
          raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Unauthorized user'

        )
    return user








        


