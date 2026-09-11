from ..memory.vector_store import PlayerEvent
from ...core.debs import session_db
import uuid





def act_req_decision(decision):
    freq_denial=decision['denied']
    freq_approval = decision['approved']
    frequency_req = decision['frequency_rate']
    
    approval_rate=(freq_approval+5)/(frequency_req+5)
    if approval_rate>=0.75:
        return {
            'approval_rate':approval_rate,
            'agent_decision':'You can approve his request,the player has good approval rate for his previous requests'
        }
    elif 0.5<=approval_rate<0.75 :
          return {
            'approval_rate':approval_rate,
            'agent_decision':'You can wait and compare with other players  ,the player has medium approval rate for his previous requests'
        }
    else:
           return {
            'approval_rate':approval_rate,
            'agent_decision':'You can deny his request,the player has a poor approval rate for his previous requests'
        }
    
def add_player_event(event,decision,session:session_db):
     result =act_req_decision(decision)
     player_id = event.payload['player_id']
     print(result,'result before committing')
     event_id= event.event_id 
     decision_agent=result['agent_decision']
     rate_approval = result['approval_rate']
     new_event_player= PlayerEvent(player_id=uuid.UUID(player_id),event_id=event_id,decision=decision_agent,rate=rate_approval)
     session.add(new_event_player)
     session.commit()
     session.refresh(new_event_player)
     print(new_event_player.id,'id event player')
     return new_event_player







    
