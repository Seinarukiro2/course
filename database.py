from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Создаем экземпляр базового класса
Base = declarative_base()


# Определяем таблицу User
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, unique=True)
    name = Column(String)
    test_counter = Column(Integer, default=0)
    payment_status = Column(Boolean, default=False)


# Создаем базу данных
engine = create_engine("sqlite:///users.db")
Base.metadata.create_all(engine)

# Создаем сессию для взаимодействия с базой данных
Session = sessionmaker(bind=engine)
session = Session()
