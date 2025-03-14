resource "aws_cloudwatch_log_group" "aegiscan_log_group" {
  name              = "/ecs/aegiscan"
  retention_in_days = 30
}
