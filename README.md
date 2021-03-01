
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](./LICENSE)

# AWS SEA Notifications to Rocket.Chat

A serveless application to send AWS SEA (Secure Environment Accelerator) Budget and Security notifications to Rocket.Chat (RC).  

## Introduction

The application is comprised of an AWS Lambda function written in Python that gets triggered through CloudWatch Events (security alerts), and SNS Topic (budgeting alerts).
The Lambda function formats and routes the notifications to proper RC channel based on their type and severity: 

- `aws-budget` receives budget notifications when the account spending is reaching it's budget thresholds. Only accounts with a set Budget threshold participate. 
- `aws-security-low` receives low-severity security notifications from team accounts in AWS SEA environment. These are *informational* alerts and don't require any actions most of the times.
- `aws-security-medium` receives medium-severity security notifications from team accounts in AWS SEA environment. These are the alerts to *monitor and potentially take remedial actions*.
- `aws-security-high` receives high-severity security notifications from team accounts in AWS SEA environment. These are alerts must be *closely watched and triaged ASAP*.
- `aws-security-critical` receives critical-severity security notifications from team accounts in AWS SEA environment. These are the most critical alerts and *should be remediated immediately*.


## Prerequisites

In order to build, package, and run the app locally, you will need:

- a `bash`-like terminal environment; testing has primarily been done using MacOS Catalina
- `Docker`
- `AWS SAM(Serverless Application Model)`- to build the Lambda function (on MacOS Catalina, ```brew tap aws/tap```, ```brew install aws-sam-cli```)
- `zip`- to compress the Lambda build artifacts into a sigle zip file


In order to deploy to AWS, you will also need:

- `terraform` 12 or newer
- the AWS CLI (on MacOS Catalina, ```brew install awscli```)
- access to an AWS account and mechanism to get temporary (STS) credentials

You would need to set up Webhook URL's for the above RC channels and add the URL's to `IncomingWebHookUrl` in a *tfvars* file prior to deployment. The *tfvars* file should contain the following variables:

- aws_region = The AWS region you want to deploy the app to, e.g. `ca-central-1`
- IncomingWebHookUrl = `"BUDGET=<Webhook URL for aws-budget>,LOW=<Webhook URL for aws-security-low>,MEDIUM=<Webhook URL for aws-security-medium>,HIGH=<Webhook URL for aws-security-high>,CRITICAL=<Webhook URL for aws-security-critical>"`
- LambdaEnvLogLevel = Lambda event log level, e.g. `INFO`
- LambdaTimeout = Lambda timeout in second, e.g. `10`

## Build, Packaging and Testing Locally

- **Build**: run ```sam build --use-container -b ../../builds``` within the lambdas/rocketchat-notification folder
- **Package**: run ```zip -r ../securityhubfindings-to-rocketchat.zip *``` within the builds/SecurityHubFindingsToRocketchat folder that gets created by the **Build** step
- **DebugLocal**: run ```sam local invoke --env-vars env.json -e events.json -t template.yaml``` within the lambdas/rocketchat-notification folder
> Please open an issue if you need samples of `env.json`, `event.json`, and `budget_events.json` files for your local testing/debugging

## Deployment to AWS

Once you have a deployment package (zip file) created in the builds folder, you can deploy the application using `Terraform`.

> You will need to *Log into AWS* before running the command below and make your credentials visible to your command shell via environment variables `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and `AWS_SESSION_TOKEN`.

## Project Status
- [x] Development
- [x] Production/Maintenance

## Documentation
<!--- Point to another readme or create a GitHub Pages (https://guides.github.com/features/pages/) --->
- [AWS SEA (Secure Environment Accelerator)](https://github.com/BCDevOps/aws-secure-environment-accelerator/blob/master/README.md)
- [AWS SAM (Serverless Application Model)](https://github.com/aws/aws-sam-cli)

## Getting Help or Reporting an Issue
<!--- Example below, modify accordingly --->
To report bugs/issues/feature requests, please file an [issue](../../issues).


## How to Contribute
<!--- Example below, modify accordingly --->
If you would like to contribute, please see our [CONTRIBUTING](./CONTRIBUTING.md) guidelines.

Please note that this project is released with a [Contributor Code of Conduct](./CODE_OF_CONDUCT.md). 
By participating in this project you agree to abide by its terms.


## License
<!--- Example below, modify accordingly --->
    Copyright 2018 Province of British Columbia

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
