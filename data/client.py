from settings import Settings
from sqlalchemy import create_engine
from sqlalchemy import MetaData, Table, Column
from sqlalchemy import Integer, String, Boolean, Float, DateTime
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
    Column("gender", String),
    Column("looking_for", String),
    Column("age", Integer),
    Column("education", String),
    Column("ethnicity", String),
    Column("is_match_plus",Boolean),
    Column("latitud",Float),
    Column("longitud",Float),

    Column("last_like_date", DateTime),
    Column("like_counter", Integer),
    Column("superlike_counter", Integer)
)


# filters = Table(
#     "filters",
#     metadata,
#     Column("userid", String, primary_key=True),
#     Column("gender", String),
#     Column("age_from", Integer),
#     Column("age_to", Integer),
#     Column("education", String),
#     Column("ethnicity", String),
#     Column("latitud",Integer),
#     Column("longitud",Integer)
# )

matchs = Table(
    "matchs",
    metadata,
    Column("id", Integer, primary_key=True),#, autoincrement=True),	
    Column("userid_qualificator", String),
    Column("userid_qualificated", String),
    Column("qualification", String),
    Column("qualification_date", DateTime),
    Column("last_message_date", DateTime),
    Column("blocked", Boolean)
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