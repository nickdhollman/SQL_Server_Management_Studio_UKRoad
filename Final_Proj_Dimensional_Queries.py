import pandas as pd
import tabulate as tbl
import os
import urllib
from datetime import datetime

# Note sqlalchemy instead of pyodbc
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from sqlalchemy.exc import SQLAlchemyError

# Connection to dimensional database (UKRoadDim)
conn_string_dw = "Driver={ODBC Driver 17 for SQL Server};Server=NICK_LENOVO_LAP\\SQLEXPRESS;Database=UKRoadDim;Trusted_Connection=yes;"
conn_string_dw = urllib.parse.quote_plus(conn_string_dw)
conn_string_dw = "mssql+pyodbc:///?odbc_connect=%s" % conn_string_dw

engine = create_engine(conn_string_dw)

# Test connection
with engine.connect() as connection:
    print("Connected to SQL Server successfully!")


def print_query_results(myQuery):
    with engine.connect() as conn:
        df_result = pd.read_sql(myQuery, conn)
        # Create a table to hold records and column names using tabulate
        result_table = tbl.tabulate(df_result, tablefmt="grid", showindex="False")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("Out_dimensional.txt", 'a') as fout: # Note that result will be appended to out.txt each time you run the program
                                            # the 'a' option in the above statement is stating to append
        fout.write(f"\n[{timestamp}] {myQuery}\n")  # Print query and the result table into out.txt file
        fout.write('\n' + result_table + '\n')

def main():
    myQuery = ("SELECT TOP 10 * "
               "FROM DimDate")
    print_query_results(myQuery)
    myQuery = ("SELECT TOP 10 * "
               "FROM DimDriver")
    print_query_results(myQuery)
    myQuery = ("SELECT TOP 10 * "
               "FROM DimLocation")
    print_query_results(myQuery)
    myQuery = ("SELECT TOP 10 * "
               "FROM DimRoad")
    print_query_results(myQuery)
    myQuery = ("SELECT TOP 10 * "
               "FROM DimVehicle")
    print_query_results(myQuery)
    myQuery = ("SELECT TOP 10 * "
               "FROM DimWeather")
    print_query_results(myQuery)
    myQuery = ("SELECT TOP 10 * "
               "FROM FactAccident")
    print_query_results(myQuery)
    myQuery = ("SELECT TOP 10 * "
               "FROM FactVehicle")
    print_query_results(myQuery)
    myQuery = ("SELECT COALESCE(CAST(d.[Year] AS VARCHAR(10)), 'Years Total') AS Years, "
               "COUNT(fa.Accident_Index) AS Total_Accidents "
               "FROM FactAccident fa "
               "JOIN DimDate d ON fa.[Date] = d.[Date] "
               "GROUP BY ROLLUP(d.[Year]) "
               "ORDER BY Years")
    print_query_results(myQuery)
    myQuery = ("SELECT d.[Year], d.[Month], "
               "COUNT(fa.Accident_Index) AS Total_Accidents "
               "FROM FactAccident fa "
               "JOIN DimDate d ON fa.[Date] = d.[Date] "
               "GROUP BY d.[Year], d.[Month] "
               "ORDER BY d.[Year], d.[Month]")
    print_query_results(myQuery)
    myQuery = ("SELECT fa.Accident_Severity, "
               "COUNT(fa.Accident_Index) AS Total_Accidents "
               "FROM FactAccident fa "
               "JOIN DimLocation l ON fa.Longitude = l.Longitude AND fa.Latitude = l.Latitude "
               "WHERE l.Urban_or_Rural_Area = 'Rural' "
               "GROUP BY fa.Accident_Severity "
               "ORDER BY Total_Accidents")
    print_query_results(myQuery)
    myQuery = ("SELECT d.[Year], d.[Quarter], "
               "COUNT(fa.Accident_Index) AS Serious_Accidents_Count "
               "FROM FactAccident fa "
               "JOIN DimDate d ON fa.[Date] = d.[Date] "
               "JOIN DimLocation l ON fa.Longitude = l.Longitude AND fa.Latitude = l.Latitude "
               "WHERE l.InScotland = 'Yes' AND fa.Accident_Severity = 'Serious' AND "
               "d.[Quarter] = 4 "
               "GROUP BY d.[Year], d.[Quarter] "
               "ORDER BY d.[Year]")
    print_query_results(myQuery)
    myQuery = ("SELECT TOP 5 r.Police_Force, "
               "COUNT(fa.Accident_Index) AS Total_Accidents "
               "FROM FactAccident fa "
               "JOIN DimRoad r ON fa.Accident_Index = r.Accident_Index "
               "GROUP BY r.Police_Force "
               "ORDER BY Total_Accidents DESC")
    print_query_results(myQuery)

if __name__ == "__main__":
    main()
    engine.dispose() # Close the connection