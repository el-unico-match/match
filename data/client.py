from settings import Settings
from sqlalchemy import create_engine
#from sqlalchemy.ext.declarative import declarative_base
#from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData,Table,Sequence,Column, ForeignKey, Integer, String
from sqlalchemy import MetaData
import databases

settings=Settings()	

DATABASE_URL = f"postgresql://{settings.db_credentials}@{settings.db_domain}:{settings.db_port}/{settings.db_name}"

database = databases.Database(DATABASE_URL)

engine = create_engine(DATABASE_URL)

metadata = MetaData()

#TABLE_ID = Sequence('matchs', start=1000)

profiles = Table(
    "profiles",
    metadata,
    Column("userid", String, primary_key=True),
    Column("username", String),
    Column("email", String),
    Column("description", String),
    Column("gender", String),
    Column("looking_for", String),
    Column("age", Integer),
    Column("education", String),
    Column("ethnicity", String)	
)

matchs = Table(
    "matchs",
    metadata,
#    Column("id", Integer,TABLE_ID,primary_key=True,server_default=TABLE_ID.next_value() ),#, autoincrement=True),	
    Column("id", Integer,primary_key=True ),#, autoincrement=True),	
    Column("userid_1", String),
    Column("qualification_1", String),
    Column("userid_2", String),
    Column("qualification_2", String)
)

metadata.create_all(engine)

#Base = declarative_base()

# Dependency
async def get_db():
    await database.connect()
    try:
        yield database
    finally:
        await database.disconnect()	