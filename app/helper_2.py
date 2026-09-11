from datetime import datetime ,timezone,timedelta 
import jwt
from .core.config import settings 
import emails
from jwt.exceptions import InvalidTokenError
from fastapi import HTTPException




secret_key_1 = settings.SECRET_KEY_2 
ALGORITHM = "HS256"




def generate_token_verification_token(payload:dict,time_expire:timedelta|None=None)->str:
    object_ver=payload.copy()
    if time_expire:
        expiring = datetime.now(timezone.utc) + time_expire 
    else:
        expiring = datetime.now(timezone.utc) + timedelta(minutes=60*12)

    object_ver.update({'exp':int(expiring.timestamp())})
    token_ver = jwt.encode(object_ver,secret_key_1,algorithm=ALGORITHM)
    return token_ver 

def verify_token(token:str):
    try:
        payload = jwt.decode(token,secret_key_1,algorithms=[ALGORITHM])
        print(payload)
        user_email = payload.get('email')
        print(user_email)
    except InvalidTokenError:
        raise HTTPException(
            status_code =401,
            detail='token invalid'

        )
    return user_email


def send_email_of_verification(subject:str,email_to:str,html_content:str)->None:
    

    if settings.email_enabled:
        message= emails.Message(
            subject=subject,
            mail_from=(settings.PROJECT_NAME,settings.EMAILS_FROM_EMAIL),
            html=html_content


        )
        response = message.send(
            to=email_to,smtp={
                'host':settings.SMTP_HOST,
                'port':settings.SMTP_PORT,
                'user':settings.SMTP_USER,
                'ssl':settings.SMTP_SSL,
                'tls':settings.SMTP_TLS,
                'password':settings.SMTP_PASSWORD
            }
        )

    

