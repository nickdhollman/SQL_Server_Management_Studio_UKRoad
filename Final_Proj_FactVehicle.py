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

class FactVehicle(Base):
    __tablename__ = 'FactVehicle'
    Accident_Index = Column(String(255), primary_key=True, autoincrement=False)
    Vehicle_Reference = Column(Integer, primary_key=True, autoincrement=False)
    Vehicle_Type = Column(String(255))
    make = Column(String(255))
    model = Column(String(255))
    Age_of_Vehicle = Column(Integer)
    Accident_Severity = Column(String(255))

def pipe_FVehicle(conStrdb, conStrdw):
    engine_db = create_engine(conStrdb)
    sqlQuery = '''
    SELECT v.Accident_Index, v.Vehicle_Reference,
    v.Vehicle_Type, v.make, v.model,
    v.Age_of_Vehicle, a.Accident_Severity
    FROM dbo.Accidents a, dbo.Vehicle v
    WHERE v.Accident_Index = a.Accident_Index
    '''
    dFrame = pd.read_sql_query(sqlQuery, engine_db)

    print(f"Loaded {len(dFrame)} rows from Accident and Vehicle table")
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
        if not session.query(FactVehicle).filter_by(
                Accident_Index=row['Accident_Index'],
                Vehicle_Reference=row['Vehicle_Reference']
        ).first():
            new_record = FactVehicle(
                Accident_Index=row['Accident_Index'],
                Vehicle_Reference=row['Vehicle_Reference'],
                Vehicle_Type=row['Vehicle_Type'],
                make=row['make'],
                model=row['model'],
                Age_of_Vehicle=row['Age_of_Vehicle'],
                Accident_Severity=row['Accident_Severity']
            )
            session.add(new_record)
            counter += 1
        else:
            print(f"Skipping duplicate: ({row['Accident_Index']}, {row['Vehicle_Reference']})")

    session.commit()
    session.close()

    # Write a log
    with open('pipe_FVehicle_log.txt', 'a') as f:
        dt_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f'TimeStamp: {dt_str} --- Number of new Vehicle records loaded into FactVehicle = {counter}\n')

# Call the function
pipe_FVehicle(conn_string_db, conn_string_dw)







