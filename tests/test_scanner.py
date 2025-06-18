import pytest
from pathlib import Path
import tempfile
import yaml
from deployment_replicator.scanner import DeploymentScanner
from deployment_replicator.patterns.helm import HelmPatternDetector

def create_helm_chart(base_path: Path, name: str):
    """Helper to create a test Helm chart"""
    chart_dir = base_path / name
    chart_dir.mkdir(parents=True)
    
    chart_data = {
        "apiVersion": "v2",
        "name": name,
        "version": "1.0.0"
    }
    
    with open(chart_dir / "Chart.yaml", "w") as f:
        yaml.dump(chart_data, f)
    
    return chart_dir

class TestDeploymentScanner:
    def test_scan_empty_repo(self):
        """Test scanning an empty repository"""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = DeploymentScanner()
            patterns = scanner.scan_repository(Path(tmpdir))
            assert patterns == []
    
    def test_scan_helm_charts(self):
        """Test scanning repository with Helm charts"""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            
            # Create test Helm charts
            create_helm_chart(base_path / "services", "app1")
            create_helm_chart(base_path / "services", "app2")
            
            scanner = DeploymentScanner()
            patterns = scanner.scan_repository(base_path)
            
            assert len(patterns) == 2
            assert all(p['type'] == 'helm' for p in patterns)
            assert {p['name'] for p in patterns} == {'app1', 'app2'}

class TestHelmPatternDetector:
    def test_detect_helm_chart(self):
        """Test Helm chart detection"""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            chart_dir = create_helm_chart(base_path, "test-app")
            
            # Add values.yaml
            values = {"image": {"tag": "v1.0.0"}}
            with open(chart_dir / "values.yaml", "w") as f:
                yaml.dump(values, f)
            
            detector = HelmPatternDetector()
            patterns = detector.detect(base_path)
            
            assert len(patterns) == 1
            assert patterns[0]['name'] == 'test-app'
            assert patterns[0]['type'] == 'helm'
            assert len(patterns[0]['configs']) == 1