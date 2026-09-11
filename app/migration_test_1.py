from sqlmodel import create_engine,inspect ,Session,select
from models import Team


engine = create_engine("sqlite:///database.db")

inspector = inspect(engine)
print('test 1 migration',inspector.get_table_names())

columns = inspector.get_columns('profile_db')
for column in columns:
    print(column['name'],column['type'])

with Session(engine) as s:
    statement = select(Team)
    teams= s.exec(statement).all()
    pass