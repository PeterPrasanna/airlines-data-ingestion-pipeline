DROP TABLE IF EXISTS flights;
DROP TABLE IF EXISTS flight_informations;
DROP TABLE IF EXISTS airports;
DROP TABLE IF EXISTS airlines;

CREATE TABLE airlines (
  airline_id VARCHAR(20) PRIMARY KEY,
  airline_name VARCHAR(100),
  iata_code VARCHAR(3),
  country_iso2 VARCHAR(2),
  country_name VARCHAR(100),
  date_founded INT,
  fleet_size INT,
  fleet_average_age FLOAT,
  status VARCHAR(50),
);

CREATE TABLE airports (
  airport_id VARCHAR(20) PRIMARY KEY,
  airport_name VARCHAR(150),
  iata_code VARCHAR(3),
  city_iata_code VARCHAR(3),
  country_iso2 VARCHAR(2),
  country_name VARCHAR(100),
  gmt FLOAT,
  timezone VARCHAR(100),
  latitude FLOAT,
  longitude FLOAT,
);

CREATE TABLE flights (
  fl_number VARCHAR(20),
  fl_date DATE,
  airline_code VARCHAR(3),
  origin VARCHAR(3),
  dest VARCHAR(3),
  distance FLOAT,
  cancelled BOOLEAN,
  cancellation_code VARCHAR(5),
  diverted BOOLEAN,
  PRIMARY KEY (fl_number, fl_date),
  FOREIGN KEY (airline_code) REFERENCES airlines(iata_code),
  FOREIGN KEY (origin)       REFERENCES airports(iata_code),
  FOREIGN KEY (dest)         REFERENCES airports(iata_code)
);

CREATE TABLE flight_informations (
  fl_number VARCHAR(20),
  fl_date DATE,
  crs_dep_time TIME,
  dep_time TIME,
  arr_time TIME,
  crs_arr_time TIME,
  delay_due_carrier FLOAT,
  delay_due_weather FLOAT,
  delay_due_nas FLOAT,
  delay_due_security FLOAT,
  delay_due_late_aircraft FLOAT,
  PRIMARY KEY (fl_number, fl_date),
  FOREIGN KEY (fl_number, fl_date) REFERENCES flights(fl_number, fl_date)
);