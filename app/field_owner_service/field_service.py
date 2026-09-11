
from ..core.debs import session_db
from ..models import User,UserField ,Fields,Court,Appointment,AppointmentOwner,Subscription,SessionApp
from sqlmodel import select
from uuid import UUID
from sqlalchemy.orm import selectinload
from datetime import time,timedelta,datetime,date
from fastapi import HTTPException
from datetime import datetime,timedelta,timezone
from zoneinfo import ZoneInfo
from enum import Enum
from decimal import Decimal
import calendar

class PeriodTime(str,Enum):
    TODAY = "today"
    LAST_7_DAYS = "last_7_days"
    THIS_MONTH = "this_month"
    LAST_MONTH = "last_month" 
class FieldOwnerService:
    def my_field(self,session:session_db,field_id:str):
        
        my_field = session.exec(select(Fields).where(Fields.id==UUID(field_id)).options(selectinload(Fields.appointments).selectinload(Appointment.invoices),selectinload(Fields.courts),selectinload(Fields.owner_appointments).selectinload(AppointmentOwner.invoices),selectinload(Fields.sessions).selectinload(SessionApp.subscription).selectinload(Subscription.invoices))).first()

        if my_field is None:
            raise HTTPException(
                status_code=401,
                detail='Invalid Field'
            )
      
        return my_field 

    
    def appointments_field(self,session:session_db,field_id:str,date_slot:str|None=None):
        query = select(Appointment).where(Appointment.field_id==UUID(field_id)).options(selectinload(Appointment.invoices),selectinload(Appointment.court))
        if date_slot is not None:
            date_value = date.fromisoformat(date_slot)
            query = query.where(Appointment.date==date_value)
        print(field_id,'field_id')
        
            
        appointments = session.exec(query).all()

      
        apps_field =[
        {
            'id':a.id,
            'date':a.date,
            'time':str(a.time)[:5],
           'status':a.status,
            
            'court_id':a.court_id,
            'start_hour':a.court.start_hour,
            'end_hour':a.court.end_hour,
             'price':a.amount,
             'payment_method':a.payment_method,
    
            'field_name':a.field.field_name,
            'field':a.field,
            'field_id':a.field_id,
            'city':a.field.city, 
            'address':a.field.address,
            'courts':a.field.courts,
            'user':a.user if a.user else a.user_field,
            'username':a.user.username,
            'phone':a.user.phone,
            'user_id': a.user_id if a.user else a.user_field_id,
             'game_id':a.game_id,
            'game':a.game,
            'created':a.created_at,
            'description':'Appointment'

        }
        for a in appointments
    ]

       
   
        return apps_field
    def app_owner_fields(self,session:session_db,field_id:str,date_slot:str|None=None):
        query = select(AppointmentOwner).where(AppointmentOwner.field_id==UUID(field_id)).options(selectinload(AppointmentOwner.invoices),selectinload(AppointmentOwner.court))

        if date_slot is not None:
            date_value = date.fromisoformat(date_slot)
            query = query.where(AppointmentOwner.date==date_value)
        
           
        apps_owner = session.exec(query).all()
        owner_booking=[
                {
                   'id':a.id,
                    'date':a.date,
                    'time':str(a.time)[:5],
                    
                    'status': a.status ,
                    
                    'court_id':a.court_id,
                     'start_hour':a.court.start_hour,
                    'end_hour':a.court.end_hour,
                    'price':a.court.session_price,
                    'payment_method':a.payment_method,
                        
                    'paid':a.payment_status,
                    'field_name':a.field.field_name,
                    'field':a.field,
                    'field_id':a.field_id,
                    'city':a.field.city, 
                    'address':a.field.address,
                    'courts':a.field.courts,
                    'user':a.user_field,
                    'username':a.username,
                    'phone':a.phone,
                    'created':a.created_at,
                    
                    'user_id': a.user_field_id,
                    'description':'Owner Appointment'
        
        
                }
                for a in apps_owner
            ]
        
        return owner_booking


    def sessions_sub_fields(self,session:session_db,field_id:str,date_slot:str|None=None):

        query = select(SessionApp).where(SessionApp.field_id==UUID(field_id)).options(selectinload(SessionApp.court),selectinload(SessionApp.subscription).selectinload(Subscription.invoices))

        if date_slot is not None:
            date_value = date.fromisoformat(date_slot)
            query = query.where(SessionApp.date==date_value)
           
        subscriptions_session = session.exec(query).all()
        
        sessions_sub=[
        
              
                        {
                            'id':sess.id,
                            'date':sess.date,
                            'subscription_id':sess.subscription_id,
                            'time':sess.time,
                            'court_id':sess.court_id,
                             'start_hour':sess.court.start_hour,
                            'end_hour':sess.court.end_hour,
                             'price':sess.subscription.amount_session,
                             'payment_method':sess.subscription.payment_method,
                                
                            'status':sess.status,
                            'status_subscription':sess.subscription.status,
                            'user':sess.subscription.user,
                            'username':sess.subscription.user.username,
                            'phone':sess.subscription.user.phone,
                            'created':sess.subscription.created_at,
                            'description':'Subscription'
                            
                    
        
                        }
                        for sess in subscriptions_session
                    ]
        
              
            
        
        return sessions_sub

    def today_app(self,arr:str,date_slot:str):
        date_value = date.fromisoformat(date_slot)
        today_apps = [app for app in arr if app.date==date_value]
        return today_apps

    def combine_apps(self,session:session_db,field_id:str,date_slot:str|None=None):
        my_field = self.my_field(session=session,field_id=field_id)
        appointments= self.appointments_field(session=session,field_id=field_id,date_slot=date_slot)
      
        booked_app = [arr for arr in appointments if arr['status']=='approved']
        pending_reqs = [arr for arr in appointments if arr['status']=='pending']
        appointments_owner= self.app_owner_fields(session=session,field_id=field_id,date_slot=date_slot)
        booked_owner = [arr for arr in appointments_owner if arr['status']=='approved']

        sessions= self.sessions_sub_fields(session=session,field_id=field_id,date_slot=date_slot)
        booked_sessions = [arr for arr in sessions if arr['status']=='approved']
        combined_apps = appointments + appointments_owner+sessions
        booked = len(booked_app) + len(booked_owner) + len(booked_sessions)

        

        return combined_apps,booked,booked_app,booked_sessions,booked_owner

    

    def dash_data(self,session:session_db,field_id:str,date_slot:str|None=None):
      my_field = self.my_field(session=session,field_id=field_id)
      subs_pending  = [sub for sub in my_field.subscriptions if sub.status=='pending']
      apps_pending = [app for app in my_field.appointments if app.status=='pending']
      courts= my_field.courts

      appointments = my_field.appointments 
      
      sessions = my_field.sessions 
      owner_apps = my_field.owner_appointments
     
      

     

      combined_apps ,booked,booked_app,booked_sessions,booked_owner= self.combine_apps(session=session,field_id=field_id,date_slot=date_slot)
       

      new_combined = appointments +  owner_apps
      for app in new_combined:
          print(app.status)
          if app.status=='approved':
              for inv in app.invoices:
                  print('inv',inv.amount,inv.due_date,type(inv.due_date),inv.status)
    

     
      
            

      

      total_cach = self.cach_collected_app(apps_approved=new_combined,date=date_slot)
      total_earning_online =self.online_transfered_app(apps_approved=new_combined,date=date_slot)
      print('earning',total_earning_online)

      total_slots = self.total_slots(courts=courts,date_slot=date_slot)
      rate  = booked/total_slots

      
    
      

      dashboard_data={
          'courts':[
              {
              'id':c.id,
              'size':c.court_size,
              'price':c.session_price,
              'type':c.type_of_court,
              'slots': self.last_slots(court=c,date_slot=date_slot,apps=combined_apps),
              }
              
              for c in courts
            
          ],
          'fieldId':field_id,
          'selectedDate':date_slot,
          'metrics':{
              'date':date_slot,
              'totalSlots':total_slots,
              'bookedSlots':booked,
              'occupancyRate':rate,
              'cashToCollectTND':total_cach,
              'appEarningsMonthTND':total_earning_online,
              'requestBooking':len(apps_pending),
             'requestSubscription':len(subs_pending),
             'app_online':round((len(booked_app)/booked),2) if booked!=0 else 0 ,
             'app_session':round((len(booked_sessions)/booked),2) if booked !=0 else 0,
             'app_owner_t':round((len(booked_owner)/booked),2) if booked!=0 else 0



              
          },
       
      }

     
      return dashboard_data

   
    def cach_collected_app(self,apps_approved:list,date):
        
        paid_cash = [inv for app in apps_approved if app.status=='approved' and  app.payment_method=='pay_on_field' for inv in app.invoices if inv.status=='paid' and str(inv.due_date)==date]

        total_cach = sum(invoice.amount for invoice in paid_cash )
        return total_cach
   
    
    def online_transfered_app(self,apps_approved:list,date):
        
        paid_online = [inv for app in apps_approved if app.status=='approved' and app.payment_method=='online' for inv in app.invoices if inv.status=='paid' and str(inv.due_date)==date]
        print(paid_online,'paid online')
        total_online = sum(invoice.amount for invoice in paid_online )
        return total_online


        



        
            

    def field_dash(self,session:session_db,field_id:str):
        field_db = session.exec(select(Fields).where(Fields.id==UUID(field_id)).options(selectinload(Fields.courts),selectinload(Fields.subscriptions),selectinload(Fields.appointments))).first()
        subs_pending  = [sub for sub in field_db.subscriptions if sub.status=='pending']
        apps_pending = [app for app in field_db.appointments if app.status=='pending']
        return field_db
    def slots(self,court,date_slot:str):
        
        date_value = datetime.strptime(date_slot, "%Y-%m-%d").date()
        
            
        current_hour= datetime.combine(date_value,court.start_hour)
        end_hour = datetime.combine(date_value,court.end_hour)
        court_slot=[]

        while current_hour <=end_hour:
            court_slot.append({'startTime':current_hour,'endTime':current_hour +  timedelta(minutes=court.session_time),
                                   'courtId':court.id,
                                  })


            current_hour = current_hour +  timedelta(minutes=court.session_time)

            
        
        

        return court_slot

    def status_slot(self,combined:list,slots:list)->list[str]:
        status_state=[]
        for app in combined:
            for s in slots :
                if s['current_hour'].time()==app.time and s['id']==app.court:
                    status_state.append({
                        'time':s['current_hour'],'status':app.status

                    })
        return status_state

    def last_slots(self,court,date_slot:str,apps:list):
        approved_slots= self.slots(court=court,date_slot=date_slot)
        slots_items=[]
        for slots in approved_slots:
        
            status='available'
            bookingDetails=None
            for app in apps:
               

                if app['court_id']==slots['courtId'] and str(app['time'])==str(slots['startTime'].time())[:5]:
                    
            
                    status = app['status']
                    bookingDetails={
                        'bookingId':app['id'],
                        'playerName':app['username'],
                        'playerPhone':app['phone'],
                        'paymentMethod': app['payment_method'],
                        'PaymentStatus':'',
                        'blockedReason':'later' ,   
                        'price':app['price'],
                        'createdAt':app['created']

                        }
                    break 
            slots_items.append({**slots,'startTime':str(slots['startTime'].time())[:5],'endTime':str(slots['endTime'].time())[:5],'status':status.capitalize(),'bookingDetails':bookingDetails})
     
            
        return slots_items
    def total_slots(self,courts,date_slot:str):
        slots_total=[]
        for c in courts :
            new_slot = self.slots(court=c,date_slot=date_slot)
            slots_total.append(len(new_slot))
        return sum(slots_total)

    def time_control(self,period:PeriodTime):


        now = datetime.now(ZoneInfo("Africa/Tunis"))

        if period==PeriodTime.TODAY:
            start_time = now.replace(hour=0,minute=0,second=0,microsecond=0)
            end_time=now 
        elif period==PeriodTime.LAST_7_DAYS:
            start_time = now - timedelta(days=7)
            end_time = now 
        elif period == PeriodTime.THIS_MONTH:
            start_time = now.replace(day=1,hour=0,minute=0,second=0,microsecond=0)
            end_time = now 
        elif period==PeriodTime.LAST_MONTH:
            first_this_month = now.replace(day=1,hour=0,minute=0,second=0,microsecond=0)
            start_time = (first_this_month - timedelta(days=28)).replace(day=1,hour=0,minute=0,second=0,microsecond=0)
            end_time = first_this_month - timedelta(seconds=1)
        else : 
            end_time=now
            start_time = now - timedelta(days=30)

        return start_time ,end_time 

    def number_of_days(self,period:PeriodTime):
        today = datetime.now()

# Previous month
        previous_month = today.month - 1 or 12
        previous_year = today.year if today.month > 1 else today.year - 1    
        days = calendar.monthrange(previous_year, previous_month)[1]
        if period ==PeriodTime.TODAY:
            number=1 
        elif period==PeriodTime.LAST_7_DAYS:
            number=7 
        elif period==PeriodTime.THIS_MONTH:
            today = datetime.now().day
            first = datetime.now().replace(day=1).day 
            number = (today-first) if today != first else 1

        elif period == PeriodTime.LAST_MONTH:
            number = days 
        else :
            number =1

        return number

    def what_changed(self,period,session:session_db,field_id:str):
        my_field= self.my_field(session=session,field_id=field_id)
        start_time,end_time = self.time_control(period)
        end_time = end_time.date()
        start_time = start_time.date()
        today = str(datetime.now().date())
        today_data = self.dash_data(session=session,field_id=field_id,date_slot=today)
        number = self.number_of_days(period=period)
         
        today_occupancy = today_data['metrics']['occupancyRate']
        cash_collected_today = today_data['metrics']['cashToCollectTND']
        online_earn = today_data['metrics']['cashToCollectTND']



      
       
        cash_collected= self.average_cash(appointments=my_field.appointments,end_time=end_time,start_date=start_time)
    
        online_transfer = self.average_online(appointments=my_field.appointments,end_time=end_time,start_date=start_time)
      
        cash_sessions=self.cash_collected_session(apps_approved=my_field.sessions,start_date=start_time,end_date=end_time)
        online_sessions= self.online_collected_session(apps_approved=my_field.sessions,start_date=start_time,end_date=end_time)
        total_cash = cash_sessions+cash_collected
        total_online = online_sessions + online_transfer
        total = total_cash + total_online
        #total_subs , total_cash_sub,cash_sub_rejected = self.sub_change(subscription=my_field.subscriptions)
        total_apps,total_cash_apps,total_rejected,apps_approved = self.booked(appointments=my_field.appointments,start_date=start_time,end_time=end_time)
        owner_apps,total_owner_apps = self.owner_apps(appointments=my_field.owner_appointments,end_time=end_time,start_date=start_time)
        new_end= str(end_time)
        total_slots = self.total_slots(courts=my_field.courts,date_slot=new_end)
        
        sessions_booked,total_sessions = self.sessions_fields(appointments=my_field.sessions,start_date=start_time,end_time=end_time)
   
        total_booked = sessions_booked + owner_apps + apps_approved
      
      
        utilization = len(total_booked)/total_slots
        print('ustilization',utilization)
        courts = self.courts_my_field(session=session,field_id=field_id)
       
        rate_average= utilization/number 
        variation = today_occupancy-rate_average
        average_cash_d = total_cash_apps/number
        average_online = total_online /number 
        var_cash = cash_collected_today - round(average_cash_d,2)
        print('variation',variation)
        var_online = online_earn - round(average_online,2)
        total_slots_t  =  today_data['metrics']['totalSlots']
        booked_today = today_data['metrics']['bookedSlots']
        rate = today_data['metrics']['occupancyRate']
       
        sessions_app = today_data['metrics']['app_session']
        online_apps = today_data['metrics']['app_online']
        owner_apps_tt = today_data['metrics']['app_owner_t'] 
        var_se = sessions_app- (round((len(sessions_booked)/len(total_booked)*100),2) if len(total_booked)!=0 else 0 )
        var_app = online_apps -  (round((len(apps_approved)/len(total_booked)*100),2) if len(total_booked)!=0 else 0)
        var_own = owner_apps_tt - (round((len(owner_apps)/len(total_booked)*100),2) if len(total_booked)!=0 else 0)





        changed_data={
            'cashCollected':total_cash,
            'onlineTransfer':round(average_online,2),
            'totalRevenue':total,
            'totalSubs':'',
            'SubCash':'',
            'subrejected':'',
            'today_rate_occ':round(today_occupancy,2),
            'cash_today':cash_collected_today,
            'online_earn':online_earn,
            'variation':round(variation,2),
            'variation_cash':var_cash, 
            'variation_online':var_online,
            'total_apps':len(total_booked),
            'total_cash_apps':round(average_cash_d,2),
            'total_rejected':total_rejected,
            'ownerApps':total_owner_apps,
            'total_slots':total_slots,
            'sessions':round((len(sessions_booked)/len(total_booked)*100),2) if len(total_booked)!=0 else 0,
            'appointments':round((len(apps_approved)/len(total_booked)*100),2) if len(total_booked)!=0 else 0,
            'owner_apps':round((len(owner_apps)/len(total_booked)*100),2) if len(total_booked)!=0 else 0,
            'field_slots_utilization':round(rate_average,2),
             'booked_t':booked_today,
             'sessions_b':sessions_app,
             'online_t_app':online_apps,
             'owner_t_apps':owner_apps_tt,
             'rate':rate,
             'session_var':var_se,
             'apps_var':var_app,
             'own_var':var_own,
            'courts':[

            
              self.utilization_courts(court=c,end_time=end_time,start_date=start_time)
                
                for c in courts
              
                
            ]

        }
        return changed_data










    def average_cash(self,appointments:list,end_time,start_date)->Decimal:
        invoices_cash = [inv for app in appointments if app.payment_method=='pay_on_field' for inv in app.invoices if inv.status=='paid' and start_date<=inv.due_date<=end_time ]

        cash_made = sum (inv.amount for inv in invoices_cash)
        return cash_made


        
    def average_online(self,appointments:list,end_time,start_date)->Decimal:
        invoices_online = [inv for app in appointments if app.payment_method=='online' for inv in app.invoices if inv.status=='paid' and start_date<=inv.due_date<=end_time ]

        cash_made = sum (inv.amount for inv in invoices_online)
        return cash_made

    def cash_collected_session(self,apps_approved,start_date,end_date):
        paid_cash_sessions = [inv for app in apps_approved if app.status=='active' and app.subscription.payment_method=='pay_on_field' for inv in app.subscription.invoices if inv.status=='paid' and start_date<=inv.due_date<=end_date ]
    
        total_sessions_cash = sum(inv.amount for inv in paid_cash_sessions)
        return total_sessions_cash 
    
    def online_collected_session(self,apps_approved,start_date,end_date):
        paid_online_sessions = [inv for app in apps_approved if app.status=='active' and app.subscription.payment_method=='online' for inv in app.subscription.invoices if inv.status=='paid' and start_date<=inv.due_date<=end_date]
        
        total_sessions_online = sum(inv.amount for inv in paid_online_sessions)
        return total_sessions_online 

        

    def total_revenue(self,invoices:list,end_time)->Decimal:
        cash_made =self.average_cash(invoices,end_time)
        online_made = self.average_online(invoices,end_time)
        total = cash_made + online_made
        return total
    #def sub_change(self,subscriptions:list,end_time)->tuple[int,int,int]:
       # subs = [sub for sub in subscriptions if sub.status =='active' and sub.approved_at.replace(tzinfo=ZoneInfo("Africa/Tunis"))<=end_time ]
       # subs_cash = [sub for sub in subscriptions if sub.status =='active' and sub.payment_method=='pay_on_field' and sub.approved_at.replace(tzinfo=ZoneInfo("Africa/Tunis"))<=end_time ]
        #subs_cash_rejected = [sub for sub in subscriptions if sub.status =='rejected' and sub.payment_method=='pay_on_field' and sub.created_at.replace(tzinfo=ZoneInfo("Africa/Tunis"))<=end_time ]

        #return len(subs),len(subs_cash),len(subs_cash_rejected)

    def booked(self,appointments:list,end_time,start_date)->tuple[int,int,int,list]:
        total_apps = [app for app in appointments if app.status=='approved'  and start_date<=app.date<=end_time]
        print('total_apps',total_apps,start_date,end_time)
        for a in total_apps:
            print('date',a.date)
        app_rejected_cash = [app for app in appointments if app.status=='rejected' and app.payment_method=='pay_on_field' and app.date <=end_time]
        apps = [app for app in appointments if app.status=='approved' and app.payment_method=='pay_on_field' and start_date<=app.date<=end_time]
        return len(total_apps),len(apps),len(app_rejected_cash),total_apps

    def owner_apps(self,appointments:list,end_time,start_date)->tuple[list,int]:
        total_apps = [app for app in appointments if app.status=='approved'  and start_date<=app.date<=end_time]
        return total_apps,len(total_apps)

    def sessions_fields(self,appointments:list,start_date,end_time)->tuple[list,int]:
        total_sessions = [sess for sess in appointments if sess.status=='approved' and start_date<=sess.date <=end_time]
        return total_sessions,len(total_sessions)

    def courts_my_field(self,session:session_db,field_id:str):
        courts = session.exec(select(Court).where(Court.field_id==UUID(field_id)).options(selectinload(Court.appointments),selectinload(Court.sessions),selectinload(Court.owner_appointments))).all()
        if courts is None :
            raise HTTPException(
                status_code=401,
                detail='Invalid Courts'
            )
        return courts 


    def total_cash_court(self,apps_approved:list,end_date,start_date):
        paid_cash = [inv for app in apps_approved if app.status=='approved' and app.payment_method=='pay_on_field' for inv in app.invoices if inv.status=='paid' and start_date<=inv.due_date<=end_date ]
        cash_amount = sum(inv.amount for inv in paid_cash)
        return cash_amount

    def total_online_court(self,apps_approved:list,end_date,start_date):
        paid_online = [inv for app in apps_approved if app.status=='approved' and app.payment_method=='online' for inv in app.invoices if inv.status=='paid' and start_date<=inv.due_date<=end_date ]
        online_amount = sum(inv.amount for inv in paid_online)
        return online_amount


  

    def utilization_courts(self,court,end_time,start_date):
        appointments = court.appointments 
        sessions = court.sessions 
        owner_appointments = court.owner_appointments 

        approved_apps=[a for a in appointments if a.status=='approved' and start_date<=a.date<=end_time]
        approved_sessions = [s for s in sessions if s.status=='approved' and  start_date<=s.date<=end_time]
        owner_apps = [o for o in owner_appointments if o.status=='approved' and start_date<=o.date<=end_time]

        total_apps = appointments + sessions + owner_appointments 

        total_approved = [a for a in total_apps if a.status == 'approved' and start_date<=a.date <=end_time]
      
        total_pending = [a for a in total_apps if a.status  == 'pending']
        total_rejected = [a for a in total_apps if a.status  == 'rejected'] 
        now = datetime.now().date()
        total_slots_court = self.slots(court=court,date_slot=str(now))
        print('total slots',total_slots_court)
        utilization  = round(len(total_approved) / len(total_slots_court),2)
        cash_court = self.total_cash_court(apps_approved = total_apps,end_date=end_time,start_date=start_date)
        online_amount = self.total_online_court(apps_approved=total_apps,end_date=end_time,start_date=start_date)
        print('cash',cash_court,'online',online_amount)
        total_rev = cash_court + online_amount

        sess= round((len(approved_sessions)/len(total_approved))*100,2) if len(total_approved) !=0 else 0
        ap=round((len(approved_apps)/len(total_approved))*100,2)  if len(total_approved) !=0 else 0
        ow=round((len(owner_appointments)/len(total_approved))*100,2)  if len(total_approved) !=0 else 0


        court_data= {
            'id':court.id,
            
            'totalCrevenue':total_rev,
            'onlineCTransfer':online_amount,
            'totalCSubs':'',
             'SubCCash':'',
             'SubCrejected':'',
             'total_c_apps':len(total_approved),
             'total_c_cash_apps':cash_court,
            'court_per':[sess,ap,ow],
            'online_book':ap,
            'sess_book':sess,
            'owner_book':ow,
            
            
             'total_c_rejected':len(total_rejected),
             'slots':len(total_slots_court),
            
             'utilization_slots':utilization


        }
        return court_data


         



    

        
        


    


    '''


     
    front end  field total utilization
    court x           court y        court z 
     utilizatiion     utilization     utilization 

    
    
    '''





                    

  
            






'''
interface TimeSlot {
  id: string;                 
  courtId: string;             
  startTime: string;        
  endTime: string;             
  status: string;
  price: number;            
  

  bookingDetails?: {
    bookingId?: string;
    playerName?: string;
    playerPhone?: string;
    paymentStatus?: PaymentStatus;
    blockedReason?: string;     
    createdAt?: string;
  };
}
//slot start time end time 

field ==>courts  ====>
  for c in court 
     list slots 
     list of slots 
     populate new list 
     start 
     end 
     status 
     price 
     courtid
     bookingDetail:{
        bookingId:string 
        
      
      
      }

      app court id status time 
      combined apps today 
      for c in courts
          slots list 
          c id 

     




//





'''
                    
                    

    






  

'''
export type SlotStatus = 'available' | 'app_booked' | 'cash_booked' | 'blocked';

export type PaymentStatus = 'paid_online' | 'pay_at_field' | 'unpaid' | 'refunded';

export type SurfaceType = 'synthetic_grass' | 'natural_grass' | 'indoor_parquet' | 'padel_turf';

export interface TimeSlot {
  id: string;                 
  courtId: string;             
  startTime: string;        
  endTime: string;             
  status: SlotStatus;
  price: number;            
  

  bookingDetails?: {
    bookingId?: string;
    playerName?: string;
    playerPhone?: string;
    paymentStatus?: PaymentStatus;
    blockedReason?: string;     
    createdAt?: string;
  };
}



export interface DailyScheduleResponse {
  fieldId: string;
  selectedDate: string;        
  metrics: DailyMetrics;
  slots: TimeSlot[];           x
}
'''
   
