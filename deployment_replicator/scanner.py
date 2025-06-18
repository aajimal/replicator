import os
import yaml
from pathlib import Path
from typing import List, Dict, Any
from .patterns.helm import HelmPatternDetector
from .patterns.argocd import ArgoCDPatternDetector

class DeploymentScanner:
    """Scans repositories for deployment patterns"""
    
    def __init__(self):
        self.detectors = [
            HelmPatternDetector(),
            ArgoCDPatternDetector(),
        ]
    
    def scan_repository(self, repo_path: Path) -> List[Dict[str, Any]]:
        """Scan a repository and extract deployment patterns"""
        patterns = []
        
        for detector in self.detectors:
            found_patterns = detector.detect(repo_path)
            patterns.extend(found_patterns)
        
        return patterns
    
    def analyze_pattern(self, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a pattern to extract configurable parameters"""
        analysis = {
            'type': pattern['type'],
            'parameters': {},
            'structure': {}
        }
        
        # Extract common parameters across configs
        if pattern['type'] == 'helm':
            analysis['parameters'] = self._extract_helm_parameters(pattern)
        elif pattern['type'] == 'argocd':
            analysis['parameters'] = self._extract_argocd_parameters(pattern)
        
        return analysis
    
    def _extract_helm_parameters(self, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """Extract parameterizable values from Helm charts"""
        params = {
            'appName': pattern['name'],
            'namespace': 'default',
            'image': {
                'repository': '',
                'tag': 'latest'
            }
        }
        
        # Parse values.yaml if it exists
        values_path = Path(pattern['path']) / 'values.yaml'
        if values_path.exists():
            with open(values_path, 'r') as f:
                values = yaml.safe_load(f) or {}
                
                # Extract common patterns
                if 'image' in values:
                    params['image'].update(values['image'])
                if 'namespace' in values:
                    params['namespace'] = values['namespace']
        
        return params
    
    def _extract_argocd_parameters(self, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """Extract parameterizable values from ArgoCD applications"""
        params = {
            'appName': pattern['name'],
            'namespace': 'argocd',
            'project': 'default',
            'repoURL': '',
            'targetRevision': 'HEAD',
            'path': ''
        }
        
        # Parse application manifest
        for config_path in pattern.get('configs', []):
            if config_path.exists():
                with open(config_path, 'r') as f:
                    manifest = yaml.safe_load(f) or {}
                    
                    if 'spec' in manifest:
                        spec = manifest['spec']
                        if 'destination' in spec:
                            params['namespace'] = spec['destination'].get('namespace', params['namespace'])
                        if 'source' in spec:
                            params['repoURL'] = spec['source'].get('repoURL', params['repoURL'])
                            params['path'] = spec['source'].get('path', params['path'])
        
        return params