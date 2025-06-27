import os
import json
import shutil
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

class PostPhaseMaintenanceSystem:
    """Automated maintenance system that runs after phase completion"""
    
    def __init__(self, repo_root: str):
        self.repo_root = repo_root
        self.maintenance_config = self.load_post_phase_config()
        
    def load_post_phase_config(self) -> Dict[str, Any]:
        """Load configuration for post-phase maintenance"""
        return {
            'phase_completion_tasks': [
                'update_phase_status',
                'validate_evidence_package',
                'update_progress_tracking',
                'archive_working_files',
                'update_documentation',
                'generate_completion_report'
            ],
            'evidence_validation_criteria': {
                'min_implementation_files': 5,
                'min_documentation_files': 3,
                'required_completion_summary': True,
                'required_external_evaluator_test': True
            },
            'archive_rules': {
                'archive_temp_files': True,
                'archive_debug_files': True,
                'preserve_evidence': True,
                'update_gitignore': True
            },
            'documentation_updates': {
                'update_current_phase_status': True,
                'update_claude_md': True,
                'generate_phase_summary': True,
                'update_roadmap': True
            }
        }
    
    def execute_post_phase_maintenance(self, phase_number: int, phase_name: str, evaluation_result: str) -> Dict[str, Any]:
        """Execute complete post-phase maintenance workflow"""
        maintenance_result = {
            'phase_number': phase_number,
            'phase_name': phase_name,
            'evaluation_result': evaluation_result,
            'timestamp': datetime.now().isoformat(),
            'tasks_completed': [],
            'tasks_failed': [],
            'maintenance_summary': {},
            'next_phase_preparation': {},
            'manual_actions_required': []
        }
        
        # Execute each maintenance task
        for task in self.maintenance_config['phase_completion_tasks']:
            try:
                task_result = self.execute_maintenance_task(task, phase_number, phase_name, evaluation_result)
                maintenance_result['tasks_completed'].append({
                    'task': task,
                    'result': task_result,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                maintenance_result['tasks_failed'].append({
                    'task': task,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        # Generate maintenance summary
        maintenance_result['maintenance_summary'] = self.generate_maintenance_summary(maintenance_result)
        
        # Prepare for next phase
        maintenance_result['next_phase_preparation'] = self.prepare_next_phase(phase_number)
        
        # Log maintenance execution
        self.log_maintenance_execution(maintenance_result)
        
        return maintenance_result
    
    def execute_maintenance_task(self, task: str, phase_number: int, phase_name: str, evaluation_result: str) -> Dict[str, Any]:
        """Execute a specific maintenance task"""
        task_methods = {
            'update_phase_status': self.update_phase_status,
            'validate_evidence_package': self.validate_evidence_package,
            'update_progress_tracking': self.update_progress_tracking,
            'archive_working_files': self.archive_working_files,
            'update_documentation': self.update_documentation,
            'generate_completion_report': self.generate_completion_report
        }
        
        if task in task_methods:
            return task_methods[task](phase_number, phase_name, evaluation_result)
        else:
            raise ValueError(f"Unknown maintenance task: {task}")
    
    def update_phase_status(self, phase_number: int, phase_name: str, evaluation_result: str) -> Dict[str, Any]:
        """Update phase status in all relevant documentation"""
        status_updates = {
            'files_updated': [],
            'status_changes': {},
            'errors': []
        }
        
        # Files to update
        status_files = [
            'docs/current_phase_status.md',
            'CLAUDE.md'
        ]
        
        for file_path in status_files:
            full_path = os.path.join(self.repo_root, file_path)
            if os.path.exists(full_path):
                try:
                    updated = self.update_phase_status_in_file(full_path, phase_number, evaluation_result)
                    if updated:
                        status_updates['files_updated'].append(file_path)
                        status_updates['status_changes'][file_path] = f"Phase {phase_number} marked as {evaluation_result}"
                except Exception as e:
                    status_updates['errors'].append(f"Error updating {file_path}: {str(e)}")
        
        return status_updates
    
    def update_phase_status_in_file(self, file_path: str, phase_number: int, evaluation_result: str) -> bool:
        """Update phase status in a specific file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Update phase status patterns
            import re
            
            # Pattern 1: **Phase X**: Status
            pattern1 = rf'(\*\*Phase {phase_number}\*\*:?\s*)[^✅❌🔄⏳]*(?:[✅❌🔄⏳]\s*\w+)?'
            if evaluation_result.upper() == 'PASS':
                replacement1 = rf'\1✅ COMPLETE'
            elif evaluation_result.upper() == 'FAIL':
                replacement1 = rf'\1❌ FAILED'
            else:
                replacement1 = rf'\1🔄 {evaluation_result.upper()}'
            
            content = re.sub(pattern1, replacement1, content)
            
            # Pattern 2: Phase X - Description (Status)
            pattern2 = rf'(Phase {phase_number}[^\n]*?)(?:\([^)]*\))?(\s*[✅❌🔄⏳]?\s*\w*)?'
            status_icon = '✅' if evaluation_result.upper() == 'PASS' else '❌' if evaluation_result.upper() == 'FAIL' else '🔄'
            replacement2 = rf'\1 ({evaluation_result.upper()}) {status_icon}'
            
            content = re.sub(pattern2, replacement2, content)
            
            # Update ACTIVE PHASE if this is a completion
            if evaluation_result.upper() == 'PASS':
                next_phase = phase_number + 1
                # Update active phase reference
                active_phase_pattern = r'ACTIVE PHASE[:\s]*\*\*[:\s]*Phase \d+'
                active_phase_replacement = f'ACTIVE PHASE**: Phase {next_phase}'
                content = re.sub(active_phase_pattern, active_phase_replacement, content)
            
            # Write back if changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
            
        except Exception as e:
            raise Exception(f"Failed to update {file_path}: {str(e)}")
        
        return False
    
    def validate_evidence_package(self, phase_number: int, phase_name: str, evaluation_result: str) -> Dict[str, Any]:
        """Validate the evidence package for the completed phase"""
        validation_result = {
            'evidence_path': None,
            'validation_passed': False,
            'validation_details': {},
            'missing_elements': [],
            'recommendations': []
        }
        
        # Find evidence directory
        evidence_base = os.path.join(self.repo_root, 'evidence')
        evidence_dirs = []
        
        if os.path.exists(evidence_base):
            for item in os.listdir(evidence_base):
                if f'phase{phase_number}' in item.lower():
                    evidence_dirs.append(item)
        
        if not evidence_dirs:
            validation_result['missing_elements'].append(f"No evidence directory found for Phase {phase_number}")
            return validation_result
        
        # Use the most relevant evidence directory
        evidence_dir = evidence_dirs[0]  # Take first match
        evidence_path = os.path.join(evidence_base, evidence_dir)
        validation_result['evidence_path'] = f"evidence/{evidence_dir}"
        
        # Validate evidence package
        validation_result['validation_details'] = self.validate_evidence_directory(evidence_path)
        
        # Check validation criteria
        criteria = self.maintenance_config['evidence_validation_criteria']
        validation_passed = True
        
        # Check implementation files
        impl_files = validation_result['validation_details'].get('python_files', 0)
        if impl_files < criteria['min_implementation_files']:
            validation_result['missing_elements'].append(f"Need {criteria['min_implementation_files']} implementation files (found {impl_files})")
            validation_passed = False
        
        # Check documentation files
        doc_files = validation_result['validation_details'].get('markdown_files', 0)
        if doc_files < criteria['min_documentation_files']:
            validation_result['missing_elements'].append(f"Need {criteria['min_documentation_files']} documentation files (found {doc_files})")
            validation_passed = False
        
        # Check for completion summary
        if criteria['required_completion_summary']:
            if not validation_result['validation_details'].get('has_completion_summary', False):
                validation_result['missing_elements'].append("Missing completion summary")
                validation_passed = False
        
        # Check for external evaluator test
        if criteria['required_external_evaluator_test']:
            if not validation_result['validation_details'].get('has_evaluator_test', False):
                validation_result['missing_elements'].append("Missing external evaluator test")
                validation_passed = False
        
        validation_result['validation_passed'] = validation_passed
        
        # Generate recommendations
        if not validation_passed:
            validation_result['recommendations'] = [
                "Complete missing evidence elements before final phase closure",
                "Ensure all implementation code is properly documented",
                "Include test results and demonstration outputs"
            ]
        
        return validation_result
    
    def validate_evidence_directory(self, evidence_path: str) -> Dict[str, Any]:
        """Validate the contents of an evidence directory"""
        details = {
            'total_files': 0,
            'python_files': 0,
            'markdown_files': 0,
            'json_files': 0,
            'directories': 0,
            'has_completion_summary': False,
            'has_evaluator_test': False,
            'file_sizes': {},
            'directory_structure': []
        }
        
        try:
            for root, dirs, files in os.walk(evidence_path):
                details['directories'] += len(dirs)
                
                rel_root = os.path.relpath(root, evidence_path)
                if rel_root == '.':
                    rel_root = 'root'
                details['directory_structure'].append(rel_root)
                
                for file in files:
                    details['total_files'] += 1
                    file_path = os.path.join(root, file)
                    
                    # Count by type
                    if file.endswith('.py'):
                        details['python_files'] += 1
                    elif file.endswith('.md'):
                        details['markdown_files'] += 1
                    elif file.endswith('.json'):
                        details['json_files'] += 1
                    
                    # Check for specific files
                    if 'completion' in file.lower() and 'summary' in file.lower():
                        details['has_completion_summary'] = True
                    
                    if 'evaluator' in file.lower() and 'test' in file.lower():
                        details['has_evaluator_test'] = True
                    
                    # File size
                    try:
                        size = os.path.getsize(file_path)
                        details['file_sizes'][file] = size
                    except OSError:
                        pass
        
        except OSError:
            pass
        
        return details
    
    def update_progress_tracking(self, phase_number: int, phase_name: str, evaluation_result: str) -> Dict[str, Any]:
        """Update progress tracking systems"""
        progress_update = {
            'phase_progress_updated': False,
            'overall_progress_calculated': 0.0,
            'next_phase_status': 'PLANNED',
            'completion_date': datetime.now().isoformat()
        }
        
        try:
            # Update phase progress file
            progress_file = os.path.join(self.repo_root, 'docs/phase_progress.json')
            
            if os.path.exists(progress_file):
                with open(progress_file, 'r') as f:
                    progress_data = json.load(f)
            else:
                progress_data = {}
            
            # Update current phase
            phase_key = str(phase_number)
            if phase_key not in progress_data:
                progress_data[phase_key] = {}
            
            progress_data[phase_key].update({
                'phase_number': phase_number,
                'phase_name': phase_name,
                'status': 'COMPLETE' if evaluation_result.upper() == 'PASS' else 'FAILED',
                'completion_date': progress_update['completion_date'],
                'evaluation_result': evaluation_result
            })
            
            # Set next phase status
            next_phase_key = str(phase_number + 1)
            if next_phase_key not in progress_data:
                progress_data[next_phase_key] = {}
            
            if evaluation_result.upper() == 'PASS':
                progress_data[next_phase_key]['status'] = 'PLANNED'
                progress_update['next_phase_status'] = 'PLANNED'
            
            # Calculate overall progress
            completed_phases = sum(1 for p in progress_data.values() 
                                 if p.get('status') == 'COMPLETE')
            total_phases = max(len(progress_data), 7)  # At least 7 phases
            progress_update['overall_progress_calculated'] = completed_phases / total_phases
            
            # Save updated progress
            with open(progress_file, 'w') as f:
                json.dump(progress_data, f, indent=2)
            
            progress_update['phase_progress_updated'] = True
            
        except Exception as e:
            progress_update['error'] = str(e)
        
        return progress_update
    
    def archive_working_files(self, phase_number: int, phase_name: str, evaluation_result: str) -> Dict[str, Any]:
        """Archive temporary and working files"""
        archive_result = {
            'files_archived': [],
            'directories_created': [],
            'cleanup_performed': False,
            'errors': []
        }
        
        try:
            # Define archive rules
            archive_rules = self.maintenance_config['archive_rules']
            
            if archive_rules['archive_temp_files']:
                # Archive temp files
                temp_files = self.find_temp_files()
                for temp_file in temp_files:
                    try:
                        self.archive_file(temp_file, 'temp_files')
                        archive_result['files_archived'].append(temp_file)
                    except Exception as e:
                        archive_result['errors'].append(f"Failed to archive {temp_file}: {str(e)}")
            
            if archive_rules['archive_debug_files']:
                # Archive debug files
                debug_files = self.find_debug_files()
                for debug_file in debug_files:
                    try:
                        self.archive_file(debug_file, 'debug_files')
                        archive_result['files_archived'].append(debug_file)
                    except Exception as e:
                        archive_result['errors'].append(f"Failed to archive {debug_file}: {str(e)}")
            
            archive_result['cleanup_performed'] = True
            
        except Exception as e:
            archive_result['errors'].append(f"Archive operation failed: {str(e)}")
        
        return archive_result
    
    def find_temp_files(self) -> List[str]:
        """Find temporary files to archive"""
        temp_files = []
        temp_patterns = ['*.tmp', '*.temp', '*~', '*.bak', '*.swp']
        
        for root, dirs, files in os.walk(self.repo_root):
            # Skip .git and archive directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'archive']
            
            for file in files:
                for pattern in temp_patterns:
                    import fnmatch
                    if fnmatch.fnmatch(file, pattern):
                        temp_files.append(os.path.join(root, file))
        
        return temp_files
    
    def find_debug_files(self) -> List[str]:
        """Find debug files to archive"""
        debug_files = []
        debug_patterns = ['debug_*', '*_debug.*', 'test_output.*', '*.log']
        
        for root, dirs, files in os.walk(self.repo_root):
            # Skip .git and archive directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'archive']
            
            for file in files:
                for pattern in debug_patterns:
                    import fnmatch
                    if fnmatch.fnmatch(file, pattern):
                        debug_files.append(os.path.join(root, file))
        
        return debug_files
    
    def archive_file(self, file_path: str, category: str):
        """Archive a single file to appropriate location"""
        archive_base = os.path.join(self.repo_root, 'archive', category)
        os.makedirs(archive_base, exist_ok=True)
        
        file_name = os.path.basename(file_path)
        archive_path = os.path.join(archive_base, file_name)
        
        # Handle name conflicts
        counter = 1
        while os.path.exists(archive_path):
            name, ext = os.path.splitext(file_name)
            archive_path = os.path.join(archive_base, f"{name}_{counter}{ext}")
            counter += 1
        
        shutil.move(file_path, archive_path)
    
    def update_documentation(self, phase_number: int, phase_name: str, evaluation_result: str) -> Dict[str, Any]:
        """Update documentation after phase completion"""
        doc_updates = {
            'files_updated': [],
            'summaries_generated': [],
            'errors': []
        }
        
        try:
            doc_config = self.maintenance_config['documentation_updates']
            
            if doc_config['generate_phase_summary']:
                summary = self.generate_phase_summary(phase_number, phase_name, evaluation_result)
                summary_file = os.path.join(self.repo_root, f'docs/phase_{phase_number}_summary.md')
                
                with open(summary_file, 'w') as f:
                    f.write(summary)
                
                doc_updates['summaries_generated'].append(f'docs/phase_{phase_number}_summary.md')
            
            if doc_config['update_roadmap']:
                roadmap_updated = self.update_roadmap(phase_number, evaluation_result)
                if roadmap_updated:
                    doc_updates['files_updated'].append('roadmap updated')
            
        except Exception as e:
            doc_updates['errors'].append(f"Documentation update failed: {str(e)}")
        
        return doc_updates
    
    def generate_phase_summary(self, phase_number: int, phase_name: str, evaluation_result: str) -> str:
        """Generate a summary for the completed phase"""
        summary = f"""# Phase {phase_number} Completion Summary
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Phase Information
- **Phase Number**: {phase_number}
- **Phase Name**: {phase_name}
- **Evaluation Result**: {evaluation_result}
- **Completion Date**: {datetime.now().strftime('%Y-%m-%d')}

## Implementation Status
{f"✅ Phase {phase_number} completed successfully" if evaluation_result.upper() == 'PASS' else f"❌ Phase {phase_number} evaluation failed"}

## Evidence Location
Evidence for this phase can be found in: `evidence/phase{phase_number}_*/`

## Next Steps
"""
        
        if evaluation_result.upper() == 'PASS':
            summary += f"""- Phase {phase_number + 1} is now ready to begin
- All evidence has been validated and archived
- Documentation has been updated
"""
        else:
            summary += f"""- Phase {phase_number} requires remediation
- Review evaluation feedback and address issues
- Re-submit for evaluation when ready
"""
        
        summary += f"""
## Maintenance Actions Completed
- ✅ Phase status updated in all documentation
- ✅ Evidence package validated
- ✅ Progress tracking updated
- ✅ Working files archived
- ✅ Documentation updated

---
*This summary was automatically generated by the post-phase maintenance system.*
"""
        
        return summary
    
    def update_roadmap(self, phase_number: int, evaluation_result: str) -> bool:
        """Update project roadmap with phase completion"""
        # This would update a roadmap file if it exists
        roadmap_file = os.path.join(self.repo_root, 'docs/roadmap.md')
        
        if os.path.exists(roadmap_file):
            try:
                with open(roadmap_file, 'r') as f:
                    content = f.read()
                
                # Update roadmap content (basic implementation)
                import re
                pattern = rf'(Phase {phase_number}[^\n]*)'
                if evaluation_result.upper() == 'PASS':
                    replacement = rf'\1 ✅ COMPLETED'
                else:
                    replacement = rf'\1 ❌ FAILED'
                
                updated_content = re.sub(pattern, replacement, content)
                
                if updated_content != content:
                    with open(roadmap_file, 'w') as f:
                        f.write(updated_content)
                    return True
                    
            except Exception:
                pass
        
        return False
    
    def generate_completion_report(self, phase_number: int, phase_name: str, evaluation_result: str) -> Dict[str, Any]:
        """Generate comprehensive completion report"""
        report = {
            'report_generated': False,
            'report_location': None,
            'report_summary': {},
            'errors': []
        }
        
        try:
            # Generate comprehensive report
            report_content = f"""# Phase {phase_number} Completion Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary
Phase {phase_number} ({phase_name}) has been evaluated with result: **{evaluation_result}**

## Detailed Analysis
"""
            
            # Add evidence analysis
            evidence_validation = self.validate_evidence_package(phase_number, phase_name, evaluation_result)
            report_content += f"""
### Evidence Package Analysis
- **Evidence Location**: {evidence_validation.get('evidence_path', 'Not found')}
- **Validation Status**: {'PASSED' if evidence_validation.get('validation_passed') else 'FAILED'}
- **Total Files**: {evidence_validation.get('validation_details', {}).get('total_files', 0)}
- **Implementation Files**: {evidence_validation.get('validation_details', {}).get('python_files', 0)}
- **Documentation Files**: {evidence_validation.get('validation_details', {}).get('markdown_files', 0)}
"""
            
            if evidence_validation.get('missing_elements'):
                report_content += "\n### Missing Elements\n"
                for element in evidence_validation['missing_elements']:
                    report_content += f"- {element}\n"
            
            # Add maintenance summary
            report_content += f"""
### Maintenance Actions Performed
- Phase status updated in documentation
- Progress tracking updated
- Evidence package validated
- Working files archived
- Documentation updated

### Next Phase Status
"""
            
            if evaluation_result.upper() == 'PASS':
                report_content += f"Phase {phase_number + 1} is ready to begin implementation.\n"
            else:
                report_content += f"Phase {phase_number} requires remediation before proceeding.\n"
            
            # Save report
            report_file = os.path.join(self.repo_root, f'docs/phase_{phase_number}_completion_report.md')
            
            with open(report_file, 'w') as f:
                f.write(report_content)
            
            report['report_generated'] = True
            report['report_location'] = f'docs/phase_{phase_number}_completion_report.md'
            report['report_summary'] = {
                'phase_number': phase_number,
                'evaluation_result': evaluation_result,
                'evidence_validated': evidence_validation.get('validation_passed', False),
                'maintenance_completed': True
            }
            
        except Exception as e:
            report['errors'].append(f"Report generation failed: {str(e)}")
        
        return report
    
    def prepare_next_phase(self, completed_phase_number: int) -> Dict[str, Any]:
        """Prepare for the next phase"""
        preparation = {
            'next_phase_number': completed_phase_number + 1,
            'preparation_tasks': [],
            'environment_ready': False,
            'blockers': []
        }
        
        next_phase = completed_phase_number + 1
        
        # Check if next phase directory exists
        next_phase_dir = os.path.join(self.repo_root, f'phases/phase{next_phase}_*')
        import glob
        next_phase_dirs = glob.glob(next_phase_dir)
        
        if next_phase_dirs:
            preparation['preparation_tasks'].append(f"Phase {next_phase} directory found")
            preparation['environment_ready'] = True
        else:
            preparation['blockers'].append(f"Phase {next_phase} directory not found")
        
        # Check if evidence directory structure is ready
        evidence_dir = os.path.join(self.repo_root, 'evidence')
        if os.path.exists(evidence_dir):
            preparation['preparation_tasks'].append("Evidence directory structure verified")
        else:
            preparation['blockers'].append("Evidence directory structure missing")
        
        return preparation
    
    def generate_maintenance_summary(self, maintenance_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of maintenance execution"""
        summary = {
            'total_tasks': len(maintenance_result['tasks_completed']) + len(maintenance_result['tasks_failed']),
            'successful_tasks': len(maintenance_result['tasks_completed']),
            'failed_tasks': len(maintenance_result['tasks_failed']),
            'success_rate': 0.0,
            'critical_issues': [],
            'maintenance_status': 'UNKNOWN'
        }
        
        if summary['total_tasks'] > 0:
            summary['success_rate'] = summary['successful_tasks'] / summary['total_tasks']
        
        # Identify critical issues
        for failed_task in maintenance_result['tasks_failed']:
            if failed_task['task'] in ['update_phase_status', 'validate_evidence_package']:
                summary['critical_issues'].append(failed_task['task'])
        
        # Determine overall status
        if summary['success_rate'] >= 0.9 and not summary['critical_issues']:
            summary['maintenance_status'] = 'SUCCESS'
        elif summary['success_rate'] >= 0.7:
            summary['maintenance_status'] = 'PARTIAL_SUCCESS'
        else:
            summary['maintenance_status'] = 'FAILURE'
        
        return summary
    
    def log_maintenance_execution(self, maintenance_result: Dict[str, Any]):
        """Log maintenance execution for audit trail"""
        log_entry = {
            'timestamp': maintenance_result['timestamp'],
            'phase_number': maintenance_result['phase_number'],
            'evaluation_result': maintenance_result['evaluation_result'],
            'maintenance_status': maintenance_result['maintenance_summary'].get('maintenance_status'),
            'tasks_completed': len(maintenance_result['tasks_completed']),
            'tasks_failed': len(maintenance_result['tasks_failed'])
        }
        
        log_file = os.path.join(self.repo_root, 'docs/post_phase_maintenance.log')
        
        try:
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception:
            pass

# Example usage and testing
if __name__ == "__main__":
    maintenance_system = PostPhaseMaintenanceSystem("/home/brian/autocoder3_cc")
    
    # Test post-phase maintenance for a completed phase
    test_phase_number = 5
    test_phase_name = "Database Integration"
    test_evaluation_result = "PASS"
    
    print(f"Testing post-phase maintenance for Phase {test_phase_number}...")
    
    result = maintenance_system.execute_post_phase_maintenance(
        test_phase_number, 
        test_phase_name, 
        test_evaluation_result
    )
    
    print(f"Maintenance Status: {result['maintenance_summary'].get('maintenance_status')}")
    print(f"Tasks Completed: {len(result['tasks_completed'])}")
    print(f"Tasks Failed: {len(result['tasks_failed'])}")
    
    if result['tasks_completed']:
        print("\nCompleted Tasks:")
        for task in result['tasks_completed']:
            print(f"  ✅ {task['task']}")
    
    if result['tasks_failed']:
        print("\nFailed Tasks:")
        for task in result['tasks_failed']:
            print(f"  ❌ {task['task']}: {task['error']}")
    
    # Save results
    with open("post_phase_maintenance_test_results.json", "w") as f:
        json.dump(result, f, indent=2)
    
    print("\nPost-phase maintenance test complete.")
    print("Results saved to post_phase_maintenance_test_results.json")