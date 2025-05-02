import pandas as pd
import urllib
import datetime
import pyodbc

from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Connection to normalized database (UKRoad)
conn_string_db = "Driver={ODBC Driver 17 for SQL Server};Server=NICK_LENOVO_LAP\\SQLEXPRESS;Database=UKRoad;Trusted_Connection=yes;"
conn_string_db = urllib.parse.quote_plus(conn_string_db)
conn_string_db = "mssql+pyodbc:///?odbc_connect=%s" % conn_string_db

# Connection to dimensional database (UKRoadDim)
conn_string_dw = "Driver={ODBC Driver 17 for SQL Server};Server=NICK_LENOVO_LAP\\SQLEXPRESS;Database=UKRoadDim;Trusted_Connection=yes;"
conn_string_dw = urllib.parse.quote_plus(conn_string_dw)
conn_string_dw = "mssql+pyodbc:///?odbc_connect=%s" % conn_string_dw

# ORM Base
class Base(DeclarativeBase):
    pass

class DimRoad(Base):
    __tablename__ = 'DimRoad'
    Accident_Index = Column(String(255), primary_key=True, autoincrement=False)
    First_Road_Number = Column(Integer)
    Second_Road_Number = Column(Integer)
    Police_Force = Column(String(255))
    Local_Authority_District = Column(String(255))
    Local_Authority_Highway = Column(String(255))
    Road_Type = Column(String(255))
    Speed_limit = Column(Integer)
    Junction_Detail = Column(String(255))
    Junction_Control = Column(String(255))
    Pedestrian_Crossing_Human_Control = Column(String(255))
    Pedestrian_Crossing_Physical_Facilities = Column(String(255))
    Carriageway_Hazards = Column(String(255))

def pipe_Road(conStrdb, conStrdw):
    engine_db = create_engine(conStrdb)
    sqlQuery = '''
    SELECT a.Accident_Index, a.[1st_Road_Number], a.[2nd_Road_Number], a.Police_Force,
           p.Local_Authority_District, p.Local_Authority_Highway, a.Road_Type,
           a.Speed_limit, a.Junction_Detail, a.Junction_Control, a.Pedestrian_Crossing_Human_Control,
           a.Pedestrian_Crossing_Physical_Facilities, a.Carriageway_Hazards
    FROM dbo.Accidents a, dbo.Police p
    WHERE a.Police_Force = p.Police_Force
    '''
    dFrame = pd.read_sql_query(sqlQuery, engine_db)

    print(f"Loaded {len(dFrame)} rows from Accident and Police table")
    print(dFrame.head())

    # rename 1st_Road_Number & 2nd_Road_Number to call below - wanting to test to see if this works to match what I am naming columns
    # this worked so will keep, but could also just call 1st_Road_Number & 2nd_Road_Number below in quotes
    dFrame.rename(columns={'1st_Road_Number': 'First_Road_Number', '2nd_Road_Number': 'Second_Road_Number'}, inplace=True)
    # Replace NaN with None - this is needed from error given initially
    # this tests if there is nan data and replaces with None
    # This is needed from what I saw online because SQLAlchemy cannot handle NaN from pandas properly.
    # SQLAlchemy instead expects None which is mapped to NULL in SQL Server
    dFrame = dFrame.where(pd.notnull(dFrame), None)

    engine_dw = create_engine(conStrdw)

    Session = sessionmaker(bind=engine_dw)
    session = Session()

    counter = 0
    for _, row in dFrame.iterrows():
        # still got error from just having code above
        # this is enforcing what I did above but with the iterrows function since I was getting a similar error
        # this tests if there is nan data and replaces with None
        # This is needed from what I saw online because SQLAlchemy cannot handle NaN from pandas properly.
        # SQLAlchemy instead expects None which is mapped to NULL in SQL Server
        row = row.where(pd.notnull(row), None)
        if not session.query(DimRoad).filter_by(
                Accident_Index=row['Accident_Index']
        ).first():
            new_record = DimRoad(
                Accident_Index=row['Accident_Index'],
                First_Road_Number=row['First_Road_Number'],
                Second_Road_Number=row['Second_Road_Number'],
                Police_Force=row['Police_Force'],
                Local_Authority_District=row['Local_Authority_District'],
                Local_Authority_Highway=row['Local_Authority_Highway'],
                Road_Type=row['Road_Type'],
                Speed_limit=row['Speed_limit'],
                Junction_Detail=row['Junction_Detail'],
                Junction_Control=row['Junction_Control'],
                Pedestrian_Crossing_Human_Control=row['Pedestrian_Crossing_Human_Control'],
                Pedestrian_Crossing_Physical_Facilities=row['Pedestrian_Crossing_Physical_Facilities'],
                Carriageway_Hazards=row['Carriageway_Hazards']
            )
            session.add(new_record)
            counter += 1
        else:
            print(f"Skipping duplicate: ({row['Accident_Index']})")

    session.commit()
    session.close()

    # Write a log
    with open('pipe_Road_log.txt', 'a') as f:
        dt_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f'TimeStamp: {dt_str} --- Number of new Road records loaded into DimRoad = {counter}\n')

# Call the function
pipe_Road(conn_string_db, conn_string_dw)







