# Development Guide

## Setting Up Development Environment

### Prerequisites
- Python 3.8+
- Git
- pip

### Initial Setup
```bash
# Clone the repository
git clone https://github.com/aajimal/replicator.git
cd replicator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
pip install -r requirements-dev.txt

# Set up pre-commit hooks
pre-commit install
```

## Development Workflow

### 1. Making Changes
```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Make your changes
# Run tests frequently
pytest tests/ -v

# Format code
black deployment_replicator/

# Check linting
flake8 deployment_replicator/
```

### 2. Testing Your Changes
```bash
# Run quick integration test
python test_deployment_replicator.py

# Run full test suite
pytest tests/ -v --cov=deployment_replicator

# Test specific functionality
pytest tests/test_scanner.py -v -k "test_helm"
```

### 3. Manual Testing
```bash
# Test CLI commands
deploy-replicate scan ./test_source_repo
deploy-replicate replicate ./test_source_repo ./test_target_repo --dry-run

# Test with real repositories
deploy-replicate scan ~/projects/my-service
```

## Code Organization

### Module Structure
```
deployment_replicator/
├── __init__.py          # Package initialization
├── cli.py               # CLI interface (Click)
├── scanner.py           # Pattern scanning orchestration
├── template_engine.py   # Template generation (Jinja2)
├── applicator.py        # Pattern application logic
├── patterns/            # Pattern detection modules
│   ├── __init__.py
│   ├── helm.py         # Helm chart detector
│   ├── argocd.py       # ArgoCD app detector
│   └── kustomize.py    # Kustomize config detector
└── utils/              # Utility modules
    ├── __init__.py
    └── git_helpers.py  # Git operations
```

### Adding a New Pattern Detector

1. **Create the detector class**:
```python
# deployment_replicator/patterns/terraform.py
from pathlib import Path
from typing import List, Dict, Any

class TerraformPatternDetector:
    """Detects Terraform configurations in a repository"""
    
    def detect(self, repo_path: Path) -> List[Dict[str, Any]]:
        """Find all Terraform configurations"""
        patterns = []
        
        # Look for *.tf files
        for tf_file in repo_path.rglob('*.tf'):
            if self._should_skip(tf_file):
                continue
            
            pattern = self._analyze_terraform_config(tf_file)
            if pattern:
                patterns.append(pattern)
        
        return patterns
    
    def _should_skip(self, file_path: Path) -> bool:
        """Check if path should be skipped"""
        skip_dirs = {'.git', '.terraform', 'node_modules', 'vendor'}
        return any(part in skip_dirs for part in file_path.parts)
    
    def _analyze_terraform_config(self, tf_file: Path) -> Dict[str, Any]:
        """Analyze a Terraform file"""
        # Implementation details
        pass
```

2. **Register the detector**:
```python
# In scanner.py
from .patterns.terraform import TerraformPatternDetector

class DeploymentScanner:
    def __init__(self):
        self.detectors = [
            HelmPatternDetector(),
            ArgoCDPatternDetector(),
            KustomizePatternDetector(),
            TerraformPatternDetector(),  # Add here
        ]
```

3. **Add template generation**:
```python
# In template_engine.py
def create_templates(self, patterns, output_dir=None):
    # ...
    elif pattern['type'] == 'terraform':
        template = self._create_terraform_template(pattern, output_dir)
    # ...

def _create_terraform_template(self, pattern, output_dir):
    # Template creation logic
    pass
```

4. **Add application logic**:
```python
# In applicator.py
def apply_patterns_direct(self, templates, target_repo, dry_run=False):
    # ...
    elif template['type'] == 'terraform':
        result = self._apply_terraform_template(template, target_repo, variables, dry_run)
    # ...
```

## Testing Guidelines

### Unit Tests
```python
# tests/test_terraform_detector.py
import pytest
from pathlib import Path
import tempfile
from deployment_replicator.patterns.terraform import TerraformPatternDetector

def test_detect_terraform_files():
    """Test Terraform file detection"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test .tf file
        tf_file = Path(tmpdir) / "main.tf"
        tf_file.write_text('resource "aws_instance" "example" {}')
        
        detector = TerraformPatternDetector()
        patterns = detector.detect(Path(tmpdir))
        
        assert len(patterns) == 1
        assert patterns[0]['type'] == 'terraform'
```

### Integration Tests
```python
def test_end_to_end_terraform_replication():
    """Test full replication workflow for Terraform"""
    # Create source repo with Terraform
    # Run replication
    # Verify target repo has Terraform files
    pass
```

## Debugging Tips

### Enable Debug Logging
```python
# Add to your test or script
import logging
logging.basicConfig(level=logging.DEBUG)

# Add debug statements
logger = logging.getLogger(__name__)
logger.debug(f"Found pattern: {pattern}")
```

### Interactive Debugging
```python
# Add breakpoints
import pdb; pdb.set_trace()

# Or use ipdb for better experience
import ipdb; ipdb.set_trace()
```

### CLI Debugging
```bash
# Run with Python debugger
python -m pdb -m deployment_replicator.cli scan ./repo

# Or add verbose flag to CLI
@click.option('--verbose', '-v', is_flag=True)
def scan(repo_path, output, verbose):
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
```

## Performance Optimization

### Profile Code
```python
import cProfile
import pstats

def profile_scanning():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Run your code
    scanner = DeploymentScanner()
    scanner.scan_repository(Path('./large-repo'))
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)
```

### Optimization Strategies
1. **Skip unnecessary directories early**
2. **Use generators for large file lists**
3. **Cache compiled regular expressions**
4. **Parallelize independent operations**

## Release Process

### 1. Update Version
```python
# deployment_replicator/__init__.py
__version__ = "0.2.0"  # Bump version

# setup.py
version="0.2.0",  # Match version
```

### 2. Update Changelog
```markdown
# CHANGELOG.md
## [0.2.0] - 2024-01-XX
### Added
- Terraform pattern detection
- Performance improvements

### Fixed
- Bug in ArgoCD detection
```

### 3. Run Final Tests
```bash
# Full test suite
pytest tests/ -v --cov=deployment_replicator

# Build distribution
python setup.py sdist bdist_wheel

# Test installation
pip install dist/deployment-replicator-0.2.0.tar.gz
```

### 4. Create Release
```bash
# Tag release
git tag -a v0.2.0 -m "Release version 0.2.0"
git push origin v0.2.0

# Create GitHub release
# Upload distribution files
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure package is installed: `pip install -e .`
   - Check PYTHONPATH includes project root

2. **Pattern Not Detected**
   - Add debug logging to detector
   - Check file path filters
   - Verify file format matches expectations

3. **Template Rendering Errors**
   - Check Jinja2 syntax
   - Verify all variables are provided
   - Test template separately

4. **Git Operations Failing**
   - Ensure GitPython is installed
   - Check repository has remotes
   - Handle non-git directories gracefully

## Contributing Guidelines

1. **Code Style**
   - Follow PEP 8
   - Use Black for formatting
   - Add type hints where helpful

2. **Documentation**
   - Update docstrings for new methods
   - Add examples for complex functionality
   - Update README for user-facing changes

3. **Testing**
   - Write tests for new features
   - Maintain >80% code coverage
   - Test edge cases and error conditions

4. **Pull Requests**
   - Create focused PRs for single features
   - Include tests and documentation
   - Update changelog if needed