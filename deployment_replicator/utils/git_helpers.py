from pathlib import Path
from typing import Optional
from git import Repo, InvalidGitRepositoryError

class GitHelper:
    """Git repository utilities"""
    
    def get_remote_url(self, repo_path: Path) -> Optional[str]:
        """Get the remote URL of a git repository"""
        try:
            repo = Repo(repo_path)
            if repo.remotes:
                return repo.remotes.origin.url
        except (InvalidGitRepositoryError, AttributeError):
            pass
        return None
    
    def is_git_repo(self, path: Path) -> bool:
        """Check if a path is a git repository"""
        try:
            Repo(path)
            return True
        except InvalidGitRepositoryError:
            return False
    
    def get_current_branch(self, repo_path: Path) -> Optional[str]:
        """Get the current branch name"""
        try:
            repo = Repo(repo_path)
            return repo.active_branch.name
        except:
            return None
    
    def has_uncommitted_changes(self, repo_path: Path) -> bool:
        """Check if repository has uncommitted changes"""
        try:
            repo = Repo(repo_path)
            return repo.is_dirty()
        except:
            return False