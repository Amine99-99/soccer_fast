from models import User




from sqlmodel import SQLModel, Session, create_engine


from core.db import engine
from core.security import hash_password





# 2️⃣ Get a normal session
session = Session(engine)
print(engine.url)

# 3️⃣ Admin creation function
def register_admin_amine(session: Session):
    hashed_password = hash_password("Amine9988man@8")
    admin = User(
    username="Amine10",
    email="mansouriamine77@gmail.com",
    hashed_password=hashed_password,
    city="Kasserine",
    address="9 Ibrahim str",
    code="1200",
    phone="46903827",
    country='Tunisia',
    is_superuser=True,
    is_active=True,
    register_as="admin",
    password='Amine9988man@8'
)
    session.add(admin)
    session.commit()
    session.refresh(admin)
    print(f"✅ Admin created! ID: {admin.id}, Email: {admin.email}")

    # confirm in DB
    check = session.query(User).filter_by(email="mansouriamine77@gmail.com").first()
    if check:
        print("✅ Confirmed: Admin exists in DB")
    else:
        print("❌ Admin not found in DB")
    return admin

# 4️⃣ Run the admin registration
if __name__ == "__main__":
    register_admin_amine(session)