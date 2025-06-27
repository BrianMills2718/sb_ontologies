import os
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from git_change_monitor import GitChangeMonitor, GitChange

@dataclass
class PhaseProgress:
    phase_number: int
    phase_name: str
    status: str  # PLANNED, IN_PROGRESS, COMPLETE, FAILED
    start_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    evidence_path: Optional[str] = None
    key_commits: List[str] = None
    progress_percentage: float = 0.0
    
    def __post_init__(self):
        if self.key_commits is None:
            self.key_commits = []

class PhaseProgressTracker:
    """Track phase completion progress automatically based on git activity and evidence"""
    
    def __init__(self, repo_root: str):
        self.repo_root = repo_root
        self.git_monitor = GitChangeMonitor(repo_root)
        self.progress_file = os.path.join(repo_root, "docs/phase_progress.json")
        self.known_phases = self.discover_phases()
    
    def discover_phases(self) -> Dict[int, str]:
        """Discover phases from repository structure"""
        phases = {}
        
        # Check evidence directories
        evidence_dir = os.path.join(self.repo_root, 'evidence')
        if os.path.exists(evidence_dir):
            for item in os.listdir(evidence_dir):
                phase_match = re.search(r'phase(\d+)', item)
                if phase_match:
                    phase_num = int(phase_match.group(1))
                    phases[phase_num] = item
        
        # Check phases directory
        phases_dir = os.path.join(self.repo_root, 'phases')
        if os.path.exists(phases_dir):
            for item in os.listdir(phases_dir):
                phase_match = re.search(r'phase(\d+)', item)
                if phase_match:
                    phase_num = int(phase_match.group(1))
                    if phase_num not in phases:
                        phases[phase_num] = item
        
        # Standard phases if none found
        if not phases:
            phases = {
                1: "Architecture Foundation",
                2: "Component Library",
                3: "Blueprint Schema",
                4: "Validation Orchestrator",
                5: "Database Integration",
                6: "System Execution Harness",
                7: "Generation Pipeline"
            }
        
        return phases
    
    def load_progress(self) -> Dict[int, PhaseProgress]:
        """Load existing phase progress from file"""
        if not os.path.exists(self.progress_file):
            return self.initialize_progress()
        
        try:
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            progress = {}
            for phase_num_str, phase_data in data.items():
                phase_num = int(phase_num_str)
                
                # Convert datetime strings back to datetime objects
                start_date = None
                completion_date = None
                if phase_data.get('start_date'):
                    start_date = datetime.fromisoformat(phase_data['start_date'])
                if phase_data.get('completion_date'):
                    completion_date = datetime.fromisoformat(phase_data['completion_date'])
                
                progress[phase_num] = PhaseProgress(
                    phase_number=phase_num,
                    phase_name=phase_data['phase_name'],
                    status=phase_data['status'],
                    start_date=start_date,
                    completion_date=completion_date,
                    evidence_path=phase_data.get('evidence_path'),
                    key_commits=phase_data.get('key_commits', []),
                    progress_percentage=phase_data.get('progress_percentage', 0.0)
                )
            
            return progress
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error loading progress file: {e}")
            return self.initialize_progress()
    
    def initialize_progress(self) -> Dict[int, PhaseProgress]:
        """Initialize progress tracking for all known phases"""
        progress = {}
        
        for phase_num, phase_name in self.known_phases.items():
            progress[phase_num] = PhaseProgress(
                phase_number=phase_num,
                phase_name=phase_name,
                status='PLANNED'
            )
        
        return progress
    
    def save_progress(self, progress: Dict[int, PhaseProgress]):
        """Save progress to file"""
        # Convert to JSON-serializable format
        data = {}
        for phase_num, phase_progress in progress.items():
            phase_dict = asdict(phase_progress)
            
            # Convert datetime objects to ISO strings
            if phase_dict['start_date']:
                phase_dict['start_date'] = phase_progress.start_date.isoformat()
            if phase_dict['completion_date']:
                phase_dict['completion_date'] = phase_progress.completion_date.isoformat()
            
            data[str(phase_num)] = phase_dict
        
        try:
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving progress file: {e}")
    
    def update_progress_from_git(self, days_back: int = 30) -> Dict[int, PhaseProgress]:
        """Update phase progress based on git activity"""
        progress = self.load_progress()
        
        # Get recent git changes
        since_time = datetime.now() - timedelta(days=days_back)
        changes = self.git_monitor.get_changes_since(since_time)
        
        # Process changes for each phase
        for change in changes:
            affected_phases = self.get_affected_phases(change)
            
            for phase_num in affected_phases:
                if phase_num in progress:
                    self.update_phase_from_change(progress[phase_num], change)
        
        # Update progress percentages
        for phase_progress in progress.values():
            phase_progress.progress_percentage = self.calculate_phase_progress(phase_progress)
        
        # Save updated progress
        self.save_progress(progress)
        
        return progress
    
    def get_affected_phases(self, change: GitChange) -> List[int]:
        """Determine which phases are affected by a git change"""
        affected_phases = []
        
        # Direct phase impact from GitChange
        if change.phase_impact and change.phase_impact.startswith('Phase'):
            phase_match = re.search(r'Phase (\d+)', change.phase_impact)
            if phase_match:
                affected_phases.append(int(phase_match.group(1)))
        
        # Check file paths for phase indicators
        for file_path in change.files_changed:
            # Evidence directories
            if file_path.startswith('evidence/phase'):
                phase_match = re.search(r'phase(\d+)', file_path)
                if phase_match:
                    phase_num = int(phase_match.group(1))
                    if phase_num not in affected_phases:
                        affected_phases.append(phase_num)
            
            # Phases directories
            elif file_path.startswith('phases/phase'):
                phase_match = re.search(r'phase(\d+)', file_path)
                if phase_match:
                    phase_num = int(phase_match.group(1))
                    if phase_num not in affected_phases:
                        affected_phases.append(phase_num)
        
        return affected_phases
    
    def update_phase_from_change(self, phase_progress: PhaseProgress, change: GitChange):
        """Update a single phase progress from a git change"""
        # Track key commits
        if change.commit_hash not in phase_progress.key_commits:
            phase_progress.key_commits.append(change.commit_hash)
        
        # Update start date if this is the first activity
        if phase_progress.start_date is None:
            phase_progress.start_date = change.date
            if phase_progress.status == 'PLANNED':
                phase_progress.status = 'IN_PROGRESS'
        
        # Check for completion indicators
        if self.is_completion_change(change):
            phase_progress.completion_date = change.date
            phase_progress.status = 'COMPLETE'
        
        # Update evidence path
        evidence_path = self.extract_evidence_path(change, phase_progress.phase_number)
        if evidence_path:
            phase_progress.evidence_path = evidence_path
    
    def is_completion_change(self, change: GitChange) -> bool:
        """Check if a change indicates phase completion"""
        message_lower = change.commit_message.lower()
        
        completion_indicators = [
            'complete', 'completed', 'finish', 'finished', 'done',
            '✅', 'pass', 'success', 'final'
        ]
        
        phase_indicators = ['phase']
        
        return (any(indicator in message_lower for indicator in completion_indicators) and
                any(indicator in message_lower for indicator in phase_indicators))
    
    def extract_evidence_path(self, change: GitChange, phase_number: int) -> Optional[str]:
        """Extract evidence path from change files"""
        for file_path in change.files_changed:
            if (file_path.startswith('evidence/') and 
                f'phase{phase_number}' in file_path):
                # Return the evidence directory path
                parts = file_path.split('/')
                if len(parts) >= 2:
                    return f"evidence/{parts[1]}"
        
        return None
    
    def calculate_phase_progress(self, phase_progress: PhaseProgress) -> float:
        """Calculate phase progress percentage"""
        if phase_progress.status == 'COMPLETE':
            return 100.0
        elif phase_progress.status == 'FAILED':
            return 0.0
        elif phase_progress.status == 'PLANNED':
            return 0.0
        
        # IN_PROGRESS - estimate based on activity
        progress = 0.0
        
        # Base progress for being started
        progress += 10.0
        
        # Progress based on number of commits
        commit_count = len(phase_progress.key_commits)
        progress += min(commit_count * 5, 30)  # Up to 30% for commits
        
        # Progress based on evidence existence
        if phase_progress.evidence_path:
            evidence_full_path = os.path.join(self.repo_root, phase_progress.evidence_path)
            if os.path.exists(evidence_full_path):
                # Count files in evidence directory
                try:
                    file_count = sum(len(files) for _, _, files in os.walk(evidence_full_path))
                    progress += min(file_count * 2, 40)  # Up to 40% for evidence files
                except OSError:
                    pass
        
        # Progress based on time since start
        if phase_progress.start_date:
            days_active = (datetime.now() - phase_progress.start_date).days
            progress += min(days_active * 2, 20)  # Up to 20% for time
        
        return min(progress, 95.0)  # Never 100% unless explicitly complete
    
    def get_current_active_phase(self, progress: Dict[int, PhaseProgress]) -> Optional[PhaseProgress]:
        """Get the currently active phase"""
        # Look for IN_PROGRESS phases
        in_progress = [p for p in progress.values() if p.status == 'IN_PROGRESS']
        
        if in_progress:
            # Return the highest numbered in-progress phase
            return max(in_progress, key=lambda p: p.phase_number)
        
        # If no in-progress, return the highest completed phase + 1
        completed = [p for p in progress.values() if p.status == 'COMPLETE']
        if completed:
            max_completed = max(completed, key=lambda p: p.phase_number)
            next_phase_num = max_completed.phase_number + 1
            if next_phase_num in progress:
                return progress[next_phase_num]
        
        # Default to Phase 1 if nothing found
        return progress.get(1)
    
    def generate_progress_report(self, progress: Dict[int, PhaseProgress]) -> str:
        """Generate a progress report"""
        report = f"""# Phase Progress Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overall Progress
"""
        
        total_phases = len(progress)
        completed_phases = len([p for p in progress.values() if p.status == 'COMPLETE'])
        overall_progress = (completed_phases / total_phases) * 100 if total_phases > 0 else 0
        
        report += f"- Total Phases: {total_phases}\n"
        report += f"- Completed Phases: {completed_phases}\n"
        report += f"- Overall Progress: {overall_progress:.1f}%\n\n"
        
        # Current active phase
        active_phase = self.get_current_active_phase(progress)
        if active_phase:
            report += f"## Current Active Phase\n"
            report += f"**Phase {active_phase.phase_number}**: {active_phase.phase_name}\n"
            report += f"- Status: {active_phase.status}\n"
            report += f"- Progress: {active_phase.progress_percentage:.1f}%\n"
            if active_phase.evidence_path:
                report += f"- Evidence: {active_phase.evidence_path}\n"
            report += "\n"
        
        # Detailed phase breakdown
        report += "## Detailed Phase Status\n\n"
        
        for phase_num in sorted(progress.keys()):
            phase = progress[phase_num]
            status_icon = {
                'COMPLETE': '✅',
                'IN_PROGRESS': '🔄',
                'FAILED': '❌',
                'PLANNED': '⏳'
            }.get(phase.status, '❓')
            
            report += f"### {status_icon} Phase {phase.phase_number}: {phase.phase_name}\n"
            report += f"- Status: {phase.status}\n"
            report += f"- Progress: {phase.progress_percentage:.1f}%\n"
            
            if phase.start_date:
                report += f"- Started: {phase.start_date.strftime('%Y-%m-%d')}\n"
            if phase.completion_date:
                report += f"- Completed: {phase.completion_date.strftime('%Y-%m-%d')}\n"
            if phase.evidence_path:
                report += f"- Evidence: {phase.evidence_path}\n"
            
            report += f"- Key Commits: {len(phase.key_commits)}\n\n"
        
        return report
    
    def export_progress_data(self, output_file: str):
        """Export progress data for external use"""
        progress = self.update_progress_from_git()
        
        export_data = {
            'generated_at': datetime.now().isoformat(),
            'overall_stats': {
                'total_phases': len(progress),
                'completed_phases': len([p for p in progress.values() if p.status == 'COMPLETE']),
                'in_progress_phases': len([p for p in progress.values() if p.status == 'IN_PROGRESS']),
                'failed_phases': len([p for p in progress.values() if p.status == 'FAILED'])
            },
            'current_active_phase': None,
            'phases': {}
        }
        
        # Get current active phase
        active_phase = self.get_current_active_phase(progress)
        if active_phase:
            export_data['current_active_phase'] = active_phase.phase_number
        
        # Export phase data
        for phase_num, phase_progress in progress.items():
            phase_dict = asdict(phase_progress)
            if phase_dict['start_date']:
                phase_dict['start_date'] = phase_progress.start_date.isoformat()
            if phase_dict['completion_date']:
                phase_dict['completion_date'] = phase_progress.completion_date.isoformat()
            
            export_data['phases'][str(phase_num)] = phase_dict
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"Progress data exported to {output_file}")

# Example usage and testing
if __name__ == "__main__":
    tracker = PhaseProgressTracker("/home/brian/autocoder3_cc")
    
    # Update progress from git activity
    progress = tracker.update_progress_from_git(days_back=30)
    
    # Generate report
    report = tracker.generate_progress_report(progress)
    
    # Save report
    with open("phase_progress_report.md", "w", encoding='utf-8') as f:
        f.write(report)
    
    print("Phase progress tracking complete.")
    print(f"Tracked {len(progress)} phases")
    
    # Show current active phase
    active_phase = tracker.get_current_active_phase(progress)
    if active_phase:
        print(f"Current active phase: Phase {active_phase.phase_number} - {active_phase.phase_name}")
        print(f"Status: {active_phase.status} ({active_phase.progress_percentage:.1f}%)")
    
    # Export data
    tracker.export_progress_data("phase_progress_data.json")