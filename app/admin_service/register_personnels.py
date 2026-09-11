from ..models import User,RegisterPersonnels 
from ..core.debs import session_db 
from ..core.security import hash_password







def register_personnels(session:session_db,personnels:RegisterPersonnels):

    

    for p in personnels.personnels:
        new_personnel = User(username=p.username,email=p.email,post_code=p.post_code,hashed_password=hash_password(p.password)
                             ,phone=p.phone,country=p.country,city=p.city,is_active=True,
                             is_superuser=True,register_as=p.register_as)

        session.add(new_personnel)
    session.commit()
    return {
        'message':'Personnel Registration Success'
    }
    


