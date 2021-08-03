variable "aws_region" {
  type        = string
  description = "The AWS region things are created in"
  default = "ca-central-1"
}

variable "IncomingWebHookUrl" {
    type        = string
    description = "Rocketchat Incoming Web Hook Urls. Should be in a delimited list of SEVERITY=https://webhookurl,SEVERITY=https://webhookurl,..."
}

variable "LambdaEnvLogLevel" {
    type = string
    default = "INFO"
}

variable "LambdaTimeout" {
    type    = number
    default = 30
}