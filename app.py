###############################################
# Dependencies
###############################################

import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt


#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)


#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

# Create route and link - precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():

    # Convert to a dictionary with date as key and prcp as the value
    results_prcp = session.query(Measurement.date, Measurement.prcp).all()


    all_precipitation = []
    for date, prcp in results_prcp:
        precipitation_dict = {}
        precipitation_dict[date] = prcp
        all_precipitation.append(precipitation_dict)

    return jsonify(all_precipitation)


# Create route and link - stations
@app.route("/api/v1.0/stations")
def stations():
    results_stations = session.query(Station.id, Station.name).all()
  
    all_stations = []
    for id, name in results_stations:
        stations_dict = {}
        stations_dict["id"] = id
        stations_dict["name"] = name
        all_stations.append(stations_dict)
    return jsonify(all_stations)
 

# Create route and link - temperatures
@app.route("/api/v1.0/tobs")
def tobs():
   

   
  # Query the dates and temperatures for the most active station over the last year of data
    most_active_station = session.query(Measurement.station).group_by(Measurement.station).order_by\
    (func.count(Measurement.id).desc()).first()
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    latest_year = dt.date(2017,8,23) - dt.timedelta(days=365)
    
    results_tobs = session.query(Measurement.station, Measurement.date, Measurement.tobs).filter\
       (Measurement.station == most_active_station[0]).filter(Measurement.date >= latest_year)\
       .order_by(Measurement.date.desc()).all()

    tobs_stations = []
    for station, date, prcp in results_tobs:
        tobs_dict = {}
        tobs_dict["station"] = station
        tobs_dict["date"] = date
        tobs_dict ["prcp"] = prcp
        tobs_stations.append(tobs_dict)
    
    return jsonify(tobs_stations)


    #Create route and link for calculations - start
#@app.route("/api/v.1.0/<start>")
# @app.route("/api/v.1.0/2015-02-24")
# def start (start = None):
#     #start = dt.strptime('2015-02-24', '%Y-%m-%d').date()

#     results_start = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs),\
#     func.avg(Measurement.tobs).filter(Measurement.date >= start))

#     results_start_list = list(np.ravel(results_start))
#     return jsonify(results_start_list)
   

#     # Create route and link for calculations - pick start and end dates
# #@app.route("/api/v.1.0/<start>/<end>")
# @app.route("/api/v.1.0/2015-02-24/2016-02-24")
# def end (start = None, end = None):
#     # start = dt.strptime('2015-02-24', '%Y-%m-%d').date()
#     # end = dt.strptime('2016-02-24', '%Y-%m-%d').date()
#     results_end = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs),\
#     func.avg(Measurement.tobs).filter(Measurement.date >= start)).filter(Measurement.date <= end).\
#     group_by(Measurement.date).all()

#     results_end_list = list(np.ravel(results_end))
#     return jsonify(results_end_list)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start(start = None, end = None):

    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        tempresults = session.query(*sel).filter(Measurement.date >= start).all()
        tempdates = list(np.ravel(tempresults))
        return jsonify(tempdates)
    
    tempresults = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    tempdates = list(np.ravel(tempresults))
    return jsonify(tempdates=tempdates)


if __name__ == '__main__':
    app.run(debug=True)
