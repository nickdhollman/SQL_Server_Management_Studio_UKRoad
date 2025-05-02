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

class DimDriver(Base):
    __tablename__ = 'DimDriver'
    Accident_Index = Column(String(255), primary_key=True, autoincrement=False)
    Vehicle_Reference = Column(Integer, primary_key=True, autoincrement=False)
    Sex_of_Driver = Column(String(255))
    Age_Band_of_Driver = Column(String(255))
    Driver_IMD_Decile = Column(Float)
    Driver_Home_Area_Type = Column(String(255))
    Journey_Purpose_of_Driver = Column(String(255))

def pipe_Driver(conStrdb, conStrdw):
    engine_db = create_engine(conStrdb)
    sqlQuery = '''
    SELECT Accident_Index, Vehicle_Reference, Sex_of_Driver, Age_Band_of_Driver,
           Driver_IMD_Decile, Driver_Home_Area_Type, Journey_Purpose_of_Driver
    FROM dbo.Vehicle
    '''
    dFrame = pd.read_sql_query(sqlQuery, engine_db)

    print(f"Loaded {len(dFrame)} rows from Vehicle table")
    print(dFrame.head())

    # Replace NaN with None - this is needed from Driver_IMD_Decile
    # this tests if there is nan data and replaces with None
    # This is needed from what I saw online because SQLAlchemy cannot handle NaN from pandas properly.
    # SQLAlchemy instead expects None which is mapped to NULL in SQL Server
    dFrame = dFrame.where(pd.notnull(dFrame), None)
    # Accident Index had scientific notation so this is needed due to python not handling this well for some reason
    # other tables did not need this but was receiving error prior to inserting this below for this table
    dFrame['Accident_Index'] = dFrame['Accident_Index'].astype(str)

    engine_dw = create_engine(conStrdw)

    Session = sessionmaker(bind=engine_dw)
    session = Session()

    counter = 0
    for _, row in dFrame.iterrows():
        # this is replacing missing values in Driver_IMD_Decile with none which was needed from error message I orginally received
        # this is needed because of reasoning above
        driver_imd_decile = row['Driver_IMD_Decile']
        if pd.isna(driver_imd_decile):
            driver_imd_decile = None

        if not session.query(DimDriver).filter_by(
                Accident_Index=row['Accident_Index'],
                Vehicle_Reference=row['Vehicle_Reference']
        ).first():
            new_record = DimDriver(
                Accident_Index=row['Accident_Index'],
                Vehicle_Reference=row['Vehicle_Reference'],
                Sex_of_Driver=row['Sex_of_Driver'],
                Age_Band_of_Driver=row['Age_Band_of_Driver'],
                Driver_IMD_Decile=driver_imd_decile,#this is because we want to use what we create above,
                                                    #not the original values
                Driver_Home_Area_Type=row['Driver_Home_Area_Type'],
                Journey_Purpose_of_Driver=row['Journey_Purpose_of_Driver']
            )
            session.add(new_record)
            counter += 1
        else:
            print(f"Skipping duplicate: ({row['Accident_Index']}, {row['Vehicle_Reference']})")

    session.commit()
    session.close()

    # Write a log
    with open('pipe_Driver_log.txt', 'a') as f:
        dt_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f'TimeStamp: {dt_str} --- Number of new Driver records loaded into DimDriver = {counter}\n')

# Call the function
pipe_Driver(conn_string_db, conn_string_dw)







