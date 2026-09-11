
from ..core.debs import session_db 
from ..models import PlansPltformRegisters,User,MyPlanPlatform,UserField,OwnerPlatformRegister,OwnerPlatformSubscription
from sqlmodel import select
from datetime import datetime,time,date,timedelta,timezone
from fastapi import HTTPException
from uuid import UUID
from ..scheduler import generate_invoice_platform


def add_plans(session:session_db,user:User,plans:PlansPltformRegisters):
      
    for plan in plans.plans:
        new_plan = MyPlanPlatform(name=plan.name,price=plan.price,billing_cycle_days=plan.billing_cycle_days,max_courts_allowed=plan.max_courts_allowed,admin_id=user.id)

        session.add(new_plan)

    session.commit()
    data = {
        'message':'Successfully Plans Registered'
    }
    return data



def subscribe_to_my_platform(session:session_db,user:UserField,sub:OwnerPlatformRegister):

    plan = session.get(MyPlanPlatform,sub.plan_id)
    if plan is None:
        raise HTTPException(
            status_code=401,
            detail='Plan Not Found'
        )
    new_sub = OwnerPlatformSubscription(billing_cycle=sub.billing_cycle,payment_method=sub.payment_method,total_amount=sub.total_amount,amount_per_period=sub.amount_per_period,user_field_id=user.id,platform_plan_id=sub.plan_id,status='pending',
                                current_period_start=sub.start_date,current_period_end=sub.end_date,duration=sub.duration,field_id=sub.field_id)


    session.add(new_sub)
    session.flush()

    generate_invoice_platform(sub_id=new_sub.id,session=session,user=user)


    session.commit()
    session.refresh(new_sub)
    pay = new_sub.payment_method


    return {
        'message':'Successfully Subscribed',
        'sub_id':new_sub.id
        }


def plans_added(session:session_db):
    plans = session.exec(select(MyPlanPlatform)).all()


    plans_active = [
        {
            'id':plan.id,
            'name':plan.name,
            'price':plan.price,
            'billing_cycle_days':[bill_cycle for bill_cycle in plan.billing_cycle_days],
            'max_courts_allowed':plan.max_courts_allowed,
            'active':plan.is_active,
            
        }
        for plan in plans
    ]

    return plans_active




def activate_my_plans(session:session_db,plan_id:str):
    my_plan = session.get(MyPlanPlatform,UUID(plan_id))

    if my_plan.is_active:
        raise HTTPException(
            status_code=401,
            detail='Plan Already Active'
        )
    my_plan.is_active=True 
    session.commit()
    return {
        "message":'Successfully Activated'
    }


    

