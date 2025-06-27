import os
import json
import subprocess
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

class PhaseCompletionValidator:
    """Validator that ensures phase completion meets all requirements before closure"""
    
    def __init__(self, repo_root: str):
        self.repo_root = repo_root
        self.validation_config = self.load_validation_config()
        
    def load_validation_config(self) -> Dict[str, Any]:
        """Load phase completion validation configuration"""
        return {
            'completion_requirements': {
                'evidence_package': {
                    'min_completeness_score': 0.85,
                    'required_sections': ['implementation', 'documentation', 'testing', 'completion'],
                    'required_files': {
                        'python_files': 5,
                        'markdown_files': 3,
                        'completion_summary': 1,
                        'external_evaluator_test': 1
                    }
                },
                'documentation_consistency': {
                    'phase_status_agreement': True,
                    'evidence_links_valid': True,
                    'completion_date_updated': True,
                    'next_phase_status_set': True
                },
                'implementation_quality': {
                    'executable_code': True,
                    'test_results_documented': True,
                    'integration_verified': True,
                    'performance_benchmarks': False  # Optional
                },
                'evaluation_compliance': {
                    'external_evaluation_completed': True,
                    'evaluation_result_documented': True,
                    'remediation_completed': True,  # If evaluation failed
                    'pass_criteria_met': True
                }
            },
            'validation_gates': {
                'gate_1_evidence': 'Evidence package completeness and quality',
                'gate_2_documentation': 'Documentation consistency and accuracy',
                'gate_3_implementation': 'Implementation quality and testing',
                'gate_4_evaluation': 'External evaluation compliance',
                'gate_5_integration': 'System integration readiness'
            },
            'enforcement_level': 'strict',  # strict, moderate, permissive
            'auto_remediation': True,
            'manual_override_allowed': False
        }
    
    def validate_phase_completion(self, phase_number: int, evaluation_result: str = None) -> Dict[str, Any]:
        """Validate that a phase is ready for completion"""
        validation_result = {
            'phase_number': phase_number,
            'evaluation_result': evaluation_result,
            'timestamp': datetime.now().isoformat(),
            'validation_gates': {},
            'overall_validation': 'UNKNOWN',
            'completion_allowed': False,
            'blocking_issues': [],
            'warnings': [],
            'recommendations': [],
            'remediation_steps': []
        }
        
        try:
            # Gate 1: Evidence Package Validation
            gate1_result = self.validate_evidence_package(phase_number)
            validation_result['validation_gates']['gate_1_evidence'] = gate1_result
            
            # Gate 2: Documentation Consistency
            gate2_result = self.validate_documentation_consistency(phase_number)
            validation_result['validation_gates']['gate_2_documentation'] = gate2_result
            
            # Gate 3: Implementation Quality
            gate3_result = self.validate_implementation_quality(phase_number)
            validation_result['validation_gates']['gate_3_implementation'] = gate3_result
            
            # Gate 4: Evaluation Compliance
            gate4_result = self.validate_evaluation_compliance(phase_number, evaluation_result)
            validation_result['validation_gates']['gate_4_evaluation'] = gate4_result
            
            # Gate 5: System Integration Readiness
            gate5_result = self.validate_integration_readiness(phase_number)
            validation_result['validation_gates']['gate_5_integration'] = gate5_result
            
            # Aggregate results
            validation_result = self.aggregate_validation_results(validation_result)
            
        except Exception as e:
            validation_result['error'] = f"Validation failed: {str(e)}"
            validation_result['overall_validation'] = 'ERROR'
            validation_result['completion_allowed'] = False
        
        return validation_result
    
    def validate_evidence_package(self, phase_number: int) -> Dict[str, Any]:
        """Validate evidence package for phase completion"""
        gate_result = {
            'gate_name': 'Evidence Package Validation',
            'status': 'UNKNOWN',
            'evidence_path': None,
            'completeness_score': 0.0,
            'required_files_check': {},
            'structure_validation': {},
            'issues': [],
            'passed': False
        }
        
        try:
            # Find evidence directory
            evidence_path = self.find_evidence_directory(phase_number)
            if not evidence_path:
                gate_result['issues'].append(f"No evidence directory found for Phase {phase_number}")
                gate_result['status'] = 'FAIL'
                return gate_result
            
            gate_result['evidence_path'] = evidence_path
            
            # Check evidence completeness
            completeness = self.check_evidence_completeness(evidence_path)
            gate_result['completeness_score'] = completeness['score']
            gate_result['required_files_check'] = completeness['file_requirements']
            gate_result['structure_validation'] = completeness['structure_check']
            
            # Validate against requirements
            requirements = self.validation_config['completion_requirements']['evidence_package']
            
            if gate_result['completeness_score'] < requirements['min_completeness_score']:
                gate_result['issues'].append(
                    f"Evidence completeness below threshold: {gate_result['completeness_score']:.1%} < {requirements['min_completeness_score']:.1%}"
                )
            
            # Check required file counts
            file_reqs = requirements['required_files']
            for file_type, min_count in file_reqs.items():
                actual_count = gate_result['required_files_check'].get(file_type, 0)
                if actual_count < min_count:
                    gate_result['issues'].append(
                        f"Insufficient {file_type}: {actual_count} < {min_count} required"
                    )
            
            # Determine gate status
            gate_result['passed'] = len(gate_result['issues']) == 0
            gate_result['status'] = 'PASS' if gate_result['passed'] else 'FAIL'
            
        except Exception as e:
            gate_result['issues'].append(f"Evidence validation error: {str(e)}")
            gate_result['status'] = 'ERROR'
        
        return gate_result
    
    def find_evidence_directory(self, phase_number: int) -> Optional[str]:
        """Find evidence directory for a phase"""
        evidence_base = os.path.join(self.repo_root, 'evidence')
        if not os.path.exists(evidence_base):
            return None
        
        # Look for phase evidence directories
        for item in os.listdir(evidence_base):
            if f'phase{phase_number}' in item.lower():
                return os.path.join(evidence_base, item)
        
        return None
    
    def check_evidence_completeness(self, evidence_path: str) -> Dict[str, Any]:
        """Check completeness of evidence package"""
        completeness = {
            'score': 0.0,
            'file_requirements': {
                'python_files': 0,
                'markdown_files': 0,
                'completion_summary': 0,
                'external_evaluator_test': 0
            },
            'structure_check': {
                'has_day_structure': False,
                'has_completion_dir': False,
                'total_files': 0
            }
        }
        
        try:
            # Count files and check structure
            total_files = 0
            day_dirs = 0
            
            for root, dirs, files in os.walk(evidence_path):
                total_files += len(files)
                
                # Check for day structure
                for dir_name in dirs:
                    if dir_name.startswith('day') and any(c.isdigit() for c in dir_name):
                        day_dirs += 1
                    if 'completion' in dir_name.lower():
                        completeness['structure_check']['has_completion_dir'] = True
                
                # Count file types
                for file in files:
                    if file.endswith('.py'):
                        completeness['file_requirements']['python_files'] += 1
                    elif file.endswith('.md'):
                        completeness['file_requirements']['markdown_files'] += 1
                    
                    if 'completion' in file.lower() and 'summary' in file.lower():
                        completeness['file_requirements']['completion_summary'] += 1
                    
                    if 'evaluator' in file.lower() and 'test' in file.lower():
                        completeness['file_requirements']['external_evaluator_test'] += 1
            
            completeness['structure_check']['has_day_structure'] = day_dirs >= 3
            completeness['structure_check']['total_files'] = total_files
            
            # Calculate score
            score = 0.0
            
            # Structure scoring (30%)
            if completeness['structure_check']['has_day_structure']:
                score += 0.15
            if completeness['structure_check']['has_completion_dir']:
                score += 0.15
            
            # File count scoring (50%)
            python_score = min(completeness['file_requirements']['python_files'] / 5, 1.0) * 0.2
            markdown_score = min(completeness['file_requirements']['markdown_files'] / 3, 1.0) * 0.15
            completion_score = min(completeness['file_requirements']['completion_summary'], 1.0) * 0.1
            evaluator_score = min(completeness['file_requirements']['external_evaluator_test'], 1.0) * 0.05
            
            score += python_score + markdown_score + completion_score + evaluator_score
            
            # File count bonus (20%)
            if total_files >= 10:
                score += 0.2
            elif total_files >= 5:
                score += 0.1
            
            completeness['score'] = min(score, 1.0)
            
        except Exception:
            pass
        
        return completeness
    
    def validate_documentation_consistency(self, phase_number: int) -> Dict[str, Any]:
        """Validate documentation consistency for phase completion"""
        gate_result = {
            'gate_name': 'Documentation Consistency',
            'status': 'UNKNOWN',
            'consistency_checks': {},
            'issues': [],
            'passed': False
        }
        
        try:
            # Check phase status agreement
            phase_status_check = self.check_phase_status_agreement(phase_number)
            gate_result['consistency_checks']['phase_status_agreement'] = phase_status_check
            
            # Check evidence links
            evidence_links_check = self.check_evidence_links_validity(phase_number)
            gate_result['consistency_checks']['evidence_links_valid'] = evidence_links_check
            
            # Check completion date
            completion_date_check = self.check_completion_date_updated(phase_number)
            gate_result['consistency_checks']['completion_date_updated'] = completion_date_check
            
            # Check next phase status
            next_phase_check = self.check_next_phase_status(phase_number)
            gate_result['consistency_checks']['next_phase_status_set'] = next_phase_check
            
            # Aggregate issues
            for check_name, check_result in gate_result['consistency_checks'].items():
                if not check_result.get('passed', False):
                    gate_result['issues'].extend(check_result.get('issues', []))
            
            gate_result['passed'] = len(gate_result['issues']) == 0
            gate_result['status'] = 'PASS' if gate_result['passed'] else 'FAIL'
            
        except Exception as e:
            gate_result['issues'].append(f"Documentation consistency error: {str(e)}")
            gate_result['status'] = 'ERROR'
        
        return gate_result
    
    def check_phase_status_agreement(self, phase_number: int) -> Dict[str, Any]:
        """Check if phase status is consistent across files"""
        check_result = {
            'passed': False,
            'phase_statuses': {},
            'conflicts': [],
            'issues': []
        }
        
        # Files to check
        status_files = [
            'CLAUDE.md',
            'docs/current_phase_status.md'
        ]
        
        for file_path in status_files:
            full_path = os.path.join(self.repo_root, file_path)
            if os.path.exists(full_path):
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extract phase status
                    phase_status = self.extract_phase_status(content, phase_number)
                    check_result['phase_statuses'][file_path] = phase_status
                    
                except Exception:
                    continue
        
        # Check for conflicts
        statuses = list(check_result['phase_statuses'].values())
        unique_statuses = set(s for s in statuses if s)
        
        if len(unique_statuses) > 1:
            check_result['conflicts'] = list(unique_statuses)
            check_result['issues'].append(f"Phase {phase_number} has conflicting statuses: {', '.join(unique_statuses)}")
        elif not unique_statuses:
            check_result['issues'].append(f"Phase {phase_number} status not found in documentation")
        
        check_result['passed'] = len(check_result['issues']) == 0
        return check_result
    
    def extract_phase_status(self, content: str, phase_number: int) -> str:
        """Extract phase status from content"""
        import re
        
        patterns = [
            (rf'Phase {phase_number}.*?✅.*?(COMPLETE|PASS)', 'COMPLETE'),
            (rf'Phase {phase_number}.*?❌.*?(FAIL|FAILED)', 'FAILED'),
            (rf'Phase {phase_number}.*?🔄.*?(IN PROGRESS|ACTIVE)', 'IN_PROGRESS')
        ]
        
        for pattern, status in patterns:
            if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
                return status
        
        return None
    
    def check_evidence_links_validity(self, phase_number: int) -> Dict[str, Any]:
        """Check if evidence links are valid"""
        check_result = {
            'passed': False,
            'evidence_references': [],
            'broken_links': [],
            'issues': []
        }
        
        # Find evidence references in documentation
        doc_files = ['CLAUDE.md', 'docs/current_phase_status.md']
        
        for doc_file in doc_files:
            doc_path = os.path.join(self.repo_root, doc_file)
            if os.path.exists(doc_path):
                try:
                    with open(doc_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Find evidence path references
                    import re
                    evidence_paths = re.findall(rf'evidence/[^\s\)]*phase{phase_number}[^\s\)]*', content)
                    check_result['evidence_references'].extend(evidence_paths)
                    
                except Exception:
                    continue
        
        # Check if referenced paths exist
        for evidence_path in set(check_result['evidence_references']):
            # Clean path
            clean_path = evidence_path.rstrip('`').rstrip('/')
            full_path = os.path.join(self.repo_root, clean_path)
            
            if not os.path.exists(full_path):
                check_result['broken_links'].append(evidence_path)
        
        if check_result['broken_links']:
            check_result['issues'].append(f"Broken evidence links: {', '.join(check_result['broken_links'])}")
        
        check_result['passed'] = len(check_result['broken_links']) == 0
        return check_result
    
    def check_completion_date_updated(self, phase_number: int) -> Dict[str, Any]:
        """Check if completion date is updated"""
        check_result = {
            'passed': False,
            'completion_dates_found': [],
            'issues': []
        }
        
        # Look for completion dates in documentation
        doc_files = ['CLAUDE.md', 'docs/current_phase_status.md']
        
        for doc_file in doc_files:
            doc_path = os.path.join(self.repo_root, doc_file)
            if os.path.exists(doc_path):
                try:
                    with open(doc_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Look for recent dates
                    import re
                    dates = re.findall(r'20\d{2}-\d{2}-\d{2}', content)
                    recent_dates = [d for d in dates if d >= '2025-06-20']  # Recent dates
                    check_result['completion_dates_found'].extend(recent_dates)
                    
                except Exception:
                    continue
        
        # Check if we have recent dates (indicating updates)
        if not check_result['completion_dates_found']:
            check_result['issues'].append("No recent completion dates found in documentation")
        
        check_result['passed'] = len(check_result['completion_dates_found']) > 0
        return check_result
    
    def check_next_phase_status(self, phase_number: int) -> Dict[str, Any]:
        """Check if next phase status is properly set"""
        check_result = {
            'passed': False,
            'next_phase_references': [],
            'issues': []
        }
        
        next_phase = phase_number + 1
        
        # Look for next phase references
        doc_files = ['CLAUDE.md', 'docs/current_phase_status.md']
        
        for doc_file in doc_files:
            doc_path = os.path.join(self.repo_root, doc_file)
            if os.path.exists(doc_path):
                try:
                    with open(doc_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Look for next phase references
                    import re
                    next_phase_refs = re.findall(rf'Phase {next_phase}[^\n]*', content)
                    check_result['next_phase_references'].extend(next_phase_refs)
                    
                except Exception:
                    continue
        
        if not check_result['next_phase_references']:
            check_result['issues'].append(f"No references to Phase {next_phase} found - next phase status not set")
        
        check_result['passed'] = len(check_result['next_phase_references']) > 0
        return check_result
    
    def validate_implementation_quality(self, phase_number: int) -> Dict[str, Any]:
        """Validate implementation quality for phase completion"""
        gate_result = {
            'gate_name': 'Implementation Quality',
            'status': 'UNKNOWN',
            'quality_checks': {},
            'issues': [],
            'passed': False
        }
        
        try:
            # Find evidence directory
            evidence_path = self.find_evidence_directory(phase_number)
            if not evidence_path:
                gate_result['issues'].append("No evidence directory found for implementation validation")
                gate_result['status'] = 'FAIL'
                return gate_result
            
            # Check for executable code
            executable_check = self.check_executable_code(evidence_path)
            gate_result['quality_checks']['executable_code'] = executable_check
            
            # Check for test results
            test_results_check = self.check_test_results_documented(evidence_path)
            gate_result['quality_checks']['test_results_documented'] = test_results_check
            
            # Check for integration verification
            integration_check = self.check_integration_verified(evidence_path)
            gate_result['quality_checks']['integration_verified'] = integration_check
            
            # Aggregate issues
            for check_name, check_result in gate_result['quality_checks'].items():
                if not check_result.get('passed', False):
                    gate_result['issues'].extend(check_result.get('issues', []))
            
            gate_result['passed'] = len(gate_result['issues']) == 0
            gate_result['status'] = 'PASS' if gate_result['passed'] else 'FAIL'
            
        except Exception as e:
            gate_result['issues'].append(f"Implementation quality validation error: {str(e)}")
            gate_result['status'] = 'ERROR'
        
        return gate_result
    
    def check_executable_code(self, evidence_path: str) -> Dict[str, Any]:
        """Check for executable code in evidence"""
        check_result = {
            'passed': False,
            'python_files': [],
            'executable_files': [],
            'issues': []
        }
        
        try:
            for root, dirs, files in os.walk(evidence_path):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        check_result['python_files'].append(file)
                        
                        # Check if file has executable code
                        if self.is_executable_code(file_path):
                            check_result['executable_files'].append(file)
            
            if len(check_result['executable_files']) < 3:
                check_result['issues'].append(f"Insufficient executable code files: {len(check_result['executable_files'])} < 3 required")
            
            check_result['passed'] = len(check_result['executable_files']) >= 3
            
        except Exception as e:
            check_result['issues'].append(f"Error checking executable code: {str(e)}")
        
        return check_result
    
    def is_executable_code(self, file_path: str) -> bool:
        """Check if a Python file contains executable code"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for implementation indicators
            indicators = [
                'def ', 'class ', 'if __name__ == "__main__"',
                'import ', 'from ', 'async def'
            ]
            
            return any(indicator in content for indicator in indicators) and len(content) > 200
            
        except Exception:
            return False
    
    def check_test_results_documented(self, evidence_path: str) -> Dict[str, Any]:
        """Check for documented test results"""
        check_result = {
            'passed': False,
            'result_files': [],
            'issues': []
        }
        
        result_patterns = ['result', 'output', 'test', 'demo', 'benchmark']
        
        try:
            for root, dirs, files in os.walk(evidence_path):
                for file in files:
                    if any(pattern in file.lower() for pattern in result_patterns):
                        if file.endswith(('.txt', '.md', '.json')):
                            check_result['result_files'].append(file)
            
            if len(check_result['result_files']) < 2:
                check_result['issues'].append("Insufficient test result documentation")
            
            check_result['passed'] = len(check_result['result_files']) >= 2
            
        except Exception as e:
            check_result['issues'].append(f"Error checking test results: {str(e)}")
        
        return check_result
    
    def check_integration_verified(self, evidence_path: str) -> Dict[str, Any]:
        """Check for integration verification"""
        check_result = {
            'passed': False,
            'integration_files': [],
            'issues': []
        }
        
        integration_patterns = ['integration', 'harness', 'system', 'workflow']
        
        try:
            for root, dirs, files in os.walk(evidence_path):
                for file in files:
                    if any(pattern in file.lower() for pattern in integration_patterns):
                        check_result['integration_files'].append(file)
            
            if len(check_result['integration_files']) < 1:
                check_result['issues'].append("No integration verification found")
            
            check_result['passed'] = len(check_result['integration_files']) >= 1
            
        except Exception as e:
            check_result['issues'].append(f"Error checking integration: {str(e)}")
        
        return check_result
    
    def validate_evaluation_compliance(self, phase_number: int, evaluation_result: str) -> Dict[str, Any]:
        """Validate evaluation compliance for phase completion"""
        gate_result = {
            'gate_name': 'Evaluation Compliance',
            'status': 'UNKNOWN',
            'evaluation_checks': {},
            'issues': [],
            'passed': False
        }
        
        try:
            # Check if evaluation was completed
            evaluation_completed_check = self.check_evaluation_completed(phase_number, evaluation_result)
            gate_result['evaluation_checks']['evaluation_completed'] = evaluation_completed_check
            
            # Check if evaluation result is documented
            result_documented_check = self.check_evaluation_result_documented(phase_number, evaluation_result)
            gate_result['evaluation_checks']['result_documented'] = result_documented_check
            
            # Check if pass criteria are met
            pass_criteria_check = self.check_pass_criteria_met(evaluation_result)
            gate_result['evaluation_checks']['pass_criteria_met'] = pass_criteria_check
            
            # Aggregate issues
            for check_name, check_result in gate_result['evaluation_checks'].items():
                if not check_result.get('passed', False):
                    gate_result['issues'].extend(check_result.get('issues', []))
            
            gate_result['passed'] = len(gate_result['issues']) == 0
            gate_result['status'] = 'PASS' if gate_result['passed'] else 'FAIL'
            
        except Exception as e:
            gate_result['issues'].append(f"Evaluation compliance error: {str(e)}")
            gate_result['status'] = 'ERROR'
        
        return gate_result
    
    def check_evaluation_completed(self, phase_number: int, evaluation_result: str) -> Dict[str, Any]:
        """Check if evaluation was completed"""
        check_result = {
            'passed': False,
            'evaluation_evidence': [],
            'issues': []
        }
        
        if not evaluation_result:
            check_result['issues'].append("No evaluation result provided")
            return check_result
        
        # Look for evaluation evidence
        evidence_path = self.find_evidence_directory(phase_number)
        if evidence_path:
            try:
                for root, dirs, files in os.walk(evidence_path):
                    for file in files:
                        if 'evaluator' in file.lower() or 'evaluation' in file.lower():
                            check_result['evaluation_evidence'].append(file)
            except Exception:
                pass
        
        if not check_result['evaluation_evidence']:
            check_result['issues'].append("No evaluation evidence found in evidence package")
        
        check_result['passed'] = len(check_result['evaluation_evidence']) > 0 and evaluation_result is not None
        return check_result
    
    def check_evaluation_result_documented(self, phase_number: int, evaluation_result: str) -> Dict[str, Any]:
        """Check if evaluation result is documented"""
        check_result = {
            'passed': False,
            'documentation_locations': [],
            'issues': []
        }
        
        if not evaluation_result:
            check_result['issues'].append("No evaluation result to document")
            return check_result
        
        # Check if result is documented in status files
        status_files = ['CLAUDE.md', 'docs/current_phase_status.md']
        
        for status_file in status_files:
            file_path = os.path.join(self.repo_root, status_file)
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Look for evaluation result
                    if evaluation_result.upper() in content.upper():
                        check_result['documentation_locations'].append(status_file)
                        
                except Exception:
                    continue
        
        if not check_result['documentation_locations']:
            check_result['issues'].append(f"Evaluation result '{evaluation_result}' not documented in status files")
        
        check_result['passed'] = len(check_result['documentation_locations']) > 0
        return check_result
    
    def check_pass_criteria_met(self, evaluation_result: str) -> Dict[str, Any]:
        """Check if pass criteria are met"""
        check_result = {
            'passed': False,
            'evaluation_result': evaluation_result,
            'issues': []
        }
        
        if not evaluation_result:
            check_result['issues'].append("No evaluation result provided")
            return check_result
        
        # Check if evaluation passed
        pass_indicators = ['PASS', 'COMPLETE', 'SUCCESS', '100%']
        
        if not any(indicator in evaluation_result.upper() for indicator in pass_indicators):
            check_result['issues'].append(f"Evaluation result '{evaluation_result}' does not indicate passing")
        else:
            check_result['passed'] = True
        
        return check_result
    
    def validate_integration_readiness(self, phase_number: int) -> Dict[str, Any]:
        """Validate system integration readiness"""
        gate_result = {
            'gate_name': 'System Integration Readiness',
            'status': 'UNKNOWN',
            'readiness_checks': {},
            'issues': [],
            'passed': False
        }
        
        try:
            # Check if next phase exists
            next_phase_check = self.check_next_phase_exists(phase_number + 1)
            gate_result['readiness_checks']['next_phase_exists'] = next_phase_check
            
            # Check system compatibility
            compatibility_check = self.check_system_compatibility(phase_number)
            gate_result['readiness_checks']['system_compatibility'] = compatibility_check
            
            # Check integration points
            integration_points_check = self.check_integration_points(phase_number)
            gate_result['readiness_checks']['integration_points'] = integration_points_check
            
            # Aggregate issues
            for check_name, check_result in gate_result['readiness_checks'].items():
                if not check_result.get('passed', False):
                    gate_result['issues'].extend(check_result.get('issues', []))
            
            gate_result['passed'] = len(gate_result['issues']) == 0
            gate_result['status'] = 'PASS' if gate_result['passed'] else 'FAIL'
            
        except Exception as e:
            gate_result['issues'].append(f"Integration readiness error: {str(e)}")
            gate_result['status'] = 'ERROR'
        
        return gate_result
    
    def check_next_phase_exists(self, next_phase_number: int) -> Dict[str, Any]:
        """Check if next phase exists and is ready"""
        check_result = {
            'passed': False,
            'next_phase_path': None,
            'issues': []
        }
        
        # Look for next phase directory
        phases_dir = os.path.join(self.repo_root, 'phases')
        if os.path.exists(phases_dir):
            for item in os.listdir(phases_dir):
                if f'phase{next_phase_number}' in item.lower():
                    check_result['next_phase_path'] = os.path.join(phases_dir, item)
                    check_result['passed'] = True
                    break
        
        if not check_result['passed']:
            check_result['issues'].append(f"Phase {next_phase_number} directory not found")
        
        return check_result
    
    def check_system_compatibility(self, phase_number: int) -> Dict[str, Any]:
        """Check system compatibility"""
        check_result = {
            'passed': True,  # Default to pass for now
            'compatibility_issues': [],
            'issues': []
        }
        
        # Placeholder for actual compatibility checks
        # This would check things like:
        # - Dependencies compatibility
        # - API compatibility
        # - Data format compatibility
        
        return check_result
    
    def check_integration_points(self, phase_number: int) -> Dict[str, Any]:
        """Check integration points"""
        check_result = {
            'passed': True,  # Default to pass for now
            'integration_points': [],
            'issues': []
        }
        
        # Placeholder for actual integration point checks
        # This would check things like:
        # - Multi-agent workflow integration
        # - Documentation maintenance integration
        # - Evidence handling integration
        
        return check_result
    
    def aggregate_validation_results(self, validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate validation results from all gates"""
        gates = validation_result['validation_gates']
        
        # Count gate results
        passed_gates = sum(1 for gate in gates.values() if gate.get('passed', False))
        total_gates = len(gates)
        
        # Collect all issues
        all_issues = []
        for gate in gates.values():
            all_issues.extend(gate.get('issues', []))
        
        validation_result['blocking_issues'] = all_issues
        
        # Determine overall validation result
        if passed_gates == total_gates:
            validation_result['overall_validation'] = 'PASS'
            validation_result['completion_allowed'] = True
        elif passed_gates >= total_gates * 0.8:  # 80% threshold for moderate enforcement
            if self.validation_config['enforcement_level'] == 'strict':
                validation_result['overall_validation'] = 'FAIL'
                validation_result['completion_allowed'] = False
            else:
                validation_result['overall_validation'] = 'PASS_WITH_WARNINGS'
                validation_result['completion_allowed'] = True
        else:
            validation_result['overall_validation'] = 'FAIL'
            validation_result['completion_allowed'] = False
        
        # Generate recommendations
        validation_result['recommendations'] = self.generate_completion_recommendations(validation_result)
        
        return validation_result
    
    def generate_completion_recommendations(self, validation_result: Dict[str, Any]) -> List[str]:
        """Generate recommendations for phase completion"""
        recommendations = []
        
        for gate_name, gate_result in validation_result['validation_gates'].items():
            if not gate_result.get('passed', False):
                if 'evidence' in gate_name.lower():
                    recommendations.append("Complete evidence package with missing implementation and documentation")
                elif 'documentation' in gate_name.lower():
                    recommendations.append("Fix documentation consistency issues and update phase status")
                elif 'implementation' in gate_name.lower():
                    recommendations.append("Improve implementation quality with more executable code and test results")
                elif 'evaluation' in gate_name.lower():
                    recommendations.append("Complete external evaluation and document results properly")
                elif 'integration' in gate_name.lower():
                    recommendations.append("Verify system integration readiness and next phase preparation")
        
        return recommendations

# Example usage and testing
if __name__ == "__main__":
    validator = PhaseCompletionValidator("/home/brian/autocoder3_cc")
    
    # Test validation for Phase 5
    test_phase = 5
    test_evaluation_result = "PASS"
    
    print(f"Validating Phase {test_phase} completion...")
    
    validation_result = validator.validate_phase_completion(test_phase, test_evaluation_result)
    
    print(f"Overall Validation: {validation_result['overall_validation']}")
    print(f"Completion Allowed: {validation_result['completion_allowed']}")
    
    # Show gate results
    print("\nValidation Gates:")
    for gate_name, gate_result in validation_result['validation_gates'].items():
        status = gate_result.get('status', 'UNKNOWN')
        status_icon = '✅' if status == 'PASS' else '❌' if status == 'FAIL' else '❓'
        print(f"  {status_icon} {gate_result.get('gate_name', gate_name)}: {status}")
    
    # Show issues
    if validation_result['blocking_issues']:
        print(f"\nBlocking Issues ({len(validation_result['blocking_issues'])}):")
        for issue in validation_result['blocking_issues']:
            print(f"  - {issue}")
    
    # Show recommendations
    if validation_result['recommendations']:
        print(f"\nRecommendations ({len(validation_result['recommendations'])}):")
        for rec in validation_result['recommendations']:
            print(f"  - {rec}")
    
    # Save results
    with open("phase_completion_validation_results.json", "w") as f:
        json.dump(validation_result, f, indent=2)
    
    print(f"\nValidation complete. Results saved to phase_completion_validation_results.json")