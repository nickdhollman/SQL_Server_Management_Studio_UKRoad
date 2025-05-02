# SQL_Server_Management_Studio_UKRoad
This is a project I did in my advanced data wrangling course that gave us the excel files for Vehicles and Accidents, with the instructions to create a database and insert data in the database using Python

The dataset was retrieved from https://www.kaggle.com/datasets/tsiaras/uk-road-safety-accidents-and-vehicles

The assumptions I made for normalization of the database are as follows:
•	Accident_Index can uniquely identify each column in the Accidents_Extract dataset 

•	Accident_Index & Vehicle_Reference can uniquely identify each column in the Vehicle_Extract dataset

•	Therefore, Accident_Index is the primary key for the accidents table & Accident_Index & Vehicle_Reference is a composite primary key in the vehicle table 

In addition:
•	1st / 2nd road class is dependent on 1st / 2nd road number (therefore these are needed in separate tables to eliminate transitive dependency)

•	Light_Condition, Weather_Condition, Road_Surface_Conditions, and Special_Conditions_at_Site are dependent on Date, 1st_Road_Number, and 2nd_Road_Number (therefore weather table is needed in separate table to eliminate transitive dependency) - I also figured date and the intersection of roads is needed to identify the unique weather conditions of the accident which is why these three rows are needed as primary key 

•	Day_of_Week and Year is dependent on Date (therefore these are needed in separate table to eliminate transitive dependency)

•	Local_authority_district and Local_authority_highway are dependent on police force (therefore these are needed in separate tables to eliminate transitive dependency)

•	I didn’t know exactly the relationship between Location_Easting_OSGR, Location_Northing_OSGR, and Longitude or Latitude but felt that Urban_or_rural_area and InScotland were dependent on both Longitude/Latitude pair and Locaton_Easting_OSGR/Location_Northing_OSGR pair so the location table is needed to eliminate transitive dependency. With that said I don’t know if accident_index is the best primary key for this table but would need to know more in a real world setting to make this distinction 

*The remaining values in the vehicle and accidents table I believe are all in 3NF but is hard to know for sure with the data given (definitely in 2NF, but had to make my best guess to ensure lack of transitive dependency)*
