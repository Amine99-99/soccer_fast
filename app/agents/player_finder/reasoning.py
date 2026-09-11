import numpy as np
from .observation import get_player,get_players_requesting
from ...core.debs import session_db
from sqlmodel import select
from ...models import User,Player,ReqJoinTeam,ReqJoinTeamGame







def analyse_player(observation):
    player = observation.get('player')
    stats = player.stats 
    scores=[]
    for s in stats:
        score_each_game_player=3*int(s.tactical_intelligence) + 2*int(s.physical_contribution) 
        +int(s.mental_attitude) +2*int(s.impact_on_the_game)+2*int(s.technical_execution)
        scores.append(score_each_game_player)
    return scores
    
def avarage_player(observation):
    player= observation.get('player')
    stats = player.stats 
   
    average_tactical_intelligence = sum(item['tactical_intelligence'] for item in stats)/len(stats)
    average_physical_contribution = sum(item['physical_contribution'] for item in stats)/len(stats)
    average_mental_attitude = sum(item['mental_attitude'] for item in stats)/len(stats)
    average_impact_on_the_game = sum(item['impact_on_the_game'] for item in stats)/len(stats)
    average_technical_execution = sum(item['technical_execution'] for item in stats)/len(stats)
    return {
        'average_tactical_intelligence':average_tactical_intelligence,
        'average_physical_contribution': average_physical_contribution,
        'average_mental_attitude':average_mental_attitude,
        'average_impact_on_the_game':average_impact_on_the_game,
        'average_technical_execution':average_technical_execution }

def players_analysis(observation):
    players=observation.get('players')
  
    score_players =[]
    for p in players:
        player_score=[]
        for s in p.stats:
            score_each_game_player=3*int(s.tactical_intelligence) + 2*int(s.physical_contribution) +int(s.mental_attitude) +2*int(s.impact_on_the_game)+2*int(s.technical_execution)
            player_score.append({
                'score':score_each_game_player,'id':p.id})
        score_players.append(player_score)
    return score_players 
def  average_players(observation):
    players=observation.get('players')
    average_players=[]
    for p in players:
        
        average={
            'id':p.id,
            'position':p.position,
            'name':p.name,
       'average_tactical_intelligence' : sum(item['tactical_intelligence'] for item in p.stats)/len(p.stats),
        'average_physical_contribution' : sum(item['physical_contribution'] for item in p.stats)/len(p.stats),
        'average_mental_attitude ': sum(item['mental_attitude'] for item in p.stats)/len(p.stats),
        'average_impact_on_the_game' : sum(item['impact_on_the_game'] for item in p.stats)/len(p.stats),
        'average_technical_execution' : sum(item['technical_execution'] for item in p.stats)/len(p.stats)}
        average_players.append(average)

    return average_players

def diciplinary_stat(observation):
   players=observation.get('players')
  
   score_players =[]
   for p in players:
        player_score=[]
        for s in p.stats:
            score_each_game_player=3*int(s.behavior) + 2*int(s.punctuality) +int(s.payment_status) +2*int(s.commitment)
            player_score.append({
                'score':score_each_game_player,'id':p.id})
        score_players.append(player_score)
   return score_players 

def  average_players(observation):
    players=observation.get('players')
    average_players=[]
    for p in players:
        
        average={
            'id':p.id,
            'position':p.position,
            'name':p.name,
       'average_behavior' : sum(item['behavior'] for item in p.stats)/len(p.stats),
        'average_puctuality' : sum(item['punctuality'] for item in p.stats)/len(p.stats),
        'average_payment_status': sum(item['payment_status'] for item in p.stats)/len(p.stats),
        'average_commitment' : sum(item['commitment'] for item in p.stats)/len(p.stats)}
      
        average_players.append(average)

    return average_players

def record_player_req(observation,session:session_db):
    player= observation.get('player')
    reqs = session.exec(select(ReqJoinTeam).where(ReqJoinTeam.player_id==player.id)).all()
    req_denied = [r for r in reqs if r.status_req=='denied']
    req_approved= [r for r in reqs if r.status_req=='approved']
    average_denied=len(req_denied)/len(reqs)
    average_approved = len(req_approved)

    average_reqs={
        'denied':len(req_denied),
        'approved':len(req_approved),
        'req_frequency':len(reqs)
    }
    return average_reqs


    






    




def reason_players(observation):


    pass 






'''


players same position  call stat see record in payment and games and teams 
  technical_execution: str
    tactical_intelligence: str
    physical_contribution: str
    mental_attitude: str
    impact_on_the_game: str
    player_id:uuid.UUID=Field(sa_column=Column(ForeignKey('player.id')))
    player:Optional['Player']=Relationship(back_populates='stats')

players non vacant posit
","","", "","","","offense"

'''