'''from typing import Annotated, Optional, List,Literal
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





class Role(str, Enum):
    coach = 'coach_captain'
    player = 'player'
    fan = 'fan'
    journalist = 'journalist'


class CourtRegister(SQLModel):
   
    type_of_court: str
    opening_days: list[str]
    start_hour: time
    end_hour: time
    session_time: float
    court_size:str 
    session_price:float


class Court(CourtRegister,table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    type_of_court: str
    opening_days: list[str] = Field(sa_column=Column(JSON))
    start_hour: time
    end_hour: time
    session_time: float
    field_id:uuid.UUID=Field(sa_column=Column(ForeignKey('field.id', ondelete="CASCADE")))
    field :'Fields'=Relationship(back_populates='courts')
    appointments:List['Appointment']=Relationship(back_populates='court')
    sessions:List['SessionApp']=Relationship(back_populates='court')
    subscriptions:List['Subscription'] = Relationship(back_populates='court')


class FieldsRegister(SQLModel):
    courts: List[CourtRegister] = Field(sa_column=Column(JSON))
    number_of_courts: str
    field_name:str
    address:str
    city:str
    postal_code:str


class Fields(SQLModel, table=True):
    __tablename__ = 'field'

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    courts: List['Court']=Relationship(back_populates='field',
        sa_relationship_kwargs={"cascade": "all,delete-orphan"})
    number_of_courts: str
    field_name:str
    address:str
    city:str
    postal_code:str
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
    phone: str
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
    teams:List['Team']=Relationship(back_populates='user', sa_relationship_kwargs={"cascade": "all,delete-orphan"})
    reqs_game:List['RequestGameJoin']=Relationship(back_populates='user')
    games:List['Game']=Relationship(back_populates='user', sa_relationship_kwargs={"cascade": "all,delete-orphan"})
    reqs_transfer:List['RequestTransfer']=Relationship(back_populates='user')
    game_stats:List['GameStat']=Relationship(back_populates='user')
    notifications : List['Notification']=Relationship(back_populates='user', sa_relationship_kwargs={"foreign_keys": "[Notification.user_id]"})
    sent_notifications : List['Notification']=Relationship(back_populates='sender', sa_relationship_kwargs={"foreign_keys": "[Notification.sender_id]"})

    subscriptions: List["Subscription"] = Relationship(back_populates="user")
    academies: List["Academy"] = Relationship(back_populates="user")
 
    programs:List['ProgramAcademy']=Relationship(back_populates='coach')
    kids:List['KidAcademy']=Relationship(back_populates='parent')
    invoices:List['Invoice']=Relationship(back_populates='user')


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

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    company_name: str = Field(max_length=200)
    company_code: str = Field(max_length=100)

    address: str
    phone: str
    city: str
    country: str

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
    invoices:List['Invoice']=Relationship(back_populates='user_field')
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
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
    
    status: str | None = 'pending'
  
    coach_name:str
    coach_id:str 
    coach_email:str 
    team_name:str 
    user_id:Optional[uuid.UUID]=Field(sa_column=Column(ForeignKey('user.id',ondelete="CASCADE")))
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



class Appointment(AppointmentBase, table=True):
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
    payment_method:str
    field: Optional['Fields'] = Relationship(back_populates='appointments')
    game_id :Optional[uuid.UUID]=Field(sa_column=Column(ForeignKey('game.id',ondelete="SET NULL")))

    game: Optional['Game'] = Relationship(
        back_populates='appointments',
        
    )
    
    
  


class PictureProfile(SQLModel):
    file: UploadFile


class PictureProfileDB(SQLModel, table=True):
    __tablename__ = 'profile_db'

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
      
        court_id:str
class AppointmentRegisterUpdate(SQLModel):
        date:date
        time:time
        field_id:str
        court_id:str 
        id:str
class AppointmentOwner(AppointmentRegisterOwner,table=True):
        id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
        status:Optional[str]=Field(default=None)
        user_field_id : uuid.UUID=Field(sa_column=Column(ForeignKey('user_field.id',ondelete="CASCADE")))
        user_field : Optional['UserField']=Relationship(back_populates='owner_appointments')
        field_id: uuid.UUID = Field(sa_column=Column(ForeignKey('field.id', ondelete="CASCADE")))
        field: Optional['Fields'] = Relationship(back_populates='owner_appointments')



class AcademyCategory(SQLModel):
    age_range:str
    gender:str 
  
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

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    name:str=Field(unique=True)
    description:str|None=None
    city:str
    address:str 
    logo:str|None=None
    programs:List['ProgramAcademy']= Relationship(back_populates='academy')

    user_id: uuid.UUID = Field(sa_column=Column(ForeignKey("user.id")))
    user: User=Relationship(back_populates='academies')


    created_at: datetime = Field(default_factory=datetime.utcnow)

    # relations
    subscriptions: List["Subscription"] = Relationship(back_populates="academy")
    membership: List["MemberAcademy"] = Relationship(back_populates="academy")


class KidAcademy(SQLModel,table=True):
    __tablename__='kid'
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

class KidsRegister(SQLModel):
    birth_date:str 
    first_name:str 
    last_name:str
    gender:str 

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

class EnrollmentAcademy(SQLModel):
    parent_account:ParentRegister
    kids:list[KidsRegister]=Field(sa_column=Column(JSON))


    



class ProgramAcademy(SQLModel, table=True):
    __tablename__ = "program"

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
    amount_fee: Decimal
    billing_cycle: str      # monthly, weekly, yearly, one_time
    currency: str = "TND"

    # Capacity
    max_players: Optional[int] = None

    # Enrollment
    enrollment_open: bool = True

    # Status
    status: str             # active, inactive, archived

    # Dates
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    name:str
    description:str 

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

    memberships: List["MemberAcademy"] = Relationship(
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

    start_date: date
    end_date: date
    duration:float

    status: str = Field(default="draft")
    number_of_sessions:int
    days_of_week:list=Field(sa_column=Column(JSON))

    created_at: datetime = Field(default_factory=datetime.utcnow)
    sessions: List["SessionApp"] = Relationship(back_populates="subscription")


class DW(SQLModel):
    day_of_week:str
    session_start:str
class SubscriptionRegisterS(SQLModel):
    number_of_sessions:str
    days_of_week:list[DW]=Field(sa_column=Column(JSON))
class SubscriptionSchedule(SQLModel, table=True):
    __tablename__ = "subscription_schedule"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    subscription_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey("subscription.id", ondelete="CASCADE"))
    )

    days_of_week:List[dict]=Field(sa_column=Column(JSON))
 


class SessionApp(SQLModel,table=True):
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


class MemberAcademy(SQLModel,table=True):
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

    status: str = Field(default="pending")
    joined_at: datetime = Field(default_factory=datetime.utcnow)


class SubscriptionRegister(SQLModel):
    start_date:date
    end_date:date 
    duration:int 
    field_id:str
    academy_id:str |None=None
    schedule:SubscriptionRegisterS

    field_name:str
    court_id:str
    plan_id:str
    program_id:str


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

class Payment(SQLModel,table=True):
    __tablename__='payment'
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True
    )
    method:str
    status:PaymentStatus
    amount:Decimal=Field(sa_column=Column(Numeric(10,2),nullable=False))
    provider:str
    transaction_ref:str|None=None
    paid_at:datetime|None=None 
    invoice_id:Optional[uuid.UUID]=Field(foreign_key='invoice.id')
    invoice:Optional['Invoice']=Relationship(back_populates='payments')
    
   
    created_at:datetime=Field(default_factory=datetime.utcnow)
    updated_at:datetime=Field(default_factory=datetime.utcnow,sa_column_kwargs={"onupdate": datetime.utcnow})


class Invoice(SQLModel,table=True):
    __tablename__='invoice'
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
    invoice_type:str
    ref_id :str 
    issue_date:date 
    due_date:date 
    created_at:datetime=Field(default_factory=datetime.utcnow)
    updated_at:datetime=Field(default_factory=datetime.utcnow,sa_column_kwargs={"onupdate": datetime.utcnow})
    payments:List['Payment']=Relationship(back_populates='invoice')
    user_id:Optional[uuid.UUID]=Field(default=None,foreign_key='user.id')
    user:Optional['User']=Relationship(back_populates='invoices')
    user_field_id:Optional[uuid.UUID]=Field(default=None,foreign_key='user_field.id')
    user_field:Optional['UserField']=Relationship(back_populates='invoices')




class PaymentRegister(SQLModel):
    method:str
    amount:float
    app_id:str









class PaymentPlanReg(SQLModel):
    allowed_methods:list=Field(sa_column=Column(JSON))
    first_payment_required:bool 

class FreezeReg(SQLModel):
    allowed:bool
    max_freeze_days:int 
    max_freezes_per_period:int


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
    id:uuid.UUID=Field(default_factory=uuid.uuid4,primary_key=True)
    status:str=Field(default='active')
    created_at:datetime=Field(default_factory=datetime.utcnow)
    freeze_plan:'FreezePlan'=Relationship(back_populates='plan')
    payment_plan:'PaymentPlan'=Relationship(back_populates='plan')
    field_id :uuid.UUID=Field(foreign_key='field.id')
    field :Fields=Relationship(back_populates='plans')
    subscriptions:'Subscription'=Relationship(back_populates='plan')

class PaymentPlan(PaymentPlanReg,table=True):
    id:uuid.UUID=Field(default_factory=uuid.uuid4,primary_key=True)
    status:str=Field(default='active')
    plan_id:uuid.UUID=Field(foreign_key='plan.id',unique=True)
    plan :SubscriptionPlan=Relationship(back_populates='payment_plan')

    created_at:datetime=Field(default_factory=datetime.utcnow)

class FreezePlan(FreezeReg,table=True):
    id:uuid.UUID=Field(default_factory=uuid.uuid4,primary_key=True)
    status:str=Field(default='active')
    created_at:datetime=Field(default_factory=datetime.utcnow)
    plan_id:uuid.UUID=Field(foreign_key='plan.id',unique=True)
    plan :SubscriptionPlan=Relationship(back_populates='freeze_plan')













'''







    
    
    