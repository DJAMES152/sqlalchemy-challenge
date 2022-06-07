import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, distinct
from flask import Flask, jsonify


# Setting up the Database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflecting the Database into a Variable
Base = automap_base()

# Reflecting the Tables
Base.prepare(engine, reflect=True)

# Saving Table References
measurement = Base.classes.measurement
station = Base.classes.station


# Setting up Flask
app = Flask(__name__)


# Routes for Flask
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Hawaii Weather Data Routes:<br/><br>"
        f"-- Precipiation Totals over the Last Year by Day: <a href=\"/api/v1.0/precipitation\">/api/v1.0/precipitation<a><br/>"
        f"-- Active Weather Stations: <a href=\"/api/v1.0/stations\">/api/v1.0/stations<a><br/>"
        f"-- Temperature Observations by day for Station USC00519281 over the Last Year: <a href=\"/api/v1.0/tobs\">/api/v1.0/tobs<a><br/>"
        f"-- Min, Average & Max Temperatures for Date Range: /api/v1.0/trip/yyyy-mm-dd/yyyy-mm-dd<br>"
        f"NOTE: If no end-date is provided, the trip api calculates stats through 08/23/17<br>" 
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Creating session from Python to the DB
    session = Session(engine)

    """Return a list of all daily precipitation totals for the last year"""
    # Querying / Summarizing the daily precipitation across all stations for the last year of available data
    
    start_date = '2016-08-23'
    sel = [measurement.date, 
        func.sum(measurement.prcp)]
    precipitation = session.query(*sel).\
            filter(measurement.date >= start_date).\
            group_by(measurement.date).\
            order_by(measurement.date).all()
   
    session.close()

    # Return a dictionary with the date as the key and the daily precipitation total as the value
    precipitation_dates = []
    precipitation_totals = []

    for date, dailytotal in precipitation:
        precipitation_dates.append(date)
        precipitation_totals.append(dailytotal)
    
    precipitation_dict = dict(zip(precipitation_dates, precipitation_totals))

    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all the active Weather stations in Hawaii"""
    # Return a list of active weather stations in Hawaii
    sel = [measurement.station]
    active_stations = session.query(*sel).\
        group_by(measurement.station).all()
    session.close()

    # Return a dictionary with the date as the key and the daily precipitation total as the value
    # Converting a list of tuples into a normal list and returning the JSonified list
    list_of_stations = list(np.ravel(active_stations)) 
    return jsonify(list_of_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Creating session from Python to the DB
    session = Session(engine)
    # Querying the last 12 months of temp observation data for the most active station
    start_date = '2016-08-23'
    sel = [measurement.date, 
        measurement.tobs]
    station_temps = session.query(*sel).\
            filter(measurement.date >= start_date, measurement.station == 'USC00519281').\
            group_by(measurement.date).\
            order_by(measurement.date).all()

    session.close()

    # Returning a dictionary with the date as key and the daily temperature observation as value
    observation_dates = []
    temperature_observations = []

    for date, observation in station_temps:
        observation_dates.append(date)
        temperature_observations.append(observation)
    
    most_active_tobs_dict = dict(zip(observation_dates, temperature_observations))

    return jsonify(most_active_tobs_dict)

@app.route("/api/v1.0/trip/<start_date>")
def trip1(start_date, end_date='2017-08-23'):
    # Calculating the minimum, average and maximum temperatures for the range of the dates starting with 'start date'.
    # Defaulting to the date 2017-08-23 if no end date is provided.

    session = Session(engine)
    query_result = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()
    session.close()

    trip_stats = []
    for min, avg, max in query_result:
        trip_dict = {}
        trip_dict["Min"] = min
        trip_dict["Average"] = avg
        trip_dict["Max"] = max
        trip_stats.append(trip_dict)

    # Returning non-null value results, returning an error message otherwise.
    if trip_dict['Min']: 
        return jsonify(trip_stats)
    else:
        return jsonify({"error": f"Date {start_date} not found or not formatted as YYYY-MM-DD."}), 404
  
@app.route("/api/v1.0/trip/<start_date>/<end_date>")
def trip2(start_date, end_date='2017-08-23'):
    # Calculating the minimum, average and maximum temperatures for the range of the dates starting with 'start date'.
    # Defaulting to the date 2017-08-23 if no end date is provided.

    session = Session(engine)
    query_result = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()
    session.close()

    trip_stats = []
    for min, avg, max in query_result:
        trip_dict = {}
        trip_dict["Min"] = min
        trip_dict["Average"] = avg
        trip_dict["Max"] = max
        trip_stats.append(trip_dict)

    # Returning non-null value results, returning an error message otherwise.
    if trip_dict['Min']: 
        return jsonify(trip_stats)
    else:
        return jsonify({"error": f"Date(s) not found, invalid date range or dates not formatted correctly."}), 404
  

if __name__ == '__main__':
    app.run(debug=True)