from pathlib import Path
from typing import List, Dict, Any
import yaml

class HelmPatternDetector:
    """Detects Helm chart patterns in a repository"""
    
    def detect(self, repo_path: Path) -> List[Dict[str, Any]]:
        """Find all Helm charts in the repository"""
        patterns = []
        
        # Look for Chart.yaml files
        for chart_file in repo_path.rglob('Chart.yaml'):
            # Skip hidden directories and common excludes
            if any(part.startswith('.') for part in chart_file.parts):
                continue
            if 'node_modules' in chart_file.parts or 'vendor' in chart_file.parts:
                continue
            
            chart_dir = chart_file.parent
            pattern = self._analyze_helm_chart(chart_dir)
            if pattern:
                patterns.append(pattern)
        
        return patterns
    
    def _analyze_helm_chart(self, chart_dir: Path) -> Dict[str, Any]:
        """Analyze a Helm chart directory"""
        chart_file = chart_dir / 'Chart.yaml'
        
        try:
            with open(chart_file, 'r') as f:
                chart_data = yaml.safe_load(f) or {}
            
            pattern = {
                'type': 'helm',
                'name': chart_data.get('name', chart_dir.name),
                'path': str(chart_dir),
                'version': chart_data.get('version', '0.1.0'),
                'configs': []
            }
            
            # Check for additional files
            values_file = chart_dir / 'values.yaml'
            if values_file.exists():
                pattern['configs'].append(values_file)
            
            # Check for template files
            templates_dir = chart_dir / 'templates'
            if templates_dir.exists():
                pattern['template_count'] = len(list(templates_dir.glob('*.yaml')))
            
            return pattern
            
        except Exception as e:
            print(f"Error analyzing Helm chart at {chart_dir}: {e}")
            return None