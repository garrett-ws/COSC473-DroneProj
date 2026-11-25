# COSC473-DroneProj
## Requirements
Run `pip install -r requirements.txt` install the necessary packages in your environment.

## Kafka Setup

Install Docker for your respective OS. [Official Site](https://docs.docker.com/engine/install/)

After installing Docker install the official Apache Kafka JVM Docker image by running `docker pull apache/kafka:4.4.0` from a terminal.

Start the Kafka Server before running the program: `docker run -p 9092:9092 apache/kafka:4.4.0`

## Output

This program will collect data from a CoDrone EDU drone will it is flying. The data is sent to a Kafka Producer, which then sends the data to a Spark Structured Streaming Window. The average values for each Window are written to disk in a .csv file. The values in the .csv files are read into a pandas dataframe and the average values for various drone sensor values plotted using matplotlib. The plotted graphs are shown on screen and saved to disk.
