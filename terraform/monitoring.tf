### Notificaciones por correo
resource "aws_sns_topic" "alerts" {
  name = "${var.project_name}-alerts"
}

# AWS manda un correo de confirmación; la suscripción no funciona hasta aceptarlo
resource "aws_sns_topic_subscription" "email" {
  count     = var.alert_email == "" ? 0 : 1
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

### Alarmas: una por métrica, definidas en alerting/alarms.json
locals {
  alarms = { for alarm in jsondecode(file("${path.module}/../alerting/alarms.json")) : alarm.name => alarm }

  # alarms.json no conoce los IDs reales; aquí se traduce cada referencia a su valor
  dimension_values = {
    instance_id = aws_instance.server.id
  }
}

resource "aws_cloudwatch_metric_alarm" "alarms" {
  for_each = local.alarms

  alarm_name          = "${var.project_name}-${each.key}"
  alarm_description   = each.value.description
  namespace           = each.value.namespace
  metric_name         = each.value.metric_name
  dimensions          = { for key, ref in each.value.dimensions : key => local.dimension_values[ref] }
  statistic           = each.value.statistic
  period              = each.value.period
  evaluation_periods  = each.value.evaluation_periods
  comparison_operator = each.value.comparison_operator
  threshold           = each.value.threshold
  treat_missing_data  = each.value.treat_missing_data

  # Avisa tanto cuando se dispara como cuando se recupera
  alarm_actions = [aws_sns_topic.alerts.arn]
  ok_actions    = [aws_sns_topic.alerts.arn]
}

### Dashboard con las 3 métricas, definido en alerting/cloudwatch-dashboard.json
resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = var.project_name
  dashboard_body = templatefile("${path.module}/../alerting/cloudwatch-dashboard.json", {
    region      = var.region
    instance_id = aws_instance.server.id
  })
}
