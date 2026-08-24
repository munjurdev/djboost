"""Kubernetes generator — add deployment manifests for K8s."""

import os
from pathlib import Path

from rich import print


def get_project_name():
    """Extract project name from manage.py."""
    import re

    if not Path("manage.py").exists():
        print("[red]Error: manage.py not found. Are you in the project root?[/red]")
        return None
    content = Path("manage.py").read_text(encoding="utf-8")
    match = re.search(r"['\"]DJANGO_SETTINGS_MODULE['\"],\s*['\"]([^.]+)\.settings['\"]", content)
    if match:
        return match.group(1)
    print("[red]Error: Could not determine project name from manage.py[/red]")
    return None


def generate_k8s_manifests(name: str):
    """Generate all Kubernetes manifests."""
    k8s_dir = Path("k8s")
    k8s_dir.mkdir(exist_ok=True)

    # deployment.yaml
    deployment = f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {name}
  labels:
    app: {name}
spec:
  replicas: 2
  selector:
    matchLabels:
      app: {name}
  template:
    metadata:
      labels:
        app: {name}
    spec:
      containers:
        - name: {name}
          image: {name}:latest
          ports:
            - containerPort: 8000
          envFrom:
            - configMapRef:
                name: {name}-config
            - secretRef:
                name: {name}-secrets
          readinessProbe:
            httpGet:
              path: /
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 5
          livenessProbe:
            httpGet:
              path: /
              port: 8000
            initialDelaySeconds: 15
            periodSeconds: 10
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "512Mi"
              cpu: "500m"
"""
    (k8s_dir / "deployment.yaml").write_text(deployment, encoding="utf-8")

    # service.yaml
    service = f"""apiVersion: v1
kind: Service
metadata:
  name: {name}
  labels:
    app: {name}
spec:
  selector:
    app: {name}
  ports:
    - port: 8000
      targetPort: 8000
      protocol: TCP
  type: ClusterIP
"""
    (k8s_dir / "service.yaml").write_text(service, encoding="utf-8")

    # ingress.yaml
    ingress = f"""apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {name}
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
    - hosts:
        - api.example.com
      secretName: {name}-tls
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: {name}
                port:
                  number: 8000
"""
    (k8s_dir / "ingress.yaml").write_text(ingress, encoding="utf-8")

    # configmap.yaml
    configmap = f"""apiVersion: v1
kind: ConfigMap
metadata:
  name: {name}-config
data:
  DB_HOST: "postgres-service"
  DB_PORT: "5432"
  REDIS_HOST: "redis-service"
  REDIS_PORT: "6379"
  CELERY_BROKER_URL: "redis://redis-service:6379/0"
  CELERY_RESULT_BACKEND: "redis://redis-service:6379/0"
"""
    (k8s_dir / "configmap.yaml").write_text(configmap, encoding="utf-8")

    # secrets.yaml (template — user fills in real values)
    secrets = f"""apiVersion: v1
kind: Secret
metadata:
  name: {name}-secrets
type: Opaque
stringData:
  SECRET_KEY: "CHANGE-ME"
  DB_NAME: "{name}_db"
  DB_USER: "{name}_user"
  DB_PASSWORD: "CHANGE-ME"
  SENTRY_DSN: ""
  AWS_ACCESS_KEY_ID: ""
  AWS_SECRET_ACCESS_KEY: ""
"""
    (k8s_dir / "secrets.yaml").write_text(secrets, encoding="utf-8")

    print("[green]✔ Created k8s/ directory with manifests:[/green]")
    print("  k8s/deployment.yaml")
    print("  k8s/service.yaml")
    print("  k8s/ingress.yaml")
    print("  k8s/configmap.yaml")
    print("  k8s/secrets.yaml")
    return True
