# Aegiscan and Temporal Environment Variables
locals {

  # Aegiscan version
  git_sha            = var.TFC_CONFIGURATION_VERSION_GIT_COMMIT_SHA
  sha256_image_tag   = local.git_sha != null ? "sha-${substr(local.git_sha, 0, 7)}" : null
  aegiscan_image_tag = var.use_git_commit_sha ? local.sha256_image_tag : var.aegiscan_image_tag

  # Aegiscan common URLs
  public_app_url         = "https://${var.domain_name}"
  public_api_url         = "https://${var.domain_name}/api"
  internal_api_url       = "http://api-service:8000"      # Service connect DNS name
  internal_executor_url  = "http://executor-service:8002" # Service connect DNS name
  temporal_cluster_url   = var.temporal_cluster_url
  temporal_cluster_queue = var.temporal_cluster_queue
  temporal_namespace     = var.temporal_namespace
  allow_origins          = "${var.domain_name},http://ui-service:3000" # Allow api service and public app to access the API

  # Temporal client authentication
  temporal_mtls_cert_arn = var.temporal_mtls_cert_arn
  temporal_api_key_arn   = var.temporal_api_key_arn

  # Aegiscan postgres env vars
  # See: https://github.com/DigitransLab/aegiscan/blob/abd5ff/aegiscan/db/engine.py#L21
  aegiscan_db_configs = {
    AEGISCAN__DB_USER      = "postgres"
    AEGISCAN__DB_PORT      = "5432"
    AEGISCAN__DB_NAME      = "postgres" # Hardcoded in RDS resource configs
    AEGISCAN__DB_PASS__ARN = data.aws_secretsmanager_secret_version.aegiscan_db_password.arn
  }

  api_env = [
    for k, v in merge({
      LOG_LEVEL                                       = var.log_level
      RUN_MIGRATIONS                                  = "true"
      TEMPORAL__CLIENT_RPC_TIMEOUT                    = var.temporal_client_rpc_timeout
      TEMPORAL__CLUSTER_NAMESPACE                     = local.temporal_namespace
      TEMPORAL__CLUSTER_QUEUE                         = local.temporal_cluster_queue
      TEMPORAL__CLUSTER_URL                           = local.temporal_cluster_url
      TEMPORAL__MTLS_ENABLED                          = var.temporal_mtls_enabled
      TEMPORAL__MTLS_CERT__ARN                        = local.temporal_mtls_cert_arn
      TEMPORAL__API_KEY__ARN                          = local.temporal_api_key_arn
      AEGISCAN__ALLOW_ORIGINS                         = local.allow_origins
      AEGISCAN__API_ROOT_PATH                         = "/api"
      AEGISCAN__API_URL                               = local.internal_api_url
      AEGISCAN__APP_ENV                               = var.aegiscan_app_env
      AEGISCAN__AUTH_ALLOWED_DOMAINS                  = var.auth_allowed_domains
      AEGISCAN__AUTH_TYPES                            = var.auth_types
      AEGISCAN__SETTING_OVERRIDE_SAML_ENABLED         = var.setting_override_saml_enabled
      AEGISCAN__SETTING_OVERRIDE_OAUTH_GOOGLE_ENABLED = var.setting_override_oauth_google_enabled
      AEGISCAN__SETTING_OVERRIDE_BASIC_AUTH_ENABLED   = var.setting_override_basic_auth_enabled
      AEGISCAN__DB_ENDPOINT                           = local.core_db_hostname
      AEGISCAN__EXECUTOR_URL                          = local.internal_executor_url
      AEGISCAN__PUBLIC_API_URL                        = local.public_api_url
      AEGISCAN__PUBLIC_APP_URL                        = local.public_app_url
      AEGISCAN__REMOTE_REPOSITORY_PACKAGE_NAME        = var.remote_repository_package_name
      AEGISCAN__REMOTE_REPOSITORY_URL                 = var.remote_repository_url
    }, local.aegiscan_db_configs) :
    { name = k, value = tostring(v) }
  ]

  worker_env = [
    for k, v in merge({
      LOG_LEVEL                         = var.log_level
      TEMPORAL__CLIENT_RPC_TIMEOUT      = var.temporal_client_rpc_timeout
      TEMPORAL__CLUSTER_NAMESPACE       = local.temporal_namespace
      TEMPORAL__CLUSTER_QUEUE           = local.temporal_cluster_queue
      TEMPORAL__CLUSTER_URL             = local.temporal_cluster_url
      TEMPORAL__MTLS_ENABLED            = var.temporal_mtls_enabled
      TEMPORAL__MTLS_CERT__ARN          = local.temporal_mtls_cert_arn
      TEMPORAL__API_KEY__ARN            = local.temporal_api_key_arn
      AEGISCAN__API_ROOT_PATH           = "/api"
      AEGISCAN__API_URL                 = local.internal_api_url
      AEGISCAN__APP_ENV                 = var.aegiscan_app_env
      AEGISCAN__DB_ENDPOINT             = local.core_db_hostname
      AEGISCAN__EXECUTOR_CLIENT_TIMEOUT = var.executor_client_timeout
      AEGISCAN__EXECUTOR_URL            = local.internal_executor_url
      AEGISCAN__PUBLIC_API_URL          = local.public_api_url
    }, local.aegiscan_db_configs) :
    { name = k, value = tostring(v) }
  ]

  executor_env = [
    for k, v in merge({
      LOG_LEVEL                                = var.log_level
      AEGISCAN__APP_ENV                        = var.aegiscan_app_env
      AEGISCAN__DB_ENDPOINT                    = local.core_db_hostname
      AEGISCAN__REMOTE_REPOSITORY_URL          = var.remote_repository_url
      AEGISCAN__REMOTE_REPOSITORY_PACKAGE_NAME = var.remote_repository_package_name
    }, local.aegiscan_db_configs) :
    { name = k, value = tostring(v) }
  ]

  ui_env = [
    for k, v in {
      NEXT_PUBLIC_API_URL    = local.public_api_url
      NEXT_PUBLIC_APP_ENV    = var.aegiscan_app_env
      NEXT_PUBLIC_APP_URL    = local.public_app_url
      NEXT_PUBLIC_AUTH_TYPES = var.auth_types
      NEXT_SERVER_API_URL    = local.internal_api_url
      NODE_ENV               = var.aegiscan_app_env
    } :
    { name = k, value = tostring(v) }
  ]

  temporal_env = [
    for k, v in {
      DB                         = "postgres12"
      DB_PORT                    = "5432"
      POSTGRES_USER              = "postgres"
      LOG_LEVEL                  = var.temporal_log_level
      TEMPORAL_BROADCAST_ADDRESS = "0.0.0.0"
      BIND_ON_IP                 = "0.0.0.0"
      NUM_HISTORY_SHARDS         = var.temporal_num_history_shards
    } :
    { name = k, value = tostring(v) }
  ]
}
