from codrone_edu.drone import *
from collections import deque
import time
from datetime import datetime, timedelta
import csv
import boto3
import os
from dotenv import load_dotenv
from kafka import KafkaProducer
import json
import pyspark
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, avg, window
from pyspark.sql.types import StructType, StructField, DoubleType, TimestampType

load_dotenv()

##############################
#  Sensor Data (Amazon S3)   #
##############################

sensorData = deque() # Hold the sensor data

# Headers are separate since some algos do not want headers in the data
sensorDataHeaders = ('timestampe, roll, pitch, yaw, height, battery')

filename = "dronedata.csv" # Name of the file to write data to and upload to S3

def getSensorData(d):
    '''Collects drone data from the following:
   -Timestamp
   -Roll
   -Pitch
   -Yaw
   -Height
   -Battery

    Args:
        d: A drone object

    The data collected from the sensors is written to the @param sensorData deque as a tuple
    '''

    now = datetime.now()
    timestamp = now.isoformat(timespec='milliseconds') # Use ISO format with miliseconds

    # Gyroscope & Accelerometer Sensors
    d_roll = d.get_angle_x()
    d_pitch = d.get_angle_y()
    d_yaw = d.get_angle_z()

    # Bottom Range Sensor    
    d_height = d.get_height()

    # State Data Sensor
    d_battery = d.get_battery()

    sensorData.append((timestamp, d_roll, d_pitch, d_yaw, d_height, d_battery))

def printSensorData():
    '''Prints the last row of sensor data'''
    print(sensorData[-1])

def writeSensorData():
    '''Writes the sensor data to a csv file'''
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(sensorData)

##############################
#       Kafka Producer       #
##############################

def kafkaStream():

    producer = KafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda v:json.dumps(v).encode('utf-8')
    )

    # 1-minute flight at 2 Hz (~120 readings)
    for i in range(120):
        data = {
            "timestamp": datetime.now().isoformat(),
            "height": drone.get_height(),
            "roll": drone.get_angle_x(),
            "pitch": drone.get_angle_y(),
            "yaw": drone.get_angle_z(),
            "battery": drone.get_battery()
        }
        producer.send("drone_telemetry", data)
        time.sleep(0.5)

    # Push any remaining windows after the 60 seconds are up
    flush_time = (datetime.now() + timedelta(seconds=25)).isoformat()
    flush_data = {
        "timestamp": flush_time,
        "height": drone.get_height(),
        "roll": drone.get_angle_x(),
        "pitch": drone.get_angle_y(),
        "yaw": drone.get_angle_z(),
        "battery": drone.get_battery()
    }
    producer.send("drone_telemetry", flush_data)

    # Now flush and close everything cleanly
    producer.flush()
    producer.close()

drone = Drone()
drone.connect()

end_time = time.time() + 3 # How long the drone collects data for in seconds, adjust as needed (for Amazon upload)

print(sensorDataHeaders)

while time.time() < end_time:
    getSensorData(drone)
    printSensorData()

writeSensorData()

# Upload the data to AWS
s3_client = boto3.client('s3')
now = datetime.now()
timestamp = now.strftime("%Y-%m-%d %H%M%S") # Format the date to remove colons to avoid issues in the filename
awspath = f'{timestamp} {filename}'
print(awspath)
s3_client.upload_file(filename, os.environ["AWS_BUCKET"], awspath)

##############################
# Spark Structured Streaming #
##############################

now = datetime.now()
timestamp = now.strftime("%Y-%m-%d %H%M%S") # Format the date to remove colons to avoid issues in the filename

batch_id = f'batch_{timestamp}' # Store each run in its own folder

spark = ( SparkSession.builder
         .appName("DroneTelemetry")
         .config("spark.jars.packages", f"org.apache.spark:spark-sql-kafka-0-10_2.13:{pyspark.__version__}")
         .getOrCreate() 
         )

schema = StructType([
    StructField("timestamp", TimestampType()),
    StructField("height", DoubleType()),
    StructField("pitch", DoubleType()),
    StructField("roll", DoubleType()),
    StructField("yaw", DoubleType()),
    StructField("battery", DoubleType())
])

raw_df = (spark.readStream
          .format("kafka")
          .option("kafka.bootstrap.servers", "localhost:9092")
          .option("subscribe", "drone_telemetry")
          .load())

telemetry_df = raw_df.select(from_json(col("value").cast("string"), schema).alias("data")).select("data.*")

agg_df = (telemetry_df
          .withWatermark("timestamp", "10 seconds")
          .groupBy(window(col("timestamp"), "10 seconds"))
          .agg(
              avg("height").alias("avg_height"),
              avg("battery").alias("avg_battery")
          )
          .select(col("window.start").alias("start_time"),
                  col("window.end").alias("end_time"),
                  "avg_height",
                  "avg_battery")
)

# Debug query, remove before submission
debug_query = (
    agg_df.writeStream
    .outputMode("update")  # Shows windows immediately as they update
    .format("console")
    .option("truncate", "false")
    .start()
)

query = (agg_df.writeStream
         .outputMode("append")
         .format("csv")
         .partitionBy("start_time")
         .option("path", f"spark_output/{batch_id}")
         .option("checkpointLocation", "checkpoint_dir")
         .start())

# Start the Kafka stream
producer_thread = threading.Thread(target=kafkaStream, daemon=True)
producer_thread.start()

query.awaitTermination()

drone.disconnect()