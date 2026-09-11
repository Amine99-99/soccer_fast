from fastapi import APIRouter,Depends,Query,HTTPException
from ..core.debs import session_db,get_admin_registered,get_current_active_user,get_courts_registred
from typing import Annotated
from ..models import OwnerPlatformRegister,User,RegisterPersonnels,PlansPltformRegisters,UserField,OwnerPlatformSubscription
from ..admin_service.admin_service import admin_data
from ..admin_service.register_personnels import register_personnels 
from ..admin_service.platform_subscription import subscribe_to_my_platform, add_plans,plans_added,activate_my_plans
from ..admin_service.user_reqs import user_fields_request_account,approve_user,deny_user
from uuid import UUID
from sqlmodel import select
from ..field_owner_service.field_service import FieldOwnerService





admin = APIRouter()


field_service = FieldOwnerService()









@admin.post('/register_personnels',status_code=201)
def register_my_personnels(session:session_db,personnels:RegisterPersonnels,user:Annotated[User,Depends(get_admin_registered)]):
    return register_personnels(session=session,personnels=personnels)


@admin.post('/plans_to_add',status_code=201)
def my_platform_plans(session:session_db,plans:PlansPltformRegisters,user:Annotated[User,Depends(get_admin_registered)]):
    return add_plans(session=session,plans=plans,user=user) 



@admin.get('/admin_dash',status_code=200)
def myplatform_dash(session:session_db,period:Annotated[str,Query()],user:Annotated[User,Depends(get_admin_registered)]):
    
    return admin_data(session=session,period=period)

@admin.get('/user_field_reqs',status_code=200)
def fields_user_req(session:session_db,user:Annotated[User,Depends(get_admin_registered)]):
    return user_fields_request_account(session=session)


@admin.post('/user_approve/{user_id}')
def approve_field_user(session:session_db,user_id:str,user:Annotated[User,Depends(get_admin_registered)]):
    print('user_id',user_id)
    return approve_user(session=session,user_id=user_id)

@admin.post('/user_deny/{user_id}')
def deny_field_user(session:session_db,user_id:str,user:Annotated[User,Depends(get_admin_registered)]):
    return deny_user(session=session,user_id=user_id)


@admin.get('/plans_added',status_code=200)
def my_plans_added(session:session_db,user:Annotated[User|UserField,Depends(get_current_active_user)]):
    return plans_added(session=session)



@admin.post('/activate_plan/{plan_id}')
def activate_plan(session:session_db,plan_id:str,user:Annotated[User,Depends(get_admin_registered)]):
    return activate_my_plans(session=session,plan_id=plan_id)


@admin.post('/subscribe_to_platform')
def subscribe_platform(session:session_db,sub:OwnerPlatformRegister,user:Annotated[UserField,Depends(get_current_active_user)]):
    return subscribe_to_my_platform(session=session,sub=sub,user=user)


@admin.delete('/delete_sub/{sub_id}')
def delete_my_sub(session:session_db,sub_id:str):

    sub = session.get(OwnerPlatformSubscription,UUID(sub_id))
    if sub is None:
        raise HTTPException(
            status_code=401,
            detail='Invalid Sub'
        )

    session.delete(sub)
    session.commit()

    return {
        'message':'success'
    }

@admin.get('/my_sub')
def my_sub_plat(session:session_db,user:Annotated[UserField,Depends(get_current_active_user)]):
    subs = session.exec(select(OwnerPlatformSubscription).where(OwnerPlatformSubscription.user_field_id==user.id)).all()

    return [
        {
            'id':su.id,
            'start_date':su.current_period_start
        }
        for su in subs
    ]


@admin.get('/my_field_dash/{field_id}')
def my_field_dash(session:session_db,field_id:str,date_slot:Annotated[str|None,Query()]=None):
    return field_service.dash_data(session=session,field_id=field_id,date_slot=date_slot)






@admin.get('/my_fields_changes_data/{field_id}')
def my_field_changes(session:session_db,field_id:str,period:Annotated[str,Query()],user:Annotated[UserField,Depends(get_courts_registred)]):
    return field_service.what_changed(session=session,field_id=field_id,period=period)









