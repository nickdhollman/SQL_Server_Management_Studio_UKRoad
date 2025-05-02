import pandas as pd
import urllib
import datetime
import pyodbc

from sqlalchemy import create_engine, Column, Integer, String, Float, Date
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

class DimWeather(Base):
    __tablename__ = 'DimWeather'
    Date = Column(Date, primary_key=True, autoincrement=False)
    First_Road_Number = Column(Integer, primary_key=True, autoincrement=False)
    Second_Road_Number = Column(Integer, primary_key=True, autoincrement=False)
    Weather_Conditions = Column(String(255))
    Light_Conditions = Column(String(255))
    Road_Surface_Conditions = Column(String(255))
    Special_Conditions_at_Site = Column(String(255))

def pipe_Weather(conStrdb, conStrdw):
    engine_db = create_engine(conStrdb)
    sqlQuery = '''
    SELECT [Date], [1st_Road_Number], [2nd_Road_Number], Weather_Conditions, Light_Conditions, 
    Road_Surface_Conditions, Special_Conditions_at_Site
    FROM dbo.Weather
    '''
    dFrame = pd.read_sql_query(sqlQuery, engine_db)

    print(f"Loaded {len(dFrame)} rows from Weather table")
    print(dFrame.head())

    engine_dw = create_engine(conStrdw)

    Session = sessionmaker(bind=engine_dw)
    session = Session()

    counter = 0
    for _, row in dFrame.iterrows():
        if not session.query(DimWeather).filter_by(
                Date=row['Date'],
                First_Road_Number=row['1st_Road_Number'],
                Second_Road_Number=row['2nd_Road_Number']
        ).first():
            new_record = DimWeather(
                Date=row['Date'],
                First_Road_Number = row['1st_Road_Number'],
                Second_Road_Number = row['2nd_Road_Number'],
                Weather_Conditions=row['Weather_Conditions'],
                Light_Conditions=row['Light_Conditions'],
                Road_Surface_Conditions=row['Road_Surface_Conditions'],
                Special_Conditions_at_Site=row['Special_Conditions_at_Site']
            )
            session.add(new_record)
            counter += 1
        else:
            print(f"Skipping duplicate: ({row['Date']}, {row['1st_Road_Number']}, {row['2nd_Road_Number']})")

    session.commit()
    session.close()

    # Write a log
    with open('pipe_Weather_log.txt', 'a') as f:
        dt_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f'TimeStamp: {dt_str} --- Number of new Weather records loaded into DimWeather = {counter}\n')

# Call the function
pipe_Weather(conn_string_db, conn_string_dw)







