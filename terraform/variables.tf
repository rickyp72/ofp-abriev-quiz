variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "eu-west-2"
}

variable "instance_name" {
  description = "Name for the Lightsail instance"
  type        = string
  default     = "ofp-quiz"
}

variable "repo_url" {
  description = "HTTPS URL of the GitHub repository to clone onto the instance"
  type        = string
  default     = "https://github.com/rickyp72/ofp-abriev-quiz.git"
}
