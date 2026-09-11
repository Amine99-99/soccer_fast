from fastapi import APIRouter ,Depends
from ..core.debs import session_db,get_current_active_user,get_admin_registered,get_provider
from ..models import PaymentCreate, PaymentOnboardingCreate, User,UserField,Invoice,InvoiceNotify,ProviderRegistration,ApproveConnection
from typing import Annotated
from sqlmodel import select
from ..payment_service import set_request_registration,connections_requests,approve_connection,deny_connection,my_connections
from ..payment_service import my_invoice, my_sub_invoices_created, my_onboardings, onboarding_req,approve_onboard,deny_onboard,my_account,pay_me_first
from ..invoice_service import get_invoices_platform_sub

filed = APIRouter()




@filed.get('/my_invoices/{sub_id}',status_code=200)
def get_my_invoices(session:session_db,sub_id:str,user:Annotated[UserField,Depends(get_current_active_user)]):
    return my_sub_invoices_created(session=session,sub_id=sub_id)
   


   


@filed.get('/users_providers',status_code=200)
def get_providers_x(session:session_db,user:Annotated[User|UserField,Depends(get_current_active_user)]):
    users= session.exec(select(User).where(User.register_as=='provider')).all()


    providers=[
        {
            'id':u.id, 
            'provider_name':u.username,
            'email':u.email,

        }
        for u in users
    ]

    return providers
@filed.post('/provider_connection_request',status_code=201)
def connction_registration(session:session_db,reg:ProviderRegistration,user:Annotated[User,Depends(get_admin_registered)]):
    return set_request_registration(session=session,reg=reg,user=user)


@filed.get('/reqs_connections')
def my_reqs_connect(session:session_db,user:Annotated[User,Depends(get_provider)]):
    return connections_requests(session=session,user=user)

@filed.post('/approve_connection')
def connect_approve(session:session_db,approve:ApproveConnection,user:Annotated[User,Depends(get_provider)]):
    return approve_connection(session=session,approve=approve,user=user)


@filed.post('/deny_connection/{req_id}')
def connect_deny(session:session_db,req_id:str,user:Annotated[User,Depends(get_provider)]):
    return deny_connection(session=session,req_id=req_id,user=user)



@filed.get('/my_provider_connections')
def my_onboard_connections(session:session_db,user:Annotated[User,UserField,Depends(get_current_active_user)]):
    return my_connections(session=session,user=user)


@filed.post('/onboard_account')
def my_onboard_request(session:session_db,onboard:PaymentOnboardingCreate,user:Annotated[User|UserField,Depends(get_current_active_user)]):
    return onboarding_req(session=session,onboard=onboard,user=user)


@filed.post('/approve_onboarding/{onboard_id}')
def onboard_approve(session:session_db,onboard_id:str,user:Annotated[User,Depends(get_provider)]):
    return approve_onboard(session=session,onboard_id=onboard_id,user=user) 

@filed.post('/deny_onboarding/{onboard_id}')
def onboard_deny(session:session_db,onboard_id:str,user:Annotated[User,Depends(get_provider)]):
    return deny_onboard(session=session,onboard_id=onboard_id,user=user)



@filed.get('/my_account_merchant')
def get_my_merchant_account(session:session_db,user:Annotated[User|UserField,Depends(get_current_active_user)]):
    return my_account(session=session,user=user)

@filed.get('/my_onboardings')
def my_onboardings_reqs(session:session_db,user:Annotated[User,Depends(get_provider)]):
    return my_onboardings(session=session,user=user)



@filed.post('/pay_me_request')
def pay_req(session:session_db,pay:PaymentCreate,user:Annotated[User|UserField,Depends(get_current_active_user)]):
    return pay_me_first(session=session,user=user,pay=pay)


@filed.get('/my_invoice/{inv_id}')
def my_invoice_data(session:session_db,inv_id:str,user:Annotated[User|UserField,Depends(get_current_active_user)]):
    return my_invoice(session=session,inv_id=inv_id)

@filed.get('/my_platform_invoice/{sub_id}')
def my_invoices_platform(session:session_db,sub_id:str,user:Annotated[UserField,Depends(get_current_active_user)]):
    return get_invoices_platform_sub(session=session,sub_id=sub_id)




