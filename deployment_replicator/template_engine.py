from pathlib import Path
from typing import List, Dict, Any, Optional
import yaml
import json
from jinja2 import Environment, FileSystemLoader, Template

class TemplateEngine:
    """Creates reusable templates from discovered patterns"""
    
    def __init__(self):
        self.env = Environment(
            loader=FileSystemLoader('.'),
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    def create_templates(self, patterns: List[Dict[str, Any]], output_dir: Optional[Path] = None) -> List[Dict[str, Any]]:
        """Generate templates from patterns"""
        templates = []
        
        for pattern in patterns:
            if pattern['type'] == 'helm':
                template = self._create_helm_template(pattern, output_dir)
            elif pattern['type'] == 'argocd':
                template = self._create_argocd_template(pattern, output_dir)
            else:
                continue
            
            if template:
                templates.append(template)
        
        return templates
    
    def _create_helm_template(self, pattern: Dict[str, Any], output_dir: Optional[Path] = None) -> Dict[str, Any]:
        """Create a Helm chart template"""
        template_data = {
            'type': 'helm',
            'name': pattern['name'],
            'files': {}
        }
        
        # Chart.yaml template
        chart_template = '''apiVersion: v2
name: {{ app_name }}
description: A Helm chart for {{ app_name }}
type: application
version: {{ chart_version | default("0.1.0") }}
appVersion: {{ app_version | default("1.0.0") }}
'''
        
        # values.yaml template
        values_template = '''# Default values for {{ app_name }}
replicaCount: {{ replica_count | default(1) }}

image:
  repository: {{ image_repository | default("nginx") }}
  pullPolicy: {{ pull_policy | default("IfNotPresent") }}
  tag: {{ image_tag | default("latest") }}

service:
  type: {{ service_type | default("ClusterIP") }}
  port: {{ service_port | default(80) }}

ingress:
  enabled: {{ ingress_enabled | default(false) }}
  className: {{ ingress_class | default("nginx") }}
  hosts:
    - host: {{ app_name }}.local
      paths:
        - path: /
          pathType: Prefix

resources:
  limits:
    cpu: {{ cpu_limit | default("100m") }}
    memory: {{ memory_limit | default("128Mi") }}
  requests:
    cpu: {{ cpu_request | default("100m") }}
    memory: {{ memory_request | default("128Mi") }}
'''
        
        # Basic deployment template
        deployment_template = '''apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "{{ app_name }}.fullname" . }}
  labels:
    {{- include "{{ app_name }}.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "{{ app_name }}.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "{{ app_name }}.selectorLabels" . | nindent 8 }}
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: {{ .Values.service.port }}
              protocol: TCP
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
'''
        
        template_data['files'] = {
            'Chart.yaml': chart_template,
            'values.yaml': values_template,
            'templates/deployment.yaml': deployment_template
        }
        
        # Save templates if output directory provided
        if output_dir:
            helm_dir = output_dir / 'helm' / pattern['name']
            helm_dir.mkdir(parents=True, exist_ok=True)
            
            for file_path, content in template_data['files'].items():
                full_path = helm_dir / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content)
        
        return template_data
    
    def _create_argocd_template(self, pattern: Dict[str, Any], output_dir: Optional[Path] = None) -> Dict[str, Any]:
        """Create an ArgoCD application template"""
        template_data = {
            'type': 'argocd',
            'name': pattern['name'],
            'files': {}
        }
        
        # ArgoCD Application template
        app_template = '''apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: {{ app_name }}
  namespace: {{ argocd_namespace | default("argocd") }}
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: {{ project | default("default") }}
  source:
    repoURL: {{ repo_url }}
    targetRevision: {{ target_revision | default("HEAD") }}
    path: {{ source_path }}
    {% if source_type == "helm" %}
    helm:
      releaseName: {{ app_name }}
      valueFiles:
        - values.yaml
    {% endif %}
  destination:
    server: {{ dest_server | default("https://kubernetes.default.svc") }}
    namespace: {{ dest_namespace | default(app_name) }}
  syncPolicy:
    automated:
      prune: {{ auto_prune | default(true) }}
      selfHeal: {{ self_heal | default(true) }}
    syncOptions:
      - CreateNamespace=true
'''
        
        template_data['files'] = {
            'application.yaml': app_template
        }
        
        # Save template if output directory provided
        if output_dir:
            argocd_dir = output_dir / 'argocd'
            argocd_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = argocd_dir / f'{pattern["name"]}-application.yaml'
            file_path.write_text(app_template)
        
        return template_data
    
    def render_template(self, template_content: str, variables: Dict[str, Any]) -> str:
        """Render a template with given variables"""
        template = Template(template_content)
        return template.render(**variables)