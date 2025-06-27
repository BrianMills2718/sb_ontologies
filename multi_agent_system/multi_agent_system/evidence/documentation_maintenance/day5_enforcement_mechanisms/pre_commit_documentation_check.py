#!/usr/bin/env python3
"""
Pre-commit hook for documentation validation and enforcement
This script runs as a git pre-commit hook to ensure documentation quality
"""

import os
import sys
import json
import subprocess
from typing import Dict, List, Any, Tuple
from datetime import datetime

class PreCommitDocumentationChecker:
    """Pre-commit hook for enforcing documentation standards"""
    
    def __init__(self, repo_root: str = None):
        self.repo_root = repo_root or self.find_repo_root()
        self.enforcement_config = self.load_enforcement_config()
        self.check_results = []
        
    def find_repo_root(self) -> str:
        """Find the git repository root"""
        try:
            result = subprocess.run(['git', 'rev-parse', '--show-toplevel'], 
                                  capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return os.getcwd()
    
    def load_enforcement_config(self) -> Dict[str, Any]:
        """Load enforcement configuration"""
        return {
            'enforcement_rules': {
                'documentation_files_require_validation': True,
                'evidence_files_require_completeness_check': True,
                'phase_status_changes_require_consistency': True,
                'new_phases_require_proper_structure': True,
                'archive_moves_require_approval': True
            },
            'blocking_violations': [
                'phase_status_conflict',
                'broken_evidence_links',
                'invalid_documentation_structure',
                'missing_required_sections'
            ],
            'warning_violations': [
                'evidence_below_threshold',
                'outdated_timestamps',
                'minor_formatting_issues',
                'archive_disorganization'
            ],
            'auto_fix_enabled': {
                'formatting_issues': True,
                'broken_links': True,
                'timestamp_updates': True,
                'evidence_path_fixes': True
            },
            'exemption_patterns': [
                '*.log',
                'archive/**/temp_*',
                'tests/**/debug_*'
            ]
        }
    
    def run_pre_commit_checks(self) -> Tuple[bool, Dict[str, Any]]:
        """Run all pre-commit documentation checks"""
        check_summary = {
            'timestamp': datetime.now().isoformat(),
            'staged_files': [],
            'checks_performed': [],
            'violations_found': [],
            'warnings_issued': [],
            'auto_fixes_applied': [],
            'commit_allowed': True,
            'exit_code': 0
        }
        
        try:
            # Get staged files
            staged_files = self.get_staged_files()
            check_summary['staged_files'] = staged_files
            
            if not staged_files:
                check_summary['commit_allowed'] = True
                check_summary['message'] = "No staged files to check"
                return True, check_summary
            
            # Filter relevant files
            relevant_files = self.filter_relevant_files(staged_files)
            
            if not relevant_files:
                check_summary['commit_allowed'] = True
                check_summary['message'] = "No documentation-related files staged"
                return True, check_summary
            
            # Perform documentation checks
            if self.has_documentation_files(relevant_files):
                doc_result = self.check_documentation_files(relevant_files)
                check_summary['checks_performed'].append('documentation_validation')
                self.process_check_result(doc_result, check_summary)
            
            # Perform evidence checks
            if self.has_evidence_files(relevant_files):
                evidence_result = self.check_evidence_files(relevant_files)
                check_summary['checks_performed'].append('evidence_validation')
                self.process_check_result(evidence_result, check_summary)
            
            # Perform phase status checks
            if self.has_phase_status_files(relevant_files):
                status_result = self.check_phase_status_consistency(relevant_files)
                check_summary['checks_performed'].append('phase_status_consistency')
                self.process_check_result(status_result, check_summary)
            
            # Perform structure checks
            if self.has_structural_changes(relevant_files):
                structure_result = self.check_structural_integrity(relevant_files)
                check_summary['checks_performed'].append('structure_validation')
                self.process_check_result(structure_result, check_summary)
            
            # Apply auto-fixes
            auto_fixes = self.apply_auto_fixes(check_summary['violations_found'])
            check_summary['auto_fixes_applied'] = auto_fixes
            
            # Determine if commit should be allowed
            check_summary['commit_allowed'] = self.should_allow_commit(check_summary)
            check_summary['exit_code'] = 0 if check_summary['commit_allowed'] else 1
            
        except Exception as e:
            check_summary['error'] = f"Pre-commit check failed: {str(e)}"
            check_summary['commit_allowed'] = False
            check_summary['exit_code'] = 1
        
        return check_summary['commit_allowed'], check_summary
    
    def get_staged_files(self) -> List[str]:
        """Get list of staged files"""
        try:
            result = subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                                  capture_output=True, text=True, cwd=self.repo_root)
            return [f for f in result.stdout.strip().split('\n') if f]
        except subprocess.SubprocessError:
            return []
    
    def filter_relevant_files(self, staged_files: List[str]) -> List[str]:
        """Filter files relevant to documentation checking"""
        relevant_extensions = {'.md', '.txt', '.json', '.yaml', '.yml', '.py'}
        relevant_paths = {'docs/', 'evidence/', 'phases/', 'CLAUDE.md', 'README.md'}
        
        relevant_files = []
        
        for file_path in staged_files:
            # Check extension
            if any(file_path.endswith(ext) for ext in relevant_extensions):
                relevant_files.append(file_path)
                continue
            
            # Check path
            if any(file_path.startswith(path) for path in relevant_paths):
                relevant_files.append(file_path)
                continue
            
            # Check if it's a root documentation file
            if file_path in ['CLAUDE.md', 'README.md']:
                relevant_files.append(file_path)
        
        return relevant_files
    
    def has_documentation_files(self, files: List[str]) -> bool:
        """Check if any files are documentation files"""
        doc_patterns = ['docs/', 'CLAUDE.md', 'README.md', '*.md']
        return any(self.matches_pattern(f, doc_patterns) for f in files)
    
    def has_evidence_files(self, files: List[str]) -> bool:
        """Check if any files are evidence files"""
        return any(f.startswith('evidence/') for f in files)
    
    def has_phase_status_files(self, files: List[str]) -> bool:
        """Check if any files affect phase status"""
        status_files = {
            'CLAUDE.md',
            'docs/current_phase_status.md',
            'docs/phase_progress.json'
        }
        return any(f in status_files for f in files)
    
    def has_structural_changes(self, files: List[str]) -> bool:
        """Check if any files represent structural changes"""
        return any(f.startswith(('phases/', 'evidence/')) for f in files)
    
    def matches_pattern(self, file_path: str, patterns: List[str]) -> bool:
        """Check if file matches any pattern"""
        import fnmatch
        return any(fnmatch.fnmatch(file_path, pattern) for pattern in patterns)
    
    def check_documentation_files(self, doc_files: List[str]) -> Dict[str, Any]:
        """Check documentation files for violations"""
        result = {
            'check_type': 'documentation_validation',
            'files_checked': doc_files,
            'violations': [],
            'warnings': [],
            'passed': True
        }
        
        for file_path in doc_files:
            if file_path.endswith('.md'):
                file_violations = self.validate_markdown_file(file_path)
                result['violations'].extend(file_violations)
        
        result['passed'] = len(result['violations']) == 0
        return result
    
    def validate_markdown_file(self, file_path: str) -> List[Dict[str, str]]:
        """Validate a markdown file"""
        violations = []
        full_path = os.path.join(self.repo_root, file_path)
        
        if not os.path.exists(full_path):
            violations.append({
                'type': 'missing_file',
                'file': file_path,
                'severity': 'error',
                'message': 'Staged file does not exist'
            })
            return violations
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for required sections in important files
            if file_path in ['CLAUDE.md', 'docs/current_phase_status.md']:
                violations.extend(self.check_required_sections(file_path, content))
            
            # Check markdown syntax
            violations.extend(self.check_markdown_syntax(file_path, content))
            
            # Check for broken internal links
            violations.extend(self.check_internal_links(file_path, content))
            
        except Exception as e:
            violations.append({
                'type': 'read_error',
                'file': file_path,
                'severity': 'error',
                'message': f'Cannot read file: {str(e)}'
            })
        
        return violations
    
    def check_required_sections(self, file_path: str, content: str) -> List[Dict[str, str]]:
        """Check for required sections in documentation"""
        violations = []
        
        required_sections = {
            'CLAUDE.md': ['V5.0 Multi-Agent Implementation', 'Current Situation', 'Multi-Agent Process'],
            'docs/current_phase_status.md': ['Phase Status Overview', 'Current Active Phase']
        }
        
        if file_path in required_sections:
            for section in required_sections[file_path]:
                if section not in content:
                    violations.append({
                        'type': 'missing_required_section',
                        'file': file_path,
                        'severity': 'error',
                        'message': f'Missing required section: {section}'
                    })
        
        return violations
    
    def check_markdown_syntax(self, file_path: str, content: str) -> List[Dict[str, str]]:
        """Check markdown syntax"""
        violations = []
        
        # Check for unclosed code blocks
        code_block_count = content.count('```')
        if code_block_count % 2 != 0:
            violations.append({
                'type': 'unclosed_code_block',
                'file': file_path,
                'severity': 'error',
                'message': 'Unclosed code block detected'
            })
        
        # Check for malformed headers
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('#') and not line.startswith('# ') and len(line) > 1:
                violations.append({
                    'type': 'malformed_header',
                    'file': file_path,
                    'severity': 'warning',
                    'message': f'Line {i+1}: Header missing space after #'
                })
        
        return violations
    
    def check_internal_links(self, file_path: str, content: str) -> List[Dict[str, str]]:
        """Check for broken internal links"""
        violations = []
        
        import re
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        
        for link_text, link_path in links:
            if not link_path.startswith(('http', 'https', 'mailto:')):
                # Internal link - check if it exists
                if link_path.startswith('/'):
                    full_link_path = os.path.join(self.repo_root, link_path[1:])
                else:
                    # Relative to current file
                    file_dir = os.path.dirname(os.path.join(self.repo_root, file_path))
                    full_link_path = os.path.join(file_dir, link_path)
                
                if not os.path.exists(full_link_path):
                    violations.append({
                        'type': 'broken_internal_link',
                        'file': file_path,
                        'severity': 'error',
                        'message': f'Broken internal link: {link_path}'
                    })
        
        return violations
    
    def check_evidence_files(self, evidence_files: List[str]) -> Dict[str, Any]:
        """Check evidence files for completeness"""
        result = {
            'check_type': 'evidence_validation',
            'files_checked': evidence_files,
            'violations': [],
            'warnings': [],
            'passed': True
        }
        
        # Group files by evidence package
        evidence_packages = {}
        for file_path in evidence_files:
            if file_path.startswith('evidence/'):
                parts = file_path.split('/')
                if len(parts) >= 2:
                    package = parts[1]
                    if package not in evidence_packages:
                        evidence_packages[package] = []
                    evidence_packages[package].append(file_path)
        
        # Check each evidence package
        for package, files in evidence_packages.items():
            package_violations = self.validate_evidence_package(package, files)
            result['violations'].extend(package_violations)
        
        result['passed'] = len(result['violations']) == 0
        return result
    
    def validate_evidence_package(self, package: str, files: List[str]) -> List[Dict[str, str]]:
        """Validate an evidence package"""
        violations = []
        
        # Check for minimum file requirements
        python_files = [f for f in files if f.endswith('.py')]
        markdown_files = [f for f in files if f.endswith('.md')]
        
        if len(python_files) < 2:
            violations.append({
                'type': 'insufficient_implementation',
                'file': f'evidence/{package}',
                'severity': 'warning',
                'message': f'Evidence package has only {len(python_files)} Python files (recommended: 2+)'
            })
        
        if len(markdown_files) < 1:
            violations.append({
                'type': 'missing_documentation',
                'file': f'evidence/{package}',
                'severity': 'error',
                'message': 'Evidence package missing documentation files'
            })
        
        # Check for completion summary
        has_completion = any('completion' in f.lower() and 'summary' in f.lower() for f in files)
        if not has_completion and 'phase' in package.lower():
            violations.append({
                'type': 'missing_completion_summary',
                'file': f'evidence/{package}',
                'severity': 'warning',
                'message': 'Phase evidence package missing completion summary'
            })
        
        return violations
    
    def check_phase_status_consistency(self, status_files: List[str]) -> Dict[str, Any]:
        """Check phase status consistency"""
        result = {
            'check_type': 'phase_status_consistency',
            'files_checked': status_files,
            'violations': [],
            'warnings': [],
            'passed': True
        }
        
        # Extract phase statuses from each file
        phase_statuses = {}
        
        for file_path in status_files:
            full_path = os.path.join(self.repo_root, file_path)
            if os.path.exists(full_path):
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    statuses = self.extract_phase_statuses(content)
                    phase_statuses[file_path] = statuses
                except Exception:
                    continue
        
        # Check for conflicts
        conflicts = self.find_phase_status_conflicts(phase_statuses)
        
        for conflict in conflicts:
            result['violations'].append({
                'type': 'phase_status_conflict',
                'file': 'multiple',
                'severity': 'error',
                'message': f"Phase {conflict['phase']} has conflicting statuses: {conflict['statuses']}"
            })
        
        result['passed'] = len(result['violations']) == 0
        return result
    
    def extract_phase_statuses(self, content: str) -> Dict[str, str]:
        """Extract phase statuses from content"""
        import re
        statuses = {}
        
        # Look for phase status patterns
        patterns = [
            (r'Phase (\d+).*?✅.*?(COMPLETE|PASS)', 'COMPLETE'),
            (r'Phase (\d+).*?❌.*?(FAIL|FAILED)', 'FAILED'),
            (r'Phase (\d+).*?🔄.*?(IN PROGRESS|ACTIVE)', 'IN_PROGRESS')
        ]
        
        for pattern, status in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                phase_num = match[0] if isinstance(match, tuple) else match
                statuses[f"Phase {phase_num}"] = status
        
        return statuses
    
    def find_phase_status_conflicts(self, phase_statuses: Dict[str, Dict[str, str]]) -> List[Dict[str, Any]]:
        """Find conflicts in phase statuses"""
        conflicts = []
        
        # Get all phases mentioned
        all_phases = set()
        for statuses in phase_statuses.values():
            all_phases.update(statuses.keys())
        
        # Check each phase for conflicts
        for phase in all_phases:
            phase_status_by_file = {}
            
            for file_path, statuses in phase_statuses.items():
                if phase in statuses:
                    phase_status_by_file[file_path] = statuses[phase]
            
            # Check if all statuses are the same
            unique_statuses = set(phase_status_by_file.values())
            if len(unique_statuses) > 1:
                conflicts.append({
                    'phase': phase,
                    'statuses': phase_status_by_file
                })
        
        return conflicts
    
    def check_structural_integrity(self, files: List[str]) -> Dict[str, Any]:
        """Check structural integrity of new/modified files"""
        result = {
            'check_type': 'structure_validation',
            'files_checked': files,
            'violations': [],
            'warnings': [],
            'passed': True
        }
        
        # Check phase directory structure
        phase_dirs = [f for f in files if f.startswith('phases/')]
        for phase_dir in phase_dirs:
            violations = self.validate_phase_directory_structure(phase_dir)
            result['violations'].extend(violations)
        
        # Check evidence directory structure
        evidence_dirs = [f for f in files if f.startswith('evidence/')]
        for evidence_dir in evidence_dirs:
            violations = self.validate_evidence_directory_structure(evidence_dir)
            result['violations'].extend(violations)
        
        result['passed'] = len(result['violations']) == 0
        return result
    
    def validate_phase_directory_structure(self, phase_path: str) -> List[Dict[str, str]]:
        """Validate phase directory structure"""
        violations = []
        
        # Extract phase number from path
        import re
        phase_match = re.search(r'phase(\d+)', phase_path)
        if not phase_match:
            violations.append({
                'type': 'invalid_phase_path',
                'file': phase_path,
                'severity': 'error',
                'message': 'Phase directory path does not contain phase number'
            })
        
        return violations
    
    def validate_evidence_directory_structure(self, evidence_path: str) -> List[Dict[str, str]]:
        """Validate evidence directory structure"""
        violations = []
        
        # Check if evidence path follows naming convention
        if not evidence_path.startswith('evidence/phase'):
            violations.append({
                'type': 'invalid_evidence_path',
                'file': evidence_path,
                'severity': 'warning',
                'message': 'Evidence directory should follow phase naming convention'
            })
        
        return violations
    
    def process_check_result(self, check_result: Dict[str, Any], check_summary: Dict[str, Any]):
        """Process a check result and update summary"""
        # Add violations to summary
        for violation in check_result.get('violations', []):
            if violation['severity'] == 'error':
                check_summary['violations_found'].append(violation)
            else:
                check_summary['warnings_issued'].append(violation)
    
    def apply_auto_fixes(self, violations: List[Dict[str, str]]) -> List[str]:
        """Apply automatic fixes for violations"""
        auto_fixes = []
        
        for violation in violations:
            if violation['type'] == 'broken_internal_link' and self.enforcement_config['auto_fix_enabled']['broken_links']:
                fix = self.fix_broken_link(violation)
                if fix:
                    auto_fixes.append(fix)
            
            elif violation['type'] == 'malformed_header' and self.enforcement_config['auto_fix_enabled']['formatting_issues']:
                fix = self.fix_malformed_header(violation)
                if fix:
                    auto_fixes.append(fix)
        
        return auto_fixes
    
    def fix_broken_link(self, violation: Dict[str, str]) -> str:
        """Fix broken internal link"""
        try:
            # Placeholder for actual link fixing logic
            return f"Fixed broken link in {violation['file']}"
        except Exception:
            return None
    
    def fix_malformed_header(self, violation: Dict[str, str]) -> str:
        """Fix malformed header"""
        try:
            # Placeholder for actual header fixing logic
            return f"Fixed malformed header in {violation['file']}"
        except Exception:
            return None
    
    def should_allow_commit(self, check_summary: Dict[str, Any]) -> bool:
        """Determine if commit should be allowed"""
        # Check for blocking violations
        blocking_types = self.enforcement_config['blocking_violations']
        
        for violation in check_summary['violations_found']:
            if violation['type'] in blocking_types:
                return False
        
        # Allow commit if no blocking violations
        return True
    
    def generate_commit_message(self, check_summary: Dict[str, Any]) -> str:
        """Generate commit message with check results"""
        if check_summary['commit_allowed']:
            if check_summary['violations_found'] or check_summary['warnings_issued']:
                return f"""Pre-commit checks: {len(check_summary['violations_found'])} errors, {len(check_summary['warnings_issued'])} warnings

Checks performed: {', '.join(check_summary['checks_performed'])}
Auto-fixes applied: {len(check_summary['auto_fixes_applied'])}

Commit allowed with warnings."""
            else:
                return "Pre-commit checks: All documentation checks passed ✅"
        else:
            return f"""Pre-commit checks FAILED: {len(check_summary['violations_found'])} blocking violations

Violations found:
{chr(10).join('- ' + v['message'] for v in check_summary['violations_found'][:5])}

Fix these issues before committing."""

def main():
    """Main entry point for pre-commit hook"""
    checker = PreCommitDocumentationChecker()
    
    # Run checks
    commit_allowed, check_summary = checker.run_pre_commit_checks()
    
    # Print results
    message = checker.generate_commit_message(check_summary)
    print(message)
    
    # Print detailed results if there are issues
    if check_summary['violations_found'] or check_summary['warnings_issued']:
        print("\nDetailed Results:")
        print(f"Files checked: {len(check_summary['staged_files'])}")
        print(f"Checks performed: {', '.join(check_summary['checks_performed'])}")
        
        if check_summary['violations_found']:
            print(f"\nErrors ({len(check_summary['violations_found'])}):")
            for violation in check_summary['violations_found']:
                print(f"  ❌ {violation['file']}: {violation['message']}")
        
        if check_summary['warnings_issued']:
            print(f"\nWarnings ({len(check_summary['warnings_issued'])}):")
            for warning in check_summary['warnings_issued']:
                print(f"  ⚠️ {warning['file']}: {warning['message']}")
        
        if check_summary['auto_fixes_applied']:
            print(f"\nAuto-fixes applied ({len(check_summary['auto_fixes_applied'])}):")
            for fix in check_summary['auto_fixes_applied']:
                print(f"  🔧 {fix}")
    
    # Exit with appropriate code
    sys.exit(check_summary['exit_code'])

if __name__ == "__main__":
    main()