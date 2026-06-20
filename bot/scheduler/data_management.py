from sqlalchemy import MetaData, Table, Column

from database_management.database_engine import(
    database_connection
)

meta = MetaData()

schedule = Table(
    name='schedule'
)

