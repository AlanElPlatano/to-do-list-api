output "server_public_ip" {
  description = "IP pública de la instancia EC2"
  value       = aws_instance.server.public_ip
}

output "server_instance_id" {
  description = "ID de la instancia EC2"
  value       = aws_instance.server.id
}

output "api_url" {
  description = "URL del endpoint de tareas"
  value       = "http://${aws_instance.server.public_ip}:${var.app_port}/tasks"
}

output "db_endpoint" {
  description = "Endpoint de la base de datos RDS"
  value       = aws_db_instance.db.address
}

output "db_secret_name" {
  description = "Nombre del secreto con las credenciales de RDS"
  value       = aws_secretsmanager_secret.db.name
}

output "dashboard_url" {
  description = "Dashboard de CloudWatch con las 3 métricas"
  value       = "https://${var.region}.console.aws.amazon.com/cloudwatch/home?region=${var.region}#dashboards/dashboard/${aws_cloudwatch_dashboard.main.dashboard_name}"
}

output "sns_topic_arn" {
  description = "Tópico de SNS al que notifican las alarmas"
  value       = aws_sns_topic.alerts.arn
}

output "private_key_pem" {
  description = "Llave privada para conectarse a la EC2 por SSH"
  value       = tls_private_key.ssh.private_key_pem
  sensitive   = true
}
