terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# --- SSH Key Pair --------------------------------------------------------

resource "tls_private_key" "quiz" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_lightsail_key_pair" "quiz" {
  name       = "${var.instance_name}-key"
  public_key = tls_private_key.quiz.public_key_openssh
}

# --- Instance -----------------------------------------------------------

resource "aws_lightsail_instance" "quiz" {
  name              = var.instance_name
  availability_zone = "${var.aws_region}a"
  blueprint_id      = "amazon_linux_2023"
  bundle_id         = "nano_3_0" # 512 MB RAM, 1 vCPU — $3.50/month
  key_pair_name     = aws_lightsail_key_pair.quiz.name

  user_data = templatefile("${path.module}/user_data.sh", {
    repo_url = var.repo_url
  })

  tags = {
    Name = var.instance_name
  }
}

# --- Static IP ----------------------------------------------------------

resource "aws_lightsail_static_ip" "quiz" {
  name = "${var.instance_name}-ip"
}

resource "aws_lightsail_static_ip_attachment" "quiz" {
  static_ip_name = aws_lightsail_static_ip.quiz.name
  instance_name  = aws_lightsail_instance.quiz.name
}

# --- Firewall -----------------------------------------------------------

resource "aws_lightsail_instance_public_ports" "quiz" {
  instance_name = aws_lightsail_instance.quiz.name

  port_info {
    protocol  = "tcp"
    from_port = 22
    to_port   = 22
  }

  port_info {
    protocol  = "tcp"
    from_port = 8080
    to_port   = 8080
  }
}
