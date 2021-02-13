variable "aws_region" {
  type        = string
  description = "The AWS region things are created in"
}

variable "IncomingWebHookUrl" {
    type        = string
    description = "Rocketchat Incoming Web Hook Urls. Should be in a delimited list of SEVERITY=https://webhookurl,SEVERITY=https://webhookurl,..."
}

variable "LambdaEnvLogLevel" {
    type = string
}

variable "LambdaTimeout" {
    type    = number
}