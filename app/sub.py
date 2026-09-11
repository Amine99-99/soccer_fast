from sqlmodel import SQLModel ,Field,Relationship
from .models import User,UserField,Fields,Player
from sqlalchemy import Column,ForeignKey,JSON
import uuid
from typing import Optional,List
from datetime import datetime,time,date







class AcademyCategory(SQLModel):
    age_range:str
    gender:str 
class AcademyRegister(SQLModel):
    name :str=Field(unique=True)
    academy_category:List[AcademyCategory]=Field(sa_column=Column(JSON))



class DaysOfWeek(SQLModel):
    day:str
    start_time:time 



     


  
  

 
class Academy(SQLModel, table=True):
    __tablename__ = "academy"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    name: str
    academy_type:List[dict]= Field(sa_column=Column(JSON))

    user_id: uuid.UUID = Field(sa_column=Column(ForeignKey("user.id")))
    user: User=Relationship(back_populates='academies')


    created_at: datetime = Field(default_factory=datetime.utcnow)

    # relations
    subscriptions: List["Subscription"] = Relationship(back_populates="academy")
    members: List["MemberAcademy"] = Relationship(back_populates="academy")

class Subscription(SQLModel, table=True):
    __tablename__ = "subscription"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # optional links (not required to be academy)
    academy_id: Optional[uuid.UUID] = Field(
        default=None,
        sa_column=Column(ForeignKey("academy.id", ondelete="CASCADE"))
    )
    academy: User=Relationship(back_populates='subscriptions')

    user_id: uuid.UUID = Field(sa_column=Column(ForeignKey("user.id")))
    user:User=Relationship(back_populates='subscriptions')

    field_id: uuid.UUID = Field(sa_column=Column(ForeignKey("field.id")))
    field:Fields=Relationship(back_populates='subscriptions')

    start_date: date
    end_date: date

    status: str = Field(default="draft")

    created_at: datetime = Field(default_factory=datetime.utcnow)

class SubscriptionRegister(SQLModel):
    days_of_week:list
class SubscriptionSchedule(SQLModel, table=True):
    __tablename__ = "subscription_schedule"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    subscription_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey("subscription.id", ondelete="CASCADE"))
    )

    days_of_week:List[dict]=Field(sa_column=Column(JSON))
 


class Session(SQLModel,table=True):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True
    )
    time:str
    date:str 
    status:str
    subscription_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey('subscription.id', ondelete="CASCADE"))
    )
    subscription: Optional['Subscription'] = Relationship(back_populates='sessions')


class MemberAcademy(SQLModel,table=True):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True
    )
    academy_id: Optional[uuid.UUID] = Field(
        sa_column=Column(ForeignKey("academy.id", ondelete="CASCADE"))
    )

    player_id: Optional[uuid.UUID] = Field(
        sa_column=Column(ForeignKey("player.id", ondelete="CASCADE"))
    )
    player:Optional['Player']=Relationship(back_populates='memberships')
    academy:Optional['Academy']=Relationship(back_populates='memberships')

    status: str = Field(default="pending")
    joined_at: datetime = Field(default_factory=datetime.utcnow)





'''


user register an academy 
player seek member ship 
acdmey set  schedule sub to   set subscripton to se field 
for each schedule we set sessions  





'''


