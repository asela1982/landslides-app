# Import necessary libraries
import os
import numpy as np
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect)
# Python script for cleaning data
from data_clean_vis import clean_data_viz


#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Database Setup
#################################################
Base = automap_base()

engine = create_engine(os.environ.get("DATABASE_URL"))

# Reflect the tables
Base.prepare(engine, reflect=True)

# Mapped classes are now created with names by default
# matching that of the table name.
Landslides = Base.classes.landslides
session = Session(engine)

# Create a route that renders index.html template
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/geodata")
def geo():
    results = session.query(Landslides.hazard_type, Landslides.latitude, Landslides.longitude).all()

    hazard_type = [result[0] for result in results]
    latitude = [result[1] for result in results]
    longitude = [result[2] for result in results]

    geo_data = [{
        "hazard_type": hazard_type,
        "latitude": latitude,
        "longitude": longitude
    }]

    return jsonify(geo_data)

@app.route("/api/leaflet")
def landslide_map():
    sel = [Landslides.latitude, Landslides.longitude, Landslides.landslide_size, Landslides.landslide_type, Landslides.trigger]

    results = session.query(*sel).all()

    mylist = []
    
    for result in results:
        landslide_map = {}
        landslide_map["latitude"] = result[0]
        landslide_map["longitude"] = result[1]
        landslide_map["landslide_size"] = result[2]
        landslide_map["landslide_type"] = result[3]
        landslide_map["trigger"] = result[4]
        mylist.append(landslide_map)

    return jsonify(mylist)

@app.route("/api/leaflet/geojson")
def leaflet_geojson():
    sel = [Landslides.latitude, Landslides.longitude, Landslides.landslide_size, Landslides.landslide_type, Landslides.trigger]

    results = session.query(*sel).all()

    mylist = []

    for result in results:
        landslide_map = {}
        landslide_map["type"] = "Feature"
        landslide_map["geometry"] = {}
        landslide_map["geometry"]["type"] = "Point"
        landslide_map["geometry"]["coordinates"] = [result[0], result[1]]
        landslide_map["properties"] = {}
        landslide_map["properties"]["landslide_size"] = result[2]
        landslide_map["properties"]["landslide_type"] = result[3]
        landslide_map["properties"]["trigger"] = result[4]
        mylist.append(landslide_map)

    crsdict = {}
    crsdict["type"] = "name"
    crsdict["properties"] = {}
    crsdict["properties"]["name"] = "urn:ogc:def:crs:OGC:1.3:CRS84"    
    
    geojson = {"type": "FeatureCollection", "features": mylist, "crs": crsdict}
    
    return jsonify(geojson)
@app.route("/api/vis")
def clean_data_for_vis():

    return jsonify(clean_data_viz())

if __name__ == "__main__":
    app.run()
