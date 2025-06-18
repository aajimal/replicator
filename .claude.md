# Deployment Pattern Replicator - Claude Code Guide

## Project Overview

This is a deployment pattern replicator that scans Git repositories for deployment patterns (Helm charts, ArgoCD manifests, Kustomize configs) and applies them to other repositories. It's designed to standardize deployment configurations across multiple services.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌────────────┐
│   Scanner   │────▶│   Template   │────▶│ Applicator │
│             │     │   Engine     │     │            │
└─────────────┘     └──────────────┘     └────────────┘
      │                                          │
      ▼                                          ▼
 [Source Repo]                            [Target Repo]
```

### Core Components

1. **Scanner** (`deployment_replicator/scanner.py`)
   - Orchestrates pattern detection across repositories
   - Uses pluggable detectors for different pattern types
   - Extracts parameterizable values from patterns

2. **Pattern Detectors** (`deployment_replicator/patterns/`)
   - `helm.py`: Finds Helm charts by looking for Chart.yaml
   - `argocd.py`: Finds ArgoCD applications (Application CRDs)
   - `kustomize.py`: Finds Kustomize configurations
   - Easy to extend: just add new detector classes

3. **Template Engine** (`deployment_replicator/template_engine.py`)
   - Converts discovered patterns into Jinja2 templates
   - Identifies parameterizable values (app names, namespaces, etc.)
   - Can save templates to disk or keep in memory

4. **Applicator** (`deployment_replicator/applicator.py`)
   - Applies templates to target repositories
   - Handles variable substitution based on repo context
   - Supports dry-run mode and force overwrites
   - Avoids duplicating existing patterns

5. **CLI** (`deployment_replicator/cli.py`)
   - Three main commands: scan, apply, replicate
   - Beautiful colored output with tables
   - Progress indicators and clear error messages

## Key Files

- `setup.py`: Package configuration, defines `deploy-replicate` CLI entry point
- `deployment_replicator/cli.py`: Click-based CLI implementation
- `deployment_replicator/scanner.py`: Main scanning logic
- `deployment_replicator/patterns/*.py`: Pattern detection modules
- `deployment_replicator/template_engine.py`: Template creation and rendering
- `deployment_replicator/applicator.py`: Pattern application logic
- `test_deployment_replicator.py`: Quick end-to-end test script

## Development Workflow

### Setup
```bash
pip install -e .
pip install -r requirements-dev.txt
```

### Running Tests
```bash
# Quick test
python test_deployment_replicator.py

# Full test suite
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=deployment_replicator
```

### Code Quality
```bash
# Format code
black deployment_replicator/ tests/

# Lint
flake8 deployment_replicator/
mypy deployment_replicator/

# Or use make
make format
make lint
```

## Common Tasks

### Adding a New Pattern Type

1. Create a new detector in `deployment_replicator/patterns/terraform.py`:
```python
class TerraformPatternDetector:
    def detect(self, repo_path: Path) -> List[Dict[str, Any]]:
        # Look for *.tf files
        # Return pattern dictionaries
```

2. Add to scanner in `deployment_replicator/scanner.py`:
```python
from .patterns.terraform import TerraformPatternDetector

self.detectors = [
    HelmPatternDetector(),
    ArgoCDPatternDetector(),
    KustomizePatternDetector(),
    TerraformPatternDetector(),  # New!
]
```

3. Add template creation logic in `template_engine.py`
4. Add application logic in `applicator.py`

### Customizing Variable Extraction

Edit `_extract_variables_for_repo()` in `applicator.py` to pull from:
- package.json for Node.js apps
- go.mod for Go apps
- pom.xml for Java apps
- Git remote URLs
- Directory structure conventions

### Adding New CLI Commands

Add new Click commands in `cli.py`:
```python
@cli.command()
@click.argument('repo_path')
def validate(repo_path):
    """Validate deployment patterns in a repository"""
    # Implementation
```

## Template Variables

Common variables available in templates:
- `{{ app_name }}` - Repository/application name
- `{{ repo_url }}` - Git repository URL
- `{{ chart_version }}` - Helm chart version
- `{{ image_repository }}` - Docker image repository
- `{{ namespace }}` - Kubernetes namespace
- `{{ source_path }}` - Path within repository

## Design Patterns

1. **Pluggable Detectors**: Each pattern type has its own detector class
2. **Template-based Generation**: Uses Jinja2 for flexible templating
3. **Repository Context**: Automatically extracts context from target repos
4. **Fail-Safe Application**: Won't overwrite existing patterns unless forced

## Error Handling

- Pattern detectors catch and log errors without crashing
- CLI provides clear error messages with colored output
- Dry-run mode for safe testing
- Git integration handles repositories that aren't git repos

## Extension Points

1. **New Pattern Types**: Add detectors in `patterns/`
2. **Variable Sources**: Extend `_extract_variables_for_repo()`
3. **Template Formats**: Modify template strings in `template_engine.py`
4. **Output Formats**: Add new output options to CLI commands
5. **Validation**: Add pattern validation before application

## Testing Strategy

- Unit tests for each detector
- Integration tests for full workflow
- Temporary directories for safe testing
- Mock Git operations where needed

## Performance Considerations

- Recursive file searches use `rglob()` efficiently
- Skips hidden directories and common excludes
- Lazy pattern detection (only scans when needed)
- Templates cached in memory during operations