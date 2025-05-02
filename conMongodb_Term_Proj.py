import pymongo
from tabulate import tabulate
import pandas as pd

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")

# List the available databases
# print("Available databases:", client.list_database_names())
def find_query(dbName, collectionName, query, projection, sort_col):
    db = client[dbName]  # Specify the database name
    collection = db[collectionName]  # Specify the collection name
    query_output = collection.find(query, projection).sort(sort_col)
    documents = list(query_output)
    df = pd.DataFrame(documents)
    column_names = list(collection.find_one(query, projection).keys())
    result_table = tabulate(df, headers = column_names, tablefmt="grid", showindex="False")
    return result_table
#
def aggregate_query(dbName, collectionName, pipeline):
    db = client[dbName]  # Specify the database name
    collection = db[collectionName]  # Specify the collection name
    pipe_output = collection.aggregate(pipeline)
    first_document = next(pipe_output, None)  # Get the first document or None if no documents
    if first_document:
        column_names = list(first_document.keys())
    else:
        print("No documents found")
    documents = list(pipe_output)
    df = pd.DataFrame(documents)
    result_table = tabulate(df, headers = column_names, tablefmt="grid", showindex="False")
    return result_table
#
db = 'UKRoad'
collection = 'Accidents'
# Execute a MongoDB NoSQL find() query

## Query #1 -- Accidents ##
# Define the query criteria
query = {"$and": [
        {"Accident_Severity": "Serious"},
        {"Urban_or_Rural_Area": "Rural"},
        {"Number_of_Vehicles": {"$gt": 2}}
    ]}
# Define projection to include only certain fields
projection = {"_id": 0, "Accident_Severity": 1, "Urban_or_Rural_Area": 1, "Number_of_Vehicles": 1, "Number_of_Casualties": 1}
# Specify any Sort
sort_col = {"Number_of_Casualties" : -1}
# Call the query output function
result_table = find_query(db, collection, query, projection, sort_col)
# Print Result
print(query)
print(result_table)

## Query #2 -- Accidents ##
# Define the query criteria
query = {"$and": [
        {"InScotland": "Yes"},
        {"Urban_or_Rural_Area": "Rural"},
        {"Day_of_Week": "Friday"},
        {"Number_of_Vehicles": {"$gt": 5}}
    ]}
# Define projection to include only certain fields
projection = {"_id": 0, "InScotland": 1, "Urban_or_Rural_Area": 1, "Day_of_Week": 1, "Number_of_Vehicles": 1}
# Specify any Sort
sort_col = {"Number_of_Vehicles" : -1}
# Call the query output function
result_table = find_query(db, collection, query, projection, sort_col)
# Print Result
print(query)
print(result_table)

## Aggregate #1 - ##
# Call an aggregation pipeline
pipeline = [
    {"$group": {"_id": "$Urban_or_Rural_Area","Total_Accidents": { "$sum": 1 }}},
    {"$project": {"_id": 0,"Urban_or_Rural_Area": "$_id", "Total_Accidents": 1}},{"$sort": { "Total_Accidents": -1 }}]
# print results
result_table = aggregate_query(db, collection, pipeline)
print(pipeline)
print(result_table)

## Query #3 -- Vehicles ##
db = 'UKRoad'
collection = 'Vehicle'
# Define the query criteria
query = {
    "Was_Vehicle_Left_Hand_Drive": "Yes",
    "Age_of_Vehicle": { "$gte": 10 }
    }
# Define projection to include only certain fields
projection = {"_id": 0,
    "Vehicle_Type": 1,
    "Was_Vehicle_Left_Hand_Drive": 1,
    "Age_of_Vehicle": 1}
# Specify any Sort
sort_col = {"Age_of_Vehicle": -1}
# Call the query output function
result_table = find_query(db, collection, query, projection, sort_col)
# Print Result
print(query)
print(result_table)

## Aggregate #2 -- Vehicles ##
# Call an aggregation pipeline
pipeline = [{"$group": {"_id": "$Vehicle_Type","Total_Vehicles": { "$sum": 1 }}},
    {"$project": {"_id": 0,"Vehicle_Type": "$_id","Total_Vehicles": 1}},
    {"$sort": {"Total_Vehicles": -1}}]
#print the result
result_table = aggregate_query(db, collection, pipeline)
print(pipeline)
print(result_table)