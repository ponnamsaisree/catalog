import sys
import os
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False)


class Apssdc(Base):
    __tablename__ = 'apssdc_name'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref="apssdc_name")

    @property
    def serialize(self):
        """Return objects data in easily serializeable formats"""
        return {
            'name': self.name,
            'id': self.id
        }


class Team_Details(Base):
    __tablename__ = 'team_details'
    id = Column(Integer, primary_key=True)
    team_name = Column(String, nullable=False)
    description = Column(String(150))
    team_count = Column(Integer)
    apssdc_name_id = Column(Integer, ForeignKey('apssdc_name.id'))
    apssdc_name = relationship(
        Apssdc, backref=backref('team_details', cascade='all, delete'))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref="team_details")

    @property
    def serialize(self):
        """Return objects data in easily serializeable formats"""
        return {
            'team_name': self. team_name,
            'description': self. description,
            'team_count': self. team_count,
            'id': self. id
        }

eng = create_engine('sqlite:///apssdc_db.db')
Base.metadata.create_all(eng)
