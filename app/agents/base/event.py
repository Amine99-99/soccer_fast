from datetime import datetime



class Event:
    def __init__(self,event_type:str,event_task:str,event_id:str,payload:dict,timestamp:str|None=None):
        self.event_type=event_type 
        self.event_task=event_task
        self.event_id=event_id
        self.payload=payload
        self.timestamp = timestamp or datetime.utcnow().isoformat()
    def to_dict(self):
        return {
            'event_type':self.event_type,
            'event_task':self.event_task,
            'event_id':self.event_id,
            'payload':self.payload,
            'timestamp':self.timestamp
        }