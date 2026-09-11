from ...models import User,ReqJoinTeamGame,ReqJoinTeam ,Player,Stat,Team
from ...core.debs import session_db
from sqlmodel import select 
from uuid import UUID








def get_player(event,session:session_db):
    player_id = event.payload['palyer_id']
    player = session.get(Player,UUID(player_id))


    return player



def get_players_requesting(event,session:session_db):
    team_id = event.payload['team_id']
    game_id = event.payload['game_id']
    
    player = get_player(event=event,session=session)
    reqs= session.exec(select(ReqJoinTeam).where((ReqJoinTeam.team_id ==UUID(team_id)) & (ReqJoinTeam.status_req=='pending'))).all()
    players= []
    for r in reqs :
        if r.player.position==player.position and r.player !=player :
            players.append(r.player)

    return players 











'''
flow  player req event dispatcher eventhandler agent tool result 
goal suggest the best player to the coach  
players list we have stats  
position same position 
player number left 
   technical_execution: str
    tactical_intelligence: str
    physical_contribution: str
    mental_attitude: str
    impact_on_the_game: str
    player_id:uuid.UUID=Field(sa_column=Column(ForeignKey('player.id')))
    player:Optional['Player']=Relationship(back_populates='stats')


'''





