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

class DimDate(Base):
    __tablename__ = 'DimDate'
    Date = Column(Date, primary_key=True, autoincrement=False)
    Day_of_Week = Column(String(255))
    Year = Column(Integer)
    Month = Column(Integer)
    Quarter = Column(Integer)

def pipe_Date(conStrdb, conStrdw):
    engine_db = create_engine(conStrdb)
    sqlQuery = '''
    SELECT [Date], Day_of_Week, [Year]
    FROM dbo.Date
    '''
    dFrame = pd.read_sql_query(sqlQuery, engine_db)
    # Create new Month and Quarter columns
    dFrame['Month'] = pd.to_datetime(dFrame['Date']).dt.month
    dFrame['Quarter'] = pd.to_datetime(dFrame['Date']).dt.quarter

    print(f"Loaded {len(dFrame)} rows from Date table")
    print(dFrame.head())

    engine_dw = create_engine(conStrdw)

    Session = sessionmaker(bind=engine_dw)
    session = Session()

    counter = 0
    for _, row in dFrame.iterrows():
        if not session.query(DimDate).filter_by(
                Date=row['Date']
        ).first():
            new_record = DimDate(
                Date=row['Date'],
                Day_of_Week = row['Day_of_Week'],
                Year = row['Year'],
                Month=row['Month'],
                Quarter=row['Quarter']
            )
            session.add(new_record)
            counter += 1
        else:
            print(f"Skipping duplicate: ({row['Date']})")

    session.commit()
    session.close()

    # Write a log
    with open('pipe_Date_log.txt', 'a') as f:
        dt_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f'TimeStamp: {dt_str} --- Number of new Date records loaded into DimDate = {counter}\n')

# Call the function
pipe_Date(conn_string_db, conn_string_dw)







