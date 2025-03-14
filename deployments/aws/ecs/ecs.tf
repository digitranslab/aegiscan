# CloudMap Namespace for Service Connect
resource "aws_service_discovery_http_namespace" "namespace" {
  name        = "aegiscan.local"
  description = "Private DNS namespace for ECS services"
}

resource "aws_ecs_cluster" "aegiscan_cluster" {
  name = "aegiscan-cluster"

  service_connect_defaults {
    namespace = aws_service_discovery_http_namespace.namespace.arn
  }
}

locals {
  local_dns_namespace = aws_ecs_cluster.aegiscan_cluster.service_connect_defaults[0].namespace
}
