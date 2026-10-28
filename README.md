# COSC473-DroneProj
## Requirements
Run `pip install -r requirements.txt` install the necessary packages for the program or:

`pip install boto3'`
`pip install botocore`
`pip install codrone_edu`
`pip install python-dateutil`
`pip install python-dotenv`
`pip install s3transfer`

## .env File

The .env file has 4 variavles that must be setup.

When using AWS Learner Lab the AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_SESSION_TOKEN can be found by clicking `AWS Details` > then under `AWS CLI` click `Show`. 

[!IMPORTANT] Whenever you relaunch an AWS Learner Lab instance, even when using the same bucket these AWS keys and token values will change.

`AWS_BUCKET=YOUR-BUCKET-NAME`
`AWS_ACCESS_KEY_ID`
`AWS_SECRET_ACCESS_KEY`
`AWS_SESSION_TOKEN`

## Output

This program will collect data from a CoDrone EDU drone will it is flying. The data will be written to a .csv file, then uploaded to an AWS S3 bucket.