variable "aws_region" {
  type        = string
  description = "The AWS region things are created in"
  default     = "ca-central-1"
}
variable "LambdaEnvLogLevel" {
  type    = string
  default = "INFO"
}

variable "LambdaTimeout" {
  type    = number
  default = 30
}

variable "ParentId" {
  type = string
}
variable "ParentId1" {
  type = string
}