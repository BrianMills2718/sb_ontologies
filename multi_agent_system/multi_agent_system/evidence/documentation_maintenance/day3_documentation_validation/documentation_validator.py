import os
import re
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path

class DocumentationValidator:
    """Comprehensive documentation validation framework"""
    
    def __init__(self, repo_root: str):
        self.repo_root = repo_root
        self.validation_rules = self.load_validation_rules()
        self.required_sections = self.get_required_sections()
        
    def load_validation_rules(self) -> Dict[str, Any]:
        """Load documentation validation rules"""
        return {
            'file_requirements': {
                'CLAUDE.md': {
                    'required_sections': ['V5.0 Multi-Agent Implementation', 'Current Situation', 'Multi-Agent Process'],
                    'required_patterns': [r'ACTIVE PHASE', r'STATUS:', r'Phase \d+'],
                    'max_age_days': 7
                },
                'docs/current_phase_status.md': {
                    'required_sections': ['Phase Status Overview', 'Current Active Phase'],
                    'required_patterns': [r'Phase \d+.*✅', r'Phase \d+.*🔄', r'evidence/'],
                    'max_age_days': 1
                },
                'docs/MULTI_AGENT_SYSTEM_GUIDE.md': {
                    'required_sections': ['Multi-Agent Process', 'How It Works', 'Success Rate'],
                    'required_patterns': [r'100%', r'external.*evaluation', r'isolated.*implementation'],
                    'max_age_days': 30
                }
            },
            'content_requirements': {
                'phase_status_consistency': True,
                'evidence_path_validation': True,
                'date_freshness_check': True,
                'cross_reference_validation': True,
                'markdown_syntax_validation': True
            },
            'structure_requirements': {
                'evidence_directory_structure': True,
                'phase_directory_structure': True,
                'documentation_completeness': True
            }
        }
    
    def get_required_sections(self) -> Dict[str, List[str]]:
        """Get required sections for different document types"""
        return {
            'phase_status': [
                'Phase Status Overview',
                'Current Active Phase', 
                'Completed Phases',
                'Evidence Locations'
            ],
            'implementation_guide': [
                'Objective',
                'Implementation Protocol',
                'Success Criteria',
                'Evidence Structure'
            ],
            'system_guide': [
                'Overview',
                'Process Description',
                'Usage Instructions',
                'Examples'
            ]
        }
    
    def validate_all_documentation(self) -> Dict[str, Any]:
        """Validate all documentation in the repository"""
        validation_results = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'UNKNOWN',
            'file_validations': {},
            'structure_validation': {},
            'content_validation': {},
            'summary': {
                'total_files_checked': 0,
                'files_passed': 0,
                'files_failed': 0,
                'critical_issues': 0,
                'warnings': 0
            }
        }
        
        # Validate individual files
        for file_path, requirements in self.validation_rules['file_requirements'].items():
            full_path = os.path.join(self.repo_root, file_path)
            validation_results['file_validations'][file_path] = self.validate_file(full_path, requirements)
            validation_results['summary']['total_files_checked'] += 1
        
        # Validate repository structure
        validation_results['structure_validation'] = self.validate_repository_structure()
        
        # Validate content consistency
        validation_results['content_validation'] = self.validate_content_consistency()
        
        # Calculate overall status
        validation_results = self.calculate_overall_status(validation_results)
        
        return validation_results
    
    def validate_file(self, file_path: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a single documentation file"""
        result = {
            'file_exists': os.path.exists(file_path),
            'file_readable': False,
            'file_age_days': None,
            'required_sections_check': {},
            'required_patterns_check': {},
            'markdown_syntax_check': {},
            'issues': [],
            'warnings': [],
            'status': 'UNKNOWN'
        }
        
        if not result['file_exists']:
            result['issues'].append(f"File does not exist: {file_path}")
            result['status'] = 'FAIL'
            return result
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            result['file_readable'] = True
            
            # Check file age
            file_stat = os.stat(file_path)
            file_age = (datetime.now().timestamp() - file_stat.st_mtime) / (24 * 3600)
            result['file_age_days'] = file_age
            
            if file_age > requirements.get('max_age_days', 30):
                result['warnings'].append(f"File is {file_age:.1f} days old (max: {requirements.get('max_age_days', 30)})")
            
            # Validate required sections
            result['required_sections_check'] = self.check_required_sections(
                content, requirements.get('required_sections', [])
            )
            
            # Validate required patterns
            result['required_patterns_check'] = self.check_required_patterns(
                content, requirements.get('required_patterns', [])
            )
            
            # Validate markdown syntax
            result['markdown_syntax_check'] = self.validate_markdown_syntax(content)
            
            # Determine status
            has_critical_issues = (
                len(result['issues']) > 0 or
                not all(result['required_sections_check'].values()) or
                not all(result['required_patterns_check'].values())
            )
            
            result['status'] = 'FAIL' if has_critical_issues else 'PASS'
            
        except Exception as e:
            result['issues'].append(f"Error reading file: {str(e)}")
            result['status'] = 'FAIL'
        
        return result
    
    def check_required_sections(self, content: str, required_sections: List[str]) -> Dict[str, bool]:
        """Check if required sections are present in content"""
        section_check = {}
        
        for section in required_sections:
            # Look for section headers (markdown H1, H2, H3)
            patterns = [
                rf'^#{1,3}\s+.*{re.escape(section)}.*$',
                rf'^\*\*{re.escape(section)}\*\*',
                rf'^{re.escape(section)}:?\s*$'
            ]
            
            found = False
            for pattern in patterns:
                if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                    found = True
                    break
            
            section_check[section] = found
        
        return section_check
    
    def check_required_patterns(self, content: str, required_patterns: List[str]) -> Dict[str, bool]:
        """Check if required patterns are present in content"""
        pattern_check = {}
        
        for pattern in required_patterns:
            try:
                found = bool(re.search(pattern, content, re.IGNORECASE))
                pattern_check[pattern] = found
            except re.error as e:
                pattern_check[pattern] = False
        
        return pattern_check
    
    def validate_markdown_syntax(self, content: str) -> Dict[str, Any]:
        """Validate markdown syntax"""
        syntax_check = {
            'has_broken_links': False,
            'has_malformed_headers': False,
            'has_unclosed_code_blocks': False,
            'broken_links': [],
            'malformed_headers': [],
            'issues': []
        }
        
        lines = content.split('\n')
        
        # Check for broken internal links
        for i, line in enumerate(lines):
            # Find markdown links [text](path)
            links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', line)
            for link_text, link_path in links:
                if link_path.startswith(('http', 'https', 'mailto:')):
                    continue  # Skip external links
                
                # Check if internal link exists
                if link_path.startswith('/'):
                    full_link_path = os.path.join(self.repo_root, link_path[1:])
                else:
                    full_link_path = os.path.join(self.repo_root, link_path)
                
                if not os.path.exists(full_link_path):
                    syntax_check['broken_links'].append(f"Line {i+1}: {link_path}")
        
        # Check for malformed headers
        for i, line in enumerate(lines):
            if line.startswith('#'):
                # Check for proper spacing after #
                if not re.match(r'^#+\s+', line):
                    syntax_check['malformed_headers'].append(f"Line {i+1}: Missing space after #")
        
        # Check for unclosed code blocks
        code_block_count = content.count('```')
        if code_block_count % 2 != 0:
            syntax_check['has_unclosed_code_blocks'] = True
            syntax_check['issues'].append("Unclosed code block detected")
        
        # Set flags
        syntax_check['has_broken_links'] = len(syntax_check['broken_links']) > 0
        syntax_check['has_malformed_headers'] = len(syntax_check['malformed_headers']) > 0
        
        return syntax_check
    
    def validate_repository_structure(self) -> Dict[str, Any]:
        """Validate overall repository structure"""
        structure_validation = {
            'evidence_structure': self.validate_evidence_structure(),
            'docs_structure': self.validate_docs_structure(),
            'phase_structure': self.validate_phase_structure(),
            'required_files': self.validate_required_files()
        }
        
        return structure_validation
    
    def validate_evidence_structure(self) -> Dict[str, Any]:
        """Validate evidence directory structure"""
        evidence_dir = os.path.join(self.repo_root, 'evidence')
        
        result = {
            'evidence_dir_exists': os.path.exists(evidence_dir),
            'phase_evidence_dirs': [],
            'missing_phase_evidence': [],
            'well_structured_phases': [],
            'issues': []
        }
        
        if not result['evidence_dir_exists']:
            result['issues'].append("Evidence directory does not exist")
            return result
        
        # Scan for phase evidence directories
        try:
            for item in os.listdir(evidence_dir):
                item_path = os.path.join(evidence_dir, item)
                if os.path.isdir(item_path) and 'phase' in item.lower():
                    result['phase_evidence_dirs'].append(item)
                    
                    # Check if well-structured
                    if self.is_well_structured_evidence_dir(item_path):
                        result['well_structured_phases'].append(item)
        except OSError as e:
            result['issues'].append(f"Error scanning evidence directory: {e}")
        
        return result
    
    def is_well_structured_evidence_dir(self, evidence_path: str) -> bool:
        """Check if evidence directory is well-structured"""
        try:
            items = os.listdir(evidence_path)
            
            # Look for expected structure indicators
            has_day_dirs = any('day' in item.lower() for item in items)
            has_python_files = any(item.endswith('.py') for item in items)
            has_md_files = any(item.endswith('.md') for item in items)
            has_completion_dir = any('completion' in item.lower() for item in items)
            
            return has_day_dirs or (has_python_files and has_md_files) or has_completion_dir
        except OSError:
            return False
    
    def validate_docs_structure(self) -> Dict[str, Any]:
        """Validate docs directory structure"""
        docs_dir = os.path.join(self.repo_root, 'docs')
        
        result = {
            'docs_dir_exists': os.path.exists(docs_dir),
            'required_docs_present': {},
            'docs_count': 0,
            'issues': []
        }
        
        required_docs = [
            'current_phase_status.md',
            'MULTI_AGENT_SYSTEM_GUIDE.md'
        ]
        
        if result['docs_dir_exists']:
            try:
                docs_files = [f for f in os.listdir(docs_dir) if f.endswith('.md')]
                result['docs_count'] = len(docs_files)
                
                for required_doc in required_docs:
                    doc_path = os.path.join(docs_dir, required_doc)
                    result['required_docs_present'][required_doc] = os.path.exists(doc_path)
            except OSError as e:
                result['issues'].append(f"Error scanning docs directory: {e}")
        else:
            result['issues'].append("Docs directory does not exist")
            for required_doc in required_docs:
                result['required_docs_present'][required_doc] = False
        
        return result
    
    def validate_phase_structure(self) -> Dict[str, Any]:
        """Validate phases directory structure"""
        phases_dir = os.path.join(self.repo_root, 'phases')
        
        result = {
            'phases_dir_exists': os.path.exists(phases_dir),
            'phase_dirs': [],
            'isolated_phases': [],
            'issues': []
        }
        
        if result['phases_dir_exists']:
            try:
                for item in os.listdir(phases_dir):
                    item_path = os.path.join(phases_dir, item)
                    if os.path.isdir(item_path) and 'phase' in item.lower():
                        result['phase_dirs'].append(item)
                        
                        # Check if isolated (has CLAUDE.md)
                        claude_md_path = os.path.join(item_path, 'CLAUDE.md')
                        if os.path.exists(claude_md_path):
                            result['isolated_phases'].append(item)
            except OSError as e:
                result['issues'].append(f"Error scanning phases directory: {e}")
        
        return result
    
    def validate_required_files(self) -> Dict[str, bool]:
        """Validate presence of required root files"""
        required_files = [
            'CLAUDE.md',
            'README.md'
        ]
        
        file_check = {}
        for required_file in required_files:
            file_path = os.path.join(self.repo_root, required_file)
            file_check[required_file] = os.path.exists(file_path)
        
        return file_check
    
    def validate_content_consistency(self) -> Dict[str, Any]:
        """Validate consistency across documentation files"""
        consistency_validation = {
            'phase_status_consistency': self.check_phase_status_consistency(),
            'evidence_path_consistency': self.check_evidence_path_consistency(),
            'date_consistency': self.check_date_consistency(),
            'cross_references': self.check_cross_references()
        }
        
        return consistency_validation
    
    def check_phase_status_consistency(self) -> Dict[str, Any]:
        """Check phase status consistency across files"""
        files_to_check = [
            'CLAUDE.md',
            'docs/current_phase_status.md'
        ]
        
        phase_statuses = {}
        
        for file_path in files_to_check:
            full_path = os.path.join(self.repo_root, file_path)
            if os.path.exists(full_path):
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extract phase statuses
                    statuses = self.extract_phase_statuses(content)
                    phase_statuses[file_path] = statuses
                except Exception as e:
                    phase_statuses[file_path] = {'error': str(e)}
        
        # Check for conflicts
        conflicts = self.find_status_conflicts(phase_statuses)
        
        return {
            'phase_statuses': phase_statuses,
            'conflicts': conflicts,
            'is_consistent': len(conflicts) == 0
        }
    
    def extract_phase_statuses(self, content: str) -> Dict[str, str]:
        """Extract phase status information from content"""
        statuses = {}
        
        # Look for various phase status patterns
        patterns = [
            (r'Phase (\d+).*?✅.*?(COMPLETE|PASS)', 'COMPLETE'),
            (r'Phase (\d+).*?🔄.*?(IN PROGRESS|ACTIVE)', 'IN_PROGRESS'),
            (r'Phase (\d+).*?❌.*?(FAIL|FAILED)', 'FAILED'),
            (r'Phase (\d+).*?⏳.*?PLANNED', 'PLANNED')
        ]
        
        for pattern, status in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                phase_num = match[0] if isinstance(match, tuple) else match
                statuses[f"Phase {phase_num}"] = status
        
        return statuses
    
    def find_status_conflicts(self, phase_statuses: Dict[str, Dict[str, str]]) -> List[Dict[str, Any]]:
        """Find conflicts in phase statuses across files"""
        conflicts = []
        
        # Get all unique phases
        all_phases = set()
        for statuses in phase_statuses.values():
            if 'error' not in statuses:
                all_phases.update(statuses.keys())
        
        # Check each phase for conflicts
        for phase in all_phases:
            phase_status_by_file = {}
            
            for file_path, statuses in phase_statuses.items():
                if 'error' not in statuses and phase in statuses:
                    phase_status_by_file[file_path] = statuses[phase]
            
            # Check if all statuses are the same
            unique_statuses = set(phase_status_by_file.values())
            if len(unique_statuses) > 1:
                conflicts.append({
                    'phase': phase,
                    'conflicting_statuses': phase_status_by_file
                })
        
        return conflicts
    
    def check_evidence_path_consistency(self) -> Dict[str, Any]:
        """Check consistency of evidence paths"""
        evidence_references = {}
        broken_paths = []
        
        # Scan documentation for evidence path references
        doc_files = [
            'CLAUDE.md',
            'docs/current_phase_status.md',
            'docs/MULTI_AGENT_SYSTEM_GUIDE.md'
        ]
        
        for doc_file in doc_files:
            full_path = os.path.join(self.repo_root, doc_file)
            if os.path.exists(full_path):
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Find evidence path references
                    evidence_paths = re.findall(r'evidence/[^\s\)]+', content)
                    evidence_references[doc_file] = evidence_paths
                    
                    # Check if paths exist
                    for evidence_path in evidence_paths:
                        # Clean up path (remove markdown artifacts)
                        clean_path = evidence_path.rstrip('`').rstrip('/')
                        full_evidence_path = os.path.join(self.repo_root, clean_path)
                        
                        if not os.path.exists(full_evidence_path):
                            broken_paths.append({
                                'referenced_in': doc_file,
                                'path': evidence_path,
                                'clean_path': clean_path
                            })
                except Exception as e:
                    evidence_references[doc_file] = {'error': str(e)}
        
        return {
            'evidence_references': evidence_references,
            'broken_paths': broken_paths,
            'all_paths_valid': len(broken_paths) == 0
        }
    
    def check_date_consistency(self) -> Dict[str, Any]:
        """Check date consistency and freshness"""
        date_info = {}
        
        # Check file modification dates vs content dates
        important_files = [
            'CLAUDE.md',
            'docs/current_phase_status.md'
        ]
        
        for file_path in important_files:
            full_path = os.path.join(self.repo_root, file_path)
            if os.path.exists(full_path):
                try:
                    # Get file modification time
                    file_stat = os.stat(full_path)
                    file_mod_time = datetime.fromtimestamp(file_stat.st_mtime)
                    
                    # Get dates mentioned in content
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    content_dates = re.findall(r'20\d{2}-\d{2}-\d{2}', content)
                    
                    date_info[file_path] = {
                        'file_modified': file_mod_time.isoformat(),
                        'content_dates': content_dates,
                        'file_age_days': (datetime.now() - file_mod_time).days
                    }
                except Exception as e:
                    date_info[file_path] = {'error': str(e)}
        
        return date_info
    
    def check_cross_references(self) -> Dict[str, Any]:
        """Check cross-references between documents"""
        cross_ref_info = {
            'internal_links': {},
            'broken_internal_links': [],
            'phase_references': {}
        }
        
        # Implementation would check internal links between docs
        # For now, return placeholder
        return cross_ref_info
    
    def calculate_overall_status(self, validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall validation status"""
        total_issues = 0
        total_warnings = 0
        files_passed = 0
        files_failed = 0
        
        # Count file validation results
        for file_path, file_result in validation_results['file_validations'].items():
            if file_result['status'] == 'PASS':
                files_passed += 1
            else:
                files_failed += 1
            
            total_issues += len(file_result.get('issues', []))
            total_warnings += len(file_result.get('warnings', []))
        
        # Update summary
        validation_results['summary'].update({
            'files_passed': files_passed,
            'files_failed': files_failed,
            'critical_issues': total_issues,
            'warnings': total_warnings
        })
        
        # Determine overall status
        if files_failed == 0 and total_issues == 0:
            validation_results['overall_status'] = 'PASS'
        elif total_issues > 0:
            validation_results['overall_status'] = 'FAIL'
        else:
            validation_results['overall_status'] = 'WARN'
        
        return validation_results
    
    def generate_validation_report(self, validation_results: Dict[str, Any]) -> str:
        """Generate human-readable validation report"""
        report = f"""# Documentation Validation Report
Generated: {validation_results['timestamp']}
Overall Status: {validation_results['overall_status']}

## Summary
- Total files checked: {validation_results['summary']['total_files_checked']}
- Files passed: {validation_results['summary']['files_passed']}
- Files failed: {validation_results['summary']['files_failed']}
- Critical issues: {validation_results['summary']['critical_issues']}
- Warnings: {validation_results['summary']['warnings']}

## File Validation Results
"""
        
        for file_path, file_result in validation_results['file_validations'].items():
            status_icon = '✅' if file_result['status'] == 'PASS' else '❌'
            report += f"\n### {status_icon} {file_path}\n"
            report += f"- Status: {file_result['status']}\n"
            report += f"- File exists: {file_result['file_exists']}\n"
            
            if file_result['file_age_days'] is not None:
                report += f"- File age: {file_result['file_age_days']:.1f} days\n"
            
            if file_result['issues']:
                report += f"- Issues: {len(file_result['issues'])}\n"
                for issue in file_result['issues']:
                    report += f"  - {issue}\n"
            
            if file_result['warnings']:
                report += f"- Warnings: {len(file_result['warnings'])}\n"
                for warning in file_result['warnings']:
                    report += f"  - {warning}\n"
        
        # Add structure validation
        report += "\n## Repository Structure Validation\n"
        structure = validation_results['structure_validation']
        
        if structure['evidence_structure']['evidence_dir_exists']:
            report += f"✅ Evidence directory exists\n"
            report += f"- Phase evidence directories: {len(structure['evidence_structure']['phase_evidence_dirs'])}\n"
            report += f"- Well-structured phases: {len(structure['evidence_structure']['well_structured_phases'])}\n"
        else:
            report += f"❌ Evidence directory missing\n"
        
        # Add consistency validation
        report += "\n## Content Consistency\n"
        consistency = validation_results['content_validation']
        
        if consistency['phase_status_consistency']['is_consistent']:
            report += "✅ Phase status is consistent across files\n"
        else:
            report += f"❌ Found {len(consistency['phase_status_consistency']['conflicts'])} phase status conflicts\n"
        
        if consistency['evidence_path_consistency']['all_paths_valid']:
            report += "✅ All evidence paths are valid\n"
        else:
            report += f"❌ Found {len(consistency['evidence_path_consistency']['broken_paths'])} broken evidence paths\n"
        
        return report

# Example usage and testing
if __name__ == "__main__":
    validator = DocumentationValidator("/home/brian/autocoder3_cc")
    results = validator.validate_all_documentation()
    
    # Generate report
    report = validator.generate_validation_report(results)
    
    # Save results
    with open("documentation_validation_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    with open("documentation_validation_report.md", "w") as f:
        f.write(report)
    
    print(f"Documentation validation complete.")
    print(f"Overall status: {results['overall_status']}")
    print(f"Files checked: {results['summary']['total_files_checked']}")
    print(f"Critical issues: {results['summary']['critical_issues']}")
    print(f"Warnings: {results['summary']['warnings']}")
    print("Detailed results saved to documentation_validation_results.json")
    print("Human-readable report saved to documentation_validation_report.md")