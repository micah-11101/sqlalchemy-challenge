# Import the dependencies.
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
from datetime import datetime, timedelta


#Global Variables

# Calculate the date one year from the last date in data set
end_date = datetime.strptime("2017-08-23", "%Y-%m-%d").date()
start_date = end_date - timedelta(days=365)

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
station = Base.classes.station
measurement = Base.classes.measurement


# Create our session (link) from Python to the DB
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
        f"/api/v1.0/start/end<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """precipitation analysis"""
    # Query precipitation and date
    precipitation_query = session.query(measurement.prcp, measurement.date).filter(measurement.date.between(start_date, end_date)).all()

    #Convert Sqlalchemy.engine.row to list
    dates = []
    precipitation_amount = []

    for p, d in precipitation_query:
        dates.append(d)
        precipitation_amount.append(p)

    # Save the query results to a dict
    precipitation_dict = dict(zip(dates, precipitation_amount))


    return jsonify(precipitation_dict)


@app.route("/api/v1.0/stations")
def stations():
    """list data of all stations"""      
    # Query the names
    stations_query = session.query(station.name).all()

    #convert to list
    stations_list = list(np.ravel(stations_query))
    

    #jsonify the list
    return jsonify(stations_list)


@app.route("/api/v1.0/tobs")
def tobs():
    """query most active station from the past year"""
    # Query tobs for top station
    tobs_query = session.query(measurement.tobs, measurement.date.desc()).\
    filter(measurement.station == "USC00519281").\
    filter(measurement.date.between(start_date, end_date)).all()


    tobs_amount = []
    dates = []
    #convert to list
    for t, d in tobs_query:
        tobs_amount.append(t)
        dates.append(d)

    tobs_list = []
    #Create list entry for each date and tobs
    for i in range(len(dates)):
        tobs_list.append(f"Date: {dates[i]}, TOBS: {tobs_amount[i]}")

    #jsonify list
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start(start):
    """return min max and avg temperature from specified start date"""
    #filter query with start date
    start_only_query = session.query(func.min(measurement.tobs), 
                                func.avg(measurement.tobs), 
                                func.max(measurement.tobs)).\
                                filter(measurement.date >= start).all()
    
    #turn query into dictionary
    temps = [{'Minimum Temperature': min,
          'Average Temperature': avg,
          'Maximum Temperature': max}
         for min, avg, max in start_only_query]

    
    return jsonify(temps)
    

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end="2017-08-23"):
    """return min max and avg temperature from specified start and end date"""
    #filter query with start and end date
    start_end_query = session.query(func.min(measurement.tobs), 
                                func.avg(measurement.tobs), 
                                func.max(measurement.tobs)).\
                                filter(measurement.date >= start).\
                                    filter(measurement.date <= end).all()
    
    #turn query into dictionary
    temps = [{'Minimum Temperature': min,
          'Average Temperature': avg,
          'Maximum Temperature': max}
         for min, avg, max in start_end_query]

    return jsonify(temps)


    

