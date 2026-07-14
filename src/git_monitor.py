"""
Git Repository Monitoring - Extract metrics from commits and PRs

This module monitors git repositories and extracts code change metrics
that are used as input to the risk prediction model.
"""

import os
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

try:
    import git
    from git import Repo
except ImportError:
    print("⚠️ GitPython not installed. Install with: pip install GitPython")

try:
    from radon.complexity import cc_visit
    from radon.metrics import mi_visit
except ImportError:
    print("⚠️ Radon not installed. Install with: pip install radon")


class GitRiskAnalyzer:
    """Extract code metrics from git repositories"""

    def __init__(self, repo_path: str):
        """Initialize with path to git repository"""
        self.repo_path = repo_path
        try:
            self.repo = Repo(repo_path)
        except Exception as e:
            raise ValueError(f"Invalid git repository: {repo_path}") from e

    def get_commit_info(self, commit_sha: str) -> Dict:
        """Get detailed info about a specific commit"""
        try:
            commit = self.repo.commit(commit_sha)
        except Exception as e:
            return {'error': f"Commit not found: {commit_sha}"}

        files_changed = commit.stats.total['files']
        lines_added = commit.stats.total['insertions']
        lines_deleted = commit.stats.total['deletions']

        return {
            'commit_sha': str(commit.hexsha)[:7],
            'author': commit.author.name,
            'email': commit.author.email,
            'timestamp': datetime.fromtimestamp(commit.committed_date),
            'message': commit.message.strip(),
            'files_changed': files_changed,
            'lines_added': lines_added,
            'lines_deleted': lines_deleted,
            'total_changes': lines_added + lines_deleted,
            'changed_files': list(commit.stats.files.keys())
        }

    def get_branch_commits(self, branch: str = 'main',
                          num_commits: int = 10) -> List[Dict]:
        """Get recent commits from a branch"""
        try:
            commits = list(self.repo.iter_commits(branch, max_count=num_commits))
        except Exception as e:
            return []

        return [self.get_commit_info(str(commit.hexsha)) for commit in commits]

    def get_files_changed_since(self, ref1: str, ref2: str) -> Dict:
        """Get files changed between two commits/branches"""
        try:
            diffs = self.repo.commit(ref1).diff(ref2)
        except Exception as e:
            return {'error': str(e)}

        files_added = []
        files_deleted = []
        files_modified = []

        for diff in diffs:
            if diff.new_file:
                files_added.append(diff.b_path)
            elif diff.deleted_file:
                files_deleted.append(diff.a_path)
            else:
                files_modified.append(diff.b_path or diff.a_path)

        return {
            'files_added': files_added,
            'files_deleted': files_deleted,
            'files_modified': files_modified,
            'total_files_changed': len(files_added) + len(files_deleted) + len(files_modified),
            'total_added': len(files_added),
            'total_deleted': len(files_deleted),
            'total_modified': len(files_modified)
        }

    def get_branch_info(self, branch: str = 'main') -> Dict:
        """Get information about a branch"""
        try:
            branch_ref = self.repo.heads[branch]
            commit = branch_ref.commit
        except Exception as e:
            return {'error': f"Branch not found: {branch}"}

        return {
            'branch': branch,
            'latest_commit': str(commit.hexsha)[:7],
            'author': commit.author.name,
            'timestamp': datetime.fromtimestamp(commit.committed_date),
            'message': commit.message.strip(),
            'commits_ahead_of_main': len(list(self.repo.iter_commits(
                f'main..{branch}'
            ))) if branch != 'main' else 0
        }

    def calculate_code_complexity(self, file_path: str) -> Optional[float]:
        """Calculate cyclomatic complexity for a Python file"""
        full_path = os.path.join(self.repo_path, file_path)

        if not file_path.endswith('.py') or not os.path.exists(full_path):
            return None

        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                code = f.read()

            complexity_results = cc_visit(code)

            if not complexity_results:
                return 1.0

            # Average complexity across all functions/classes
            complexities = [item.complexity for item in complexity_results]
            return sum(complexities) / len(complexities)
        except Exception as e:
            return None

    def analyze_branch_changes(self, branch: str, base_branch: str = 'main') -> Dict:
        """Analyze all changes in a branch compared to base"""
        files_info = self.get_files_changed_since(base_branch, branch)

        if 'error' in files_info:
            return files_info

        # Calculate complexity for modified files
        complexity_scores = []
        for file_path in files_info['files_modified']:
            complexity = self.calculate_code_complexity(file_path)
            if complexity is not None:
                complexity_scores.append(complexity)

        avg_complexity = sum(complexity_scores) / len(complexity_scores) if complexity_scores else 1.0

        # Get contributor info
        commits = list(self.repo.iter_commits(f'{base_branch}..{branch}'))
        contributors = set()
        for commit in commits:
            contributors.add(commit.author.name)

        return {
            'branch': branch,
            'base_branch': base_branch,
            'files_changed': files_info['total_files_changed'],
            'files_added': files_info['total_added'],
            'files_deleted': files_info['total_deleted'],
            'files_modified': files_info['total_modified'],
            'lines_changed': sum(
                self.repo.commit(f'{base_branch}..{branch}').stats.total.get(k, 0)
                for k in ['insertions', 'deletions']
            ),
            'lines_added': sum(
                self.repo.commit(f'{base_branch}..{branch}').stats.total.get('insertions', 0)
            ),
            'complexity_score': avg_complexity,
            'num_commits': len(commits),
            'contributors': list(contributors),
            'num_contributors': len(contributors)
        }

    def get_developer_history(self, author_name: str,
                            num_commits: int = 100) -> Dict:
        """Get commit history for a developer"""
        commits = list(self.repo.iter_commits(all=True, max_count=num_commits))

        author_commits = [c for c in commits if c.author.name == author_name]

        if not author_commits:
            return {
                'author': author_name,
                'total_commits': 0,
                'first_commit': None,
                'last_commit': None
            }

        return {
            'author': author_name,
            'total_commits': len(author_commits),
            'first_commit': datetime.fromtimestamp(author_commits[-1].committed_date),
            'last_commit': datetime.fromtimestamp(author_commits[0].committed_date),
            'avg_lines_per_commit': sum(c.stats.total['insertions'] for c in author_commits) / len(author_commits)
        }


# Example usage
if __name__ == '__main__':
    # Initialize analyzer
    analyzer = GitRiskAnalyzer('.')

    # Get recent commits
    print("📝 Recent Commits:")
    commits = analyzer.get_branch_commits('main', num_commits=3)
    for commit in commits:
        print(f"  {commit['commit_sha']}: {commit['author']}")
        print(f"    Files: {commit['files_changed']}, Lines: +{commit['lines_added']}/-{commit['lines_deleted']}")

    # Get branch info
    print("\n🌿 Branch Info:")
    branch_info = analyzer.get_branch_info('main')
    print(f"  Latest: {branch_info['latest_commit']} by {branch_info['author']}")
