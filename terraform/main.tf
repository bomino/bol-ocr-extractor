# Terraform configuration for BOL OCR Extractor infrastructure
# Multi-cloud support with provider-specific modules

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.20"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.10"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }
  
  # Remote state backend (uncomment and configure for production)
  # backend "s3" {
  #   bucket         = "your-terraform-state-bucket"
  #   key            = "bol-ocr/terraform.tfstate"
  #   region         = "us-west-2"
  #   encrypt        = true
  #   dynamodb_table = "terraform-locks"
  # }
}

# Local variables
locals {
  project_name = "bol-ocr-extractor"
  environment  = var.environment
  
  common_tags = {
    Project     = local.project_name
    Environment = local.environment
    ManagedBy   = "terraform"
    Owner       = var.owner
  }
}

# Random password generation
resource "random_password" "redis_password" {
  length  = 32
  special = true
}

resource "random_password" "grafana_password" {
  length  = 16
  special = false
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

# VPC Module
module "vpc" {
  source = "./modules/vpc"
  
  project_name = local.project_name
  environment  = local.environment
  
  vpc_cidr             = var.vpc_cidr
  availability_zones   = data.aws_availability_zones.available.names
  private_subnet_cidrs = var.private_subnet_cidrs
  public_subnet_cidrs  = var.public_subnet_cidrs
  
  tags = local.common_tags
}

# EKS Module
module "eks" {
  source = "./modules/eks"
  
  project_name = local.project_name
  environment  = local.environment
  
  vpc_id              = module.vpc.vpc_id
  private_subnet_ids  = module.vpc.private_subnet_ids
  public_subnet_ids   = module.vpc.public_subnet_ids
  
  cluster_version     = var.eks_cluster_version
  node_group_config   = var.node_group_config
  
  tags = local.common_tags
}

# RDS Module (for future database needs)
module "rds" {
  source = "./modules/rds"
  count  = var.enable_rds ? 1 : 0
  
  project_name = local.project_name
  environment  = local.environment
  
  vpc_id            = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  
  db_config = var.db_config
  
  tags = local.common_tags
}

# ElastiCache Module (Redis)
module "elasticache" {
  source = "./modules/elasticache"
  
  project_name = local.project_name
  environment  = local.environment
  
  vpc_id            = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  
  redis_config = var.redis_config
  auth_token   = random_password.redis_password.result
  
  tags = local.common_tags
}

# S3 Module (for file storage and backups)
module "s3" {
  source = "./modules/s3"
  
  project_name = local.project_name
  environment  = local.environment
  
  bucket_configs = var.s3_bucket_configs
  
  tags = local.common_tags
}

# CloudWatch Module (monitoring and logging)
module "cloudwatch" {
  source = "./modules/cloudwatch"
  
  project_name = local.project_name
  environment  = local.environment
  
  eks_cluster_name = module.eks.cluster_name
  
  tags = local.common_tags
}

# ACM Certificate
resource "aws_acm_certificate" "main" {
  domain_name               = var.domain_name
  subject_alternative_names = ["*.${var.domain_name}"]
  validation_method         = "DNS"
  
  lifecycle {
    create_before_destroy = true
  }
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-certificate"
  })
}

# Route53 hosted zone (if managing DNS)
resource "aws_route53_zone" "main" {
  count = var.manage_dns ? 1 : 0
  name  = var.domain_name
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-zone"
  })
}

# Certificate validation
resource "aws_acm_certificate_validation" "main" {
  certificate_arn         = aws_acm_certificate.main.arn
  validation_record_fqdns = [for record in aws_route53_record.cert_validation : record.fqdn]
  
  timeouts {
    create = "5m"
  }
}

# DNS validation records
resource "aws_route53_record" "cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.main.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }
  
  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = var.manage_dns ? aws_route53_zone.main[0].zone_id : var.existing_zone_id
}

# Kubernetes provider configuration
provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_ca_certificate)
  
  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args        = ["eks", "get-token", "--cluster-name", module.eks.cluster_name]
  }
}

# Helm provider configuration
provider "helm" {
  kubernetes {
    host                   = module.eks.cluster_endpoint
    cluster_ca_certificate = base64decode(module.eks.cluster_ca_certificate)
    
    exec {
      api_version = "client.authentication.k8s.io/v1beta1"
      command     = "aws"
      args        = ["eks", "get-token", "--cluster-name", module.eks.cluster_name]
    }
  }
}

# Install essential Kubernetes add-ons
module "k8s_addons" {
  source = "./modules/k8s-addons"
  
  project_name     = local.project_name
  environment      = local.environment
  cluster_name     = module.eks.cluster_name
  cluster_version  = var.eks_cluster_version
  
  # Add-ons configuration
  enable_aws_load_balancer_controller = true
  enable_external_dns                 = var.manage_dns
  enable_cert_manager                  = true
  enable_cluster_autoscaler            = true
  enable_metrics_server                = true
  enable_prometheus                    = true
  enable_grafana                       = true
  
  # Configuration
  domain_name      = var.domain_name
  certificate_arn  = aws_acm_certificate_validation.main.certificate_arn
  grafana_password = random_password.grafana_password.result
  
  depends_on = [module.eks]
}

# Deploy application
module "app_deployment" {
  source = "./modules/app-deployment"
  
  project_name = local.project_name
  environment  = local.environment
  
  # Application configuration
  app_image         = var.app_image
  app_replicas      = var.app_replicas
  domain_name       = var.domain_name
  certificate_arn   = aws_acm_certificate_validation.main.certificate_arn
  
  # Redis configuration
  redis_endpoint = module.elasticache.redis_endpoint
  redis_password = random_password.redis_password.result
  
  # S3 configuration
  s3_bucket_name = module.s3.app_bucket_name
  
  depends_on = [module.k8s_addons]
}