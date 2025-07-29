# Terraform variables for BOL OCR Extractor infrastructure

# General configuration
variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "owner" {
  description = "Owner of the resources"
  type        = string
  default     = "devops-team"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

# Networking configuration
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
}

# EKS configuration
variable "eks_cluster_version" {
  description = "Kubernetes version for EKS cluster"
  type        = string
  default     = "1.28"
}

variable "node_group_config" {
  description = "EKS node group configuration"
  type = object({
    instance_types = list(string)
    capacity_type  = string
    disk_size      = number
    ami_type       = string
    scaling_config = object({
      desired_size = number
      max_size     = number
      min_size     = number
    })
  })
  default = {
    instance_types = ["t3.medium", "t3.large"]
    capacity_type  = "ON_DEMAND"
    disk_size      = 50
    ami_type       = "AL2_x86_64"
    scaling_config = {
      desired_size = 2
      max_size     = 10
      min_size     = 1
    }
  }
}

# RDS configuration
variable "enable_rds" {
  description = "Whether to create RDS instance"
  type        = bool
  default     = false
}

variable "db_config" {
  description = "RDS database configuration"
  type = object({
    engine            = string
    engine_version    = string
    instance_class    = string
    allocated_storage = number
    storage_encrypted = bool
    multi_az          = bool
    backup_retention  = number
    backup_window     = string
    maintenance_window = string
  })
  default = {
    engine            = "postgres"
    engine_version    = "15.4"
    instance_class    = "db.t3.micro"
    allocated_storage = 20
    storage_encrypted = true
    multi_az          = false
    backup_retention  = 7
    backup_window     = "03:00-04:00"
    maintenance_window = "sun:04:00-sun:05:00"
  }
}

# Redis configuration
variable "redis_config" {
  description = "ElastiCache Redis configuration"
  type = object({
    node_type               = string
    num_cache_clusters      = number
    port                    = number
    parameter_group_name    = string
    engine_version          = string
    at_rest_encryption      = bool
    transit_encryption      = bool
    automatic_failover      = bool
  })
  default = {
    node_type               = "cache.t3.micro"
    num_cache_clusters      = 2
    port                    = 6379
    parameter_group_name    = "default.redis7"
    engine_version          = "7.0"
    at_rest_encryption      = true
    transit_encryption      = true
    automatic_failover      = true
  }
}

# S3 configuration
variable "s3_bucket_configs" {
  description = "S3 bucket configurations"
  type = map(object({
    versioning_enabled = bool
    encryption_enabled = bool
    lifecycle_rules = list(object({
      id                          = string
      enabled                     = bool
      expiration_days            = number
      noncurrent_version_expiration_days = number
      transition_to_ia_days      = number
      transition_to_glacier_days = number
    }))
  }))
  default = {
    app-storage = {
      versioning_enabled = true
      encryption_enabled = true
      lifecycle_rules = [
        {
          id                          = "temp-files-cleanup"
          enabled                     = true
          expiration_days            = 7
          noncurrent_version_expiration_days = 3
          transition_to_ia_days      = 30
          transition_to_glacier_days = 90
        }
      ]
    }
    backups = {
      versioning_enabled = true
      encryption_enabled = true
      lifecycle_rules = [
        {
          id                          = "backup-retention"
          enabled                     = true
          expiration_days            = 365
          noncurrent_version_expiration_days = 30
          transition_to_ia_days      = 30
          transition_to_glacier_days = 90
        }
      ]
    }
  }
}

# DNS and SSL configuration
variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = "bol-ocr.example.com"
}

variable "manage_dns" {
  description = "Whether to manage DNS with Route53"
  type        = bool
  default     = false
}

variable "existing_zone_id" {
  description = "Existing Route53 zone ID (if not managing DNS)"
  type        = string
  default     = ""
}

# Application configuration
variable "app_image" {
  description = "Docker image for the application"
  type        = string
  default     = "ghcr.io/your-org/bol-ocr-extractor:latest"
}

variable "app_replicas" {
  description = "Number of application replicas"
  type        = number
  default     = 2
  
  validation {
    condition     = var.app_replicas >= 1 && var.app_replicas <= 20
    error_message = "App replicas must be between 1 and 20."
  }
}

# Monitoring configuration
variable "monitoring_config" {
  description = "Monitoring and observability configuration"
  type = object({
    enable_prometheus     = bool
    enable_grafana       = bool
    enable_alertmanager  = bool
    enable_jaeger        = bool
    retention_days       = number
    storage_size         = string
  })
  default = {
    enable_prometheus    = true
    enable_grafana      = true
    enable_alertmanager = true
    enable_jaeger       = false
    retention_days      = 30
    storage_size        = "10Gi"
  }
}

# Security configuration
variable "security_config" {
  description = "Security configuration"
  type = object({
    enable_pod_security_policy = bool
    enable_network_policies    = bool
    enable_service_mesh        = bool
    allowed_source_ranges      = list(string)
  })
  default = {
    enable_pod_security_policy = true
    enable_network_policies    = true
    enable_service_mesh        = false
    allowed_source_ranges      = ["0.0.0.0/0"]  # Restrict in production
  }
}

# Backup configuration
variable "backup_config" {
  description = "Backup configuration"
  type = object({
    enable_velero           = bool
    backup_schedule         = string
    backup_retention_days   = number
    backup_storage_location = string
  })
  default = {
    enable_velero           = true
    backup_schedule         = "0 2 * * *"  # Daily at 2 AM
    backup_retention_days   = 30
    backup_storage_location = "s3"
  }
}

# Cost optimization
variable "cost_optimization" {
  description = "Cost optimization settings"
  type = object({
    enable_spot_instances    = bool
    spot_instance_percentage = number
    enable_cluster_autoscaler = bool
    enable_vertical_pod_autoscaler = bool
  })
  default = {
    enable_spot_instances    = false  # Enable for non-prod environments
    spot_instance_percentage = 50
    enable_cluster_autoscaler = true
    enable_vertical_pod_autoscaler = false
  }
}