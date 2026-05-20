output "public_ip" {
  description = "Static public IP address of the instance"
  value       = aws_lightsail_static_ip.quiz.ip_address
}

output "app_url" {
  description = "URL to access the quiz"
  value       = "http://${aws_lightsail_static_ip.quiz.ip_address}:8080"
}

output "ssh_command" {
  description = "SSH command to connect to the instance"
  value       = "ssh -i ~/.ssh/${var.instance_name}.pem ec2-user@${aws_lightsail_static_ip.quiz.ip_address}"
}

output "private_key" {
  description = "Private key for SSH — save with: terraform output -raw private_key > ~/.ssh/ofp-quiz.pem && chmod 400 ~/.ssh/ofp-quiz.pem"
  value       = tls_private_key.quiz.private_key_pem
  sensitive   = true
}
