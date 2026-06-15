-- Table structure for table airports

DROP TABLE IF EXISTS airports;
CREATE TABLE airports (
  airport_id SERIAL PRIMARY KEY,
  iata_code VARCHAR(3),
  name VARCHAR(100),
  country VARCHAR(100),
  latitude FLOAT,
  longitude FLOAT
);

-- Table structure for table flights

DROP TABLE IF EXISTS flights;
CREATE TABLE flights (
  flight_id SERIAL PRIMARY KEY,
  flight_number VARCHAR(20),
  departure_airport VARCHAR(3),
  arrival_airport VARCHAR(3),
  scheduled_departure TIMESTAMP,
  actual_departure TIMESTAMP,
  scheduled_arrival TIMESTAMP,
  actual_arrival TIMESTAMP,
  status VARCHAR(50)
);

-- Table structure for table airlines

DROP TABLE IF EXISTS airlines;
CREATE TABLE airlines (
  airline_id SERIAL PRIMARY KEY,
  iata_code VARCHAR(3),
  icao_code VARCHAR(4),
  name VARCHAR(100),
  country VARCHAR(100),
  fleet_size INT,
  status VARCHAR(100),
  type VARCHAR(100)
);