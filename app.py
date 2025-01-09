import json
from datetime import datetime as dt
import time as time
from apscheduler.schedulers.background import BackgroundScheduler
import Amberloop as al
import datalog as dl
import homeassistant as ha

with open("/opt/amber/config/config.json", "r") as f:
    config = json.load(f)

amberSiteId = config["amber"]["site_id"]
amberApiToken   = config["amber"]["access_token"]
amberPriceSeconds = config["amber"]["amber5minPrice_seconds"]
amberPriceMinutes = config["amber"]["amber5minPrice_minutes"]
log_5min_values = False
log_5min_forecasts = False
if config["Log_database"]["log_amber_5min_current_values"].lower() == "true":
    log_5min_values = True
if config["Log_database"]["log_amber_5min_forecasts"].lower() == "true":
    log_5min_forecasts = True
    
amberEstimatePrice = True



if log_5min_values:
    logs = dl.DataLog()
    logs.create_table_amber()
    logs.conn.close() # .close_connection()


def amberResetEstimatePrice():
    global amberEstimatePrice    
    amberEstimatePrice = True
    return amberEstimatePrice

def amber5minPrice():
    global amberEstimatePrice
    if amberEstimatePrice:
        #print("amberEstimatePrice is: ", amberEstimatePrice)
        requestTime = dt.now()
        amberData = al.get_amber_data(amberApiToken, amberSiteId,  13,5,5)
        responseTime = dt.now()
        amberEstimatePrice = amberData["current"]["general"].estimate
        if not amberEstimatePrice:
            ha.post5MinPrice(amberData)
            ha.post5minPeriods(amberData)
        if log_5min_values:
            logamber = dl.DataLog()
            logamber.log_amber_data(requestTime, responseTime, amberData)
            logamber.conn.close() # .close_connection()
        #print("Request: ", requestTime )
        ##print("Response: ", responseTime )
        #print("amberTIme: ", amberData["current"]["general"].start_time)
        #print("Price Estimate: ", amberData["current"]["general"].estimate)
    #else:
        #print("amberEstimatePrice already have it")

if __name__ == '__main__':
    #amberEstimatePrice = True
    # creating the BackgroundScheduler object
    scheduler = BackgroundScheduler()
    # setting the scheduled task
    scheduler.add_job(amberResetEstimatePrice, 'cron', minute='0,5,10,15,20,25,30,35,40,45,50,55' ,second=5)
    scheduler.add_job(amber5minPrice, 'cron', minute=amberPriceMinutes ,second=amberPriceSeconds)
    # starting the scheduled task using the scheduler object
    scheduler.start()
    try:
        # To simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary but recommended
        scheduler.shutdown()
