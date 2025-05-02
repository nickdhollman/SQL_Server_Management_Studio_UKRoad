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

class DimLocation(Base):
    __tablename__ = 'DimLocation'
    Longitude = Column(Float, primary_key=True, autoincrement=False)
    Latitude = Column(Float, primary_key=True, autoincrement=False)
    Urban_or_Rural_Area = Column(String(255))
    InScotland = Column(String(255))
    Location_Easting_OSGR = Column(Integer)
    Location_Northing_OSGR = Column(Integer)

def pipe_Location(conStrdb, conStrdw):
    engine_db = create_engine(conStrdb)
    sqlQuery = '''
    SELECT Longitude, Latitude, Urban_or_Rural_Area,
           InScotland, Location_Easting_OSGR, Location_Northing_OSGR
    FROM dbo.Location
    '''
    dFrame = pd.read_sql_query(sqlQuery, engine_db)

    print(f"Loaded {len(dFrame)} rows from Location table")
    print(dFrame.head())

    engine_dw = create_engine(conStrdw)

    Session = sessionmaker(bind=engine_dw)
    session = Session()

    counter = 0
    for _, row in dFrame.iterrows():
        # Skip rows where Longitude or Latitude is missing - similar to Driver_IMD_Decile
        # Since Longitude & Latitude are how I am determining the Primary Key values for location they are both needed as NOT NULL in dataset
        # Because of this I am skipping over rows in data retrieved that are null for either
        if pd.isna(row['Longitude']) or pd.isna(row['Latitude']):
            continue  # skip this row
        if not session.query(DimLocation).filter_by(
                Longitude=row['Longitude'],
                Latitude=row['Latitude']
        ).first():
            new_record = DimLocation(
                Longitude=row['Longitude'],
                Latitude=row['Latitude'],
                Urban_or_Rural_Area=row['Urban_or_Rural_Area'],
                InScotland=row['InScotland'],
                Location_Easting_OSGR=row['Location_Easting_OSGR'],
                Location_Northing_OSGR=row['Location_Northing_OSGR']
            )
            session.add(new_record)
            counter += 1
        else:
            print(f"Skipping duplicate: ({row['Longitude']}, {row['Latitude']})")

    session.commit()
    session.close()

    # Write a log
    with open('pipe_Location_log.txt', 'a') as f:
        dt_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f'TimeStamp: {dt_str} --- Number of new Location records loaded into DimLocation = {counter}\n')

# Call the function
pipe_Location(conn_string_db, conn_string_dw)







