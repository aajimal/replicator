import click
import sys
from pathlib import Path
from colorama import init, Fore, Style
from tabulate import tabulate

from .scanner import DeploymentScanner
from .template_engine import TemplateEngine
from .applicator import PatternApplicator

init(autoreset=True)

@click.group()
def cli():
    """Deployment Pattern Replicator - Learn and apply deployment patterns across repos"""
    pass

@cli.command()
@click.argument('repo_path', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output directory for templates')
def scan(repo_path, output):
    """Scan a repository for deployment patterns"""
    click.echo(f"{Fore.CYAN}🔍 Scanning repository: {repo_path}{Style.RESET_ALL}")
    
    scanner = DeploymentScanner()
    patterns = scanner.scan_repository(Path(repo_path))
    
    if not patterns:
        click.echo(f"{Fore.YELLOW}⚠️  No deployment patterns found{Style.RESET_ALL}")
        return
    
    # Display found patterns
    table_data = []
    for pattern in patterns:
        table_data.append([
            pattern['type'],
            pattern['name'],
            pattern['path'],
            len(pattern.get('configs', []))
        ])
    
    click.echo(f"\n{Fore.GREEN}✅ Found {len(patterns)} deployment patterns:{Style.RESET_ALL}")
    click.echo(tabulate(table_data, headers=['Type', 'Name', 'Path', 'Configs'], tablefmt='grid'))
    
    if output:
        engine = TemplateEngine()
        templates = engine.create_templates(patterns, Path(output))
        click.echo(f"\n{Fore.GREEN}📝 Generated {len(templates)} templates in {output}{Style.RESET_ALL}")

@cli.command()
@click.argument('template_dir', type=click.Path(exists=True))
@click.argument('target_repo', type=click.Path(exists=True))
@click.option('--dry-run', is_flag=True, help='Show what would be applied without making changes')
@click.option('--force', is_flag=True, help='Overwrite existing patterns')
def apply(template_dir, target_repo, dry_run, force):
    """Apply deployment patterns to a target repository"""
    click.echo(f"{Fore.CYAN}🎯 Applying patterns to: {target_repo}{Style.RESET_ALL}")
    
    applicator = PatternApplicator()
    results = applicator.apply_patterns(
        Path(template_dir), 
        Path(target_repo),
        dry_run=dry_run,
        force=force
    )
    
    # Display results
    for result in results:
        status_color = Fore.GREEN if result['status'] == 'applied' else Fore.YELLOW
        click.echo(f"{status_color}{'[DRY RUN] ' if dry_run else ''}{result['pattern']} -> {result['status']}{Style.RESET_ALL}")
        if result.get('message'):
            click.echo(f"  └─ {result['message']}")

@cli.command()
@click.argument('source_repo', type=click.Path(exists=True))
@click.argument('target_repo', type=click.Path(exists=True))
@click.option('--dry-run', is_flag=True, help='Show what would be applied without making changes')
def replicate(source_repo, target_repo, dry_run):
    """One-shot command to scan source and apply to target"""
    click.echo(f"{Fore.CYAN}🔄 Replicating patterns from {source_repo} to {target_repo}{Style.RESET_ALL}")
    
    # Scan source
    scanner = DeploymentScanner()
    patterns = scanner.scan_repository(Path(source_repo))
    
    if not patterns:
        click.echo(f"{Fore.YELLOW}⚠️  No patterns found in source repository{Style.RESET_ALL}")
        return
    
    # Create templates in memory
    engine = TemplateEngine()
    templates = engine.create_templates(patterns)
    
    # Apply to target
    applicator = PatternApplicator()
    results = applicator.apply_patterns_direct(templates, Path(target_repo), dry_run=dry_run)
    
    # Summary
    applied = sum(1 for r in results if r['status'] == 'applied')
    skipped = sum(1 for r in results if r['status'] == 'skipped')
    click.echo(f"\n{Fore.GREEN}✅ Applied: {applied}, Skipped: {skipped}{Style.RESET_ALL}")

if __name__ == '__main__':
    cli()