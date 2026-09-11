
from .models import UserField,User,UserPublic,UserFieldPublic
from .core.debs import session_db

class MyProfile:
    def get_my_profile(self,current_profile:User|UserField):
        
        if isinstance(current_profile,User):
            user_public=UserPublic(      
                id=current_profile.id, 
                username=current_profile.username ,
                email=current_profile.email,
                register_as=current_profile.register_as,
                phone=current_profile.phone)
                
            return user_public
        elif isinstance(current_profile,UserField):
            user_field_public = UserFieldPublic(
            id=current_profile.id, 
            username=current_profile.username ,
            email=current_profile.email,
            register_as=current_profile.register_as,
            company_name=current_profile.company_name,
            company_code=current_profile.company_code,
            phone=current_profile.phone,
         

            )
               
            return user_field_public

