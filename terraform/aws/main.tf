terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 2.70"
    }
  }
}
provider "aws" {
  region = var.aws_region
}

locals {
  //Put all common tags here
  common_tags = {
    Project = "Rocketchat Notifications"   
  }  
}



resource "aws_iam_role" "security_hub_to_rocketchat_role" {
  name = "security_hub_to_rocketchat_role"
  path = "/service-role/"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF

  tags = local.common_tags
}


resource "aws_iam_role_policy_attachment" "lambda_xray_writeonly" {
  role       = aws_iam_role.security_hub_to_rocketchat_role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSXrayWriteOnlyAccess"
}


resource "aws_iam_role_policy_attachment" "lambda_org_list_accounts" {
  role       = aws_iam_role.security_hub_to_rocketchat_role.name
  policy_arn = aws_iam_policy.org_policy.arn
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution_role" {
  role       = aws_iam_role.security_hub_to_rocketchat_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "null_resource" "sam_execute" {

 provisioner "local-exec" {

    command = "/bin/bash ../../terraform/aws/build.sh"
  }
}

# Lambda
resource "aws_lambda_function" "findings_to_rocketchat" {
  depends_on = ["null_resource.sam_execute"]
  filename      = "/builds/securityhubfindings-to-rocketchat.zip"
  function_name = "sea-send-securityhubfindings-to-rocketchat"
  role          = aws_iam_role.security_hub_to_rocketchat_role.arn
  handler       = "index.handler"
  

  
  runtime = "python3.8"
  timeout = var.LambdaTimeout

  environment {
    variables = {
      IncomingWebHookUrl = var.IncomingWebHookUrl,
      LOG_LEVEL = var.LambdaEnvLogLevel,
      ParentId = var.ParentId
    }
  }

  tags = local.common_tags
}


# CloudWatch Events Rules
resource "aws_cloudwatch_event_rule" "security_hub_findings_to_rocketchat" {
  name        = "SecurityHubFindingsToRocketchatFromImport"
  description = "CloudWatchEvents Rule to enable SecurityHub Findings to Rocketchat"

  event_pattern = <<EOF
{
  "source": [
      "aws.securityhub"
  ],
  "detail-type": [
    "Security Hub Findings - Imported"
  ],
  "detail": {
      "findings": {
          "Severity": {
              "Label": [
                  "HIGH", "CRITICAL"
              ]
          },
          "ProductFields": {
              "aws/securityhub/ProductName": [
                  "GuardDuty"
              ]
          }
      }
  }
}
EOF

    tags = local.common_tags
}

resource "aws_cloudwatch_event_target" "findings_to_rocketchat" {
  rule      = aws_cloudwatch_event_rule.security_hub_findings_to_rocketchat.name
  target_id = "FindingsToRocketchat"
  arn       = aws_lambda_function.findings_to_rocketchat.arn
}

# Lambda Permissions
resource "aws_lambda_permission" "security_hub_findings_to_rocketchat_event_rule_lambda_invoke_permissions" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.findings_to_rocketchat.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.security_hub_findings_to_rocketchat.arn
}

resource "aws_lambda_permission" "security_hub_findings_to_rocketchat_sns_lambda_invoke_permissions" {
  statement_id  = "AllowExecutionFromSNS"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.findings_to_rocketchat.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.rocketchat_alert_topic.arn
}

# SNS Topic
resource "aws_sns_topic" "rocketchat_alert_topic" {
  name = "rocketchat-alerts"
  display_name = "Rocketchat Alerts"
  tags = local.common_tags
}

resource "aws_sns_topic_policy" "default" {
  arn = aws_sns_topic.rocketchat_alert_topic.arn
  policy = data.aws_iam_policy_document.sns_topic_policy.json
}

data "aws_iam_policy_document" "sns_topic_policy" {
  statement {
    actions = [    
      "SNS:Publish"
    ]
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["budgets.amazonaws.com"]
    }
    resources = [
      aws_sns_topic.rocketchat_alert_topic.arn,
    ]    
  }
}




resource "aws_iam_policy" "org_policy" {
  name        = "org_list_accounts"
  path        = "/"
  description = "list accounts"

  # Terraform's "jsonencode" function converts a
  # Terraform expression result to valid JSON syntax.
  policy = jsonencode({
    Version = "2012-10-17"
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "organizations:ListPoliciesForTarget",
                "organizations:DescribeEffectivePolicy",
                "organizations:ListRoots",
                "organizations:ListTargetsForPolicy",
                "organizations:ListTagsForResource",
                "organizations:ListDelegatedServicesForAccount",
                "organizations:DescribeAccount",
                "organizations:ListAWSServiceAccessForOrganization",
                "organizations:DescribePolicy",
                "organizations:ListChildren",
                "organizations:ListPolicies",
                "organizations:ListAccountsForParent",
                "organizations:ListHandshakesForOrganization",
                "organizations:ListDelegatedAdministrators",
                "organizations:ListHandshakesForAccount",
                "organizations:ListAccounts",
                "organizations:ListCreateAccountStatus",
                "organizations:DescribeOrganization",
                "organizations:DescribeOrganizationalUnit",
                "organizations:ListParents",
                "organizations:ListOrganizationalUnitsForParent",
                "organizations:DescribeHandshake",
                "organizations:DescribeCreateAccountStatus"
            ],
            "Resource": "*"
        }
    ]
  })
}