from typing import Annotated, Optional, List,Literal
import uuid
from datetime import date, time
from enum import Enum
from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel, Session, create_engine
from fastapi import Depends, UploadFile
from sqlalchemy import Column, JSON, ForeignKey,Numeric
from datetime import datetime
from sqlalchemy import UniqueConstraint
from pydantic import field_validator
from decimal import Decimal
from pydantic import HttpUrl,model_validator,field_validator




class Role(str, Enum):
    coach = 'coach_captain'
    player = 'player'
    fan = 'fan'
    journalist = 'journalist'


class CourtRegister(SQLModel):
   
    type_of_court: str
    opening_days: list[str] = Field(sa_column=Column(JSON))
    start_hour: time
    end_hour: time
    session_time: int
    court_size:str 
    session_price:float
    court_name:str|None=None


class Court(CourtRegister,table=True):
    __tablename__='court'
    __table_args__ = {"extend_existing": True}
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
   
    
    field_id:uuid.UUID=Field(sa_column=Column(ForeignKey('field.id', ondelete="CASCADE")))
    field :'Fields'=Relationship(back_populates='courts')
    appointments:List['Appointment']=Relationship(back_populates='court')
    sessions:List['SessionApp']=Relationship(back_populates='court')
    subscriptions:List['Subscription'] = Relationship(back_populates='court')
    owner_appointments:List['AppointmentOwner']=Relationship(back_populates='court', sa_relationship_kwargs={"cascade": "all,delete-orphan"})



class FieldsRegister(SQLModel):
    courts: List[CourtRegister] = Field(sa_column=Column(JSON))
    number_of_courts: str
    field_name:str
    address:str
    city:str
    postal_code:str


class Fields(SQLModel, table=True):
    __tablename__ = 'field'
    __table_args__ = {"extend_existing": True}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    courts: List['Court']=Relationship(back_populates='field',
        sa_relationship_kwargs={"cascade": "all,delete-orphan"})
   
    field_name:str
    address:str
    city:str
    postal_code:str
    status:str
    is_active:Optional[bool]=Field(default=True)
    user_field_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey('user_field.id', ondelete="CASCADE"))
    )

    user_field: Optional['UserField'] = Relationship(back_populates='fields')
    appointments: List['Appointment'] = Relationship(
        back_populates='field',
        sa_relationship_kwargs={"cascade": "all,delete-orphan"}
    )
    owner_appointments:List['AppointmentOwner']=Relationship(back_populates='field', sa_relationship_kwargs={"cascade": "all,delete-orphan"})
    games:List['Game']=Relationship(back_populates='field', sa_relationship_kwargs={"cascade": "all,delete-orphan"})
    subscriptions: List["Subscription"] = Relationship(back_populates="field")
    plans:List['SubscriptionPlan']=Relationship(back_populates='field')
    sessions:List['SessionApp']=Relationship(back_populates='field')
    create_at:datetime=Field(default_factory=datetime.utcnow)
    approved_at:datetime|None=None
    approved_by : str|None=None
    





class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, max_length=225, index=True)
    username: str = Field(unique=True, max_length=40, index=True)
    is_active: bool = False
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=225)
    register_as: str
    phone:str


class UserBaseField(SQLModel):
    email: EmailStr = Field(unique=True, max_length=225, index=True)
    username: str = Field(unique=True, max_length=40, index=True)
    is_active: bool = False
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=225)
    register_as: str
    phone:str


class UserCreate(UserBase):
    password: str = Field(min_length=9, max_length=40)
    address: str
    phone: str
    city: str
    country: str


class UserRegister(SQLModel):
    username: str = Field(unique=True, max_length=40, index=True)
    email: EmailStr = Field(unique=True, index=True, max_length=225)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=225)
    address: str
    phone: str
    city: str
    country: str
    register_as: str='coach'

class UserRegisterPlayer(SQLModel):
    username: str = Field(unique=True, max_length=40, index=True)
    email: EmailStr = Field(unique=True, index=True, max_length=225)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=225)
    address: str
    phone: str
    city: str
    country: str
    register_as: str='player'
    position:str

'''
    export const PersonnelSchema = z.object({
  personnels: z.array(
    z.object({
    
      '''

class RegisterPersonnel(UserBase):
      password:str=Field(min_length=8,max_length=40)
      address:str 
      city:str 
      post_code:str 
      country:str 
      username:str=Field(unique=True)
      


class RegisterPersonnels(SQLModel):
    personnels:List[RegisterPersonnel]=Field(sa_column=Column(JSON))






class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=225)
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    email: EmailStr | None = Field(default=None, max_length=225)
    full_name: str | None = Field(default=None, max_length=225)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


class User(UserBase, table=True):
    __table_args__ = {"extend_existing": True}
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str

    tokens: Optional['TokenBase'] = Relationship(
        back_populates='user',
        sa_relationship_kwargs={"cascade": "all,delete-orphan"}
    )
    appointments: List['Appointment'] = Relationship(
        back_populates='user',
        sa_relationship_kwargs={"cascade": "all,delete-orphan"}
    )

    address: str
   
    city: str
    country: str

    profile_picture: Optional['PictureProfileDB'] = Relationship(
        back_populates='user',
        sa_relationship_kwargs={"uselist": False, "cascade": "all,delete-orphan"}
    )
    player: Optional['Player'] = Relationship(
        back_populates='user',
        sa_relationship_kwargs={"uselist": False, "cascade": "all,delete-orphan"}
    )
    teams:Optional['Team']=Relationship(back_populates='user', sa_relationship_kwargs={"uselist": False,"cascade": "all,delete-orphan"})
    reqs_game:List['RequestGameJoin']=Relationship(back_populates='user')
    games:List['Game']=Relationship(back_populates='user', sa_relationship_kwargs={"cascade": "all,delete-orphan"})
    reqs_transfer:List['RequestTransfer']=Relationship(back_populates='user')
    game_stats:List['GameStat']=Relationship(back_populates='user')
    notifications : List['Notification']=Relationship(back_populates='user', sa_relationship_kwargs={"foreign_keys": "[Notification.user_id]"})
    sent_notifications : List['Notification']=Relationship(back_populates='sender', sa_relationship_kwargs={"foreign_keys": "[Notification.sender_id]"})

    subscriptions: List["Subscription"] = Relationship(back_populates="user")
    academies: Optional["Academy"] = Relationship( back_populates='user', sa_relationship_kwargs={"uselist": False})
 
    programs:List['ProgramAcademy']=Relationship(back_populates='coach')
    kids:List['KidAcademy']=Relationship(back_populates='parent')
    invoices:List['Invoice']=Relationship(back_populates='payer', sa_relationship_kwargs={"foreign_keys": "[Invoice.payer_id]"})
    invoices_payee:List['Invoice']=Relationship(back_populates='payee', sa_relationship_kwargs={"foreign_keys": "[Invoice.payee_id]"})


class FieldRegister(SQLModel):
    username: str = Field(unique=True, max_length=40, index=True)
    email: EmailStr = Field(unique=True, index=True, max_length=225)
    register_as: str
    full_name: str | None = Field(default=None, max_length=225)
    password: str = Field(min_length=9, max_length=40)
    company_name: str = Field(max_length=200)
    company_code: str = Field(max_length=100)
    address: str
    phone: str
    city: str
    country: str


class UserField(UserBaseField, table=True):
    __tablename__ = 'user_field'
    __table_args__ = {"extend_existing": True}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    company_name: str = Field(max_length=200)
    company_code: str = Field(max_length=100)

    address: str
    phone: str
    city: str
    country: str
    status:str=Field(default='pending')

    fields: List['Fields'] = Relationship(
        back_populates='user_field',
        sa_relationship_kwargs={"cascade": "all,delete-orphan"}
    )

    tokens: List['TokenBase'] = Relationship(
        back_populates='user_field',
        sa_relationship_kwargs={"cascade": "all,delete-orphan"}
    )

    profile_picture: Optional['PictureProfileDB'] = Relationship(
        back_populates='user_field',
        sa_relationship_kwargs={"uselist": False, "cascade": "all,delete-orphan"}
    )

    appointments: List['Appointment'] = Relationship(
        back_populates='user_field',
        sa_relationship_kwargs={"cascade": "all,delete-orphan"}
    )
    teams:List['Team']=Relationship(back_populates='user_field', sa_relationship_kwargs={"cascade": "all,delete-orphan"})
    owner_appointments:List['AppointmentOwner']=Relationship(back_populates='user_field', sa_relationship_kwargs={"cascade": "all,delete-orphan"})
    
    games:List['Game']=Relationship(back_populates='user_field', sa_relationship_kwargs={"cascade": "all,delete-orphan"})
    reqs_game:List['RequestGameJoin']=Relationship(back_populates='user_field')
    reqs_transfer:List['RequestTransfer']=Relationship(back_populates='user_field')
    game_stats:List['GameStat']=Relationship(back_populates='user_field')
    notifications :List['Notification']=Relationship(back_populates='user_field', sa_relationship_kwargs={"foreign_keys": "[Notification.user_field_id]"})
    sent_notifications :List['Notification']=Relationship(back_populates='sender_field', sa_relationship_kwargs={"foreign_keys": "[Notification.sender_field_id]"})
    kids:List['KidAcademy']=Relationship(back_populates='parent_field')
    invoices:List['Invoice']=Relationship(back_populates='payer_field', sa_relationship_kwargs={"foreign_keys": "[Invoice.payer_field_id]"})
    invoices_payee:List['Invoice']=Relationship(back_populates='payee_field', sa_relationship_kwargs={"foreign_keys": "[Invoice.payee_field_id]"})
    subscriptions_platform:List['OwnerPlatformSubscription']=Relationship(back_populates='user_field')
class UserPublic(UserBase):
    id: uuid.UUID


class UserFieldPublic(UserBaseField):
    id: uuid.UUID
    company_name: str = Field(max_length=200)
    company_code: str = Field(max_length=100)
  


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


class Token(SQLModel):
    token_access: str
    token_type: str


class TokenData(SQLModel):
    user_id: str


class TokenBase(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: int = Field(default=None, primary_key=True)
    hashed_token: str
    is_active: bool = True

    user_id: Optional[uuid.UUID] = Field(
        sa_column=Column(ForeignKey('user.id', ondelete="CASCADE"))
    )
    user: Optional['User'] = Relationship(back_populates='tokens')

    user_field_id: Optional[uuid.UUID] = Field(
        sa_column=Column(ForeignKey('user_field.id', ondelete="CASCADE"))
    )
    user_field: Optional['UserField'] = Relationship(back_populates='tokens')


class PlayersRegister(SQLModel):
    player_status:str
    name: str
    position:str
    phone:str
class GameTeam(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("team_id", "game_id"),
       {"extend_existing": True}
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    team_id: Optional[uuid.UUID] = Field(
        sa_column=Column(ForeignKey("team.id", ondelete="CASCADE"))
    )

    game_id: Optional[uuid.UUID] = Field(
        sa_column=Column(ForeignKey("game.id", ondelete="CASCADE"))
    )

    status: str | None = None

    joined_at: datetime = Field(default_factory=datetime.utcnow)
class MemberShip(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    team_id: Optional[uuid.UUID] = Field(
        sa_column=Column(ForeignKey("team.id", ondelete="CASCADE"))
    )

    player_id: Optional[uuid.UUID] = Field(
        sa_column=Column(ForeignKey("player.id", ondelete="CASCADE"))
    )
    player:Optional['Player']=Relationship(back_populates='memberships')
    team:Optional['Team']=Relationship(back_populates='memberships')

    status: str = Field(default="pending")
    # pending | active | rejected | left

    available_for_game: bool = Field(default=True)
    description:str|None=Field(default=None)

    joined_at: datetime = Field(default_factory=datetime.utcnow)

class Notification(SQLModel,table=True):
    __table_args__ = {"extend_existing": True}
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    is_read: bool = Field(default=False, index=True)
    user_id:Optional[uuid.UUID]=Field(sa_column=Column(ForeignKey('user.id',ondelete="CASCADE")))
    user:Optional['User']=Relationship(back_populates='notifications',  sa_relationship_kwargs={"foreign_keys": "[Notification.user_id]"})
    user_field_id:Optional[uuid.UUID]=Field(sa_column=Column(ForeignKey('user_field.id',ondelete="CASCADE")))
    user_field:Optional['UserField']=Relationship(back_populates='notifications',  sa_relationship_kwargs={"foreign_keys": "[Notification.user_field_id]"})
    sender_id: Optional[uuid.UUID] = Field(sa_column=Column(ForeignKey('user.id',ondelete="CASCADE")))
    

    sender: Optional["User"] = Relationship(back_populates='sent_notifications',  sa_relationship_kwargs={"foreign_keys": "[Notification.sender_id]"})
    sender_field_id:Optional[uuid.UUID] = Field(sa_column=Column(ForeignKey('user_field.id',ondelete="CASCADE")))
 
    
    sender_field: Optional["UserField"] = Relationship(back_populates='sent_notifications',  sa_relationship_kwargs={"foreign_keys": "[Notification.sender_field_id]"})
    
    type: str = Field(index=True)

   
    reference_id: Optional[uuid.UUID] = Field(default=None, index=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)





class Player(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True
    )

    user_id: Optional[uuid.UUID] = Field(
        sa_column=Column(ForeignKey("user.id", ondelete="CASCADE"), unique=True)
    )

    user: Optional["User"] = Relationship(
        back_populates="player",
        sa_relationship_kwargs={"uselist": False}
    )

    phone: str = Field(index=True, unique=True)
    name: str

    reqs_join_team_game: List["ReqJoinTeamGame"] = Relationship(
        back_populates="player",
        
    )

    player_status: str


   

    stats: List["Stat"] = Relationship(
        back_populates="player",
        
    )
    stats_disciplin :List['StatDisciplinary']=Relationship(back_populates='player')

    position: str

  
    reqs_team: List["ReqJoinTeam"] = Relationship(
        back_populates="player"
    )

    memberships: List["MemberShip"] = Relationship(back_populates="player")

class RequestGameJoin(SQLModel,table=True):
     __table_args__ = {"extend_existing": True}
     id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True
    )
     
     status:str|None='pending'
     game_id:uuid.UUID=Field(sa_column=Column(ForeignKey('game.id')))
     game:Optional['Game'] = Relationship(back_populates='reqs_game')
     team_id:Optional[uuid.UUID] = Field(sa_column=Column(ForeignKey('team.id')))
     team :Optional['Team']=Relationship(back_populates='reqs_game')
     user_id :Optional[uuid.UUID] = Field(sa_column=Column(ForeignKey('user.id')))
     user :Optional['User']=Relationship(back_populates='reqs_game')
     user_field_id:Optional[uuid.UUID] = Field(sa_column=Column(ForeignKey('user_field.id')))
     user_field:Optional['UserField']=Relationship(back_populates='reqs_game')
     #game_snapshot:dict=Field(sa_column=Column(JSON))
class ReqJoinTeamGame(SQLModel,table=True):
    __table_args__ = {"extend_existing": True}
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True
    )
    status_req:str|None='pending'
    requested_user_id:str
    game_id:uuid.UUID=Field(sa_column=Column(ForeignKey('game.id')))
    game:Optional['Game']=Relationship(back_populates='reqs_join_team_game')
    team_id:uuid.UUID=Field(sa_column=Column(ForeignKey('team.id')))
    team:Optional['Team']=Relationship(back_populates='reqs_join_team_game')
    player_id:uuid.UUID=Field(sa_column=Column(ForeignKey('player.id')))
    player:Optional['Player']=Relationship(back_populates='reqs_join_team_game')
    #team_snapshot:dict=Field(sa_column=Column(JSON))
class ReqJoinTeam(SQLModel,table=True):
    __table_args__ = {"extend_existing": True}
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True
    )
    status_req:str|None='pending'
    requested_user_id:str
  
    team_id:uuid.UUID=Field(sa_column=Column(ForeignKey('team.id')))
    team:Optional['Team']=Relationship(back_populates='reqs_team')
    player_id:uuid.UUID=Field(sa_column=Column(ForeignKey('player.id')))
    player:Optional['Player']=Relationship(back_populates='reqs_team')
    #team_snapshot:dict=Field(sa_column=Column(JSON))
   
   
    
class Transfer(SQLModel):
    date:date
    time:time
    app_id:str

class RequestTransfer(SQLModel,table=True):
    __table_args__ = {"extend_existing": True}
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True
    )
    app_id:str
    status_req:str|None='pending' 
    user_requested_id:str
    user_id:Optional[uuid.UUID]=Field(sa_column=Column(ForeignKey('user.id')))
    user:Optional['User']= Relationship(back_populates='reqs_transfer')
    user_field_id:Optional[uuid.UUID]=Field(sa_column=Column(ForeignKey('user_field.id')))
    user_field:Optional['UserField']= Relationship(back_populates='reqs_transfer')
   
      
        
                          

class GameStat(SQLModel,table=True):
     __tablename__='game_stat'
     __table_args__ = {"extend_existing": True}
     id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True
    )
     game_id:uuid.UUID=Field(sa_column=Column(ForeignKey('game.id')))
     game:Optional['Game']=Relationship(back_populates='game_stats')
     team_id:uuid.UUID=Field(sa_column=Column(ForeignKey('team.id')))
     team:Optional['Team']=Relationship(back_populates='game_stats')
   
     user_id : Optional[uuid.UUID]=Field(sa_column=Column(ForeignKey('user.id')))   
     user:Optional['User']=Relationship(back_populates='game_stats')
     user_field_id:Optional[uuid.UUID]=Field(sa_column=Column(ForeignKey('user_field.id')))
     user_field :Optional['UserField']=Relationship(back_populates='game_stats')
     stats :List['Stat']=Relationship(back_populates='game_stat')
     stats_disciplin :List['StatDisciplinary']=Relationship(back_populates='game_stat')
    


class StatRegister(SQLModel):
    technical_execution: str
    tactical_intelligence: str
    physical_contribution: str
    mental_attitude: str
    impact_on_the_game: str
    player_id: str

class StatDisciplinRegister(SQLModel):
    attendance: str
    punctuality: str
    behavior: str
    commitment: str
    payment_status: str
    player_id:str
  


class GameRegisterStat(SQLModel):
    game_id:str
    team_id:str
    stats:List[StatRegister]=Field(sa_column=Column(JSON))


class GameRegisterStatDisciplinary(SQLModel):
    game_id:str
    team_id:str
    stats_disciplinary:List[StatDisciplinRegister]=Field(sa_column=Column(JSON))


class Stat(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

   
    technical_execution: str
    tactical_intelligence: str
    physical_contribution: str
    impact_on_the_game: str

   
    mental_attitude: str

 

 
    player_id: uuid.UUID = Field(sa_column=Column(ForeignKey("player.id")))
    player: Optional["Player"] = Relationship(back_populates="stats")

    game_stat_id: Optional[uuid.UUID] = Field(
        sa_column=Column(ForeignKey("game_stat.id"))
    )

    game_stat: Optional["GameStat"] = Relationship(back_populates="stats")

class StatDisciplinary(SQLModel,table=True):
    __tablename__='stat_disciplin'
    __table_args__ = {"extend_existing": True}
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
    attendance: str
    punctuality: str
    behavior: str
    commitment: str
    payment_status: str
    player_id: uuid.UUID = Field(sa_column=Column(ForeignKey("player.id")))
    player: Optional["Player"] = Relationship(back_populates="stats_disciplin")
    game_stat_id: Optional[uuid.UUID] = Field(
        sa_column=Column(ForeignKey("game_stat.id"))
    )

    game_stat: Optional["GameStat"] = Relationship(back_populates="stats_disciplin")


class BuildTeam(SQLModel):
    coach_name:str
    team_name:str
   
   
    game_id:str|None=None
    
                     
                     
                     
                     
                     
                     
                     
                     
                     
                     
                     
                     
                     
                     
                     
                     
                     
                     
                  

class Team(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
    
    status: str | None = 'pending'
  
    coach_name:str
    coach_id:str 
    coach_email:str 
    team_name:str 
    user_id:Optional[uuid.UUID]=Field(sa_column=Column(ForeignKey('user.id',ondelete="CASCADE"),unique=True))
    user:Optional['User']=Relationship(back_populates='teams')
    user_field_id:Optional[uuid.UUID]=Field(sa_column=Column(ForeignKey('user_field.id',ondelete="CASCADE")))
    user_field:Optional['UserField']=Relationship(back_populates='teams')
    game_stats: List["GameStat"] = Relationship(
        back_populates="team",
       
    )
    games: list["Game"] = Relationship(
        back_populates="teams",
        link_model=GameTeam
    )
    reqs_join_team_game: List["ReqJoinTeamGame"] = Relationship(
        back_populates="team",
        
    )
    memberships:List['MemberShip']=Relationship(back_populates='team')
    reqs_game: List["RequestGameJoin"] = Relationship(
        back_populates="team",
        
    )
    reqs_team: List["ReqJoinTeam"] = Relationship(
        back_populates="team"
    )


    


class GameBase(SQLModel):
    date: date
    time: time

    app_id:str


class Game(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    date: date
    time: time
    status: str | None = 'pending'
    teams: list["Team"] = Relationship(
        back_populates="games",
        link_model=GameTeam
    )
    players_per_team:Optional[int]=Field(default=None)
    

   
    appointments: List['Appointment'] = Relationship(
        back_populates='game',
        
    )
    reqs_join_team_game: List["ReqJoinTeamGame"] = Relationship(
        back_populates="game",
        
    )
    reqs_game: List["RequestGameJoin"] = Relationship(
        back_populates="game",
        
    )
    game_stats:List['GameStat']=Relationship(back_populates='game')
    user_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey('user.id', ondelete="CASCADE"))
    )
    user: Optional['User'] = Relationship(back_populates='games')

    user_field_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey('user_field.id', ondelete="CASCADE"))
    )
    user_field: Optional['UserField'] = Relationship(back_populates='games')

    field_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey('field.id', ondelete="CASCADE"))
    )
    field: Optional['Fields'] = Relationship(back_populates='games')
    


class StatusAppointment(str, Enum):
    pass


class AppointmentBase(SQLModel):
    date: date
    time: time
    status: str='pending'
    payment_method:Optional[str]=Field(default=None)
  
class AppointmentRegister(SQLModel):
    date: date
    time: time
    field_id:str
    court_id:uuid.UUID
    payment_method:str
    field_name:str
    amount:Decimal



class Appointment(AppointmentBase, table=True):
    __table_args__ = {"extend_existing": True}
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    court_id:uuid.UUID=Field(foreign_key='court.id')
    court :Court=Relationship(back_populates='appointments')


    user_id: Optional[uuid.UUID] = Field(
        sa_column=Column(ForeignKey('user.id', ondelete="CASCADE"))
    )
    user: Optional['User'] = Relationship(back_populates='appointments')

    user_field_id: Optional[uuid.UUID]= Field(
        sa_column=Column(ForeignKey('user_field.id', ondelete="CASCADE"))
    )
    user_field: Optional['UserField'] = Relationship(back_populates='appointments')

    field_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey('field.id', ondelete="CASCADE"))
    )
    
    field: Optional['Fields'] = Relationship(back_populates='appointments')
    game_id :Optional[uuid.UUID]=Field(sa_column=Column(ForeignKey('game.id',ondelete="SET NULL")))

    game: Optional['Game'] = Relationship(
        back_populates='appointments',
        
    )
    invoices:List['Invoice']=Relationship(back_populates='appointment')
    created_at:datetime=Field(default_factory=datetime.utcnow)
    approved_at:datetime|None=None
    amount:Optional[Decimal]=Field(default=None)
    
    
  


class PictureProfile(SQLModel):
    file: UploadFile


class PictureProfileDB(SQLModel, table=True):
    __tablename__ = 'profile_db'
    __table_args__ = {"extend_existing": True}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    file: str

    user_id: Optional[uuid.UUID] = Field(
        
        sa_column=Column(ForeignKey("user.id", ondelete="CASCADE"),unique=True)
    )
    user: Optional['User'] = Relationship(
        back_populates='profile_picture',
        sa_relationship_kwargs={"uselist": False}
    )

    user_field_id: Optional[uuid.UUID] = Field(
        
    sa_column=Column(
        ForeignKey("user_field.id", ondelete="CASCADE"),unique=True
    )
)
    user_field: Optional['UserField'] = Relationship(
        back_populates='profile_picture',
        sa_relationship_kwargs={"uselist": False}
    )

   
        
class AppointmentRegisterOwner(SQLModel):
        date:date
        time:time
        id_field:str
        username:str 
        phone:str 
        payment_status:str
      
       
class AppointmentRegisterUpdate(SQLModel):
        date:date
        time:time
        field_id:str
        court_id:str 
        id:str
class AppointmentOwner(AppointmentRegisterOwner,table=True):
        __tablename__='appointment_owner'
        __table_args__ = {"extend_existing": True}
        id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
        status:Optional[str]=Field(default=None)
        payment_method:str|None=None
        user_field_id : uuid.UUID=Field(sa_column=Column(ForeignKey('user_field.id',ondelete="CASCADE")))
        user_field : Optional['UserField']=Relationship(back_populates='owner_appointments')
        field_id: uuid.UUID = Field(sa_column=Column(ForeignKey('field.id', ondelete="CASCADE")))
        field: Optional['Fields'] = Relationship(back_populates='owner_appointments')
        court_id: uuid.UUID = Field(sa_column=Column(ForeignKey('court.id', ondelete="CASCADE")))
        court: Optional['Court'] = Relationship(back_populates='owner_appointments')
        invoices:List['Invoice']=Relationship(back_populates='appointment_owner')
        created_at:datetime=Field(default_factory=datetime.utcnow)
    



class AcademyCategory(SQLModel):
     name: str
     description_program: Optional[str] = None

    # Eligibility
     min_age: int
     max_age: int
     gender: str

    # Business
     amount_fee: Decimal
     billing_cycle: str      # monthly, weekly, yearly, one_time
    

    # Capacity
     max_players: Optional[int] = None

    # Enrollment
     enrollment_open: bool = True
     training_level: str  
    # beginner, intermediate, advanced, elite

     training_focus: Optional[str] = None

        
  
class AcademyRegister(SQLModel):
    name :str=Field(unique=True)
    programs:List[AcademyCategory]=Field(sa_column=Column(JSON))
    description:str|None=None
    city:str
    address:str 
    logo:str|None=None



class DaysOfWeek(SQLModel):
    day:str
    start_time:time 



     


  
  

 
class Academy(SQLModel, table=True):
    __tablename__ = "academy"
    __table_args__ = {"extend_existing": True}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    name:str=Field(unique=True)
    description:str|None=None
    city:str
    address:str 
    logo:str|None=None
    programs:List['ProgramAcademy']= Relationship(back_populates='academy')

    user_id: uuid.UUID = Field(sa_column=Column(ForeignKey("user.id"),unique=True))
    user: User=Relationship(back_populates='academies')


    created_at: datetime = Field(default_factory=datetime.utcnow)

    # relations
    subscriptions: List["Subscription"] = Relationship(back_populates="academy")
    membership: List["MemberAcademy"] = Relationship(back_populates="academy")


class KidAcademy(SQLModel,table=True):
    __tablename__='kid'
    __table_args__ = {"extend_existing": True}
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    birth_date:str 
    first_name:str 
    last_name:str
    gender:str 
    parent_id:Optional[uuid.UUID]=Field(foreign_key='user.id')
    parent:Optional['User']=Relationship(back_populates='kids')
    parent_field_id:Optional[uuid.UUID]=Field(foreign_key='user_field.id')
    parent_field:Optional['UserField']=Relationship(back_populates='kids')
    created_at:datetime = Field(default_factory=datetime.utcnow)
    membership: List["MemberAcademy"] = Relationship(back_populates="kid")

class Days(SQLModel):
    day_of_week:str 
    session_start:str


class Period(SQLModel):
    days:int 
    months:int

class KidsRegister(SQLModel):
    birth_date:str 
    name:str 
    last_name:str
    gender:str
    period:Period
    total_amount:Decimal
    days_session:list[Days]
    start_date:date
    end_date:date 


  

class ParentRegister(SQLModel):
    username: str = Field(unique=True, max_length=40, index=True)
    email: EmailStr = Field(unique=True, index=True, max_length=225)
    password: str = Field(min_length=8, max_length=40)
    
    address: str
    phone: str
    city: str
    country: str
    post_code:str
    register_as: str='parent'


class KidsEnroll(SQLModel):
    academy_id:uuid.UUID
    program_id:uuid.UUID
    billing_cycle:str 
    amount_period:Decimal
    kids:list[KidsRegister]=Field(sa_column=Column(JSON))

class EnrollementAcademy(SQLModel):
    parent_account:ParentRegister
    kids_enroll:KidsEnroll
   


    



class ProgramAcademy(SQLModel, table=True):
    __tablename__ = "program"
    __table_args__ = {"extend_existing": True}

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True
    )

    # Basic information
    name: str
    description: Optional[str] = None

    # Eligibility
    min_age: int
    max_age: int
    gender: str
   

    # Business
    amount_fee_period: Decimal
    sessions_per_week:int |None=None

    
   
    

    # Capacity
    max_players: Optional[int] = None

    # Enrollment
    enrollment_open: bool = True

    # Status
    status: str             # active, inactive, archived

    # Dates
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    training_level: str  
    # beginner, intermediate, advanced, elite

    training_focus: Optional[str] = None
    # technical, tactical, physical, goalkeeper, competition

   

    # Relationships
    academy_id: uuid.UUID = Field(foreign_key="academy.id")
    academy: "Academy" = Relationship(back_populates="programs")

    coach_id: Optional[uuid.UUID] = Field(
        default=None,
        foreign_key="user.id"
    )
    coach: Optional["User"] = Relationship(
        back_populates="programs"
    )

    membership: List["MemberAcademy"] = Relationship(
        back_populates="program"
    )

    subscriptions: List["Subscription"] = Relationship(
        back_populates="program"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow}
    )

class Subscription(SQLModel, table=True):
    __tablename__ = "subscription"
    __table_args__ = {"extend_existing": True}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # optional links (not required to be academy)
    academy_id: Optional[uuid.UUID] = Field(
        default=None,
        sa_column=Column(ForeignKey("academy.id", ondelete="CASCADE"))
    )
    academy:Optional['Academy']=Relationship(back_populates='subscriptions')
    program_id: Optional[uuid.UUID] = Field(
        default=None,
        sa_column=Column(ForeignKey("program.id", ondelete="CASCADE"))
    )
    program:Optional['ProgramAcademy']=Relationship(back_populates='subscriptions')

    user_id: Optional[uuid.UUID] = Field(sa_column=Column(ForeignKey("user.id")))
    user:Optional['User']=Relationship(back_populates='subscriptions')

    field_id: uuid.UUID = Field(sa_column=Column(ForeignKey("field.id")))
    field:Fields=Relationship(back_populates='subscriptions')
    plan_id:uuid.UUID=Field(sa_column=Column(ForeignKey("plan.id")))
    plan:'SubscriptionPlan'=Relationship(back_populates='subscriptions')
    court_id: uuid.UUID = Field(sa_column=Column(ForeignKey("court.id")))
    court:Court=Relationship(back_populates='subscriptions')
    billing_cycle:str

    start_date: date
    end_date: date
    duration:float
    payment_method:Optional[str]=Field(default=None)

    status: str = Field(default="draft")
    number_of_sessions:int
    days_of_week:list=Field(sa_column=Column(JSON))
    total_amount:Decimal = Field(default=Decimal('0.00'),
    sa_column=Column(Numeric(10, 2), nullable=False)
)
    amount_per_period:Decimal = Field(default=Decimal('0.00'),
    sa_column=Column(Numeric(10, 2), nullable=False)
)
    amount_session:Decimal = Field(default=Decimal('0.00'),
    sa_column=Column(Numeric(10, 2), nullable=False)
)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    sessions: List["SessionApp"] = Relationship(back_populates="subscription")
    invoices:List['Invoice']=Relationship(back_populates='subscription')
    approved_at:datetime|None=None


class DW(SQLModel):
    day_of_week:str
    session_start:str
class SubscriptionRegisterS(SQLModel):
    billing_cycle:str
    payment_method:str
   
    days_of_week:list[DW]=Field(sa_column=Column(JSON))
class SubscriptionSchedule(SQLModel, table=True):
    __tablename__ = "subscription_schedule"
    __table_args__ = {"extend_existing": True}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    subscription_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey("subscription.id", ondelete="CASCADE"))
    )

    days_of_week:List[dict]=Field(sa_column=Column(JSON))
 


class SessionApp(SQLModel,table=True):
    __table_args__ = {"extend_existing": True}
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True
    )
    time:time
    date:date
    status:str
    field_id: uuid.UUID = Field(sa_column=Column(ForeignKey("field.id")))
    field:Fields=Relationship(back_populates='sessions')
    court_id: uuid.UUID = Field(sa_column=Column(ForeignKey("court.id")))
    court:Court=Relationship(back_populates='sessions')

    subscription_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey('subscription.id', ondelete="CASCADE"))
    )
    subscription: Optional['Subscription'] = Relationship(back_populates='sessions')

class Period(SQLModel):
    months:int
    days:int

class MemberAcademy(SQLModel,table=True):
    __tablename__='member_academy'
    __table_args__ = {"extend_existing": True}
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True
    )
    academy_id: Optional[uuid.UUID] = Field(
        sa_column=Column(ForeignKey("academy.id", ondelete="CASCADE"))
    )

    kid_id: Optional[uuid.UUID] = Field(
        sa_column=Column(ForeignKey("kid.id", ondelete="CASCADE"))
    )
    kid:Optional['KidAcademy']=Relationship(back_populates='membership')
    academy:Optional['Academy']=Relationship(back_populates='membership')
    program_id:Optional[uuid.UUID] = Field(
        sa_column=Column(ForeignKey("program.id", ondelete="CASCADE"))
    )
    program:Optional['ProgramAcademy']=Relationship(back_populates='membership')
    start_date:date 
    end_date:date 
    billing_cycle:str 
    amount_period:Decimal 
    total_amount:Decimal
    session_number:int 
    days_session:list[dict]=Field(sa_column=Column(JSON))
  
   
    period:Optional[dict] = Field(default=None,
        sa_column=Column(JSON)
    )
      

    status: str = Field(default="pending")
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    invoices:List['Invoice']=Relationship(back_populates='member_academy')

class Amounts(SQLModel):
    number_of_sessions:int
    total_amount:Decimal
    amount_session:Decimal
    amount_per_period:Decimal


class SubscriptionRegister(SQLModel):
    start_date:date
    end_date:date 
    duration:int 
    field_id:uuid.UUID
    academy_id:uuid.UUID |None=None
    schedule:SubscriptionRegisterS
    amounts:Amounts

    field_name:str
    court_id:uuid.UUID
    plan_id:uuid.UUID
    program_id:uuid.UUID|None=None


    @field_validator('duration')
    @classmethod
    def validate_duration(cls,value:int):
        if value<0:
            raise ValueError('Invalid Duration')

        return value
        

class PaymentMethod(str,Enum):
    CARD="CARD"
    CASH="CASH"

class PaymentStatus(str,Enum):
    INITIATED = "INITIATED"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PENDING_CASH = "PENDING_CASH"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED" 




class InvoiceNotify(SQLModel,table=True):
    __table_args__ = {"extend_existing": True}
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True
    )
    ref_id:uuid.UUID 
    status:str='pending'
    type: str
    payer_id:uuid.UUID 
    payee_id:uuid.UUID
    create_at :datetime=Field(default_factory=datetime.utcnow)


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
  
    status:str 
   
    subscription_id: Optional[uuid.UUID]= Field(
        sa_column=Column(ForeignKey('subscription.id'))
    )
    subscription: Optional['Subscription'] = Relationship(back_populates='invoices')
    owner_platform_subscription: Optional['OwnerPlatformSubscription'] = Relationship(back_populates='invoices')
    owner_platform_subscription_id: Optional[uuid.UUID]= Field(
            sa_column=Column(ForeignKey('owner_platform_subscription.id'))
        )
   
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
    payment_method:str|None=None
    created_at:datetime=Field(default_factory=datetime.utcnow)
    updated_at:datetime=Field(default_factory=datetime.utcnow,sa_column_kwargs={"onupdate": datetime.utcnow})
    payments:List['Payment']=Relationship(back_populates='invoice')
    payer_id:Optional[uuid.UUID]=Field(default=None,foreign_key='user.id')
    payer:Optional['User']=Relationship(back_populates='invoices',  sa_relationship_kwargs={"foreign_keys": "[Invoice.payer_id]"})
    payer_field_id:Optional[uuid.UUID]=Field(default=None,foreign_key='user_field.id')
    payer_field:Optional['UserField']=Relationship(back_populates='invoices',  sa_relationship_kwargs={"foreign_keys": "[Invoice.payer_field_id]"})
    payee_id:Optional[uuid.UUID]=Field(default=None,foreign_key='user.id')
    payee:Optional['User']=Relationship(back_populates='invoices_payee',  sa_relationship_kwargs={"foreign_keys": "[Invoice.payee_id]"})
    payee_field_id:Optional[uuid.UUID]=Field(default=None,foreign_key='user_field.id')
    payee_field:Optional['UserField']=Relationship(back_populates='invoices_payee',  sa_relationship_kwargs={"foreign_keys": "[Invoice.payee_field_id]"})


class ErrorScheduler(SQLModel,table=True):
    __tablename__='error_schedule'
    __table_args__ = {"extend_existing": True}
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True
    )
    type:str 
    ref_id:uuid.UUID|None=None 
    error_message:str
    created_at:datetime=Field(default_factory=datetime.utcnow)





class PaymentRegister(SQLModel):
    method:str
    amount:float
    app_id:str









class PaymentPlanReg(SQLModel):
    allowed_methods:list=Field(sa_column=Column(JSON))
    first_payment_required:bool 

class FreezeReg(SQLModel):
    allowed:bool
    max_freezes_per_period:int
    max_freeze_days:int 
   


class BenefitsReg(SQLModel):
    applied_discount:int|None=None 
    base_discount:float|None=None
class PlansReg(SQLModel):
    name:str 
    type:str 
    session_price:float 
    mode:str
    max_sessions_per_week:int
    court_size:list[str]=Field(sa_column=Column(JSON))
    target_groups:list=Field(sa_column=Column(JSON))
    payment:PaymentPlanReg
    freeze:FreezeReg
    base_benefits:BenefitsReg


    

class Plan(SQLModel):
    name:str 
    type:str 
    session_price:float 
    mode:str
    max_sessions_per_week:int
    target_groups:list[str]=Field(sa_column=Column(JSON))
    court_size:list[str]=Field(sa_column=Column(JSON))
    final_price:float
    base_benefits:dict=Field(sa_column=Column(JSON))
   
class SubTypes(SQLModel):
    sub_types:List[PlansReg]=Field(sa_column=Column(JSON))
    

class PlanRegister(SQLModel):
    field_id:str 
    field_name:str
    plans:SubTypes





class SubscriptionPlan(Plan,table=True):
    __tablename__='plan'
    __table_args__ = {"extend_existing": True}
    id:uuid.UUID=Field(default_factory=uuid.uuid4,primary_key=True)
    status:str=Field(default='active')
    created_at:datetime=Field(default_factory=datetime.utcnow)
    freeze_plan:'FreezePlan'=Relationship(back_populates='plan')

    payment_plan:'PaymentPlan'=Relationship(back_populates='plan')
    field_id :uuid.UUID=Field(foreign_key='field.id')
    field :Fields=Relationship(back_populates='plans')
    subscriptions:'Subscription'=Relationship(back_populates='plan')
    

class PaymentPlan(PaymentPlanReg,table=True):
    __table_args__ = {"extend_existing": True}
    id:uuid.UUID=Field(default_factory=uuid.uuid4,primary_key=True)
    status:str=Field(default='active')
    plan_id:uuid.UUID=Field(foreign_key='plan.id',unique=True)
    plan :SubscriptionPlan=Relationship(back_populates='payment_plan')

    created_at:datetime=Field(default_factory=datetime.utcnow)

class FreezePlan(FreezeReg,table=True):
    __table_args__ = {"extend_existing": True}
    id:uuid.UUID=Field(default_factory=uuid.uuid4,primary_key=True)
    status:str=Field(default='active')
    created_at:datetime=Field(default_factory=datetime.utcnow)
    plan_id:uuid.UUID=Field(foreign_key='plan.id',unique=True)
    plan :SubscriptionPlan=Relationship(back_populates='freeze_plan')



class ProviderConnectionRequest(SQLModel, table=True):


    __tablename__='connection_request'
    __table_args__ = {"extend_existing": True}

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True
    )

    # Provider selected
    provider_name: str
    # SoccerPay / PaySecure
    provider_id:uuid.UUID
    user_id:uuid.UUID


    # Platform information
    platform_name: str

    business_type: str
    # marketplace / saas / other

    description: str

    website: Optional[str] = None


    # Owner/Admin information
    owner_name: str

    owner_email: str

    owner_phone: str


    # Business information
    country: str

    city: str

    business_address: str

    tax_id: Optional[str] = None

    registration_number: Optional[str] = None


    # Payment activity
    expected_monthly_volume: Optional[Decimal] = None

    average_transaction_amount: Optional[Decimal] = None

    currency: str
    # TND / EUR / USD


    # Request status
    status: str = "pending"
    user_id:Optional[uuid.UUID]|None=None
  


    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )

    updated_at: Optional[datetime] = None


    # Relationship
    permissions: List["ProviderPermissionRequest"] = Relationship(
        back_populates="connection_request"
    )
   
    provider_connections: List["ProviderConnection"] = Relationship(
            back_populates="connection_request"
        )

class ProviderPermissionRequest(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True
    )


    connection_request_id:uuid.UUID = Field(
        foreign_key="connection_request.id"
    )
    connection_request:'ProviderConnectionRequest'=Relationship(back_populates='permissions')


    permission_name: str
    # create_accounts
    # process_payments
    # transfer_money
    # receive_webhooks
    # view_transactions


    status: str = "pending"
    # pending
    # approved
    # rejected


    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )


class ProviderRegistration(SQLModel):

    # Provider selected
    provider_name: str
    # SoccerPay / PaySecure
    provider_id:uuid.UUID


    # Platform information
    platform_name: str

    business_type: str
    # marketplace / saas / other

    description: str

    website: Optional[str] = None


    # Owner/Admin information
    owner_name: str

    owner_email: str

    owner_phone: str


    # Business information
    country: str

    city: str

    business_address: str

    tax_id: Optional[str] = None

    registration_number: Optional[str] = None


    # Payment activity
    expected_monthly_volume: Optional[Decimal] = None

    average_transaction_amount: Optional[Decimal] = None

    currency: str
    permissions:List[str]=Field(sa_column=Column(JSON))
    # TND / EUR / USD



class ApproveConnection(SQLModel):
    req_id:uuid.UUID 
    permissions:List[str]=Field(sa_column=Column(JSON))



class ProviderConnection(SQLModel, table=True):

    __tablename__='provider_connection'
    __table_args__ = {"extend_existing": True}

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True
    )

    connection_request_id:uuid.UUID = Field(
            foreign_key="connection_request.id"
        )
    connection_request:'ProviderConnectionRequest'=Relationship(back_populates='provider_connections')
    provider_name: str

    account_id: str

    client_id: str

    secret_key: str

    webhook_url: Optional[str] = None

    webhook_secret: Optional[str] = None

    granted_permissions: list[str] = Field(
        sa_column=Column(JSON)
    )

    status: str = "active"

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )
    payments:List['Payment']=Relationship(back_populates='provider_connection')
    merchant_accounts:List['MerchantAccount']=Relationship(back_populates='provider_connection')
    onboardings:List['PaymentOnboardingRequest']=Relationship(back_populates='provider_connection')


class PaymentOnboardingRequest(SQLModel, table=True):

    __tablename__='onboarding'
    __table_args__ = {"extend_existing": True}

    id: uuid.UUID = Field(
            default_factory=uuid.uuid4,
            primary_key=True
        )
    

    provider_connection_id:Optional['uuid.UUID'] = Field(default=None,
            foreign_key="provider_connection.id"
        )
    provider_connection:Optional['ProviderConnection']=Relationship(back_populates='onboardings')
    owner_type:str
    provider_name:str 
    provider_id:uuid.UUID

   

    business_id: uuid.UUID


    business_name: str

    business_type: str

    country: str

    city: str

    business_address: Optional[str]


    website: Optional[str]|None=None


    tax_id: Optional[str]|None=None

    registration_number: Optional[str]|None=None


    owner_name: str

    owner_email: str

    owner_phone: str


    currency: str


    expected_monthly_volume: Optional[float]|None=None

    average_transaction_amount: Optional[float]|None=None


    status: str='pending'

    provider_application_id: Optional[str]|None=None

    rejection_reason: Optional[str]|None=None

    merchant_accounts:'MerchantAccount'=Relationship(back_populates='onboarding')



class MerchantAccount(SQLModel, table=True):
    __tablename__='merchant_account'
    __table_args__ = {"extend_existing": True}

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True
    )


    # The approved onboarding request
    onboarding_id: uuid.UUID = Field(
        foreign_key="onboarding.id",unique=True
    )
    onboarding:'PaymentOnboardingRequest'=Relationship(back_populates='merchant_accounts')


    # Which provider created this merchant
    provider_connection_id: uuid.UUID = Field(
        foreign_key="provider_connection.id"
    )
    provider_connection:'ProviderConnection'=Relationship(back_populates='merchant_accounts')


    # Business that owns this merchant account

    merchant_type: str
    # platform
    # field
    # academy


    merchant_id: uuid.UUID
    # field.id / academy.id / platform.id


    # ID returned by SoccerPay

    provider_merchant_id: str
    # Example:
    # merchant_soccerpay_001


    provider_name: str
    # SoccerPay


    status: str = "active"
    # active
    # suspended
    # closed


    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )


    updated_at: datetime = Field(
        default_factory=datetime.utcnow
    )
    payments:List['Payment']=Relationship(back_populates='merchant_account')




class PaymentOnboardingCreate(SQLModel):

    # Who is requesting merchant account

    owner_type: str
    # platform
    # field
    # academy
    # business


    owner_id: uuid.UUID
    provider_connection_id: uuid.UUID



    # Provider selection

    provider_name: str

    provider_id: uuid.UUID



    # Business information

    business_name: str = Field(
        min_length=2
    )


    business_type: str
    # marketplace
    # field
    # academy
    # saas
    # other


    description: str = Field(
        min_length=10
    )


    website:str|None = None



    # Contact information

    owner_name: str = Field(
        min_length=2
    )


    owner_email: EmailStr


    owner_phone: str = Field(
        min_length=8
    )



    # Location

    country: str = Field(
        min_length=2
    )


    city: str = Field(
        min_length=2
    )


    business_address: str = Field(
        min_length=5
    )



    # Legal information

    tax_id: Optional[str] = None


    registration_number: Optional[str] = None



    # Payment activity

    currency: str
    # TND
    # EUR
    # USD


    expected_monthly_volume: Optional[Decimal] = None


    average_transaction_amount: Optional[Decimal] = None

class Payment(SQLModel,table=True):
    __tablename__='payment'
    __table_args__ = {"extend_existing": True}
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True
    )
    method:str
    status:str
      # Merchant receiving the money
    merchant_account_id: Optional[uuid.UUID] = Field(
            foreign_key="merchant_account.id"
        )
    
    
    merchant_account:Optional['MerchantAccount']=Relationship(back_populates='payments')
    provider_connection_id: Optional[uuid.UUID] = Field(
            foreign_key="provider_connection.id"
        )
    provider_connection:Optional['ProviderConnection']=Relationship(back_populates='payments')
    
    amount:Decimal=Field(sa_column=Column(Numeric(10,2),nullable=False))
    provider:str
    transaction_ref:str|None=None
    paid_at:datetime|None=None 
    invoice_id:Optional[uuid.UUID]=Field(foreign_key='invoice.id')
    invoice:Optional['Invoice']=Relationship(back_populates='payments')
    provider_response: Optional[str] = None
    
   
    created_at:datetime=Field(default_factory=datetime.utcnow)
    updated_at:datetime=Field(default_factory=datetime.utcnow,sa_column_kwargs={"onupdate": datetime.utcnow})


class PaymentCreate(SQLModel):
    invoice_id:uuid.UUID
    payment_method:str 
    currency:str 
    provider_connection_id:uuid.UUID 
    provider:str 
    amount:Decimal





class Selected(SQLModel):
    date:date 
    time:time

class ReviewReschedule(SQLModel):
    sub_id:uuid.UUID
    selected:List[Selected]=Field(sa_column=Column(JSON))






class PlanPlatformRegister(SQLModel):
    name:str 
    price:Decimal 
    billing_cycle_days:list[str]=Field(sa_column=Column(JSON))
    max_courts_allowed:int

class PlansPltformRegisters(SQLModel):
    plans:List[PlanPlatformRegister]=Field(sa_column=Column(JSON))
      
      
class MyPlanPlatform(PlanPlatformRegister,table=True):
    __tablename__='platform_plan'
    __table_args__ = {"extend_existing": True}
    id:uuid.UUID=Field(default_factory=uuid.uuid4,primary_key=True)
    is_active:bool=False 
    created_at :datetime=Field(default_factory=datetime.utcnow)
    admin_id:uuid.UUID=Field(foreign_key='user.id')
    subscriptions_platform:List['OwnerPlatformSubscription']=Relationship(back_populates='platform_plan')


 

   






   

class OwnerPlatformRegister(SQLModel):
    plan_id:uuid.UUID 
    field_id:uuid.UUID
    start_date:date 
    duration:int=Field(gt=0) 
    end_date:date
   
   
    billing_cycle:str
    payment_method:str
            
              
    total_amount:Decimal = Field(gt=0)
    amount_per_period:Decimal = Field(gt=0) 
  
    

    
   

class OwnerPlatformSubscription(SQLModel, table=True):
    __tablename__ = 'owner_platform_subscription'
    __table_args__ = {"extend_existing": True}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
    # Linked to UserField (The venue owner)
    user_field_id: uuid.UUID = Field(foreign_key='user_field.id', ondelete="CASCADE", unique=True)
    user_field: Optional['UserField'] = Relationship(back_populates='subscriptions_platform')
    field_id:uuid.UUID

    # Linked to chosen plan from catalog
    platform_plan_id: uuid.UUID = Field(foreign_key='platform_plan.id')
    platform_plan: Optional[MyPlanPlatform] = Relationship(back_populates='subscriptions_platform')

    # Subscription State
    status: str = Field(default="INACTIVE")  # "ACTIVE", "PAST_DUE", "CANCELED"
    current_period_start: date
    current_period_end: date
    duration:int
    billing_cycle:str
    payment_method:Optional[str]=Field(default=None)
    
      
    total_amount:Decimal = Field(default=Decimal('0.00'),
        sa_column=Column(Numeric(10, 2), nullable=False)
    )
    amount_per_period:Decimal = Field(default=Decimal('0.00'),
        sa_column=Column(Numeric(10, 2), nullable=False)
    )
    invoices:List['Invoice']=Relationship(back_populates='owner_platform_subscription')
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)













   















'''


user register an academy 
player seek member ship 
acdmey set  schedule sub to   set subscripton to se field 
for each schedule we set sessions  

UserField
User  
Fields 
Appointment 
Team 
Player 
Game 
Stat
GameStat 
Academy 
Payment 
Subscription 
SubConfiguration
OwnerAppointment
MemberAcademy 
Membership
Notificatio 


User id name role player   register join team Memebrship Membership ==>Notifcation  notify Team ==>Team Respond ==>Notification==>Notify Player 
User id name role coach create Team select Field selcte slot  book single session  Appointment ==>Appointment state pend ==>Notifcation==>Notify Owner Field

Field Owner register field configure sub recieve reqs approve deny reciev payment 
Coach create Acdemy   set sub academy
Player join acdemy  coach accept 
Field Owner book Apppointment Apppintment owner user notifed 
Coach create a game 

Sub published User req to buy a sub Field owner decide 
landing page 
authenticate subsc ribe 




'''







    
    
    