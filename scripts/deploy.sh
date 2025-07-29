#!/bin/bash

# BOL OCR Extractor Deployment Script
# Comprehensive deployment automation for Kubernetes

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
K8S_DIR="$ROOT_DIR/k8s"
MONITORING_DIR="$ROOT_DIR/monitoring"

# Default values
ENVIRONMENT="${ENVIRONMENT:-dev}"
NAMESPACE="${NAMESPACE:-bol-ocr}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
REGISTRY="${REGISTRY:-ghcr.io}"
IMAGE_NAME="${IMAGE_NAME:-bol-ocr-extractor}"
DOMAIN="${DOMAIN:-bol-ocr.example.com}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed or not in PATH"
        exit 1
    fi
    
    # Check if helm is installed
    if ! command -v helm &> /dev/null; then
        log_error "helm is not installed or not in PATH"
        exit 1
    fi
    
    # Check if we can connect to the cluster
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Function to create namespace
create_namespace() {
    log_info "Creating namespace: $NAMESPACE"
    
    if kubectl get namespace "$NAMESPACE" &> /dev/null; then
        log_warning "Namespace $NAMESPACE already exists"
    else
        kubectl apply -f "$K8S_DIR/namespace.yaml"
        log_success "Namespace $NAMESPACE created"
    fi
}

# Function to generate TLS certificates (self-signed for development)
generate_tls_certs() {
    log_info "Generating TLS certificates..."
    
    local cert_dir="$ROOT_DIR/ssl"
    mkdir -p "$cert_dir"
    
    if [[ ! -f "$cert_dir/tls.crt" ]] || [[ ! -f "$cert_dir/tls.key" ]]; then
        # Generate self-signed certificate for development
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout "$cert_dir/tls.key" \
            -out "$cert_dir/tls.crt" \
            -subj "/CN=$DOMAIN/O=BOL-OCR/C=US" \
            -addext "subjectAltName=DNS:$DOMAIN,DNS:*.$DOMAIN"
        
        log_success "Self-signed TLS certificates generated"
    else
        log_info "TLS certificates already exist"
    fi
    
    # Create Kubernetes TLS secret
    kubectl create secret tls bol-ocr-tls \
        --cert="$cert_dir/tls.crt" \
        --key="$cert_dir/tls.key" \
        --namespace="$NAMESPACE" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    log_success "TLS secret created/updated"
}

# Function to create secrets
create_secrets() {
    log_info "Creating secrets..."
    
    # Generate random passwords if not set
    REDIS_PASSWORD=${REDIS_PASSWORD:-$(openssl rand -base64 32)}
    GRAFANA_PASSWORD=${GRAFANA_PASSWORD:-$(openssl rand -base64 16)}
    
    # Create secrets from template
    sed -e "s|REDIS_PASSWORD_BASE64|$(echo -n "$REDIS_PASSWORD" | base64 -w 0)|g" \
        -e "s|GRAFANA_PASSWORD_BASE64|$(echo -n "$GRAFANA_PASSWORD" | base64 -w 0)|g" \
        "$K8S_DIR/secret.yaml" | kubectl apply -f -
    
    log_success "Secrets created/updated"
    log_info "Redis password: $REDIS_PASSWORD"
    log_info "Grafana password: $GRAFANA_PASSWORD"
}

# Function to deploy application
deploy_application() {
    log_info "Deploying application components..."
    
    # Update image tag in deployment
    local temp_deployment=$(mktemp)
    sed "s|image: bol-ocr-extractor:latest|image: $REGISTRY/$IMAGE_NAME:$IMAGE_TAG|g" \
        "$K8S_DIR/deployment.yaml" > "$temp_deployment"
    
    # Apply manifests in order
    kubectl apply -f "$K8S_DIR/configmap.yaml"
    kubectl apply -f "$K8S_DIR/rbac.yaml"
    kubectl apply -f "$K8S_DIR/pvc.yaml"
    kubectl apply -f "$temp_deployment"
    kubectl apply -f "$K8S_DIR/service.yaml"
    
    # Clean up temp file
    rm "$temp_deployment"
    
    log_success "Application components deployed"
}

# Function to deploy networking
deploy_networking() {
    log_info "Deploying networking components..."
    
    # Update domain in ingress
    local temp_ingress=$(mktemp)
    sed "s|bol-ocr.example.com|$DOMAIN|g" \
        "$K8S_DIR/ingress.yaml" > "$temp_ingress"
    
    kubectl apply -f "$K8S_DIR/networkpolicy.yaml"
    kubectl apply -f "$temp_ingress"
    
    # Clean up temp file
    rm "$temp_ingress"
    
    log_success "Networking components deployed"
}

# Function to deploy security policies
deploy_security() {
    log_info "Deploying security policies..."
    
    # Check if Pod Security Policies are supported
    if kubectl api-resources | grep -q podsecuritypolicy; then
        kubectl apply -f "$K8S_DIR/podsecuritypolicy.yaml"
        log_success "Pod Security Policies deployed"
    else
        log_warning "Pod Security Policies not supported in this cluster version"
    fi
}

# Function to wait for deployment
wait_for_deployment() {
    log_info "Waiting for deployment to be ready..."
    
    local deployments=("bol-ocr-app" "nginx" "redis")
    
    for deployment in "${deployments[@]}"; do
        log_info "Waiting for $deployment..."
        kubectl rollout status deployment/"$deployment" -n "$NAMESPACE" --timeout=300s
        log_success "$deployment is ready"
    done
}

# Function to run health checks
run_health_checks() {
    log_info "Running health checks..."
    
    # Check if pods are running
    local failed_pods=$(kubectl get pods -n "$NAMESPACE" --field-selector=status.phase!=Running -o name 2>/dev/null | wc -l)
    if [[ $failed_pods -gt 0 ]]; then
        log_warning "Some pods are not running:"
        kubectl get pods -n "$NAMESPACE" --field-selector=status.phase!=Running
    fi
    
    # Check if services are accessible
    local app_service=$(kubectl get service bol-ocr-app-service -n "$NAMESPACE" -o jsonpath='{.spec.clusterIP}')
    if [[ -n "$app_service" ]]; then
        log_success "Application service is accessible at $app_service"
    else
        log_error "Application service is not accessible"
    fi
    
    # Port forward for local testing (optional)
    if [[ "${PORT_FORWARD:-false}" == "true" ]]; then
        log_info "Setting up port forwarding for local access..."
        kubectl port-forward -n "$NAMESPACE" service/nginx-service 8080:80 &
        log_info "Application available at http://localhost:8080"
    fi
}

# Function to deploy monitoring
deploy_monitoring() {
    log_info "Deploying monitoring stack..."
    
    # Create monitoring namespace if it doesn't exist
    kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -
    
    # Deploy Prometheus using Helm
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo update
    
    # Install or upgrade Prometheus
    helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
        --namespace monitoring \
        --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false \
        --set prometheus.prometheusSpec.podMonitorSelectorNilUsesHelmValues=false \
        --set grafana.adminPassword="$GRAFANA_PASSWORD" \
        --values - <<EOF
prometheus:
  prometheusSpec:
    storageSpec:
      volumeClaimTemplate:
        spec:
          accessModes: ["ReadWriteOnce"]
          resources:
            requests:
              storage: 50Gi
grafana:
  persistence:
    enabled: true
    size: 5Gi
EOF
    
    log_success "Monitoring stack deployed"
}

# Function to show deployment summary
show_summary() {
    log_info "Deployment Summary"
    echo "===================="
    echo "Environment: $ENVIRONMENT"
    echo "Namespace: $NAMESPACE"
    echo "Image: $REGISTRY/$IMAGE_NAME:$IMAGE_TAG"
    echo "Domain: $DOMAIN"
    echo ""
    
    log_info "Deployed Components:"
    kubectl get all -n "$NAMESPACE"
    echo ""
    
    log_info "Ingress Information:"
    kubectl get ingress -n "$NAMESPACE"
    echo ""
    
    log_info "Storage Information:"
    kubectl get pvc -n "$NAMESPACE"
    echo ""
    
    log_success "Deployment completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Update your DNS to point $DOMAIN to the load balancer IP"
    echo "2. Access the application at https://$DOMAIN"
    echo "3. Monitor the application using the dashboards"
    echo "4. Review logs: kubectl logs -n $NAMESPACE -l app=bol-ocr-extractor"
}

# Function to rollback deployment
rollback_deployment() {
    log_warning "Rolling back deployment..."
    
    local deployments=("bol-ocr-app" "nginx" "redis")
    
    for deployment in "${deployments[@]}"; do
        if kubectl get deployment "$deployment" -n "$NAMESPACE" &> /dev/null; then
            kubectl rollout undo deployment/"$deployment" -n "$NAMESPACE"
            log_info "Rolled back $deployment"
        fi
    done
    
    log_success "Rollback completed"
}

# Function to clean up deployment
cleanup_deployment() {
    log_warning "Cleaning up deployment..."
    
    read -p "Are you sure you want to delete all BOL OCR resources? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kubectl delete namespace "$NAMESPACE" --ignore-not-found=true
        log_success "Cleanup completed"
    else
        log_info "Cleanup cancelled"
    fi
}

# Main function
main() {
    case "${1:-deploy}" in
        "deploy")
            check_prerequisites
            create_namespace
            generate_tls_certs
            create_secrets
            deploy_application
            deploy_networking
            deploy_security
            wait_for_deployment
            run_health_checks
            
            if [[ "${DEPLOY_MONITORING:-true}" == "true" ]]; then
                deploy_monitoring
            fi
            
            show_summary
            ;;
        "rollback")
            rollback_deployment
            ;;
        "cleanup")
            cleanup_deployment
            ;;
        "health")
            run_health_checks
            ;;
        *)
            echo "Usage: $0 {deploy|rollback|cleanup|health}"
            echo ""
            echo "Commands:"
            echo "  deploy   - Deploy the BOL OCR application"
            echo "  rollback - Rollback to previous deployment"
            echo "  cleanup  - Remove all deployed resources"
            echo "  health   - Run health checks"
            echo ""
            echo "Environment Variables:"
            echo "  ENVIRONMENT        - Deployment environment (dev|staging|prod)"
            echo "  NAMESPACE          - Kubernetes namespace"
            echo "  IMAGE_TAG          - Docker image tag"
            echo "  DOMAIN             - Application domain"
            echo "  PORT_FORWARD       - Enable port forwarding (true|false)"
            echo "  DEPLOY_MONITORING  - Deploy monitoring stack (true|false)"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"