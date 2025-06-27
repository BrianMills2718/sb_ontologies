import subprocess
import json
import os
import re
from datetime import datetime
from typing import Dict, List, Any, Optional

class AutomatedStatusTracker:
    """Automated tracking of repository status and changes"""
    
    def __init__(self, repo_root: str):
        self.repo_root = repo_root
        self.status_file = os.path.join(repo_root, "docs/current_phase_status.md")
        self.tracking_log = os.path.join(repo_root, "docs/status_tracking.log")
        
    def detect_recent_changes(self, since_hours: int = 24) -> Dict[str, List[str]]:
        """Detect repository changes in the last N hours"""
        # Get git log for recent changes
        cmd = [
            "git", "log", 
            f"--since={since_hours} hours ago",
            "--name-only", 
            "--pretty=format:%H|%s|%an|%ad",
            "--date=iso"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.repo_root)
            return self.parse_git_changes(result.stdout)
        except subprocess.SubprocessError as e:
            print(f"Error running git command: {e}")
            return {}
    
    def parse_git_changes(self, git_output: str) -> Dict[str, List[str]]:
        """Parse git log output to categorize changes"""
        changes = {
            'phase_completions': [],
            'implementation_changes': [],
            'documentation_updates': [],
            'evidence_additions': [],
            'test_changes': [],
            'configuration_changes': []
        }
        
        if not git_output.strip():
            return changes
            
        lines = git_output.strip().split('\n')
        current_commit = None
        
        for line in lines:
            if '|' in line and len(line.split('|')) == 4:
                # Commit info line: hash|subject|author|date
                current_commit = line.split('|')
            elif line.strip() and current_commit:
                # File change line
                file_path = line.strip()
                self.categorize_file_change(file_path, current_commit[1], changes)
                
        return changes
    
    def categorize_file_change(self, file_path: str, commit_message: str, changes: Dict[str, List[str]]):
        """Categorize a file change based on path and commit message"""
        # Phase completion detection
        if any(keyword in commit_message.upper() for keyword in ["PHASE", "COMPLETE", "✅", "PASS"]):
            if "COMPLETE" in commit_message.upper() or "PASS" in commit_message.upper():
                changes['phase_completions'].append(f"{file_path}: {commit_message}")
        
        # File path categorization
        if file_path.startswith('evidence/'):
            changes['evidence_additions'].append(file_path)
        elif file_path.startswith(('docs/', 'CLAUDE.md', 'README.md')):
            changes['documentation_updates'].append(file_path)
        elif file_path.startswith(('autocoder/', 'blueprint_language/', 'components/')):
            changes['implementation_changes'].append(file_path)
        elif file_path.startswith(('test', 'tests/')):
            changes['test_changes'].append(file_path)
        elif file_path.endswith(('.yaml', '.yml', '.json', '.toml', '.ini')):
            changes['configuration_changes'].append(file_path)
    
    def detect_phase_transitions(self, changes: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Detect potential phase transitions from changes"""
        transitions = []
        
        # Look for phase completion indicators
        for completion in changes['phase_completions']:
            # Extract phase number from commit message
            phase_match = re.search(r'PHASE\s+(\d+)', completion, re.IGNORECASE)
            if phase_match:
                phase_num = phase_match.group(1)
                transitions.append({
                    'type': 'phase_completion',
                    'phase': f"Phase {phase_num}",
                    'evidence': completion,
                    'timestamp': datetime.now().isoformat()
                })
        
        # Look for new evidence directories
        for evidence_path in changes['evidence_additions']:
            if evidence_path.startswith('evidence/phase'):
                phase_match = re.search(r'evidence/phase(\d+)', evidence_path)
                if phase_match:
                    phase_num = phase_match.group(1)
                    transitions.append({
                        'type': 'evidence_addition',
                        'phase': f"Phase {phase_num}",
                        'evidence': evidence_path,
                        'timestamp': datetime.now().isoformat()
                    })
        
        return transitions
    
    def update_current_status_file(self, detected_changes: Dict[str, List[str]]):
        """Update the current status file based on detected changes"""
        transitions = self.detect_phase_transitions(detected_changes)
        
        if transitions:
            for transition in transitions:
                self.process_phase_transition(transition)
                
        # Always log the change detection
        self.add_status_update_entry(detected_changes, transitions)
    
    def process_phase_transition(self, transition: Dict[str, Any]):
        """Process detected phase transitions"""
        print(f"Processing {transition['type']}: {transition['phase']}")
        
        if transition['type'] == 'phase_completion':
            self.update_phase_status(transition['phase'], 'COMPLETE')
        elif transition['type'] == 'evidence_addition':
            self.update_phase_evidence(transition['phase'], transition['evidence'])
    
    def update_phase_status(self, phase: str, status: str):
        """Update phase status in the status file"""
        if not os.path.exists(self.status_file):
            print(f"Status file not found: {self.status_file}")
            return
            
        try:
            with open(self.status_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for existing phase status pattern
            phase_pattern = rf'(\*\*{re.escape(phase)}\*\*.*?)(\n|$)'
            match = re.search(phase_pattern, content, re.MULTILINE)
            
            if match:
                # Update existing phase status
                old_line = match.group(1)
                if status == 'COMPLETE':
                    new_line = f"**{phase}**: ✅ COMPLETE"
                elif status == 'IN_PROGRESS':
                    new_line = f"**{phase}**: 🔄 IN PROGRESS"
                else:
                    new_line = f"**{phase}**: {status}"
                    
                content = content.replace(old_line, new_line)
                
                with open(self.status_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                print(f"Updated {phase} status to {status}")
            else:
                print(f"Phase {phase} not found in status file")
                
        except Exception as e:
            print(f"Error updating status file: {e}")
    
    def update_phase_evidence(self, phase: str, evidence_path: str):
        """Update phase evidence location in documentation"""
        # This could update evidence references in documentation
        print(f"New evidence for {phase}: {evidence_path}")
    
    def add_status_update_entry(self, changes: Dict[str, List[str]], transitions: List[Dict[str, Any]]):
        """Add automated status update entry"""
        update_entry = f"""
================================================================================
Automated Status Update - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
================================================================================

Recent Changes Detected:
- Implementation changes: {len(changes['implementation_changes'])}
- Documentation updates: {len(changes['documentation_updates'])}
- Evidence additions: {len(changes['evidence_additions'])}
- Phase completions: {len(changes['phase_completions'])}
- Test changes: {len(changes['test_changes'])}
- Configuration changes: {len(changes['configuration_changes'])}

Phase Transitions Detected:
{json.dumps(transitions, indent=2) if transitions else "None"}

Change Details:
{json.dumps(changes, indent=2)}

"""
        
        # Append to tracking log
        try:
            with open(self.tracking_log, "a", encoding='utf-8') as f:
                f.write(update_entry)
            print(f"Status update logged to {self.tracking_log}")
        except Exception as e:
            print(f"Error writing to tracking log: {e}")
    
    def get_current_repository_status(self) -> Dict[str, Any]:
        """Get comprehensive current repository status"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'git_status': self.get_git_status(),
            'active_branch': self.get_current_branch(),
            'recent_commits': self.get_recent_commits(5),
            'evidence_directories': self.scan_evidence_directories(),
            'documentation_files': self.scan_documentation_files()
        }
        
        return status
    
    def get_git_status(self) -> Dict[str, Any]:
        """Get current git status"""
        try:
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, cwd=self.repo_root)
            
            modified_files = []
            added_files = []
            deleted_files = []
            
            for line in result.stdout.strip().split('\n'):
                if line:
                    status_code = line[:2]
                    filename = line[3:]
                    
                    if 'M' in status_code:
                        modified_files.append(filename)
                    elif 'A' in status_code:
                        added_files.append(filename)
                    elif 'D' in status_code:
                        deleted_files.append(filename)
            
            return {
                'modified': modified_files,
                'added': added_files,
                'deleted': deleted_files,
                'clean': len(modified_files + added_files + deleted_files) == 0
            }
        except subprocess.SubprocessError:
            return {'error': 'Unable to get git status'}
    
    def get_current_branch(self) -> str:
        """Get current git branch"""
        try:
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                  capture_output=True, text=True, cwd=self.repo_root)
            return result.stdout.strip()
        except subprocess.SubprocessError:
            return 'unknown'
    
    def get_recent_commits(self, count: int) -> List[Dict[str, str]]:
        """Get recent commits"""
        try:
            cmd = ['git', 'log', f'-{count}', '--pretty=format:%H|%s|%an|%ad', '--date=iso']
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.repo_root)
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('|')
                    if len(parts) == 4:
                        commits.append({
                            'hash': parts[0],
                            'subject': parts[1],
                            'author': parts[2],
                            'date': parts[3]
                        })
            
            return commits
        except subprocess.SubprocessError:
            return []
    
    def scan_evidence_directories(self) -> List[str]:
        """Scan for evidence directories"""
        evidence_dir = os.path.join(self.repo_root, 'evidence')
        if not os.path.exists(evidence_dir):
            return []
        
        try:
            return [d for d in os.listdir(evidence_dir) 
                   if os.path.isdir(os.path.join(evidence_dir, d))]
        except OSError:
            return []
    
    def scan_documentation_files(self) -> List[str]:
        """Scan for documentation files"""
        docs_files = []
        
        # Check root level docs
        for filename in ['CLAUDE.md', 'README.md']:
            if os.path.exists(os.path.join(self.repo_root, filename)):
                docs_files.append(filename)
        
        # Check docs directory
        docs_dir = os.path.join(self.repo_root, 'docs')
        if os.path.exists(docs_dir):
            try:
                for filename in os.listdir(docs_dir):
                    if filename.endswith('.md'):
                        docs_files.append(f"docs/{filename}")
            except OSError:
                pass
        
        return docs_files

# Example usage and testing
if __name__ == "__main__":
    tracker = AutomatedStatusTracker("/home/brian/autocoder3_cc")
    
    # Get current status
    current_status = tracker.get_current_repository_status()
    print("Current Repository Status:")
    print(json.dumps(current_status, indent=2))
    
    # Detect recent changes
    recent_changes = tracker.detect_recent_changes(24)
    print("\nRecent Changes (24 hours):")
    print(json.dumps(recent_changes, indent=2))
    
    # Update status based on changes
    tracker.update_current_status_file(recent_changes)
    print(f"\nStatus tracking complete. Check {tracker.tracking_log} for details.")