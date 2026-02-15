"""
Flask Documentation:     https://flask.palletsprojects.com/
Jinja2 Documentation:    https://jinja.palletsprojects.com/
Werkzeug Documentation:  https://werkzeug.palletsprojects.com/
This file creates your application.
"""

# from crypt import methods
import site 

from app import app, Config,  mongo, Mqtt
from flask import escape, render_template, request, jsonify, send_file, redirect, make_response, send_from_directory 
from json import dumps, loads 
from werkzeug.utils import secure_filename
from datetime import datetime,timedelta, timezone
from os import getcwd
from os.path import join, exists
from time import time, ctime
from math import floor
 

#####################################
#   Routing for your application    #
#####################################

@app.route('/api/climo/get/<start>/<end>', methods=['GET']) 
def get_all(start,end):   
    '''RETURNS ALL THE DATA FROM THE DATABASE THAT EXIST IN BETWEEN THE START AND END TIMESTAMPS'''
   
    if request.method == "GET":
        # I am calling the getAllInRange function from my database helper (mongo) 
        # to fetch all documents between the two timestamps
        data = mongo.getAllInRange(start, end)
        
        if data:
            return jsonify({"status":"found", "data": data})

    # FILE DATA NOT EXIST
    return jsonify({"status":"not found","data":[]})
   


@app.route('/api/mmar/temperature/<start>/<end>', methods=['GET']) 
def get_temperature_mmar(start,end):   
    '''RETURNS MIN, MAX, AVG AND RANGE FOR TEMPERATURE. THAT FALLS WITHIN THE START AND END DATE RANGE'''
   
    if request.method == "GET": 
        # I updated this to specifically call the temperature MMAR function
        # This will return the Min, Max, Avg and Range for the specified period
        data = mongo.temperatureMMAR(start, end)
        
        if data:
            return jsonify({"status":"found", "data": data})

    # FILE DATA NOT EXIST
    return jsonify({"status":"not found","data":[]})





@app.route('/api/mmar/humidity/<start>/<end>', methods=['GET']) 
def get_humidity_mmar(start,end):   
    '''RETURNS MIN, MAX, AVG AND RANGE FOR HUMIDITY. THAT FALLS WITHIN THE START AND END DATE RANGE'''
   
    if request.method == "GET": 
        # I updated this to call the humidity aggregation function
        # It processes the data in the backend and returns the calculated statistics
        data = mongo.humidityMMAR(start, end)
        
        if data:
            return jsonify({"status":"found", "data": data})

    # FILE DATA NOT EXIST
    return jsonify({"status":"not found","data":[]})





@app.route('/api/frequency/<variable>/<start>/<end>', methods=['GET']) 
def get_freq_distro(variable,start,end):   
    '''RETURNS FREQUENCY DISTRIBUTION FOR SPECIFIED VARIABLE'''
   
    if request.method == "GET": 
        # I added this to call the frequency distribution function
        # This takes the variable (temp/humidity/heatindex) and returns counts in buckets
        data = mongo.frequencyDistro(variable, start, end)
        
        if data:
            return jsonify({"status":"found", "data": data})

    # FILE DATA NOT EXIST
    return jsonify({"status":"not found","data":[]})



@app.route('/api/file/get/<filename>', methods=['GET']) 
def get_images(filename):   
    '''RETURNS REQUESTED FILE FROM UPLOADS FOLDER'''
   
    if request.method == "GET":
        # I updated this to serve files from the defined uploads folder
        file_path = join(getcwd(), Config.UPLOADS_FOLDER, filename)
        
        if exists(file_path):
            return send_from_directory(join(getcwd(), Config.UPLOADS_FOLDER), filename)
        
        # FILE DOES NOT EXIST
        return jsonify({"status":"file not found"}), 404



@app.route('/api/file/upload',methods=["POST"])  
def upload():
    '''SAVES A FILE TO THE UPLOADS FOLDER'''
    
    if request.method == "POST": 
        file     = request.files['file']
        filename = secure_filename(file.filename)
        file.save(join(getcwd(),Config.UPLOADS_FOLDER , filename))
        return jsonify({"status":"File upload successful", "filename":f"{filename}" })

 


###############################################################
# The functions below should be applicable to all Flask apps. #
###############################################################


@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)

@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also tell the browser not to cache the rendered page. If we wanted
    to we could change max-age to 600 seconds which would be 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

@app.errorhandler(405)
def page_not_found(error):
    """Custom 404 page."""    
    return jsonify({"status": 404}), 404