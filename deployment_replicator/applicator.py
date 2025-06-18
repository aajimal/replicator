from pathlib import Path
from typing import List, Dict, Any
import yaml
from jinja2 import Template
from .scanner import DeploymentScanner
from .utils.git_helpers import GitHelper

class PatternApplicator:
    """Applies deployment patterns to target repositories"""
    
    def __init__(self):
        self.scanner = DeploymentScanner()
        self.git_helper = GitHelper()
    
    def apply_patterns(self, template_dir: Path, target_repo: Path, 
                      dry_run: bool = False, force: bool = False) -> List[Dict[str, Any]]:
        """Apply templates from a directory to a target repository"""
        results = []
        
        # Scan target repo for existing patterns
        existing_patterns = self.scanner.scan_repository(target_repo)
        existing_types = {p['type']: p for p in existing_patterns}
        
        # Load and apply templates
        for template_type in ['helm', 'argocd']:
            type_dir = template_dir / template_type
            if not type_dir.exists():
                continue
            
            for template_path in type_dir.iterdir():
                if template_path.is_dir():  # Helm chart directory
                    result = self._apply_helm_chart(
                        template_path, target_repo, 
                        existing_types.get('helm'),
                        dry_run, force
                    )
                elif template_path.suffix in ['.yaml', '.yml']:  # ArgoCD app
                    result = self._apply_argocd_app(
                        template_path, target_repo,
                        existing_types.get('argocd'),
                        dry_run, force
                    )
                else:
                    continue
                
                if result:
                    results.append(result)
        
        return results
    
    def apply_patterns_direct(self, templates: List[Dict[str, Any]], target_repo: Path,
                            dry_run: bool = False) -> List[Dict[str, Any]]:
        """Apply templates directly without saving to disk first"""
        results = []
        
        for template in templates:
            variables = self._extract_variables_for_repo(target_repo)
            
            if template['type'] == 'helm':
                result = self._apply_helm_template(template, target_repo, variables, dry_run)
            elif template['type'] == 'argocd':
                result = self._apply_argocd_template(template, target_repo, variables, dry_run)
            else:
                continue
            
            if result:
                results.append(result)
        
        return results
    
    def _apply_helm_chart(self, template_dir: Path, target_repo: Path, 
                         existing: Any, dry_run: bool, force: bool) -> Dict[str, Any]:
        """Apply a Helm chart template"""
        chart_name = template_dir.name
        
        if existing and not force:
            return {
                'pattern': f'helm/{chart_name}',
                'status': 'skipped',
                'message': 'Helm chart already exists'
            }
        
        target_path = target_repo / 'deployments' / 'helm' / chart_name
        
        if dry_run:
            return {
                'pattern': f'helm/{chart_name}',
                'status': 'would_apply',
                'message': f'Would create Helm chart at {target_path}'
            }
        
        # Create chart directory and copy files
        target_path.mkdir(parents=True, exist_ok=True)
        
        for file_path in template_dir.rglob('*'):
            if file_path.is_file():
                relative_path = file_path.relative_to(template_dir)
                target_file = target_path / relative_path
                target_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Render template files
                if file_path.suffix in ['.yaml', '.yml', '.j2']:
                    content = file_path.read_text()
                    variables = self._extract_variables_for_repo(target_repo)
                    rendered = Template(content).render(**variables)
                    target_file.write_text(rendered)
                else:
                    target_file.write_bytes(file_path.read_bytes())
        
        return {
            'pattern': f'helm/{chart_name}',
            'status': 'applied',
            'message': f'Created Helm chart at {target_path}'
        }
    
    def _apply_argocd_app(self, template_file: Path, target_repo: Path,
                         existing: Any, dry_run: bool, force: bool) -> Dict[str, Any]:
        """Apply an ArgoCD application template"""
        app_name = template_file.stem.replace('-application', '')
        
        if existing and not force:
            return {
                'pattern': f'argocd/{app_name}',
                'status': 'skipped',
                'message': 'ArgoCD application already exists'
            }
        
        target_path = target_repo / 'deployments' / 'argocd' / template_file.name
        
        if dry_run:
            return {
                'pattern': f'argocd/{app_name}',
                'status': 'would_apply',
                'message': f'Would create ArgoCD app at {target_path}'
            }
        
        # Create directory and render template
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        content = template_file.read_text()
        variables = self._extract_variables_for_repo(target_repo)
        rendered = Template(content).render(**variables)
        target_path.write_text(rendered)
        
        return {
            'pattern': f'argocd/{app_name}',
            'status': 'applied',
            'message': f'Created ArgoCD application at {target_path}'
        }
    
    def _apply_helm_template(self, template: Dict[str, Any], target_repo: Path,
                           variables: Dict[str, Any], dry_run: bool) -> Dict[str, Any]:
        """Apply a Helm template from memory"""
        chart_name = template['name']
        target_path = target_repo / 'deployments' / 'helm' / chart_name
        
        if dry_run:
            return {
                'pattern': f'helm/{chart_name}',
                'status': 'would_apply',
                'message': f'Would create Helm chart at {target_path}'
            }
        
        # Create files from template
        for file_path, content in template['files'].items():
            full_path = target_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            rendered = Template(content).render(**variables)
            full_path.write_text(rendered)
        
        return {
            'pattern': f'helm/{chart_name}',
            'status': 'applied',
            'message': f'Created Helm chart at {target_path}'
        }
    
    def _apply_argocd_template(self, template: Dict[str, Any], target_repo: Path,
                              variables: Dict[str, Any], dry_run: bool) -> Dict[str, Any]:
        """Apply an ArgoCD template from memory"""
        app_name = template['name']
        target_path = target_repo / 'deployments' / 'argocd' / f'{app_name}-application.yaml'
        
        if dry_run:
            return {
                'pattern': f'argocd/{app_name}',
                'status': 'would_apply',
                'message': f'Would create ArgoCD app at {target_path}'
            }
        
        # Create application file
        target_path.parent.mkdir(parents=True, exist_ok=True)
        content = template['files']['application.yaml']
        rendered = Template(content).render(**variables)
        target_path.write_text(rendered)
        
        return {
            'pattern': f'argocd/{app_name}',
            'status': 'applied',
            'message': f'Created ArgoCD application at {target_path}'
        }
    
    def _extract_variables_for_repo(self, repo_path: Path) -> Dict[str, Any]:
        """Extract variables from repository context"""
        repo_name = repo_path.name
        
        # Try to get git remote URL
        repo_url = self.git_helper.get_remote_url(repo_path) or f'https://github.com/org/{repo_name}'
        
        return {
            'app_name': repo_name,
            'repo_url': repo_url,
            'repo_name': repo_name,
            'chart_version': '0.1.0',
            'app_version': '1.0.0',
            'image_repository': f'myorg/{repo_name}',
            'image_tag': 'latest',
            'source_path': 'deployments/helm/' + repo_name,
            'dest_namespace': repo_name,
            'source_type': 'helm'
        }