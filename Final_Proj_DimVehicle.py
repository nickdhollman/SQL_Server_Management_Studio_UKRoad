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

class DimVehicle(Base):
    __tablename__ = 'DimVehicle'
    Accident_Index = Column(String(255), primary_key=True, autoincrement=False)
    Vehicle_Reference = Column(Integer, primary_key=True, autoincrement=False)
    X1st_Point_of_Impact = Column(String(255))
    Was_Vehicle_Left_Hand_Drive = Column(String(255))
    Engine_Capacity_CC = Column(Integer)
    Propulsion_Code = Column(String(255))
    Towing_and_Articulation = Column(String(255))
    Vehicle_Manoeuvre = Column(String(255))
    Vehicle_Location_Restricted_Lane = Column(Integer)
    Junction_Location = Column(String(255))
    Skidding_and_Overturning = Column(String(255))
    Hit_Object_in_Carriageway = Column(String(255))
    Vehicle_Leaving_Carriageway = Column(String(255))
    Hit_Object_off_Carriageway = Column(String(255))

def pipe_Vehicle(conStrdb, conStrdw):
    engine_db = create_engine(conStrdb)
    sqlQuery = '''
    SELECT Accident_Index, Vehicle_Reference, X1st_Point_of_Impact, 
    Was_Vehicle_Left_Hand_Drive, Engine_Capacity_CC, Propulsion_Code,
    Towing_and_Articulation, Vehicle_Manoeuvre, Vehicle_Location_Restricted_Lane,
    Junction_Location, Skidding_and_Overturning, Hit_Object_in_Carriageway,
    Vehicle_Leaving_Carriageway, Hit_Object_off_Carriageway
    FROM dbo.Vehicle
    '''
    dFrame = pd.read_sql_query(sqlQuery, engine_db)

    print(f"Loaded {len(dFrame)} rows from Vehicle table")
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
        if not session.query(DimVehicle).filter_by(
                Accident_Index=row['Accident_Index'],
                Vehicle_Reference=row['Vehicle_Reference']
        ).first():
            new_record = DimVehicle(
                Accident_Index=row['Accident_Index'],
                Vehicle_Reference=row['Vehicle_Reference'],
                X1st_Point_of_Impact=row['X1st_Point_of_Impact'],
                Was_Vehicle_Left_Hand_Drive=row['Was_Vehicle_Left_Hand_Drive'],
                Engine_Capacity_CC=row['Engine_Capacity_CC'],
                Propulsion_Code=row['Propulsion_Code'],
                Towing_and_Articulation=row['Towing_and_Articulation'],
                Vehicle_Manoeuvre=row['Vehicle_Manoeuvre'],
                Vehicle_Location_Restricted_Lane=row['Vehicle_Location_Restricted_Lane'],
                Junction_Location=row['Junction_Location'],
                Skidding_and_Overturning=row['Skidding_and_Overturning'],
                Hit_Object_in_Carriageway=row['Hit_Object_in_Carriageway'],
                Vehicle_Leaving_Carriageway=row['Vehicle_Leaving_Carriageway'],
                Hit_Object_off_Carriageway=row['Hit_Object_off_Carriageway']
            )
            session.add(new_record)
            counter += 1
        else:
            print(f"Skipping duplicate: ({row['Accident_Index']}, {row['Vehicle_Reference']})")

    session.commit()
    session.close()

    # Write a log
    with open('pipe_Vehicle_log.txt', 'a') as f:
        dt_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f'TimeStamp: {dt_str} --- Number of new Vehicle records loaded into DimVehicle = {counter}\n')

# Call the function
pipe_Vehicle(conn_string_db, conn_string_dw)







