import asyncio

from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID
from fastapi import HTTPException

from dateutil.relativedelta import relativedelta
from sqlmodel import Session, select


from .models import (User,Subscription,MemberAcademy,InvoiceNotify,
                     Invoice,ErrorScheduler,UserField,Fields,OwnerPlatformSubscription)
from .core.debs import session_db,engine




def create_invoice_sub(ref_id:UUID,amount:Decimal,due_date:datetime,payer_id:UUID,payee_field_id:UUID):
    today = datetime.now().date()





    return Invoice(subscription_id=ref_id,amount=amount,status='pending',issue_date=today,
                   due_date=due_date,payer_id=payer_id,payee_field_id=payee_field_id)

def create_member_invoice(ref_id:UUID,amount:Decimal):
    return Invoice(member_academy_id=ref_id,amount=amount)

def create_error_scheduler(error,notify:InvoiceNotify):
    return ErrorScheduler(type=notify.type,ref_id=notify.ref_id,error_message=str(error))



def generate_invoice_subscription(sub_id:UUID,session:session_db,user:UserField):

    sub_db = session.get(Subscription,sub_id)
    if sub_db is None:
        raise HTTPException(
            status_code=401,
            detail='Invalid Subscription'
        )

    field = session.get(Fields,sub_db.field_id)
       
    
    start_date = sub_db.start_date 
    end_date = sub_db.end_date 
    billing_date = start_date
    today = datetime.now().date()
    print('today',today)
    print(sub_db.billing_cycle,'billing cycle')
    new_inv=[]
    
    while billing_date<end_date:
        print(billing_date,'billdate')
        new_invoice=Invoice(subscription_id=sub_id,amount=sub_db.amount_per_period,status='pending',issue_date=billing_date,
                           due_date=billing_date,payer_id=user.id,payee_field_id=field.user_field_id)
        session.add(new_invoice)
        new_inv.append(new_invoice)
        
        if sub_db.billing_cycle=='Monthly':
            billing_date = billing_date + relativedelta(months=1)
        elif sub_db.billing_cycle=='1' or sub_db.billing_cycle=='2' :
            billing_date = billing_date +timedelta(weeks=int(sub_db.billing_cycle))
        else:
            raise HTTPException(
                     status_code=400,
                      detail="Invalid billing cycle"
                             )

   
    for inv in new_inv:
        if inv.due_date==start_date and start_date!= today :
            inv.due_date=today
    session.commit()

def generate_invoice_platform(sub_id:UUID,session:session_db,user:UserField):

    sub_db = session.get(OwnerPlatformSubscription,sub_id)
   

    if sub_db is None:
        raise HTTPException(
            status_code=401,
            detail='Invalid Subscription'
        )
    user_db = session.exec(select(User).where(User.register_as=='admin')).first()
    if user_db is None:
        raise HTTPException(
            status_code=401,
            detail='Invalid Platform Admin'
                )


       
    
    start_date = sub_db.current_period_start 
    end_date = sub_db.current_period_end
    billing_date = start_date
    today = datetime.now().date()
    print('today',today)
    print(sub_db.billing_cycle,'billing cycle')
    new_inv=[]
    
    while billing_date<end_date:
        print(billing_date,'billdate')
        new_invoice=Invoice(owner_platform_subscription_id=sub_id,amount=sub_db.amount_per_period,status='pending',issue_date=billing_date,
                           due_date=billing_date,payer_field_id=user.id,payee_id=user_db.id)
        session.add(new_invoice)
        new_inv.append(new_invoice)
        
        if sub_db.billing_cycle=='Monthly':
            billing_date = billing_date + relativedelta(months=1)
        
        

        else:
            raise HTTPException(
                     status_code=400,
                      detail="Invalid billing cycle"
                             )

   
    for inv in new_inv:
        if inv.due_date==start_date and start_date!= today :
            inv.due_date=today
    session.commit()

def invoice_issuing(session:session_db):
    # if date is due date 
    pass
  
            

        

def generate_invoice_member_academy(notify:InvoiceNotify,session):
    member_academy_db = session.get(MemberAcademy,notify.ref_id)
    if member_academy_db is None:
        raise Exception(
            'MemberShip Academy not found'
        )
    start_date = member_academy_db.start_date 
    end_date = member_academy_db.end_date 
    billing_date =start_date 
    today= datetime.now().date()
    list_invoices=[]
    while billing_date<=end_date:
        pass
       
       
        
        


def handle_generation(notify:InvoiceNotify,session):
    if notify.type=='Subscription':
        generate_invoice_subscription(notify=notify,session=session)
    elif notify.type =='MemberAcademy':
        generate_invoice_member_academy(notify=notify,session=session)

    else :
        raise Exception(
            f'Unknown invoice type: {notify.type}'
        )
    
async def worker_scheduler():
    session=None 
    while True:
        try:
            session=Session(engine)
            notify = session.exec(select(InvoiceNotify).where(InvoiceNotify.status=='pending')).first()
            print('notify',notify)
            if notify is not None:
                try:
                    handle_generation(notify=notify,session=session)
                    notify.status='treated'
                except Exception as e:
                    session.rollback()
                    new_error=create_error_scheduler(error=str(e),notify=notify)
                    session.add(new_error)
                    session.commit()



       
        
        except Exception as e:
            print('Worker Failure',e)

        finally:
            if session:
               session.commit()
               
               session.close()

        await asyncio.sleep(3600)


def start_invoice_worker():
    asyncio.create_task(worker_scheduler())

       

    

  
   




