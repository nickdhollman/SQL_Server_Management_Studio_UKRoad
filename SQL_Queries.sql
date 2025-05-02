USE [UKRoad];
--1. Design and implement a normalized OLTP database based on the extracted Accidents and Vehicles data. 
--You will then develop 2 Views and 5 useful SQL queries. At least two of the 5 SQL queries must use one or more of these views.  
--At least two of the 5 SQL queries must employ aggregations. At least three of the 5 SQL queries must involve JOINS or sub-queries.	
-- Query 1 - Most common vehicle types involved in accidents
SELECT Vehicle_Type, COUNT(*) AS Count
FROM Vehicle
GROUP BY Vehicle_Type
ORDER BY Count DESC;

-- *Query 2* - Average age of vehicles in accidents by severity
SELECT a.Accident_Severity, AVG(v.Age_of_Vehicle) AS Avg_Vehicle_Age
FROM Vehicle v, Accidents a 
WHERE a.Accident_Index = v.Accident_Index
GROUP BY a.Accident_Severity;

-- *Query 3* - Driver age band distribution by accident severity
SELECT a.Accident_Severity, v.Age_Band_of_Driver, COUNT(*) AS Count
FROM Vehicle v, Accidents a 
WHERE a.Accident_Index = v.Accident_Index
GROUP BY a.Accident_Severity, v.Age_Band_of_Driver
ORDER BY a.Accident_Severity, Count DESC;

-- Query 4 - Accidents by weather condition:
SELECT Weather_Conditions, COUNT(*) AS Count
FROM Weather
GROUP BY Weather_Conditions
ORDER BY Count DESC;

-- Query 5 - Accident severity vs. weather:
SELECT w.Weather_Conditions, a.Accident_Severity, COUNT(*) AS Count
FROM Accidents a, Weather w
WHERE a.Date = w.Date
    AND a.[1st_Road_Number] = w.[1st_Road_Number]
    AND a.[2nd_Road_Number] = w.[2nd_Road_Number]
GROUP BY w.Weather_Conditions, a.Accident_Severity
ORDER BY Count DESC;

-- Query 6 - Urban vs. rural accident comparison:
SELECT l.Urban_or_rural_area, COUNT(*) AS Total_Accidents
FROM Location l
GROUP BY l.Urban_or_rural_area;

-- Query 7 -- Top 10 accident-prone roads (1st road):
SELECT TOP 10 [1st_Road_Number], COUNT(*) AS Accident_Count
FROM Accidents
GROUP BY [1st_Road_Number]
ORDER BY Accident_Count DESC;

-- *Query 8* -- Accidents by day of the week:
SELECT d.Day_of_Week, COUNT(*) AS Total_Accidents
FROM Accidents a
INNER JOIN [Date] d ON a.[Date] = d.[Date]
GROUP BY d.Day_of_Week
ORDER BY Total_Accidents DESC;

-- Query 9 -- Monthly accident trend:
SELECT MONTH([Date]) AS Month, COUNT(*) AS Total_Accidents
FROM Accidents
GROUP BY MONTH([Date])
ORDER BY Month;

-- Query 10 -- Accidents involving left-hand drive vehicles in rural areas:
SELECT COUNT(*) AS Left_Hand_Rural_Total
FROM Vehicle v
INNER JOIN Accidents a ON a.Accident_Index = v.Accident_Index
INNER JOIN [Location] l ON a.Accident_Index = l.Accident_Index
WHERE v.Was_Vehicle_Left_Hand_Drive = 'Yes' AND l.Urban_or_rural_area = 'Rural';

-- View 1 - joins Accidents with Weather and Date, and summarizes accident severity by weather conditions and day of the week.
CREATE VIEW v_Accident_Weather_Summary AS
SELECT 
    a.Accident_Index,
    d.Day_of_Week,
    a.Accident_Severity,
    w.Weather_Conditions,
    w.Light_Conditions,
    w.Road_Surface_Conditions,
    w.Special_Conditions_at_Site
FROM Accidents a, [Date] d, Weather w
WHERE a.[Date] = d.[Date] AND a.[Date] = w.[Date] AND a.[1st_Road_Number] = w.[1st_Road_Number] AND a.[2nd_Road_Number] = w.[2nd_Road_Number];

SELECT Weather_Conditions, COUNT(*) AS Total
FROM v_Accident_Weather_Summary
GROUP BY Weather_Conditions;

-- View 2 - This view combines Vehicle and Accidents for a snapshot of vehicle and driver profiles involved in accidents.
CREATE VIEW v_Vehicle_Driver_Summary AS
SELECT 
    v.Accident_Index,
    v.Vehicle_Reference,
    a.Accident_Severity,
    v.Vehicle_Type,
    v.Age_of_Vehicle,
    v.Sex_of_Driver,
    v.Age_Band_of_Driver,
    v.Driver_IMD_Decile,
    v.Driver_Home_Area_Type,
    v.Journey_Purpose_of_Driver
FROM Vehicle v, Accidents a
WHERE v.Accident_Index = a.Accident_Index;

SELECT Age_Band_of_Driver, COUNT(*) AS Total
FROM v_Vehicle_Driver_Summary
WHERE Accident_Severity = 'Serious'
GROUP BY Age_Band_of_Driver;

---2. Design and implement a dimensional OLAP data warehouse. The dimensional warehouse will contain data that has been extracted, 
-- transformed, and loaded from the OLTP database. 
-- You will develop 5 extended SQL queries that showcase the different OLAP operations such as rollup and drill-down.
USE [UKRoadDim];
-- Query 1 - ROLL-UP - total accidents by year
SELECT
    COALESCE(CAST(d.[Year] AS VARCHAR(10)), 'Years Total') AS Years,
    COUNT(fa.Accident_Index) AS Total_Accidents
FROM FactAccident fa
JOIN DimDate d ON fa.[Date] = d.[Date]
GROUP BY ROLLUP(d.[Year])
ORDER BY Years;

-- Query 2 - Drill down - accidents by year and month 
SELECT
    d.[Year],
    d.[Month],
    COUNT(fa.Accident_Index) AS Total_Accidents
FROM FactAccident fa
JOIN DimDate d ON fa.[Date] = d.[Date]
GROUP BY d.[Year], d.[Month]
ORDER BY d.[Year], d.[Month];

-- Query 3 - Slice - Accidents in Rural areas
SELECT
    fa.Accident_Severity,
    COUNT(fa.Accident_Index) AS Total_Accidents
FROM FactAccident fa
JOIN DimLocation l ON fa.Longitude = l.Longitude AND fa.Latitude = l.Latitude
WHERE l.Urban_or_Rural_Area = 'Rural'
GROUP BY fa.Accident_Severity
ORDER BY Total_Accidents DESC;

-- Query 4 - Dice - Serious Accidents in Scotland during Quarter 4
-- You could also not state AND d.[Quarter] = 4 to get Serious Accidents in Scotland by Quarter
SELECT
    d.[Year],
    d.[Quarter],
    COUNT(fa.Accident_Index) AS Serious_Accidents_Count
FROM FactAccident fa
JOIN DimDate d ON fa.[Date] = d.[Date]
JOIN DimLocation l ON fa.Longitude = l.Longitude AND fa.Latitude = l.Latitude
WHERE l.InScotland = 'Yes'
  AND fa.Accident_Severity = 'Serious'
  AND d.[Quarter] = 4
GROUP BY d.[Year], d.[Quarter]
ORDER BY d.[Year];

-- Query 5 - Top N - Top 5 Police forces by Numbe of Accidents 
SELECT TOP 5
    r.Police_Force,
    COUNT(fa.Accident_Index) AS Total_Accidents
FROM FactAccident fa
JOIN DimRoad r ON fa.Accident_Index = r.Accident_Index
GROUP BY r.Police_Force
ORDER BY Total_Accidents DESC;

