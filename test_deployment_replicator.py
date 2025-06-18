#!/usr/bin/env python3
"""Quick test script to verify the deployment replicator is working"""

import os
import tempfile
import shutil
from pathlib import Path
import yaml

# Create test repositories
def create_test_repos():
    # Create source repo with Helm chart
    source_dir = Path("test_source_repo")
    source_dir.mkdir(exist_ok=True)
    
    # Create Helm chart
    helm_dir = source_dir / "deployments" / "helm" / "test-app"
    helm_dir.mkdir(parents=True, exist_ok=True)
    
    # Chart.yaml
    chart_yaml = {
        "apiVersion": "v2",
        "name": "test-app",
        "version": "1.0.0",
        "description": "Test application"
    }
    with open(helm_dir / "Chart.yaml", "w") as f:
        yaml.dump(chart_yaml, f)
    
    # values.yaml
    values_yaml = {
        "image": {
            "repository": "nginx",
            "tag": "latest"
        },
        "service": {
            "port": 80
        }
    }
    with open(helm_dir / "values.yaml", "w") as f:
        yaml.dump(values_yaml, f)
    
    # Create ArgoCD app
    argocd_dir = source_dir / "deployments" / "argocd"
    argocd_dir.mkdir(parents=True, exist_ok=True)
    
    argocd_app = {
        "apiVersion": "argoproj.io/v1alpha1",
        "kind": "Application",
        "metadata": {
            "name": "test-app",
            "namespace": "argocd"
        },
        "spec": {
            "project": "default",
            "source": {
                "repoURL": "https://github.com/example/test-app",
                "path": "deployments/helm/test-app",
                "targetRevision": "HEAD"
            },
            "destination": {
                "server": "https://kubernetes.default.svc",
                "namespace": "test-app"
            }
        }
    }
    with open(argocd_dir / "test-app.yaml", "w") as f:
        yaml.dump(argocd_app, f)
    
    # Create target repo (empty)
    target_dir = Path("test_target_repo")
    target_dir.mkdir(exist_ok=True)
    
    print("✅ Created test repositories")
    return source_dir, target_dir

if __name__ == "__main__":
    # Create test repos
    source_repo, target_repo = create_test_repos()
    
    print("\n🔧 Testing deployment replicator...\n")
    
    # Test scanning
    print("1. Testing scan command:")
    os.system(f"deploy-replicate scan {source_repo}")
    
    # Test replication
    print("\n2. Testing replicate command (dry-run):")
    os.system(f"deploy-replicate replicate {source_repo} {target_repo} --dry-run")
    
    # Test actual replication
    print("\n3. Testing actual replication:")
    os.system(f"deploy-replicate replicate {source_repo} {target_repo}")
    
    # Check results
    print("\n4. Checking results:")
    helm_result = (target_repo / "deployments" / "helm" / "test-app" / "Chart.yaml").exists()
    argocd_result = list((target_repo / "deployments" / "argocd").glob("*.yaml"))
    
    if helm_result:
        print("✅ Helm chart replicated successfully")
    else:
        print("❌ Helm chart replication failed")
    
    if argocd_result:
        print("✅ ArgoCD application replicated successfully")
    else:
        print("❌ ArgoCD application replication failed")
    
    # Cleanup
    print("\n🧹 Cleaning up test repositories...")
    shutil.rmtree(source_repo)
    shutil.rmtree(target_repo)
    
    print("\n✨ Test complete!")