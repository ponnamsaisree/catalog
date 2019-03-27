from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from setup_file import *

engine = create_engine('sqlite:///apssdc_db.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Existing Apssdc delete
session.query(Apssdc).delete()
# Existing Team_Details delete
session.query(Team_Details).delete()
# Existing Team_Details delete.
session.query(User).delete()

# user data
User1 = User(name="Sai Sree", email="ponnamsaisree@gmail.com",)
session.add(User1)
session.commit()
print ("User added successfully")
# sample data
Apssdc_1 = Apssdc(name="CSE", user_id=1)
session.add(Apssdc_1)
session.commit()

Apssdc_2 = Apssdc(name="ECE", user_id=1)
session.add(Apssdc_2)
session.commit()

Apssdc_3 = Apssdc(name="CIVIL", user_id=1)
session.add(Apssdc_3)
session.commit()

Apssdc_4 = Apssdc(name="MECHANICAL", user_id=1)
session.add(Apssdc_4)
session.commit()

Apssdc_5 = Apssdc(name="EEE", user_id=1)
session.add(Apssdc_5)
session.commit()
# Using different Teams for details
Team_1 = Team_Details(team_name="Python",
                      description="Covering Python Basics"
                      "and Advanced Concepts",
                      team_count="26",
                      apssdc_name_id=1,
                      user_id=1)
session.add(Team_1)
session.commit()

Team_2 = Team_Details(team_name="Android", description="Develop Android Apps",
                      team_count="30",
                      apssdc_name_id=2,
                      user_id=1)
session.add(Team_2)
session.commit()

Team_3 = Team_Details(team_name="PWA",
                      description="Developing Web Apps",
                      team_count="15",
                      apssdc_name_id=3,
                      user_id=1)
session.add(Team_3)
session.commit()

Team_4 = Team_Details(team_name="SCI",
                      description="SCI Projects ",
                      team_count="16",
                      apssdc_name_id=4,
                      user_id=1)
session.add(Team_4)
session.commit()

Team_5 = Team_Details(team_name="IOT",
                      description="IOT Projects",
                      team_count="20",
                      apssdc_name_id=5, user_id=1)
session.add(Team_5)
session.commit()
print("data has been inserted sucessfully ")
