from models import User




from sqlmodel import SQLModel, Session, create_engine


from core.db import engine
from core.security import hash_password





# 2️⃣ Get a normal session
session = Session(engine)
print(engine.url)

# 3️⃣ Admin creation function
def register_provider(session: Session):
    hashed_password = hash_password("Amine9988man@s")
    provider_1 = User(
    username="SoccerPay",
    email="soccer_pay@gmail.com",
    hashed_password=hashed_password,
    city="Kasserine",
    address="9 Ibrahim str",
    country="Tunisia",
    code="1200",
    phone="4694444",
    is_superuser=False,
    is_active=True,
    register_as="provider",
    password='Amine9988man@s'
)
    session.add(provider_1)
    session.commit()
    session.refresh(provider_1)
    print(f"✅ Provider created! ID: {provider_1.id}, Email: {provider_1.email}")

    # confirm in DB
    check = session.query(User).filter_by(email="soccer_pay@gmail.com").first()
    if check:
        print("✅ Confirmed: Provider exists in DB")
    else:
        print("❌ Provider not found in DB")
    return provider_1
def register_provider1(session: Session):
    hashed_password = hash_password("Amine9988man@p")
    provider_2 = User(
    username="SecurePay",
    email="secure_pay@gmail.com",
    hashed_password=hashed_password,
    city="Kasserine",
    address="12 Ibrahim str",
    code="1200",
    country="Tunisia",
    phone="4690555",
    is_superuser=True,
    is_active=True,
    register_as="provider",
    password='Amine9988man@p'
)
    session.add(provider_2)
    session.commit()
    session.refresh(provider_2)
    print(f"✅ Provider created! ID: {provider_2.id}, Email: {provider_2.email}")

    # confirm in DB
    check = session.query(User).filter_by(email="secure_pay@gmail.com").first()
    if check:
        print("✅ Confirmed: Provider 2 exists in DB")
    else:
        print("❌ Provider 2 not found in DB")
    return provider_2


# 4️⃣ Run the admin registration
if __name__ == "__main__":
    register_provider(session)
    register_provider1(session)