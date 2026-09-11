from .models import MerchantAccount,User,UserField,Invoice,ProviderConnectionRequest,PaymentOnboardingCreate
from .models import PaymentOnboardingRequest, ProviderPermissionRequest,ProviderConnection ,ProviderRegistration,ApproveConnection
from .core.debs import session_db
from uuid import UUID
from sqlmodel import select
from .core.security import generate_account_id,generate_client_id, generate_secret_key,generate_merchant_id
from fastapi import HTTPException
from .helper_stat import notify
from sqlalchemy.orm import selectinload
import requests
from .models import Fields,Payment,PaymentCreate,Subscription,MemberAcademy,Appointment,OwnerPlatformSubscription
from .helper_subscription import approve_sub
from .helper_academy import approve_academy_member
from .helper_3 import approve_appointment
from datetime import datetime ,date,timedelta,timezone

def create_registration_provider(session:session_db,reg:ProviderRegistration,user:User):

    new_req= ProviderConnectionRequest(provider_name=reg.provider_name,provider_id=reg.provider_id,platform_name=reg.platform_name,
                                       business_type=reg.business_type,description=reg.description,website=reg.website,
                                       owner_name=reg.owner_name,owner_email=reg.owner_email,owner_phone=reg.owner_phone,
                                       country=reg.country,city=reg.city,business_address=reg.business_address,tax_id=reg.tax_id,
                                       registration_number=reg.registration_number,expected_monthly_volume=reg.expected_monthly_volume,
                                       average_transaction_amount=reg.average_transaction_amount,currency=reg.currency,user_id=user.id
                                       
                                       )
    
    return new_req 


def set_request_registration(session:session_db,reg:ProviderRegistration,user:User):
    req = create_registration_provider(session=session,reg=reg,user=user)

    session.add(req)
    session.flush()
    req_id = req.id 
    for perm in reg.permissions:
        new_perm= ProviderPermissionRequest( connection_request_id=req_id,permission_name=perm)
        session.add(new_perm)

    session.commit()

    return {
        'message':f'Connection Request to {reg.provider_name} sent '
    }



def approve_connection(session:session_db,approve:ApproveConnection,user:User):
    print(user.id,'user_id')
    req = session.get(ProviderConnectionRequest,approve.req_id)
    if req.status=='active':
            raise HTTPException(
                status_code=409,
                detail='The request has been already approved'
            )


    req.status='active'
    permissions=  session.exec(select(ProviderPermissionRequest).where(ProviderPermissionRequest.status=='pending',ProviderPermissionRequest.connection_request_id==req.id)).all()

    granted=[]
    for p in permissions:
        if p in approve.permissions:
            p.status='approved'
            granted.append(p)
        else :
            p.status='denied'

    client_id=generate_client_id()
    account_id=generate_account_id(req.provider_name)
    secret_key = generate_secret_key()

    new_connect= ProviderConnection(
        connection_request_id=req.id,user_id=req.user_id,account_id=account_id,
        client_id=client_id,secret_key=secret_key,provider_name=req.provider_name,
        granted_permissions=granted
        )
    notify(session=session,user_id=str(req.user_id),sender_id=str(user.id),type=f'Your Coonection Request Approved by{req.provider_name}',ref_id=str(req.id),read=False)
    session.add(new_connect)
    session.commit()


def deny_connection(session:session_db,req_id:str,user:User):
    req = session.get(ProviderConnectionRequest,UUID(req_id))

    if req.status=='denied':
        raise HTTPException(
            status_code=409,
            detail='The request has been already denied'
        )



    req.status='denied'
    notify(session=session,user_id=req.user_id,sender_id=str(user.id),type=f'Your Coonection Request denied by{req.provider_name}',ref_id=str(req.id),read=False)

    
    session.commit()




def onboarding_req(session:session_db,onboard:PaymentOnboardingCreate,user:User|UserField):
    new_onboard= PaymentOnboardingRequest(provider_connection_id=onboard.provider_connection_id,average_transaction_amount=onboard.average_transaction_amount,expected_monthly_volume=onboard.expected_monthly_volume,
                                          currency=onboard.currency,owner_phone=onboard.owner_phone,owner_email=onboard.owner_email,owner_name=onboard.owner_name,
                                          provider_id=onboard.provider_id,
                                          registration_number=onboard.registration_number,tax_id=onboard.tax_id,website=onboard.website,
                                          provider_name=onboard.provider_name,
                                          business_address=onboard.business_address,city=onboard.city,country=onboard.country,business_type=onboard.business_type,
                                          business_name=onboard.business_name,
                                          business_id=onboard.owner_id,owner_type=onboard.owner_type)

    


    session.add(new_onboard)

    session.commit()
    notify(session=session,user_id=str(onboard.provider_id),sender_id=str(user.id),type=f'Onbaord Request by {onboard.business_name}',ref_id=str(onboard.provider_connection_id),read=False)



    return {
        'message':'Onboard Payment Request sent'
    }


def approve_onboard(session:session_db,onboard_id:str,user:User):
    onboard = session.get(PaymentOnboardingRequest,UUID(onboard_id))
    print('onboard',onboard.provider_connection_id)
    
    connection = session.exec(select(ProviderConnection).where(ProviderConnection.id==onboard.provider_connection_id)).first()
    if connection is None :
        raise HTTPException(
                        status_code=401,
                        detail='Invalid Credentials'
                    )

    if onboard.status=='active':
            raise HTTPException(
                status_code=409,
                detail='Onboard Payment Request already approved'
            )

    onboard.status='active'
       
    
     
  

    provider_merchant_id =generate_merchant_id(onboard.provider_name)
    new_merchant_account=MerchantAccount(onboarding_id=onboard.id,provider_connection_id=onboard.provider_connection_id,
                                         provider_name=onboard.provider_name,provider_merchant_id=provider_merchant_id,
                                         merchant_type=onboard.owner_type,merchant_id=onboard.business_id)


    session.add(new_merchant_account)
    session.commit()
    notify(session=session,user_id=str(new_merchant_account.merchant_id),sender_id=str(user.id),type=f'Your Onboard Request approved',ref_id=onboard_id,read=False)


    return {
        'message':'New Merchant Account Created'
    }






def deny_onboard(session:session_db,onboard_id:str,user:User):
    onboard = session.get(PaymentOnboardingRequest,UUID(onboard_id))
    if onboard.status=='denied':
        raise HTTPException(
            status_code=409,
            detail='Onboard Payment Request already denied'
        )
    onboard.status='denied'


 
    session.commit()
    notify(session=session,user_id=str(onboard.business_id),sender_id=str(user.id),type=f'Your Onboard Request denied',ref_id=onboard_id,read=False)


    return {
        'message':'Onboard Payment Request Denied'
    }



def connections_requests(session:session_db,user:User):
    reqs_connect = session.exec(select(ProviderConnectionRequest).where(ProviderConnectionRequest.status=='pending',ProviderConnectionRequest.provider_id==user.id).options(selectinload(ProviderConnectionRequest.permissions))).all()

    print('reqs',reqs_connect)
    connections = [
        {
            'id':r.id,
            'platform':r.platform_name,
            'city':r.city,
            'permissions':[
                {
                    'id':p.id,
                    'name':p.permission_name,
                    'status':p.status

                }
                for p in r.permissions
            ]


        }
        for r in reqs_connect

        
    ]
    

    return connections


def my_connections(session:session_db,user:User):
    connections =session.exec(select(ProviderConnection).options(selectinload(ProviderConnection.connection_request))).all()



    on_board_data=[
        {
        'id':r.id,
        'connect_id':r.connection_request_id,
        'provider_name':r.provider_name,
        'provider_id':r.connection_request.provider_id,
        'permissions':r.granted_permissions



        }
        for r in connections

    ]
    print(on_board_data)
    return on_board_data



def my_onboardings(session:session_db,user:User):
    onboards = session.exec(select(PaymentOnboardingRequest).where(PaymentOnboardingRequest.provider_id==user.id,PaymentOnboardingRequest.status=='pending')).all()


    reqs_onboard = [
        {
            'id':o.id,
            'name':o.owner_name,
            'owner':o.owner_type,
            'business':o.business_type,

        }
        for o in onboards
    ]
    return  reqs_onboard 

def my_account(session:session_db,user:User|UserField):
    my_account = session.exec(select(MerchantAccount).where(MerchantAccount.merchant_id==user.id)).first()

    my_merchant_account={
        'id':my_account.id,
       'onboarding_id':my_account.onboarding_id,
       'provider_connection_id':my_account.provider_connection_id,
       'provider_name':my_account.provider_name,
       'merchant_id':my_account.merchant_id,
       'provider_merchant_id':my_account.provider_merchant_id,
       'merchant_type':my_account.merchant_type

    }

    return my_merchant_account



def my_sub_invoices_created(session:session_db,sub_id:str):

    invoices = session.exec(select(Invoice).where(Invoice.subscription_id==UUID(sub_id),Invoice.status=='pending')).all()
    my_invoices=[
        {
            'id':inv.id,
            'amount':inv.amount,
          
            'status':inv.status,
            'issue_date':inv.issue_date,
            'due_date':inv.due_date,
            'payee_id':inv.payee_field_id,
            'payee':inv.payee_field,
            'payer_id':inv.payer_id,
            'payer':inv.payer
            
        }
        for inv in invoices
    ]

    return my_invoices


#payment menu allocated provider recieve request validate pay return to field owner and payer


def pay_me_first(session:session_db,pay:PaymentCreate,user:User|UserField):
    connection = session.get(ProviderConnection,pay.provider_connection_id)
    if connection is None :
            raise HTTPException(
                            status_code=401,
                            detail='Invalid Credentials'
                        )
    
    invoice = session.get(Invoice,pay.invoice_id)
    if invoice is None:
        raise HTTPException(
            status_code=401,
            detail='Invalid Invoice'
        )
    payee_id = invoice.payee_id if invoice.payee else invoice.payee_field_id 
    merchant = session.exec(select(MerchantAccount).where(MerchantAccount.merchant_id==payee_id)).first()
    if merchant is None:
        raise HTTPException(
            status_code=401,
            detail='invalid Payment Credentials'
        )
    new_pay = Payment(merchant_account_id=merchant.id,method=pay.payment_method,amount=pay.amount,provider=pay.provider,
                       invoice_id=pay.invoice_id,
                      provider_connection_id=pay.provider_connection_id,status='paid')
    session.add(new_pay)
    invoice.status='paid'


    if invoice.subscription_id is not None:
        sub = session.get(Subscription,invoice.subscription_id)
        if sub is None:
            raise HTTPException(
                status_code=401,
                detail='Invalid Subscription '
            )
        new_pay.transaction_ref=str(invoice.subscription_id)
        approve_sub(session=session,sub_id=str(invoice.subscription_id),user=user)
    elif invoice.owner_platform_subscription is not None:
            sub = session.get(OwnerPlatformSubscription,invoice.owner_platform_subscription_id)
            field_db = session.get(Fields,sub.field_id)
            active = field_db.is_active
            if field_db is None and active :
                            raise HTTPException(
                                status_code=401,
                                detail='Invalid Field '
                            )

            if sub is None:
                raise HTTPException(
                    status_code=401,
                    detail='Invalid Subscription '
                )
            new_pay.transaction_ref=str(invoice.owner_platform_subscription_id)
            field_db.is_active=True 
            field_db.status='active'
            
            field_db.approved_at = datetime.now()
        

            

    elif invoice.member_academy_id is not None:
        member = session.get(MemberAcademy,invoice.member_academy_id)
        if member is None:
                    raise HTTPException(
                        status_code=401,
                        detail='Invalid Membership '
                    )
        new_pay.transaction_ref=str(invoice.member_academy_id)
        approve_academy_member(session=session,member_id=str(invoice.member_academy_id),user=user)

    elif invoice.appointment_id is not None:
         app = session.get(Appointment,invoice.appointment_id)
         if app is None:
                             raise HTTPException(
                                 status_code=401,
                                 detail='Invalid Appointment ')
         new_pay.transaction_ref=str(invoice.appointment_id)
         app.approved_at = datetime.now()

         approve_appointment(session=session,user=user,app_id=str(app.id))
         

        

    
    session.commit()
    return {
        'message':'Payment Processing'
    }



def my_invoice(session:session_db,inv_id:str):
    inv =  session.get(Invoice,UUID(inv_id))


    invoice = {
                 'id':inv.id,
                 'amount':inv.amount,
               
                 'status':inv.status,
                 'issue_date':inv.issue_date,
                 'due_date':inv.due_date,
                 'payee_id':inv.payee_field_id,
                 'payee':inv.payee_field,
                 'payer_id':inv.payer_id,
                 'payer':inv.payer
                 
             }
    return invoice

      

