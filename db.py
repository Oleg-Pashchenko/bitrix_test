import os
import dotenv
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime

dotenv.load_dotenv()

Base = declarative_base()


class Chat(Base):
    __tablename__ = 'chats'
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_name = Column(String)
    guest_name = Column(String)
    messages = relationship("Message", back_populates="chat")


class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(Integer, ForeignKey('chats.id'))
    date = Column(DateTime)
    text = Column(String)
    is_incoming = Column(Boolean)
    chat = relationship("Chat", back_populates="messages")


DATABASE_URL = (
    f"postgresql://{os.getenv('POSTGRESQL_USER')}:{os.getenv('POSTGRESQL_PASSWORD')}@{os.getenv('POSTGRESQL_HOST')}:"
    f"{os.getenv('POSTGRESQL_PORT')}/{os.getenv('POSTGRESQL_DBNAME')}")

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


def save(chat_name, guest_name, messages_arr):
    chat = session.query(Chat).filter_by(chat_name=chat_name, guest_name=guest_name).first()
    if not chat:
        chat = Chat(chat_name=chat_name, guest_name=guest_name)
        session.add(chat)
        session.commit()

    messages = [
        Message(
            chat_id=chat.id,
            date=datetime.datetime.fromisoformat(message['date']),
            text=message['text'],
            is_incoming=message['is_incoming']
        )
        for message in messages_arr
    ]
    session.bulk_save_objects(messages)
    session.commit()
    print(f"Saved chat: {chat_name} ({guest_name}) with {len(messages_arr)} messages.")

