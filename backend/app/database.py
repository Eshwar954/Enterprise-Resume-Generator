from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,DeclarativeBase

DATABASE_URL="sqlite:///database.db"
engine = create_engine(DATABASE_URL)
Session_local=sessionmaker(bind=engine,autoflush=False,autocommit=False)

class Base(DeclarativeBase):
    pass
def get_db():
    db=Session_local()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)
