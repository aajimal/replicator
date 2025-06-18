# Deployment Pattern Replicator

A tool that learns deployment patterns from one repository and applies them to others. It scans for Helm charts, ArgoCD manifests, and other deployment configurations, then replicates these patterns across your repositories.

## Quick Start

```bash
# Install
pip install -e .

# Scan a repository for patterns
deploy-replicate scan ./my-template-repo -o ./templates

# Apply patterns to another repository
deploy-replicate apply ./templates ./target-repo --dry-run

# One-shot replication
deploy-replicate replicate ./source-repo ./target-repo
```

## Features

- **Pattern Detection**: Automatically finds Helm charts and ArgoCD applications
- **Template Generation**: Creates reusable templates from discovered patterns
- **Smart Application**: Only applies missing patterns, respects existing configs
- **Dry Run Mode**: Preview changes before applying
- **Parameterization**: Automatically adapts patterns to target repositories

## Usage Examples

### 1. Building a Template Library

```bash
# Scan multiple repos to build a comprehensive template library
deploy-replicate scan ./microservice-a -o ./company-templates
deploy-replicate scan ./microservice-b -o ./company-templates
deploy-replicate scan ./platform-repo -o ./company-templates
```

### 2. Standardizing Deployments

```bash
# Apply standard patterns to all team repositories
for repo in team-repos/*; do
    deploy-replicate apply ./company-templates "$repo"
done
```

### 3. Quick Replication

```bash
# Copy deployment setup from one service to another
deploy-replicate replicate ./auth-service ./new-payment-service
```

## Extending

### Adding New Pattern Types

1. Create a new detector in `deployment_replicator/patterns/`
2. Implement the `detect()` method
3. Add to scanner's detector list

### Customizing Templates

Templates use Jinja2 syntax. Common variables:
- `{{ app_name }}` - Repository/application name
- `{{ repo_url }}` - Git repository URL
- `{{ image_repository }}` - Docker image repository
- `{{ namespace }}` - Kubernetes namespace

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

## Development

```bash
# Run tests
pytest

# Install dev dependencies
pip install -r requirements-dev.txt

# Format code
black deployment_replicator/
```

## TODO

- [ ] Support for Kustomize patterns
- [ ] Terraform module detection
- [ ] Config validation before applying
- [ ] Interactive mode for customization
- [ ] Pattern versioning
- [ ] Rollback capability