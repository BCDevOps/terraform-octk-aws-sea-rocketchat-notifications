variable "aws_region" {
  type        = string
  description = "The AWS region things are created in"
  default     = "ca-central-1"
}

variable "IncomingWebHookUrl" {
  type        = string
  description = "Teams Incoming Web Hook Urls. Should be based on account-type=https://webhookurl,type=https://webhookurl,..."
}

variable "LambdaEnvLogLevel" {
  type    = string
  default = "INFO"
}

variable "LambdaTimeout" {
  type    = number
  default = 30
}

variable "security_ou_id" {
  type = string
}
variable "infrastructure_ou_id" {
  type = string
}