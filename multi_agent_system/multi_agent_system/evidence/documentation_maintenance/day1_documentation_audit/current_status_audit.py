import os
import re
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class DocumentationStatus:
    file_path: str
    last_modified: datetime
    current_phase_mentioned: str
    completion_status: Dict[str, str]
    inconsistencies: List[str]

class DocumentationAuditor:
    """Comprehensive documentation state analysis"""
    
    def __init__(self, repo_root: str):
        self.repo_root = repo_root
        self.status_files = [
            'docs/current_phase_status.md',
            'CLAUDE.md',
            'docs/repository_structure_analysis.md',
            'docs/V5_architecture_spec.md'
        ]
        
    def audit_all_documentation(self) -> Dict[str, DocumentationStatus]:
        """Audit all documentation files for consistency"""
        results = {}
        
        for file_path in self.status_files:
            full_path = os.path.join(self.repo_root, file_path)
            if os.path.exists(full_path):
                results[file_path] = self.audit_single_file(full_path)
            else:
                # Create placeholder for missing files
                results[file_path] = DocumentationStatus(
                    file_path=file_path,
                    last_modified=datetime.now(),
                    current_phase_mentioned="File Not Found",
                    completion_status={},
                    inconsistencies=[f"Critical file missing: {file_path}"]
                )
                
        return results
    
    def audit_single_file(self, file_path: str) -> DocumentationStatus:
        """Audit a single documentation file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract phase information
        current_phase = self.extract_current_phase(content)
        completion_status = self.extract_completion_status(content)
        inconsistencies = self.find_inconsistencies(content, file_path)
        
        return DocumentationStatus(
            file_path=file_path,
            last_modified=datetime.fromtimestamp(os.path.getmtime(file_path)),
            current_phase_mentioned=current_phase,
            completion_status=completion_status,
            inconsistencies=inconsistencies
        )
    
    def extract_current_phase(self, content: str) -> str:
        """Extract current phase from document content"""
        # Look for patterns like "Phase 5", "Current Phase", etc.
        patterns = [
            r'ACTIVE PHASE[:\s]+Phase (\d+)',
            r'Current Phase[:\s]+Phase (\d+)',
            r'Phase (\d+)[:\s]+.*(?:IN PROGRESS|CURRENT|ACTIVE)',
            r'ACTIVE PHASE[:\s]*\*\*[:\s]*Phase (\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return f"Phase {match.group(1)}"
                
        return "Unknown"
    
    def extract_completion_status(self, content: str) -> Dict[str, str]:
        """Extract phase completion status from content"""
        status_map = {}
        
        # Look for completion indicators
        phase_patterns = [
            (r'Phase (\d+).*?✅.*?COMPLETE', 'COMPLETE'),
            (r'Phase (\d+).*?🔄.*?IN PROGRESS', 'IN_PROGRESS'),
            (r'Phase (\d+).*?⏳.*?PLANNED', 'PLANNED'),
            (r'Phase (\d+).*?❌.*?FAIL', 'FAILED'),
            (r'Phase (\d+).*?PASS.*?✅', 'COMPLETE'),
            (r'Phase (\d+).*?100%.*?PASS', 'COMPLETE')
        ]
        
        for pattern, status in phase_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            for phase_num in matches:
                status_map[f"Phase {phase_num}"] = status
                
        return status_map
    
    def find_inconsistencies(self, content: str, file_path: str) -> List[str]:
        """Find potential inconsistencies in documentation"""
        inconsistencies = []
        
        # Check for conflicting phase status
        if "COMPLETE" in content and "IN PROGRESS" in content:
            # Check if they refer to different phases
            complete_phases = re.findall(r'Phase (\d+).*?(?:COMPLETE|✅)', content, re.IGNORECASE)
            progress_phases = re.findall(r'Phase (\d+).*?(?:IN PROGRESS|🔄)', content, re.IGNORECASE)
            
            overlap = set(complete_phases) & set(progress_phases)
            if overlap:
                inconsistencies.append(f"Phase {overlap} marked as both COMPLETE and IN PROGRESS")
            
        # Check for outdated information
        if "flask" in content.lower() and "harness" in content.lower():
            inconsistencies.append("References both Flask and Harness - may indicate outdated content")
            
        # Check for missing evidence references
        if "phase" in content.lower() and "evidence/" not in content:
            inconsistencies.append("Phase mentioned but no evidence location provided")
            
        # Check for dated timestamps
        old_dates = re.findall(r'20\d{2}-\d{2}-\d{2}', content)
        if old_dates:
            latest_date = max(old_dates)
            current_date = datetime.now().strftime('%Y-%m-%d')
            if latest_date < current_date:
                inconsistencies.append(f"Contains potentially outdated date: {latest_date}")
        
        # Check for broken phase references
        if "Phase 0" in content:
            inconsistencies.append("References Phase 0 which may be deprecated")
            
        return inconsistencies
    
    def generate_audit_report(self, audit_results: Dict[str, DocumentationStatus]) -> str:
        """Generate comprehensive audit report"""
        report = f"""# Documentation Audit Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
Total files audited: {len(audit_results)}

## Current Phase Consensus
"""
        
        # Analyze current phase consensus
        phase_mentions = {}
        for file_path, status in audit_results.items():
            phase = status.current_phase_mentioned
            if phase not in phase_mentions:
                phase_mentions[phase] = []
            phase_mentions[phase].append(file_path)
            
        for phase, files in phase_mentions.items():
            report += f"- {phase}: {', '.join(files)}\n"
            
        # Check for inconsistencies
        if len(phase_mentions) > 1:
            report += f"\n⚠️ **INCONSISTENCY**: Multiple phases mentioned as current!\n"
            
        # Detailed file analysis
        report += "\n## Detailed File Analysis\n\n"
        for file_path, status in audit_results.items():
            report += f"### {file_path}\n"
            report += f"- Last Modified: {status.last_modified}\n"
            report += f"- Current Phase: {status.current_phase_mentioned}\n"
            report += f"- Completion Status: {status.completion_status}\n"
            
            if status.inconsistencies:
                report += f"- **Inconsistencies Found**: {len(status.inconsistencies)}\n"
                for inconsistency in status.inconsistencies:
                    report += f"  - {inconsistency}\n"
            else:
                report += f"- **Status**: No inconsistencies detected\n"
            report += "\n"
            
        # Summary of all inconsistencies
        all_inconsistencies = []
        for status in audit_results.values():
            all_inconsistencies.extend(status.inconsistencies)
            
        if all_inconsistencies:
            report += f"## Critical Issues Found\n\n"
            report += f"Total inconsistencies: {len(all_inconsistencies)}\n\n"
            for i, issue in enumerate(all_inconsistencies, 1):
                report += f"{i}. {issue}\n"
        else:
            report += f"## Status: ✅ No Critical Issues Found\n"
            
        return report

# Example usage and testing
if __name__ == "__main__":
    auditor = DocumentationAuditor("/home/brian/autocoder3_cc")
    results = auditor.audit_all_documentation()
    report = auditor.generate_audit_report(results)
    
    with open("documentation_audit_report.md", "w") as f:
        f.write(report)
        
    print("Documentation audit complete. Report saved to documentation_audit_report.md")
    print(f"Files audited: {len(results)}")
    
    # Print summary
    for file_path, status in results.items():
        print(f"{file_path}: {status.current_phase_mentioned} ({len(status.inconsistencies)} issues)")