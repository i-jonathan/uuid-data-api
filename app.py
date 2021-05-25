import os
import uuid
from datetime import datetime

from sqlalchemy import create_engine, Table, Column, DateTime, String, Integer, MetaData, select
from sqlalchemy_utils import database_exists, create_database


def connect_database(table: str, user: str, password: str):
    url = f'postgresql+psycopg2://{user}:{password}@localhost:5432/{table}'
    # Echo set to True to basically enable verbose mode
    engine = create_engine(url, echo=True)
    # check if database exists before attempting creation
    if not database_exists(url):
        create_database(engine.url)
    
    return engine


# Create environmental variables database_name, db_user and db_pass.
table_name = os.getenv('database_name')
db_user = os.getenv('db_user')
db_pass = os.getenv('db_pass')

db_engine = connect_database(table_name, db_user, db_pass)
connection = db_engine.connect()


def create_table(engine):
    meta_data = MetaData()
    # data variable specifies the structure of the table to be created in our postgres database
    data = Table(
        'data', meta_data,
        Column('id', Integer, primary_key=True),
        Column('created', DateTime),
        Column('uuid', String)
    )
    # No need to check if table exists since a check is in the create_all function
    meta_data.create_all(engine)
    return data


def add_data(to_table):
    # insert
    insert_data = to_table.insert().values(created=datetime.now(), uuid=uuid.uuid4())
    connection.execute(insert_data)


def fetch_format_data(from_table) -> dict:
    # Fetch all data from the database and appropriately format to the proper return structure
    selection = select(from_table)
    response = connection.execute(selection)
    all_data = {}
    for row in reversed(list(response)):
        all_data[str(row[1])] = row[2]
    
    return all_data
