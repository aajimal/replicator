from pathlib import Path
from typing import List, Dict, Any
import yaml

class ArgoCDPatternDetector:
    """Detects ArgoCD application patterns in a repository"""
    
    def detect(self, repo_path: Path) -> List[Dict[str, Any]]:
        """Find all ArgoCD applications in the repository"""
        patterns = []
        
        # Common ArgoCD paths
        argocd_paths = [
            'argocd',
            'argo-cd',
            'deployments/argocd',
            'k8s/argocd',
            '.argocd',
        ]
        
        # Look for application manifests
        for argocd_path in argocd_paths:
            full_path = repo_path / argocd_path
            if full_path.exists() and full_path.is_dir():
                patterns.extend(self._scan_argocd_directory(full_path))
        
        # Also look for any application.yaml files
        for app_file in repo_path.rglob('*application*.yaml'):
            if self._is_argocd_app(app_file):
                pattern = self._analyze_argocd_app(app_file)
                if pattern and pattern not in patterns:
                    patterns.append(pattern)
        
        return patterns
    
    def _scan_argocd_directory(self, argocd_dir: Path) -> List[Dict[str, Any]]:
        """Scan an ArgoCD directory for applications"""
        patterns = []
        
        for yaml_file in argocd_dir.glob('*.yaml'):
            if self._is_argocd_app(yaml_file):
                pattern = self._analyze_argocd_app(yaml_file)
                if pattern:
                    patterns.append(pattern)
        
        return patterns
    
    def _is_argocd_app(self, file_path: Path) -> bool:
        """Check if a YAML file is an ArgoCD Application"""
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f) or {}
            
            return (
                data.get('apiVersion', '').startswith('argoproj.io/') and
                data.get('kind') == 'Application'
            )
        except:
            return False
    
    def _analyze_argocd_app(self, app_file: Path) -> Dict[str, Any]:
        """Analyze an ArgoCD application file"""
        try:
            with open(app_file, 'r') as f:
                app_data = yaml.safe_load(f) or {}
            
            metadata = app_data.get('metadata', {})
            spec = app_data.get('spec', {})
            
            pattern = {
                'type': 'argocd',
                'name': metadata.get('name', app_file.stem),
                'path': str(app_file.parent),
                'configs': [app_file],
                'source_type': 'helm' if 'helm' in spec.get('source', {}) else 'kustomize'
            }
            
            return pattern
            
        except Exception as e:
            print(f"Error analyzing ArgoCD app at {app_file}: {e}")
            return None