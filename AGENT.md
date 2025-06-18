# Deployment Pattern Replicator - Ampcode Configuration

## Quick Start

```bash
# Install and test
pip install -e . && python test_deployment_replicator.py

# Basic usage
deploy-replicate scan ./source-repo
deploy-replicate replicate ./source-repo ./target-repo --dry-run
```

## Project Structure

```yaml
deployment_replicator/
  cli.py:           # CLI entry point - Click commands
  scanner.py:       # Pattern detection orchestrator
  template_engine.py: # Jinja2 template generation
  applicator.py:    # Apply patterns to repos
  patterns/:        # Pluggable pattern detectors
    helm.py:        # Detects Helm charts
    argocd.py:      # Detects ArgoCD apps
    kustomize.py:   # Detects Kustomize configs
  utils/:           # Helper utilities
    git_helpers.py: # Git operations
```

## Core Concepts

### Pattern Detection Flow
```python
# Scanner uses all detectors
Scanner.scan_repository()
  → HelmPatternDetector.detect()     # Finds Chart.yaml
  → ArgoCDPatternDetector.detect()   # Finds Application CRDs
  → KustomizePatternDetector.detect() # Finds kustomization.yaml
  → Returns: List[Pattern]
```

### Pattern Structure
```python
{
    'type': 'helm',              # Pattern type
    'name': 'my-service',        # Pattern name
    'path': '/path/to/chart',    # Location found
    'configs': [Path, ...],      # Config files
    'version': '1.0.0',          # Version info
    # Type-specific fields...
}
```

### Template Generation
```python
# Templates are Jinja2 with variables
TemplateEngine.create_templates(patterns)
  → Extracts parameterizable values
  → Creates Jinja2 templates
  → Returns template dict with files
```

### Application Process
```python
# Applicator handles the merge
Applicator.apply_patterns()
  → Scan target for existing patterns
  → Extract variables from target repo
  → Render templates with variables
  → Write files (or dry-run)
```

## Key Operations

### Scanning Repository
```python
scanner = DeploymentScanner()
patterns = scanner.scan_repository(Path('./my-repo'))
# Returns: [{type, name, path, configs}, ...]
```

### Creating Templates
```python
engine = TemplateEngine()
templates = engine.create_templates(patterns, output_dir)
# Creates: helm/app/Chart.yaml, values.yaml, etc.
```

### Applying Patterns
```python
applicator = PatternApplicator()
results = applicator.apply_patterns(
    template_dir=Path('./templates'),
    target_repo=Path('./target'),
    dry_run=True
)
# Returns: [{pattern, status, message}, ...]
```

## Adding New Pattern Types

### 1. Create Detector
```python
# deployment_replicator/patterns/terraform.py
class TerraformPatternDetector:
    def detect(self, repo_path: Path) -> List[Dict[str, Any]]:
        patterns = []
        for tf_file in repo_path.rglob('*.tf'):
            # Analyze and create pattern dict
        return patterns
```

### 2. Register Detector
```python
# In scanner.py __init__
self.detectors = [
    HelmPatternDetector(),
    TerraformPatternDetector(),  # Add here
]
```

### 3. Add Template Logic
```python
# In template_engine.py
def _create_terraform_template(self, pattern, output_dir):
    # Return template with Jinja2 variables
```

## Variable System

### Default Variables
- `app_name`: From repo directory name
- `repo_url`: From git remote origin
- `namespace`: Often same as app_name
- `image_repository`: Constructed from app_name

### Custom Variable Extraction
```python
# In applicator.py
def _extract_variables_for_repo(self, repo_path):
    # Add logic to extract from:
    # - package.json
    # - go.mod
    # - Makefile
    # - .env files
```

## CLI Commands

### scan
```bash
deploy-replicate scan <repo> [-o <output_dir>]
# Finds patterns and optionally saves templates
```

### apply
```bash
deploy-replicate apply <templates> <target> [--dry-run] [--force]
# Applies saved templates to target repo
```

### replicate
```bash
deploy-replicate replicate <source> <target> [--dry-run]
# One-shot scan and apply
```

## Testing

### Unit Test Example
```python
def test_helm_detection():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test Chart.yaml
        # Run detector
        # Assert pattern found
```

### Integration Test
```bash
python test_deployment_replicator.py
# Creates test repos, runs full workflow
```

## Common Patterns

### Helm Chart Detection
- Looks for: `Chart.yaml`
- Captures: name, version, values.yaml
- Templates: Chart.yaml, values.yaml, deployment.yaml

### ArgoCD App Detection
- Looks for: `kind: Application` in YAML
- Common paths: `argocd/`, `deployments/argocd/`
- Templates: application.yaml with sync policies

### Kustomize Detection
- Looks for: `kustomization.yaml`
- Captures: resources, overlays structure
- Templates: base and overlay configurations

## Debugging

### Enable Verbose Output
```python
# Add logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Dry Run First
```bash
# Always test with --dry-run
deploy-replicate apply ./templates ./target --dry-run
```

### Check Git Status
```python
# GitHelper provides utilities
git_helper = GitHelper()
is_repo = git_helper.is_git_repo(path)
remote_url = git_helper.get_remote_url(path)
```

## Performance Tips

1. **Exclude Patterns**: Skip `.git`, `node_modules`, `vendor`
2. **Lazy Loading**: Only parse files when needed
3. **Batch Operations**: Apply all patterns in one pass
4. **Cache Templates**: Reuse rendered templates

## Error Handling

- Detectors catch exceptions and continue
- CLI shows colored error messages
- Dry-run mode for safety
- Force flag for overwrites

## Future Enhancements

1. **Validation**: Pre-apply validation of patterns
2. **Rollback**: Undo applied patterns
3. **Diff View**: Show what will change
4. **Config File**: `.replicator.yml` for defaults
5. **Parallel Scanning**: Speed up large repos
6. **Pattern Library**: Share templates across teams