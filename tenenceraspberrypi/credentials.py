# Google Speech to Text API Credentials
with open('Tenence-688d118144e0.json') as data_file:
    json_credentials = data_file.read()


# AWS Polly Credentials
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
aws_access_key_id = 'AKIAJ5WWXSI4NCFPC7CA',
aws_secret_access_key = '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',
region_name = 'us-east-2'

session = Session(
    aws_access_key_id='AKIAJ5WWXSI4NCFPC7CA',
    aws_secret_access_key='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',
    region_name='us-east-2'
)
polly = session.client('polly')