from .core.debs import session_db
from uuid import UUID
from datetime import date
from decimal import Decimal
from sqlmodel import select
from .models import Invoice






def get_invoices_platform_sub(session:session_db,sub_id:str):
    invoices = session.exec(select(Invoice).where(Invoice.owner_platform_subscription_id==UUID(sub_id),Invoice.status=='pending')).all()
    my_invoices=[
            {
                'id':inv.id,
                'amount':inv.amount,
              
                'status':inv.status,
                'issue_date':inv.issue_date,
                'due_date':inv.due_date,
                'payee_id':inv.payee_id,
                'payee':inv.payee,
                'payer_id':inv.payer_field_id,
                'payer':inv.payer_field
                
            }
            for inv in invoices
        ]
    
    return my_invoices
'''


invoice 
approved booking online one invoice
approve subscription list of invoice due date 
approved academy memebrship 


due date 


create invoice 
invoice 

recurring invoices


class Invoice(SQLModel,table=True):
    __tablename__='invoice'
    __table_args__ = {"extend_existing": True}
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True
    )
    amount:Decimal = Field(default=Decimal('0.00'),
    sa_column=Column(Numeric(10, 2), nullable=False)
)
    paid_amount:Decimal=Field(default=Decimal('0.00'),
    sa_column=Column(Numeric(10, 2), nullable=False)
)
    remaining_amount:Decimal=Field(default=Decimal('0.00'),
    sa_column=Column(Numeric(10, 2), nullable=False)
)
    status:str 
    invoice_type:
    subscription_id: Optional[uuid.UUID]= Field(
        sa_column=Column(ForeignKey('subscription.id'))
    )
    subscription: Optional['Subscription'] = Relationship(back_populates='invoices')
    appointment_id: Optional[uuid.UUID] = Field(
        sa_column=Column(ForeignKey('appointment.id'))
    )
    appointment: Optional['Appointment'] = Relationship(back_populates='invoices')
    appointment_owner_id: Optional[uuid.UUID] = Field(
        sa_column=Column(ForeignKey('appointment_owner.id'))
    )
    appointment_owner: Optional['AppointmentOwner'] = Relationship(back_populates='invoices')
    member_academy_id: Optional[uuid.UUID] = Field(
        sa_column=Column(ForeignKey('member_academy.id'))
    )
    member_academy: Optional['MemberAcademy'] = Relationship(back_populates='invoices')

    issue_date:date 
    due_date:date 
    created_at:datetime=Field(default_factory=datetime.utcnow)
    updated_at:datetime=Field(default_factory=datetime.utcnow,sa_column_kwargs={"onupdate": datetime.utcnow})
    payments:List['Payment']=Relationship(back_populates='invoice')
    user_id:Optional[uuid.UUID]=Field(default=None,foreign_key='user.id')
    user:Optional['User']=Relationship(back_populates='invoices')
    user_field_id:Optional[uuid.UUID]=Field(default=None,foreign_key='user_field.id')
    user_field:Optional['UserField']=Relationship(back_populates='invoices')
appointment 
invoice create 

appointment ==>online payment ===>approved ===>invoice generated status=paid one single invoice
appointment ===>pay_on_field ===>pending ====>owner approve invoice generated status=unpaid  one single invoice 


subscription approved ===>invoice one generated for the first due date 
recurring invoices for all due dates until program finish 
approved ==>appointment id ==>sent 
genearet Invoice with appointment 
????? invoice how to populate the right attribute ref  
ref_id 
type 







'''

def create_invoice(session:session_db,ref_id:UUID,type:str,date,amount):
    
    new_invoice = (
        


    )
    return new_invoice 




    
    






