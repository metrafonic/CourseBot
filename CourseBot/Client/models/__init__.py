from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import *
from sqlalchemy.orm import relationship
import datetime

engine = create_engine('sqlite:///database.db')
Base = declarative_base()

association_table = Table('association', Base.metadata,
    Column('sourse_id', String, ForeignKey('course.id')),
    Column('channel_id', Integer, ForeignKey('channel.id'))
)
class Lecture(Base):
    __tablename__ = "lecture"
    id = Column(Integer, primary_key=True)
    course_id = Column(String, ForeignKey('course.id'))
    audio = Column(String)
    camera = Column(String)
    screen = Column(String)
    combined = Column(String)
    length = Column(String)
    title = Column(String)
    lecturer = Column(String)
    released = Column(DateTime)

class Course(Base):
    __tablename__ = "course"
    id = Column(String, primary_key=True)
    name = Column(String)
    channels = relationship("Channel", secondary=association_table)
    lectures = relationship("Lecture", backref="course")
    added = Column(DateTime, default=datetime.datetime.now())

class Channel(Base):
    __tablename__ = "channel"
    id = Column(Integer, primary_key=True)

def init_db():
    Course.__table__.create(bind=engine, checkfirst=True)
    Channel.__table__.create(bind=engine, checkfirst=True)
    Lecture.__table__.create(bind=engine, checkfirst=True)
    association_table.create(bind=engine, checkfirst=True)