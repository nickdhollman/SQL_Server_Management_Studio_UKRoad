import pandas as pd
import urllib
import datetime
import pyodbc

from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Time
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

class FactAccident(Base):
    __tablename__ = 'FactAccident'
    Accident_Index = Column(String(255), primary_key=True, autoincrement=False)
    Date = Column(Date)
    Longitude = Column(Float)
    Latitude = Column(Float)
    First_Road_Number = Column(Integer)
    Second_Road_Number = Column(Integer)
    Number_of_Vehicles = Column(Integer)
    Number_of_Casualties = Column(Integer)
    Accident_Severity = Column(String(255))
    Time = Column(Time)

def pipe_FAccident(conStrdb, conStrdw):
    engine_db = create_engine(conStrdb)
    sqlQuery = '''
    SELECT a.Accident_Index, a.[Date], l.Longitude, l.Latitude,
    a.[1st_Road_Number], a.[2nd_Road_Number], a.Number_of_Vehicles,
    a.Number_of_Casualties, a.Accident_Severity, a.[Time]
    FROM dbo.Accidents a, dbo.Location l
    WHERE a.Accident_Index = l.Accident_Index
    '''
    dFrame = pd.read_sql_query(sqlQuery, engine_db)

    print(f"Loaded {len(dFrame)} rows from Accident and Location table")
    print(dFrame.head())

    engine_dw = create_engine(conStrdw)

    Session = sessionmaker(bind=engine_dw)
    session = Session()

    counter = 0
    for _, row in dFrame.iterrows():
        # I was getting error similar to previous tables based off Nan values, so inserted below code
        # which tests if there is nan data and replaces with None
        # This is needed from what I saw online because SQLAlchemy cannot handle NaN from pandas properly.
        # SQLAlchemy instead expects None which is mapped to NULL in SQL Server
        row = row.where(pd.notnull(row), None)
        if not session.query(FactAccident).filter_by(
                Accident_Index=row['Accident_Index']
        ).first():
            new_record = FactAccident(
                Accident_Index=row['Accident_Index'],
                Date=row['Date'],
                Longitude=row['Longitude'],
                Latitude=row['Latitude'],
                First_Road_Number=row['1st_Road_Number'],
                Second_Road_Number=row['2nd_Road_Number'],
                Number_of_Vehicles=row['Number_of_Vehicles'],
                Number_of_Casualties=row['Number_of_Casualties'],
                Accident_Severity=row['Accident_Severity'],
                Time=row['Time']
            )
            session.add(new_record)
            counter += 1
        else:
            print(f"Skipping duplicate: ({row['Accident_Index']})")

    session.commit()
    session.close()

    # Write a log
    with open('pipe_FAccident_log.txt', 'a') as f:
        dt_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f'TimeStamp: {dt_str} --- Number of new Accident records loaded into FactAccident = {counter}\n')

# Call the function
pipe_FAccident(conn_string_db, conn_string_dw)







