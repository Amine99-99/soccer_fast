@auth.post('/register',response_model=User,status_code=201)
def register(session:session_db,user_register:UserRegister):
    user_e  = get_user_by_email(session=session,email=user_register.email)
    user_d = get_active_user(session=session,email=user_register.email)
    
    print('user register is ',list(user_register))
    
    if user_e:
          print("User already registred")
          raise HTTPException(
            status_code=400,
            detail='User Already Registred'
        )
   
    token_verification_time= time_veri
    token_verif_ = generate_token_verification_token({'email':user_register.email},timedelta(minutes=token_verification_time))
    verification_url = f'{settings.FRONTEND_HOST}/verify_token?token={token_verif_}'
    if user_d :
          subject_v=f"New nevrification link for {settings.PROJECT_NAME}"
          html_content = f""" 
                   <h3>Welcome to {settings.PROJECT_NAME}</h3>
                     <p>Please click the link below to verify your email:</p>
                  <a href="{verification_url}">{verification_url}Verify Email</a> """
          send_email_of_verification(subject=subject_v,html_content=html_content,email_to=user_register.email)
          return {
                    "message":"We sent you new verification link."
          }
    user_create = UserCreate.model_validate(user_register)
    user=create_user(session=session,user_create=user_create)
    token_verif = generate_token_verification_token({'email':user.email},timedelta(minutes=token_verification_time))
    verification_url = f'{settings.FRONTEND_HOST}/verify_token?token={token_verif}'
    print('url',verification_url)
 
    if not user_e or not user_d:
        
    
        subject=f"Verify your account for {settings.PROJECT_NAME}"
        html_content = f""" 
                   <h3>Welcome to {settings.PROJECT_NAME}</h3>
                     <p>Please click the link below to verify your email:</p>
                  <a href="{verification_url}">{verification_url}Verify Email</a> """
        send_email_of_verification(subject=subject,html_content=html_content,email_to=user.email)
        return {

        "message":"User registered successfully Please check your email to verify your account."
            

        
    }
 

@auth.post('/verify_token')
def verify(token:str,session:session_db):
     print('recieved',token)
     user_email = verify_token(token=token)
     print('em',user_email)
     user = session.query(User).filter(User.email == user_email).first()
     user_field = session.query(UserField).filter(UserField.email==user_email).first()
     print('user is',user,'userfield is',user_field)
     if not user and  not user_field:
          raise HTTPException(
               status_code=401,
               detail='Invalid token'
          )
     if user:
       user.is_active=True 
     elif user_field:
       user_field.is_active=True
     
     
     session.commit()
     return {
          'message':'User Successflly activated'
     }


@auth.post('/register_field',response_model=UserField,status_code=201)
def register_field(session:session_db,user_field:FieldRegister):
    user_e  = get_field_by_email(session=session,email=user_field.email)
    user_d = get_active_field(session=session,email=user_field.email)

    
    print('user register is ',list(user_field))
    if user_e:
          print("User already registred")
          raise HTTPException(
            status_code=400,
            detail='User Already Registred'
        )
       
    token_verification_time= time_veri
    token_verif_ = generate_token_verification_token({'email':user_field.email},timedelta(minutes=token_verification_time))
    verification_url = f'{settings.FRONTEND_HOST}/verify_token?token={token_verif_}'
    if user_d :
          subject_v=f"New nevrification link for {settings.PROJECT_NAME}"
          html_content = f""" 
                   <h3>Welcome to {settings.PROJECT_NAME}</h3>
                     <p>Please click the link below to verify your email:</p>
                  <a href="{verification_url}">{verification_url}Verify Email</a> """
          send_email_of_verification(subject=subject_v,html_content=html_content,email_to=user_field.email)
          return {
                    "message":"We sent you new verification link."
          }
 
   
    user=create_user_field(session=session,field_create=user_field)
    token_verif = generate_token_verification_token({'email':user.email},timedelta(minutes=token_verification_time))
    verification_url = f'{settings.FRONTEND_HOST}/verify_token?token={token_verif}'
    print('url',verification_url)
    if not user_e or not user_d:
        
    
        subject=f"Verify your account for {settings.PROJECT_NAME}"
        html_content = f""" 
                   <h3>Welcome to {settings.PROJECT_NAME}</h3>
                     <p>Please click the link below to verify your email:</p>
                  <a href="{verification_url}">{verification_url}Verify Email</a> """
        send_email_of_verification(subject=subject,html_content=html_content,email_to=user.email)
        return {

        "message":"User registered successfully Please check your email to verify your account."
      }




