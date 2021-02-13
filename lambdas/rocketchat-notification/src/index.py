import boto3
import botocore
import json
import logging
import requests
import time
import os
import math
import urllib.parse
from os import environ
from datetime import datetime
from datetime import date


webHookUrlValues = os.getenv('IncomingWebHookUrl')

def setup_default_logging(request_id, level=logging.INFO):
  """Creates the logging formatter.

  Args:
      request_id: (str) The id of the execution context (i.e. the Lambda execution ID).
      level: logging level to use.
  """
  logger = logging.getLogger()
  console_handler = logging.StreamHandler()
  formatter = logging.Formatter(
    '[%(levelname)s] %(asctime)s {0} [%(module)s:%(lineno)d]: %(message)s'.format(request_id))
  console_handler.setFormatter(formatter)

  # Get rid of any default handlers (Lambda apparently adds one).
  logger.handlers = []
  logger.addHandler(console_handler)
  logger.setLevel(level)
  return logger


def handler(event, context):

    environ["request_id"] = context.aws_request_id
    logger = setup_default_logging(environ["request_id"], environ["LOG_LEVEL"])
    responseStatus = 'SUCCESS'
    reason = None
    responseData = {}
    
    result = {
        'StatusCode': '200',
        'Body':  {'message': 'success'}
    }


    try:
      logging.getLogger().info(event)
      
      request_type = event['RequestType'].upper() if ('RequestType' in event) else ""
      logging.getLogger().info(request_type)

      if webHookUrlValues != None:
        channels = webHookUrlValues.split(',')
        webHookUrlLookup = {}

        for channel in channels:
          channelMap = channel.split('=')
          webHookUrlLookup[channelMap[0]] = channelMap[1]
        
        # Check for message
        if "Records" in event:
          logging.getLogger().info("has records")
          for record in event["Records"]:
            if "EventSource" in record and record["EventSource"] == "aws:sns":
              subject = record["Sns"]["Subject"]
              msg = record["Sns"]["Message"]

              attachment = [
                {                        
                  "title": subject,                  
                  "text": msg
                }
              ]

              rocketChatMessage = {        
                "text": "*AWS Notification*",
                "attachments": attachment
              }
          
              if subject.startswith("AWS Budgets:"):
                webHookUrlName = "BUDGET"
              else:
                webHookUrlName = "GENERAL"

              if webHookUrlName in webHookUrlLookup:
                response = requests.post(
                  webHookUrlLookup[webHookUrlName],        
                  data=json.dumps(rocketChatMessage),
                  headers={"Content-Type": "application/json"}
                )
              else:
                logging.getLogger().info('configuration "{}" not in mapping. Skipping.'.format(webHookUrlName))
            else:
              logging.getLogger().info('Unknown event source "{}" not in mapping. Skipping.'.format(record["EventSource"]))
                
        else:
          logging.getLogger().info("has security hub findings")
          # Security Hub Findings
          for finding in event["detail"]["findings"]:

            responseData = ""
          
            consoleUrl = "https://{region}.console.aws.amazon.com/securityhub".format(region=os.getenv('AWS_REGION'))
            findingTitle = finding["Title"]
            findingType = finding["Types"][0]
            findingDescription = finding["Description"]
            findingTime = finding["UpdatedAt"]
            lastObservedAt = finding["LastObservedAt"]
            account = finding["AwsAccountId"]
            region = finding["Resources"][0]["Region"]
            resourceType =finding["Resources"][0]["Type"]
            messageId = finding["Id"]

            lastSeen = findingTime

            colour = "#7CD197"
            severity = ""
            
            severityNormalized = finding["Severity"]["Normalized"]

            if 1 <=severityNormalized and severityNormalized <= 39:
              severity = "LOW"
              colour = "#879596"
            elif 40 <=severityNormalized and severityNormalized <= 69:
              severity = "MEDIUM"
              colour = "#ed7211"
            elif 70 <=severityNormalized and severityNormalized <= 89:
              severity = "HIGH"
              colour = "#ed7211"
            elif 90 <=severityNormalized and severityNormalized <= 100:
              severity = "CRITICAL"
              colour = "#ff0209"
            else:
              severity = "INFORMATIONAL"
              colour = "#007cbc"  


            findQuery = "search=Id%3D%255Coperator%255C%253AEQUALS%255C%253A{messageId}".format(messageId=urllib.parse.quote(messageId, safe=''))        

            attachment = [
              {                        
                "title": findingTitle,
                "title_link": "{console}/home?region={region}#/findings?{findQuery}".format(console=consoleUrl,region=region,findQuery=findQuery),
                "text": findingDescription,
                "color": colour,
                "ts": findingTime,
                "fields": [
                  {
                    "title": "Severity",
                    "value": severity,
                    "short": True
                  },
                  {
                    "title": "Region",
                    "value": region,
                    "short": True
                  },
                  {
                    "title": "Resource Type",
                    "value": resourceType,
                    "short": True
                  },
                  {
                    "title": "Last Seen",
                    "value": lastObservedAt,
                    "short": True
                  },
                  {
                    "title": "Finding Type",
                    "value": findingType,
                    "short": True
                  }
                ]
              }
            ]

            rocketChatMessage = {        
              "text": "*AWS SecurityHub finding in {region} for Acct: {account}*".format(region=region, account=account),
              "attachments": attachment
            }
          
            if severity in webHookUrlLookup:
              response = requests.post(
                webHookUrlLookup[severity],        
                data=json.dumps(rocketChatMessage),
                headers={"Content-Type": "application/json"}
              )
            else:
              logging.getLogger().info('severity "{}" not in mapping. Skipping.'.format(severity))
          
    except Exception as error:
        logging.getLogger().error(error, exc_info=True)
        responseStatus = 'FAILED'
        reason = str(error)
        result = {
        'statusCode': '500',
        'body':  {'message': reason}
        }

    return json.dumps(result)