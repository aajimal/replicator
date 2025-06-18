from pathlib import Path
from typing import List, Dict, Any
import yaml

class KustomizePatternDetector:
    """Detects Kustomize patterns in a repository"""
    
    def detect(self, repo_path: Path) -> List[Dict[str, Any]]:
        """Find all Kustomize configurations in the repository"""
        patterns = []
        
        # Look for kustomization.yaml files
        for kust_file in repo_path.rglob('kustomization.yaml'):
            # Skip hidden directories
            if any(part.startswith('.') for part in kust_file.parts):
                continue
            
            pattern = self._analyze_kustomization(kust_file)
            if pattern:
                patterns.append(pattern)
        
        # Also check for kustomization.yml
        for kust_file in repo_path.rglob('kustomization.yml'):
            if any(part.startswith('.') for part in kust_file.parts):
                continue
            
            pattern = self._analyze_kustomization(kust_file)
            if pattern and pattern not in patterns:
                patterns.append(pattern)
        
        return patterns
    
    def _analyze_kustomization(self, kust_file: Path) -> Dict[str, Any]:
        """Analyze a kustomization file"""
        try:
            with open(kust_file, 'r') as f:
                kust_data = yaml.safe_load(f) or {}
            
            kust_dir = kust_file.parent
            
            pattern = {
                'type': 'kustomize',
                'name': kust_dir.name,
                'path': str(kust_dir),
                'configs': [kust_file],
                'resources': kust_data.get('resources', []),
                'has_overlays': (kust_dir.parent / 'overlays').exists()
            }
            
            # Check for base and overlays structure
            if 'base' in kust_dir.parts:
                pattern['structure'] = 'base'
            elif 'overlays' in kust_dir.parts:
                pattern['structure'] = 'overlay'
                pattern['overlay_name'] = kust_dir.name
            
            return pattern
            
        except Exception as e:
            print(f"Error analyzing Kustomization at {kust_file}: {e}")
            return None