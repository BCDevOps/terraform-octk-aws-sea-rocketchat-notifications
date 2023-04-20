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

import boto3
ssm = boto3.client('ssm')
parameter = ssm.get_parameter(Name='/ecf/channels/webhooks', WithDecryption=True)
print(parameter['Parameter']['Value'])
webHookUrlValues = parameter['Parameter']['Value']
ParentId = os.getenv("ParentId")
ParentId1 = os.getenv("ParentId1")

client = boto3.client("organizations", region_name="ca-central-1")


def setup_default_logging(request_id, level=logging.INFO):
    """Creates the logging formatter.

    Args:
        request_id: (str) The id of the execution context (i.e. the Lambda execution ID).
        level: logging level to use.
    """
    logger = logging.getLogger()
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(levelname)s] %(asctime)s {0} [%(module)s:%(lineno)d]: %(message)s".format(
            request_id
        )
    )
    console_handler.setFormatter(formatter)

    # Get rid of any default handlers (Lambda apparently adds one).
    logger.handlers = []
    logger.addHandler(console_handler)
    logger.setLevel(level)
    return logger


def handler(event, context):

    environ["request_id"] = context.aws_request_id
    logger = setup_default_logging(environ["request_id"], environ["LOG_LEVEL"])
    responseStatus = "SUCCESS"
    reason = None
    responseData = {}

    result = {"StatusCode": "200", "Body": {"message": "success"}}

    try:
        logging.getLogger().info(event)

        request_type = event["RequestType"].upper() if (
            "RequestType" in event) else ""
        logging.getLogger().info(request_type)

        if webHookUrlValues != None:
            channels = webHookUrlValues.split(",")
            webHookUrlLookup = {}

            for channel in channels:
                channelMap = channel.split("=")
                webHookUrlLookup[channelMap[0]] = channelMap[1]

            # Check for message
            if "Records" in event:
                logging.getLogger().info("has records")
                for record in event["Records"]:
                    if "EventSource" in record and record["EventSource"] == "aws:sns":
                        subject = record["Sns"]["Subject"]
                        msg = record["Sns"]["Message"]

                        attachment = [{"title": subject, "text": msg}]

                        rocketChatMessage = {
                            "text": "*AWS Notification*",
                            "attachments": attachment,
                        }
                        teamsMessage = {
                            "@type": "MessageCard",
                            "@context": "http://schema.org/extensions",
                            "themeColor": "0076D7",
                            "summary": "AWS Alert",
                            "sections": [{
                                "activityTitle": "AWS Notification",
                                "activityImage": "https://logos-world.net/wp-content/uploads/2021/08/Amazon-Web-Services-AWS-Logo.png",
                                "facts": [{
                                        "name": "Title",
                                        "value": subject
                                }, {
                                    "name": "Message",
                                    "value": msg
                                }],
                                "markdown": True
                            }]
                        }

                        if subject.startswith("AWS Budgets:"):
                            webHookUrlName = "BUDGET"
                            # [1] = "BUDGET_TEAMS"
                        else:
                            webHookUrlName = "GENERAL"

                        for key, value in webHookUrlName.items():
                            if webHookUrlName in key:

                                if "rocketchat" in webHookUrlLookup:
                                    response = requests.post(
                                        webHookUrlLookup[key],
                                        data=json.dumps(rocketChatMessage),
                                        headers={
                                            "Content-Type": "application/json"},
                                    )
                                if "teams" in webHookUrlLookup:
                                    response = requests.post(
                                        webHookUrlLookup[key],
                                        data=json.dumps(teamsMessage),
                                        headers={
                                            "Content-Type": "application/json"},
                                    )
                            else:
                                logging.getLogger().info(
                                    'configuration "{}" not in mapping. Skipping.'.format(
                                        webHookUrlName
                                    )
                                )
                    else:
                        logging.getLogger().info(
                            'Unknown event source "{}" not in mapping. Skipping.'.format(
                                record["EventSource"]
                            )
                        )

            else:
                logging.getLogger().info("has security hub findings")
                # Security Hub Findings
                response = client.list_accounts_for_parent(ParentId=ParentId)
                response1 = client.list_accounts_for_parent(ParentId=ParentId1)

                core_accounts = []

                for acc in response["Accounts"]:
                    core_accounts.append(acc["Id"])
                for acc in response1["Accounts"]:
                    core_accounts.append(acc["Id"])

                for finding in event["detail"]["findings"]:

                    responseData = ""

                    consoleUrl = (
                        "https://{region}.console.aws.amazon.com/securityhub".format(
                            region=os.getenv("AWS_REGION")
                        )
                    )
                    findingTitle = finding["Title"]
                    findingType = finding["Types"][0]
                    findingDescription = finding["Description"]
                    findingTime = finding["UpdatedAt"]
                    lastObservedAt = finding.get("LastObservedAt", None)
                    account = finding["AwsAccountId"]
                    region = finding["Resources"][0].get("Region", None)
                    resourceType = finding["Resources"][0]["Type"]
                    messageId = finding["Id"]

                    lastSeen = findingTime

                    colour = "#7CD197"
                    severity = ""
                    if account in core_accounts:
                        accountType = "core"
                    else:
                        accountType = "workload"
                    severityNormalized = finding["Severity"]["Normalized"]

                    if 1 <= severityNormalized and severityNormalized <= 39:
                        severity = "LOW"
                        colour = "#879596"
                    elif 40 <= severityNormalized and severityNormalized <= 69:
                        severity = "MEDIUM"
                        colour = "#ed7211"
                    elif 70 <= severityNormalized and severityNormalized <= 89:
                        severity = "HIGH"
                        colour = "#ed7211"
                    elif 90 <= severityNormalized and severityNormalized <= 100:
                        severity = "CRITICAL"
                        colour = "#ff0209"
                    else:
                        severity = "INFORMATIONAL"
                        colour = "#007cbc"

                    findQuery = "search=Id%3D%255Coperator%255C%253AEQUALS%255C%253A{messageId}".format(
                        messageId=urllib.parse.quote(messageId, safe="")
                    )

                    attachment = [
                        {
                            "title": findingTitle,
                            "title_link": "{console}/home?region={region}#/findings?{findQuery}".format(
                                console=consoleUrl, region=region, findQuery=findQuery
                            ),
                            "text": findingDescription,
                            "color": colour,
                            "ts": findingTime,
                            "fields": [
                                {"title": "Severity",
                                    "value": severity, "short": True},
                                {"title": "Region", "value": region, "short": True},
                                {
                                    "title": "Resource Type",
                                    "value": resourceType,
                                    "short": True,
                                },
                                {
                                    "title": "Last Seen",
                                    "value": lastObservedAt,
                                    "short": True,
                                },
                                {
                                    "title": "Finding Type",
                                    "value": findingType,
                                    "short": True,
                                },
                            ],
                        }
                    ]

                    rocketChatMessage = {
                        "text": "*AWS SecurityHub finding in {region} for Acct: {account}*".format(
                            region=region, account=account
                        ),
                        "attachments": attachment,
                    }
                    teamsMessage = {
                        "@type": "MessageCard",
                        "@context": "http://schema.org/extensions",
                        "themeColor": "0076D7",
                        "summary": "{console}/home?region={region}#/findings?{findQuery}".format(
                            console=consoleUrl, region=region, findQuery=findQuery
                        ),
                        "sections": [
                            {
                                "activityTitle": findingDescription,
                                "activityImage": "https://logos-world.net/wp-content/uploads/2021/08/Amazon-Web-Services-AWS-Logo.png",
                                "activitySubtitle": "*AWS SecurityHub finding in {region} for Acct: {account}*".format(
                                    region=region, account=account
                                ),
                                "facts": [
                                    {"name": "Resource Type",
                                        "value": resourceType},
                                    {"name": "Last Seen", "value": lastObservedAt},
                                    {"name": "Severity", "value": severity},
                                    {"name": "Region", "value": region},
                                    {"name": "Finding Type", "value": findingType},
                                ],
                                "markdown": True,
                            }
                        ],
                        "potentialAction": [
                            {
                                "@type": "OpenUri",
                                "name": "Learn More",
                                "targets": [
                                    {
                                        "os": "default",
                                        "uri": "{console}/home?region={region}#/findings?{findQuery}".format(
                                            console=consoleUrl,
                                            region=region,
                                            findQuery=findQuery,
                                        ),
                                    }
                                ],
                            }
                        ],
                    }
                    for key, value in webHookUrlLookup.items():
                        if accountType in key and severity in key:
                            if "teams" in key:
                                response = requests.post(
                                    webHookUrlLookup["{0}".format(key)],
                                    data=json.dumps(teamsMessage),
                                    headers={
                                        "Content-Type": "application/json"},
                                )

                            if "rocketchat" in key:
                                requests.post(
                                    webHookUrlLookup["{0}".format(key)],
                                    data=json.dumps(rocketChatMessage),
                                    headers={
                                        "Content-Type": "application/json"},
                                )

                        else:
                            logging.getLogger().info(
                                'severity webhookInvocation "{}" not in mapping for key "{}". Skipping.'.format(
                                    severity, key
                                )
                            )

    except Exception as error:
        logging.getLogger().error(error, exc_info=True)
        responseStatus = "FAILED"
        reason = str(error)
        result = {"statusCode": "500", "body": {"message": reason}}

    return json.dumps(result)
