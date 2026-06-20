from sqlalchemy import create_engine

database_engine = create_engine('sqlite:///bot_database.db', echo=True)

database_connection = database_engine.connect()
