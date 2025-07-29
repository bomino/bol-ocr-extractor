# Terraform outputs for BOL OCR Extractor infrastructure

# VPC outputs
output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.vpc_id
}

output "vpc_cidr" {
  description = "CIDR block of the VPC"
  value       = module.vpc.vpc_cidr
}

output "private_subnet_ids" {
  description = "IDs of the private subnets"
  value       = module.vpc.private_subnet_ids
}

output "public_subnet_ids" {
  description = "IDs of the public subnets"
  value       = module.vpc.public_subnet_ids
}

# EKS outputs
output "cluster_id" {
  description = "EKS cluster ID"
  value       = module.eks.cluster_id
}

output "cluster_name" {
  description = "EKS cluster name"
  value       = module.eks.cluster_name
}

output "cluster_endpoint" {
  description = "Endpoint for EKS control plane"
  value       = module.eks.cluster_endpoint
}

output "cluster_security_group_id" {
  description = "Security group ID attached to the EKS cluster"
  value       = module.eks.cluster_security_group_id
}

output "cluster_iam_role_arn" {
  description = "IAM role ARN associated with EKS cluster"
  value       = module.eks.cluster_iam_role_arn
}

output "node_groups" {
  description = "EKS node groups"
  value       = module.eks.node_groups
}

output "oidc_provider_arn" {
  description = "The ARN of the OIDC Provider for EKS"
  value       = module.eks.oidc_provider_arn
}

# Redis outputs
output "redis_endpoint" {
  description = "Redis cluster endpoint"
  value       = module.elasticache.redis_endpoint
  sensitive   = true
}

output "redis_port" {
  description = "Redis cluster port"
  value       = module.elasticache.redis_port
}

output "redis_auth_token" {
  description = "Redis authentication token"
  value       = random_password.redis_password.result
  sensitive   = true
}

# RDS outputs (conditional)
output "rds_endpoint" {
  description = "RDS instance endpoint"
  value       = var.enable_rds ? module.rds[0].db_endpoint : null
  sensitive   = true
}

output "rds_port" {
  description = "RDS instance port"
  value       = var.enable_rds ? module.rds[0].db_port : null
}

# S3 outputs
output "s3_bucket_names" {
  description = "Names of created S3 buckets"
  value       = module.s3.bucket_names
}

output "s3_bucket_arns" {
  description = "ARNs of created S3 buckets"
  value       = module.s3.bucket_arns
}

output "app_storage_bucket_name" {
  description = "Name of the application storage bucket"
  value       = module.s3.app_bucket_name
}

output "backups_bucket_name" {
  description = "Name of the backups bucket"
  value       = module.s3.backups_bucket_name
}

# SSL Certificate outputs
output "certificate_arn" {
  description = "ARN of the SSL certificate"
  value       = aws_acm_certificate.main.arn
}

output "certificate_domain_name" {
  description = "Domain name of the SSL certificate"
  value       = aws_acm_certificate.main.domain_name
}

# DNS outputs
output "route53_zone_id" {
  description = "Route53 hosted zone ID"
  value       = var.manage_dns ? aws_route53_zone.main[0].zone_id : var.existing_zone_id
}

output "domain_name" {
  description = "Domain name for the application"
  value       = var.domain_name
}

# Application URLs
output "application_url" {
  description = "URL of the deployed application"
  value       = "https://${var.domain_name}"
}

output "monitoring_url" {
  description = "URL of the monitoring dashboard"
  value       = "https://monitoring.${var.domain_name}"
}

# Monitoring outputs
output "cloudwatch_log_group_name" {
  description = "CloudWatch log group name"
  value       = module.cloudwatch.log_group_name
}

output "cloudwatch_log_group_arn" {
  description = "CloudWatch log group ARN"
  value       = module.cloudwatch.log_group_arn
}

# Security outputs
output "cluster_security_group_rules" {
  description = "Security group rules for the cluster"
  value       = module.eks.security_group_rules
}

# Kubectl configuration
output "kubectl_config_command" {
  description = "Command to configure kubectl"
  value       = "aws eks update-kubeconfig --region ${var.aws_region} --name ${module.eks.cluster_name}"
}

# Helm configuration
output "helm_config_command" {
  description = "Command to configure helm with the cluster"
  value       = "helm repo add stable https://charts.helm.sh/stable && helm repo update"
}

# Application configuration
output "application_config" {
  description = "Application configuration values"
  value = {
    replicas        = var.app_replicas
    image          = var.app_image
    domain         = var.domain_name
    environment    = var.environment
    redis_endpoint = module.elasticache.redis_endpoint
    s3_bucket      = module.s3.app_bucket_name
  }
  sensitive = true
}

# Cost estimation
output "estimated_monthly_cost" {
  description = "Estimated monthly cost breakdown (approximate)"
  value = {
    eks_cluster     = "$73"     # EKS control plane
    worker_nodes    = "$60-120" # Based on instance types and count
    load_balancer   = "$23"     # ALB
    redis           = "$15-30"  # Based on node type
    s3_storage      = "$5-20"   # Based on usage
    data_transfer   = "$10-50"  # Based on traffic
    total_estimate  = "$186-316"
    note           = "Costs vary based on usage, region, and configuration. This is an approximate estimate."
  }
}

# Resource tags
output "common_tags" {
  description = "Common tags applied to all resources"
  value = {
    Project     = "bol-ocr-extractor"
    Environment = var.environment
    ManagedBy   = "terraform"
    Owner       = var.owner
  }
}

# Backup configuration
output "backup_configuration" {
  description = "Backup configuration details"
  value = {
    s3_backup_bucket = module.s3.backups_bucket_name
    backup_schedule  = var.backup_config.backup_schedule
    retention_days   = var.backup_config.backup_retention_days
    enabled         = var.backup_config.enable_velero
  }
}

# Security configuration summary
output "security_configuration" {
  description = "Security configuration summary"
  value = {
    encryption_at_rest = {
      s3_buckets     = "AES-256"
      redis          = "Enabled"
      ebs_volumes    = "Enabled"
      rds           = var.enable_rds ? "Enabled" : "N/A"
    }
    encryption_in_transit = {
      application_traffic = "TLS 1.2+"
      redis_traffic      = "Enabled"
      cluster_traffic    = "Enabled"
    }
    network_security = {
      vpc_isolation         = "Enabled"
      private_subnets      = "Enabled"
      security_groups      = "Configured"
      network_policies     = var.security_config.enable_network_policies ? "Enabled" : "Disabled"
    }
    access_control = {
      iam_roles           = "Configured"
      rbac               = "Enabled"
      pod_security_policy = var.security_config.enable_pod_security_policy ? "Enabled" : "Disabled"
    }
  }
}