import subprocess
import json
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

@dataclass
class GitChange:
    commit_hash: str
    commit_message: str
    author: str
    date: datetime
    files_changed: List[str]
    change_type: str
    phase_impact: Optional[str] = None

class GitChangeMonitor:
    """Monitor and categorize git changes for documentation maintenance"""
    
    def __init__(self, repo_root: str):
        self.repo_root = repo_root
        
    def get_changes_since(self, since_time: datetime) -> List[GitChange]:
        """Get all git changes since specified time"""
        since_str = since_time.strftime('%Y-%m-%d %H:%M:%S')
        
        cmd = [
            "git", "log",
            f"--since={since_str}",
            "--name-only",
            "--pretty=format:COMMIT|%H|%s|%an|%ad",
            "--date=iso"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.repo_root)
            return self.parse_git_log(result.stdout)
        except subprocess.SubprocessError as e:
            print(f"Error getting git changes: {e}")
            return []
    
    def parse_git_log(self, git_output: str) -> List[GitChange]:
        """Parse git log output into structured changes"""
        changes = []
        lines = git_output.strip().split('\n')
        
        current_commit = None
        files_in_commit = []
        
        for line in lines:
            if line.startswith('COMMIT|'):
                # Save previous commit if exists
                if current_commit:
                    changes.append(self.create_git_change(current_commit, files_in_commit))
                
                # Parse new commit info
                parts = line[7:].split('|')  # Remove 'COMMIT|' prefix
                if len(parts) >= 4:
                    current_commit = {
                        'hash': parts[0],
                        'message': parts[1],
                        'author': parts[2],
                        'date': self.parse_git_date(parts[3])
                    }
                    files_in_commit = []
            elif line.strip() and current_commit:
                # File in current commit
                files_in_commit.append(line.strip())
        
        # Don't forget the last commit
        if current_commit:
            changes.append(self.create_git_change(current_commit, files_in_commit))
        
        return changes
    
    def create_git_change(self, commit_info: Dict[str, Any], files: List[str]) -> GitChange:
        """Create GitChange object from parsed commit info"""
        change_type = self.categorize_change_type(commit_info['message'], files)
        phase_impact = self.detect_phase_impact(commit_info['message'], files)
        
        return GitChange(
            commit_hash=commit_info['hash'],
            commit_message=commit_info['message'],
            author=commit_info['author'],
            date=commit_info['date'],
            files_changed=files,
            change_type=change_type,
            phase_impact=phase_impact
        )
    
    def parse_git_date(self, date_str: str) -> datetime:
        """Parse git date string to datetime"""
        try:
            # Git ISO format: 2025-06-23 16:37:39 +0000
            date_part = date_str.split(' +')[0]  # Remove timezone
            return datetime.strptime(date_part, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return datetime.now()
    
    def categorize_change_type(self, commit_message: str, files: List[str]) -> str:
        """Categorize the type of change based on message and files"""
        message_lower = commit_message.lower()
        
        # Priority-based categorization
        if any(keyword in message_lower for keyword in ['feat:', 'feature:', 'implement', 'add']):
            return 'feature'
        elif any(keyword in message_lower for keyword in ['fix:', 'bug:', 'patch']):
            return 'bugfix'
        elif any(keyword in message_lower for keyword in ['docs:', 'doc:', 'documentation']):
            return 'documentation'
        elif any(keyword in message_lower for keyword in ['test:', 'testing']):
            return 'test'
        elif any(keyword in message_lower for keyword in ['refactor:', 'cleanup', 'clean']):
            return 'refactor'
        elif any(keyword in message_lower for keyword in ['config:', 'configure']):
            return 'configuration'
        elif 'phase' in message_lower and 'complete' in message_lower:
            return 'phase_completion'
        
        # File-based categorization
        if files:
            if any(f.startswith('evidence/') for f in files):
                return 'evidence'
            elif any(f.startswith('docs/') or f.endswith('.md') for f in files):
                return 'documentation'
            elif any(f.startswith(('test', 'tests/')) for f in files):
                return 'test'
            elif any(f.endswith(('.py', '.js', '.ts')) for f in files):
                return 'implementation'
        
        return 'other'
    
    def detect_phase_impact(self, commit_message: str, files: List[str]) -> Optional[str]:
        """Detect which phase this change impacts"""
        message_lower = commit_message.lower()
        
        # Direct phase mentions in commit message
        phase_match = re.search(r'phase\s+(\d+)', message_lower)
        if phase_match:
            return f"Phase {phase_match.group(1)}"
        
        # Phase detection from file paths
        for file_path in files:
            if file_path.startswith('evidence/phase'):
                phase_match = re.search(r'phase(\d+)', file_path)
                if phase_match:
                    return f"Phase {phase_match.group(1)}"
            elif file_path.startswith('phases/phase'):
                phase_match = re.search(r'phase(\d+)', file_path)
                if phase_match:
                    return f"Phase {phase_match.group(1)}"
        
        # Component/system impact detection
        if any(f.startswith(('autocoder/', 'blueprint_language/')) for f in files):
            return 'Core System'
        elif any(f.startswith('examples/') for f in files):
            return 'Examples'
        
        return None
    
    def get_change_summary(self, changes: List[GitChange]) -> Dict[str, Any]:
        """Generate summary of changes"""
        summary = {
            'total_commits': len(changes),
            'total_files_changed': sum(len(c.files_changed) for c in changes),
            'change_types': {},
            'phase_impacts': {},
            'authors': {},
            'timespan': None
        }
        
        if not changes:
            return summary
        
        # Count change types
        for change in changes:
            change_type = change.change_type
            summary['change_types'][change_type] = summary['change_types'].get(change_type, 0) + 1
        
        # Count phase impacts
        for change in changes:
            if change.phase_impact:
                phase = change.phase_impact
                summary['phase_impacts'][phase] = summary['phase_impacts'].get(phase, 0) + 1
        
        # Count authors
        for change in changes:
            author = change.author
            summary['authors'][author] = summary['authors'].get(author, 0) + 1
        
        # Calculate timespan
        if len(changes) > 1:
            dates = [c.date for c in changes]
            earliest = min(dates)
            latest = max(dates)
            summary['timespan'] = {
                'earliest': earliest.isoformat(),
                'latest': latest.isoformat(),
                'duration_hours': (latest - earliest).total_seconds() / 3600
            }
        
        return summary
    
    def filter_changes_by_type(self, changes: List[GitChange], change_type: str) -> List[GitChange]:
        """Filter changes by type"""
        return [c for c in changes if c.change_type == change_type]
    
    def filter_changes_by_phase(self, changes: List[GitChange], phase: str) -> List[GitChange]:
        """Filter changes by phase impact"""
        return [c for c in changes if c.phase_impact == phase]
    
    def get_phase_completion_changes(self, changes: List[GitChange]) -> List[GitChange]:
        """Get changes that indicate phase completions"""
        completion_changes = []
        
        for change in changes:
            message_lower = change.commit_message.lower()
            if (change.change_type == 'phase_completion' or
                ('phase' in message_lower and any(keyword in message_lower 
                 for keyword in ['complete', 'finish', 'done', '✅', 'pass']))):
                completion_changes.append(change)
        
        return completion_changes
    
    def get_documentation_impact_changes(self, changes: List[GitChange]) -> List[GitChange]:
        """Get changes that require documentation updates"""
        doc_impact_changes = []
        
        for change in changes:
            # Direct documentation changes
            if change.change_type == 'documentation':
                doc_impact_changes.append(change)
                continue
            
            # Changes that typically require doc updates
            if change.change_type in ['feature', 'phase_completion']:
                doc_impact_changes.append(change)
                continue
            
            # Changes to core system files
            if any(f.startswith(('autocoder/', 'blueprint_language/')) for f in change.files_changed):
                doc_impact_changes.append(change)
        
        return doc_impact_changes
    
    def export_changes_report(self, changes: List[GitChange], output_file: str):
        """Export changes to a detailed report"""
        summary = self.get_change_summary(changes)
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': summary,
            'changes': [
                {
                    'commit_hash': c.commit_hash,
                    'commit_message': c.commit_message,
                    'author': c.author,
                    'date': c.date.isoformat(),
                    'files_changed': c.files_changed,
                    'change_type': c.change_type,
                    'phase_impact': c.phase_impact
                }
                for c in changes
            ]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"Changes report exported to {output_file}")

# Example usage and testing
if __name__ == "__main__":
    monitor = GitChangeMonitor("/home/brian/autocoder3_cc")
    
    # Get changes from the last 7 days
    since_time = datetime.now() - timedelta(days=7)
    changes = monitor.get_changes_since(since_time)
    
    print(f"Found {len(changes)} changes in the last 7 days")
    
    # Generate summary
    summary = monitor.get_change_summary(changes)
    print("\nChange Summary:")
    print(json.dumps(summary, indent=2))
    
    # Show phase completion changes
    phase_completions = monitor.get_phase_completion_changes(changes)
    print(f"\nPhase completion changes: {len(phase_completions)}")
    for change in phase_completions:
        print(f"  - {change.commit_message} ({change.phase_impact})")
    
    # Export detailed report
    monitor.export_changes_report(changes, "git_changes_report.json")
    print("\nDetailed report exported to git_changes_report.json")