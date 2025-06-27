import os
import re
from typing import Dict, List, Tuple, Any
from datetime import datetime
import json

class DocumentationConsistencyChecker:
    """Advanced consistency checking across all documentation files"""
    
    def __init__(self, repo_root: str):
        self.repo_root = repo_root
        self.critical_files = [
            'docs/current_phase_status.md',
            'CLAUDE.md',
            'docs/MULTI_AGENT_SYSTEM_GUIDE.md'
        ]
        
    def check_cross_file_consistency(self) -> Dict[str, Any]:
        """Check consistency across multiple documentation files"""
        results = {
            'phase_consistency': self.check_phase_consistency(),
            'status_consistency': self.check_status_consistency(),
            'evidence_path_consistency': self.check_evidence_paths(),
            'timeline_consistency': self.check_timeline_consistency(),
            'architecture_consistency': self.check_architecture_references()
        }
        
        return results
    
    def check_phase_consistency(self) -> Dict[str, Any]:
        """Check if all files agree on current phase"""
        phase_info = {}
        
        for file_path in self.critical_files:
            full_path = os.path.join(self.repo_root, file_path)
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract phase information
                current_phase = self.extract_current_phase(content)
                active_phases = self.extract_all_phase_statuses(content)
                
                phase_info[file_path] = {
                    'current_phase': current_phase,
                    'active_phases': active_phases,
                    'last_modified': datetime.fromtimestamp(os.path.getmtime(full_path))
                }
        
        # Analyze consistency
        current_phases = [info['current_phase'] for info in phase_info.values()]
        unique_phases = set(current_phases)
        
        consistency_result = {
            'files_checked': list(phase_info.keys()),
            'phase_mentions': phase_info,
            'unique_current_phases': list(unique_phases),
            'is_consistent': len(unique_phases) <= 1,
            'issues': []
        }
        
        if len(unique_phases) > 1:
            consistency_result['issues'].append(f"Multiple current phases found: {unique_phases}")
            
        return consistency_result
    
    def check_status_consistency(self) -> Dict[str, Any]:
        """Check if phase completion statuses are consistent"""
        status_info = {}
        
        for file_path in self.critical_files:
            full_path = os.path.join(self.repo_root, file_path)
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                phase_statuses = self.extract_phase_completion_statuses(content)
                status_info[file_path] = phase_statuses
        
        # Find conflicts
        conflicts = []
        all_phases = set()
        for statuses in status_info.values():
            all_phases.update(statuses.keys())
        
        for phase in all_phases:
            phase_statuses = {}
            for file_path, statuses in status_info.items():
                if phase in statuses:
                    phase_statuses[file_path] = statuses[phase]
            
            unique_statuses = set(phase_statuses.values())
            if len(unique_statuses) > 1:
                conflicts.append({
                    'phase': phase,
                    'conflicting_statuses': phase_statuses
                })
        
        return {
            'status_by_file': status_info,
            'conflicts': conflicts,
            'is_consistent': len(conflicts) == 0
        }
    
    def check_evidence_paths(self) -> Dict[str, Any]:
        """Check if evidence paths mentioned in docs actually exist"""
        evidence_references = {}
        missing_paths = []
        
        for file_path in self.critical_files:
            full_path = os.path.join(self.repo_root, file_path)
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find evidence path references
                evidence_paths = re.findall(r'evidence/[^\s\)]+', content)
                evidence_references[file_path] = evidence_paths
                
                # Check if paths exist
                for evidence_path in evidence_paths:
                    full_evidence_path = os.path.join(self.repo_root, evidence_path)
                    if not os.path.exists(full_evidence_path):
                        missing_paths.append({
                            'referenced_in': file_path,
                            'missing_path': evidence_path
                        })
        
        return {
            'evidence_references': evidence_references,
            'missing_paths': missing_paths,
            'all_paths_exist': len(missing_paths) == 0
        }
    
    def check_timeline_consistency(self) -> Dict[str, Any]:
        """Check if dates and timelines are consistent across files"""
        timeline_info = {}
        
        for file_path in self.critical_files:
            full_path = os.path.join(self.repo_root, file_path)
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract dates
                dates = re.findall(r'20\d{2}-\d{2}-\d{2}', content)
                phase_dates = re.findall(r'Phase \d+.*?20\d{2}-\d{2}-\d{2}', content)
                
                timeline_info[file_path] = {
                    'dates_found': dates,
                    'phase_dates': phase_dates,
                    'file_modified': datetime.fromtimestamp(os.path.getmtime(full_path)).strftime('%Y-%m-%d')
                }
        
        return {
            'timeline_by_file': timeline_info,
            'needs_review': any(len(info['dates_found']) > 0 for info in timeline_info.values())
        }
    
    def check_architecture_references(self) -> Dict[str, Any]:
        """Check consistency of architecture and system references"""
        architecture_terms = {}
        
        key_terms = [
            'harness', 'flask', 'multi-agent', 'blueprint', 
            'component', 'orchestrator', 'execution'
        ]
        
        for file_path in self.critical_files:
            full_path = os.path.join(self.repo_root, file_path)
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                
                term_counts = {}
                for term in key_terms:
                    term_counts[term] = content.count(term)
                
                architecture_terms[file_path] = term_counts
        
        # Check for potential conflicts (e.g., Flask vs Harness)
        conflicts = []
        for file_path, terms in architecture_terms.items():
            if terms.get('flask', 0) > 0 and terms.get('harness', 0) > 0:
                conflicts.append(f"{file_path}: References both Flask and Harness architectures")
        
        return {
            'architecture_terms': architecture_terms,
            'potential_conflicts': conflicts,
            'is_consistent': len(conflicts) == 0
        }
    
    def extract_current_phase(self, content: str) -> str:
        """Extract current phase from document content"""
        patterns = [
            r'ACTIVE PHASE[:\s]*\*\*[:\s]*Phase (\d+)',
            r'ACTIVE PHASE[:\s]+Phase (\d+)',
            r'Current Phase[:\s]+Phase (\d+)',
            r'Phase (\d+)[:\s]+.*(?:IN PROGRESS|CURRENT|ACTIVE)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return f"Phase {match.group(1)}"
                
        return "Unknown"
    
    def extract_all_phase_statuses(self, content: str) -> Dict[str, str]:
        """Extract all phase status information"""
        statuses = {}
        
        # Look for various phase status patterns
        patterns = [
            (r'Phase (\d+).*?✅.*?(?:COMPLETE|PASS)', 'COMPLETE'),
            (r'Phase (\d+).*?🔄.*?(?:IN PROGRESS|ACTIVE)', 'IN_PROGRESS'),
            (r'Phase (\d+).*?⏳.*?PLANNED', 'PLANNED'),
            (r'Phase (\d+).*?❌.*?(?:FAIL|FAILED)', 'FAILED')
        ]
        
        for pattern, status in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            for phase_num in matches:
                statuses[f"Phase {phase_num}"] = status
        
        return statuses
    
    def extract_phase_completion_statuses(self, content: str) -> Dict[str, str]:
        """Extract phase completion statuses more comprehensively"""
        return self.extract_all_phase_statuses(content)
    
    def generate_consistency_report(self, consistency_results: Dict[str, Any]) -> str:
        """Generate comprehensive consistency report"""
        report = f"""# Documentation Consistency Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary
"""
        
        # Overall consistency status
        issues_found = []
        if not consistency_results['phase_consistency']['is_consistent']:
            issues_found.append("Phase consistency issues")
        if not consistency_results['status_consistency']['is_consistent']:
            issues_found.append("Status consistency issues")
        if not consistency_results['evidence_path_consistency']['all_paths_exist']:
            issues_found.append("Missing evidence paths")
        if not consistency_results['architecture_consistency']['is_consistent']:
            issues_found.append("Architecture reference conflicts")
            
        if issues_found:
            report += f"❌ **Issues Found**: {', '.join(issues_found)}\n\n"
        else:
            report += f"✅ **All Consistency Checks Passed**\n\n"
        
        # Detailed results
        report += "## Phase Consistency Analysis\n"
        phase_result = consistency_results['phase_consistency']
        if phase_result['is_consistent']:
            report += "✅ All files agree on current phase\n"
        else:
            report += f"❌ Inconsistent current phases: {phase_result['unique_current_phases']}\n"
            for issue in phase_result['issues']:
                report += f"- {issue}\n"
        report += "\n"
        
        # Status consistency
        report += "## Status Consistency Analysis\n"
        status_result = consistency_results['status_consistency']
        if status_result['is_consistent']:
            report += "✅ Phase statuses are consistent across files\n"
        else:
            report += f"❌ Found {len(status_result['conflicts'])} status conflicts:\n"
            for conflict in status_result['conflicts']:
                report += f"- {conflict['phase']}: {conflict['conflicting_statuses']}\n"
        report += "\n"
        
        # Evidence paths
        report += "## Evidence Path Validation\n"
        evidence_result = consistency_results['evidence_path_consistency']
        if evidence_result['all_paths_exist']:
            report += "✅ All referenced evidence paths exist\n"
        else:
            report += f"❌ Found {len(evidence_result['missing_paths'])} missing evidence paths:\n"
            for missing in evidence_result['missing_paths']:
                report += f"- {missing['missing_path']} (referenced in {missing['referenced_in']})\n"
        report += "\n"
        
        # Architecture consistency
        report += "## Architecture Reference Consistency\n"
        arch_result = consistency_results['architecture_consistency']
        if arch_result['is_consistent']:
            report += "✅ Architecture references are consistent\n"
        else:
            report += f"❌ Found architecture conflicts:\n"
            for conflict in arch_result['potential_conflicts']:
                report += f"- {conflict}\n"
        
        return report

# Example usage and testing
if __name__ == "__main__":
    checker = DocumentationConsistencyChecker("/home/brian/autocoder3_cc")
    results = checker.check_cross_file_consistency()
    report = checker.generate_consistency_report(results)
    
    with open("consistency_check_report.md", "w") as f:
        f.write(report)
    
    print("Consistency check complete. Report saved to consistency_check_report.md")
    print(f"Results: {json.dumps(results, indent=2, default=str)}")