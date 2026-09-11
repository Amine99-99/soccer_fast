from ..core.debs import session_db ,get_admin_registered 
from ..models import UserField
from sqlmodel import select
from uuid import UUID
from fastapi import HTTPException









def user_fields_request_account(session:session_db):

    reqs_account = session.exec(select(UserField)).all()

    users_field = [

        {
            'id':user.id,
            'username':user.username,
            'company_name':user.company_name,
            'company_code':user.company_code,
            'address':user.address,
            'city':user.city,
            'status':user.status

        }
        for user in reqs_account
    ]
    return users_field 



def approve_user(session:session_db,user_id:str):
    user = session.get(UserField,UUID(user_id))
    if user.status=='approved account':
        raise HTTPException(
            status_code=401,
            detail='User Already has approved account'
        )
    user.status='approved account'

    session.commit()
    return {
        'message':'User Account Approved'
    }


def deny_user(session:session_db,user_id:str):
    user = session.get(UserField,UUID(user_id))
    if user.status=='denied account':
        raise HTTPException(
            status_code=401,
            detail='User Already has denied account'
        )
    user.status='denied account'

    session.commit()
    return {
        'message':'User Account Denied'
    }


