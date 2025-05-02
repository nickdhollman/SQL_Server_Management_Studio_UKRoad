import pandas as pd
import tabulate as tbl
import os
import urllib
from datetime import datetime

# Note sqlalchemy instead of pyodbc
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from sqlalchemy.exc import SQLAlchemyError

# Load CSVs - I changed all '-' in csv files to underscores to prevent errors when using data (ex; Pedestrian_Crossing_Physical_Facilities)
accidents_df = pd.read_csv("C:\\Users\\nickd\\OneDrive - Oklahoma A and M System\\Advanced Data Wrangling\\Term_Project\\ProjectDataFiles\\Accidents_extract.csv")
print(accidents_df.shape)
print(accidents_df.dtypes)
vehicles_df = pd.read_csv("C:\\Users\\nickd\\OneDrive - Oklahoma A and M System\\Advanced Data Wrangling\\Term_Project\\ProjectDataFiles\\Vehicles_extract.csv")
print(vehicles_df.shape)
print(vehicles_df.dtypes)

# subset CSV data
Accidents = accidents_df[['Accident_Index','Accident_Severity','Number_of_Vehicles','Number_of_Casualties',
                          'Carriageway_Hazards','Did_Police_Officer_Attend_Scene_of_Accident',
                          'LSOA_of_Accident_Location','Date','Time','1st_Road_Number','2nd_Road_Number',
                          'Police_Force','Road_Type','Speed_limit','Junction_Detail','Junction_Control',
                          'Pedestrian_Crossing_Human_Control','Pedestrian_Crossing_Physical_Facilities']]
print(Accidents.shape)
Date = accidents_df[['Date','Day_of_Week','Year']]
print(Date.shape)
First_Road = accidents_df[['1st_Road_Number','1st_Road_Class']]
print(First_Road.shape)
Second_Road = accidents_df[['2nd_Road_Number','2nd_Road_Class']]
print(Second_Road.shape)
Location = accidents_df[['Accident_Index','Location_Easting_OSGR','Location_Northing_OSGR','Longitude',
                         'Latitude','Urban_or_Rural_Area','InScotland']]
print(Location.shape)
Police = accidents_df[['Police_Force','Local_Authority_District','Local_Authority_Highway']]
print(Police.shape)
Vehicle = vehicles_df[['Vehicle_Reference','Accident_Index','Vehicle_Type','X1st_Point_of_Impact',
                       'Was_Vehicle_Left_Hand_Drive','Engine_Capacity_CC','Propulsion_Code',
                       'Age_of_Vehicle','make','model','Towing_and_Articulation','Vehicle_Manoeuvre',
                       'Vehicle_Location_Restricted_Lane','Junction_Location','Skidding_and_Overturning',
                       'Hit_Object_in_Carriageway','Vehicle_Leaving_Carriageway',
                       'Hit_Object_off_Carriageway','Sex_of_Driver','Age_Band_of_Driver',
                       'Driver_IMD_Decile','Driver_Home_Area_Type','Journey_Purpose_of_Driver']]
print(Vehicle.shape)
Weather = accidents_df[['Date','1st_Road_Number','2nd_Road_Number','Light_Conditions',
                        'Weather_Conditions','Road_Surface_Conditions','Special_Conditions_at_Site']]
print(Weather.shape)

# create functions to do validity checks on dataframes for null values (validate_no_nulls)
# and ensuring unique values for all primary keys for accidents, date, vehicles
error_log = "Out.txt"
def validate_no_nulls(df, columns, error_log, table_name):
    nulls = df[columns].isnull().sum()
    null_cols = nulls[nulls > 0]
    if not null_cols.empty:
        with open(error_log, 'a') as fout:
            fout.write(f"\n[{datetime.now()}] Null PK Values found in {table_name}\n")
            fout.write(null_cols.to_string())
            fout.write("\n")
        return False
    return True
def validate_unique(df, subset, error_log, table_name):
    duplicates = df[df.duplicated(subset=subset, keep=False)]
    if not duplicates.empty:
        with open(error_log, 'a') as fout:
            fout.write(f"\n[{datetime.now()}] Duplicate PK Values found in {table_name}\n")
            fout.write(duplicates.to_csv(index=False))
        return False
    return True

# export tables as csv
Accidents = Accidents.drop_duplicates(subset=["Accident_Index"])
### Validation check for no null & all unique values for primary key of Accidents ###
validate_no_nulls(Accidents, ["Accident_Index"], error_log, "Accidents")
validate_unique(Accidents, ["Accident_Index"], error_log, "Accidents")
Accidents.to_csv('C:\\Users\\nickd\\OneDrive - Oklahoma A and M System\\Advanced Data Wrangling\\Term_Project\\ProjectDataFiles\\Accidents.csv', index=False)
Date = Date.drop_duplicates(subset=["Date"])
### Validation check for no null & all unique values for primary key of Date ###
validate_no_nulls(Date, ["Date"], error_log, "Date")
validate_unique(Date, ["Date"], error_log, "Date")
Date.to_csv('C:\\Users\\nickd\\OneDrive - Oklahoma A and M System\\Advanced Data Wrangling\\Term_Project\\ProjectDataFiles\\Date.csv', index=False)
First_Road = First_Road.drop_duplicates(subset=["1st_Road_Number"])
First_Road.to_csv('C:\\Users\\nickd\\OneDrive - Oklahoma A and M System\\Advanced Data Wrangling\\Term_Project\\ProjectDataFiles\\First_Road.csv', index=False)
Second_Road = Second_Road.drop_duplicates(subset=["2nd_Road_Number"])
# there was one null value for road number - dropping
Second_Road.dropna(subset=['2nd_Road_Number'], inplace=True)
Second_Road.to_csv('C:\\Users\\nickd\\OneDrive - Oklahoma A and M System\\Advanced Data Wrangling\\Term_Project\\ProjectDataFiles\\Second_Road.csv', index=False)
Location = Location.drop_duplicates(subset=["Accident_Index"])
Location.to_csv('C:\\Users\\nickd\\OneDrive - Oklahoma A and M System\\Advanced Data Wrangling\\Term_Project\\ProjectDataFiles\\Location.csv', index=False)
Police = Police.drop_duplicates(subset=["Police_Force"])
Police.to_csv('C:\\Users\\nickd\\OneDrive - Oklahoma A and M System\\Advanced Data Wrangling\\Term_Project\\ProjectDataFiles\\Police.csv', index=False)
Vehicle = Vehicle.drop_duplicates(subset=["Accident_Index", "Vehicle_Reference"])
### Validation check for no null & all unique values for primary key of Vehicles ###
validate_no_nulls(Vehicle, ["Accident_Index", "Vehicle_Reference"], error_log, "Vehicle")
validate_unique(Vehicle, ["Accident_Index", "Vehicle_Reference"], error_log, "Vehicle")
Vehicle.to_csv('C:\\Users\\nickd\\OneDrive - Oklahoma A and M System\\Advanced Data Wrangling\\Term_Project\\ProjectDataFiles\\Vehicle.csv', index=False)
Weather = Weather.drop_duplicates(subset=["Date",'1st_Road_Number', '2nd_Road_Number'])
# need to drop null value from 2nd row number above (1 row with null 2nd row number)
Weather.dropna(subset=['2nd_Road_Number'], inplace=True)
Weather.to_csv('C:\\Users\\nickd\\OneDrive - Oklahoma A and M System\\Advanced Data Wrangling\\Term_Project\\ProjectDataFiles\\Weather.csv', index=False)
#define connection string
conn_str = "Driver={ODBC Driver 17 for SQL Server};Server=NICK_LENOVO_LAP\\SQLEXPRESS;"
conn_str = conn_str + "Database=UKRoad;Trusted_Connection=yes;"
conn_str = urllib.parse.quote_plus(conn_str)
conn_str = "mssql+pyodbc:///?odbc_connect=%s" % conn_str

engine = create_engine(conn_str)

# Test connection
with engine.connect() as connection:
    print("Connected to SQL Server successfully!")


def execute_stored_procedures(procName):  # procName is for DROP_TABLES, CREATE_TABLES, etc.
    myQuery = "EXEC " + procName
    with engine.begin() as conn:
        conn.execute(text(myQuery))  # Execute the stored procedure


def insert_from_csv(tblName, file_name, dir_name):
    df = pd.read_csv(file_name)  # Read the csv file into a Pandas dataframe called df
    print(df)
    # what below section is doing is trying to convert df to sql (try:),
    # it will print database error if it runs into an error (except:),
    # and if no error occurs the code will continue to run
    try:
        # Load DataFrame into SQL Server table
        df.to_sql(tblName, con=engine, schema="dbo", if_exists="append",
                  index=False)  # schema=dbo which is the default for MyStoreDW
        # if_exists = append will add data to the file if there is already data in it
        print("Data inserted successfully!")
        # log timestamp & number of records
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("Out.txt", 'a') as fout:
            fout.write(f"[{timestamp}] Inserted {len(df)} records into {tblName}\n")
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
    finally:
        pass


def print_query_results(myQuery):
    with engine.connect() as conn:
        df_result = pd.read_sql(myQuery, conn)
        # Create a table to hold records and column names using tabulate
        result_table = tbl.tabulate(df_result, tablefmt="grid", showindex="False")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("Out.txt", 'a') as fout: # Note that result will be appended to out.txt each time you run the program
                                            # the 'a' option in the above statement is stating to append
        fout.write(f"\n[{timestamp}] {myQuery}\n")  # Print query and the result table into out.txt file
        fout.write('\n' + result_table + '\n')

def main():
    execute_stored_procedures("DROP_TABLES") #this is dropping tables
    execute_stored_procedures("CREATE_TABLES_c") #this is creating tables - I had a few drafts of create tables to generate ER diagram I thought made theoretical sense
    data_dir = os.getcwd()
    insert_from_csv ('Police', r'C:\\Users\\nickd\\OneDrive - Oklahoma A and M System\\Advanced Data Wrangling\\Term_Project\\ProjectDataFiles\\Police.csv',data_dir) #this inserting data into tables
    #below is selecting top 10 rows each table
    #you need a space at the end of each line or else you will often see an error (except the last line)
    myQuery = ("SELECT TOP 10 * "
               "FROM Police")
    #below is printing out query above
    print_query_results(myQuery)
    insert_from_csv('Date',
                    r'C:\\Users\\nickd\\OneDrive - Oklahoma A and M System\\Advanced Data Wrangling\\Term_Project\\ProjectDataFiles\\Date.csv',
                    data_dir)  # this inserting data into tables
    # you need a space at the end of each line or else you will often see an error (except the last line)
    myQuery = ("SELECT TOP 10 * "
               "FROM Date")
    print_query_results(myQuery)
    insert_from_csv('First_Road',
                    r'C:\\Users\\nickd\\OneDrive - Oklahoma A and M System\\Advanced Data Wrangling\\Term_Project\\ProjectDataFiles\\First_Road.csv',
                    data_dir)  # this inserting data into tables
    # you need a space at the end of each line or else you will often see an error (except the last line)
    myQuery = ("SELECT TOP 10 * "
               "FROM First_Road")
    # below is printing out query above
    print_query_results(myQuery)
    insert_from_csv('Second_Road',
                    r'C:\\Users\\nickd\\OneDrive - Oklahoma A and M System\\Advanced Data Wrangling\\Term_Project\\ProjectDataFiles\\Second_Road.csv',
                    data_dir)  # this inserting data into tables
    # you need a space at the end of each line or else you will often see an error (except the last line)
    myQuery = ("SELECT TOP 10 * "
               "FROM Second_Road")
    # below is printing out query above
    print_query_results(myQuery)
    insert_from_csv('Weather',
                    r'C:\\Users\\nickd\\OneDrive - Oklahoma A and M System\\Advanced Data Wrangling\\Term_Project\\ProjectDataFiles\\Weather.csv',
                    data_dir)  # this inserting data into tables
    # you need a space at the end of each line or else you will often see an error (except the last line)
    myQuery = ("SELECT TOP 10 * "
               "FROM Weather")
    # below is printing out query above
    print_query_results(myQuery)
    insert_from_csv('Accidents',
                    r'C:\\Users\\nickd\\OneDrive - Oklahoma A and M System\\Advanced Data Wrangling\\Term_Project\\ProjectDataFiles\\Accidents.csv',
                    data_dir)  # this inserting data into tables
    # you need a space at the end of each line or else you will often see an error (except the last line)
    myQuery = ("SELECT TOP 10 * "
               "FROM Accidents")
    # below is printing out query above
    print_query_results(myQuery)
    insert_from_csv('Location',
                    r'C:\\Users\\nickd\\OneDrive - Oklahoma A and M System\\Advanced Data Wrangling\\Term_Project\\ProjectDataFiles\\Location.csv',
                    data_dir)  # this inserting data into tables
    # you need a space at the end of each line or else you will often see an error (except the last line)
    myQuery = ("SELECT TOP 10 * "
               "FROM Location")
    # below is printing out query above
    print_query_results(myQuery)
    insert_from_csv('Vehicle',
                    r'C:\\Users\\nickd\\OneDrive - Oklahoma A and M System\\Advanced Data Wrangling\\Term_Project\\ProjectDataFiles\\Vehicle.csv',
                    data_dir)  # this inserting data into tables
    # you need a space at the end of each line or else you will often see an error (except the last line)
    myQuery = ("SELECT TOP 10 * "
               "FROM Vehicle")
    # below is printing out query above
    print_query_results(myQuery)
    #### MORE COMPLEX QUERIES FOR #1 IN FINAL PROJECT ####
    ## Creation of View was done in SQL Server and was submitted with assignment ##
    ## First Query on View ##
    myQuery = ("SELECT Weather_Conditions, COUNT(*) AS Total "
               "FROM v_Accident_Weather_Summary "
               "GROUP BY Weather_Conditions")
    print_query_results(myQuery)
    ## Second Query on View ##
    myQuery = ("SELECT Age_Band_of_Driver, COUNT(*) AS Total "
               "FROM v_Vehicle_Driver_Summary "
               "WHERE Accident_Severity = 'Serious' "
               "GROUP BY Age_Band_of_Driver")
    print_query_results(myQuery)
    ## First Query Involving Join ##
    myQuery = ("SELECT a.Accident_Severity, AVG(v.Age_of_Vehicle) AS Avg_Vehicle_Age "
               "FROM Vehicle v, Accidents a "
               "WHERE a.Accident_Index = v.Accident_Index "
               "GROUP BY a.Accident_Severity")
    print_query_results(myQuery)
    ## Second Query Involving Join ##
    myQuery = ("SELECT a.Accident_Severity, v.Age_Band_of_Driver, COUNT(*) AS Count "
               "FROM Vehicle v, Accidents a "
               "WHERE a.Accident_Index = v.Accident_Index "
               "GROUP BY a.Accident_Severity, v.Age_Band_of_Driver "
               "ORDER BY a.Accident_Severity, Count DESC")
    print_query_results(myQuery)
    ## Third Query Involving Join ##
    myQuery = ("SELECT d.Day_of_Week, COUNT(*) AS Total_Accidents "
               "FROM Accidents a INNER JOIN [Date] d ON a.[Date] = d.[Date] "
               "GROUP BY d.Day_of_Week "
               "ORDER BY Total_Accidents DESC")
    print_query_results(myQuery)

if __name__ == "__main__":
    main()
    engine.dispose() # Close the connection