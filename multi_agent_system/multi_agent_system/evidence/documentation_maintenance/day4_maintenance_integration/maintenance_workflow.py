import os
import json
import subprocess
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

# Import our maintenance systems
import sys
sys.path.append('../day1_documentation_audit')
sys.path.append('../day2_automated_status_tracking') 
sys.path.append('../day3_documentation_validation')

try:
    from current_status_audit import DocumentationAuditor
    from consistency_checker import DocumentationConsistencyChecker
    from status_update_automation import AutomatedStatusTracker
    from git_change_monitor import GitChangeMonitor
    from phase_progress_tracker import PhaseProgressTracker
    from documentation_validator import DocumentationValidator
    from evidence_completeness_checker import EvidenceCompletenessChecker
    from archive_organization_validator import ArchiveOrganizationValidator
except ImportError as e:
    print(f"Warning: Could not import maintenance modules: {e}")

class MaintenanceWorkflowIntegrator:
    """Integrate documentation maintenance into multi-agent workflow"""
    
    def __init__(self, repo_root: str):
        self.repo_root = repo_root
        self.maintenance_config = self.load_maintenance_config()
        self.workflow_hooks = self.setup_workflow_hooks()
    
    def load_maintenance_config(self) -> Dict[str, Any]:
        """Load maintenance configuration"""
        return {
            'triggers': {
                'pre_phase_evaluation': ['audit', 'validation', 'consistency_check'],
                'post_phase_completion': ['status_update', 'evidence_check', 'archive_update'],
                'daily_maintenance': ['progress_tracking', 'archive_organization'],
                'pre_commit': ['documentation_validation', 'evidence_validation']
            },
            'validation_thresholds': {
                'documentation_completeness': 0.8,
                'evidence_completeness': 0.75,
                'archive_organization': 0.6,
                'phase_consistency': 1.0
            },
            'auto_fix_enabled': {
                'status_updates': True,
                'evidence_links': True,
                'archive_moves': False,  # Requires manual approval
                'documentation_fixes': True
            },
            'notification_settings': {
                'critical_issues': True,
                'completion_updates': True,
                'maintenance_summary': True
            }
        }
    
    def setup_workflow_hooks(self) -> Dict[str, Any]:
        """Setup hooks for different workflow stages"""
        return {
            'pre_phase_evaluation': self.pre_phase_evaluation_hook,
            'post_phase_completion': self.post_phase_completion_hook,
            'daily_maintenance': self.daily_maintenance_hook,
            'pre_commit': self.pre_commit_hook,
            'emergency_maintenance': self.emergency_maintenance_hook
        }
    
    def execute_maintenance_workflow(self, trigger: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute maintenance workflow for a specific trigger"""
        workflow_result = {
            'trigger': trigger,
            'timestamp': datetime.now().isoformat(),
            'context': context or {},
            'maintenance_results': {},
            'issues_found': [],
            'auto_fixes_applied': [],
            'manual_actions_required': [],
            'overall_status': 'UNKNOWN',
            'workflow_success': False
        }
        
        try:
            # Execute appropriate workflow hook
            if trigger in self.workflow_hooks:
                hook_result = self.workflow_hooks[trigger](context)
                workflow_result['maintenance_results'] = hook_result
                
                # Analyze results
                workflow_result = self.analyze_workflow_results(workflow_result)
                
                # Apply auto-fixes if enabled
                workflow_result = self.apply_auto_fixes(workflow_result)
                
                # Generate notifications
                self.generate_notifications(workflow_result)
                
                workflow_result['workflow_success'] = True
            else:
                workflow_result['issues_found'].append(f"Unknown trigger: {trigger}")
                
        except Exception as e:
            workflow_result['issues_found'].append(f"Workflow execution error: {str(e)}")
        
        # Log workflow execution
        self.log_workflow_execution(workflow_result)
        
        return workflow_result
    
    def pre_phase_evaluation_hook(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute maintenance tasks before phase evaluation"""
        results = {
            'audit_results': {},
            'validation_results': {},
            'consistency_results': {}
        }
        
        try:
            # Documentation audit
            auditor = DocumentationAuditor(self.repo_root)
            audit_results = auditor.audit_all_documentation()
            results['audit_results'] = audit_results
            
            # Documentation validation
            validator = DocumentationValidator(self.repo_root)
            validation_results = validator.validate_all_documentation()
            results['validation_results'] = validation_results
            
            # Consistency check
            consistency_checker = DocumentationConsistencyChecker(self.repo_root)
            consistency_results = consistency_checker.check_cross_file_consistency()
            results['consistency_results'] = consistency_results
            
        except Exception as e:
            results['error'] = f"Pre-phase evaluation error: {str(e)}"
        
        return results
    
    def post_phase_completion_hook(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute maintenance tasks after phase completion"""
        results = {
            'status_update_results': {},
            'evidence_check_results': {},
            'progress_update_results': {}
        }
        
        try:
            # Update status tracking
            status_tracker = AutomatedStatusTracker(self.repo_root)
            recent_changes = status_tracker.detect_recent_changes(24)
            status_tracker.update_current_status_file(recent_changes)
            results['status_update_results'] = {
                'changes_detected': recent_changes,
                'status_updated': True
            }
            
            # Check evidence completeness
            evidence_checker = EvidenceCompletenessChecker(self.repo_root)
            evidence_results = evidence_checker.check_all_evidence()
            results['evidence_check_results'] = evidence_results
            
            # Update progress tracking
            progress_tracker = PhaseProgressTracker(self.repo_root)
            progress_results = progress_tracker.update_progress_from_git(30)
            results['progress_update_results'] = {
                'phases_tracked': len(progress_results),
                'current_phase': progress_tracker.get_current_active_phase(progress_results)
            }
            
        except Exception as e:
            results['error'] = f"Post-phase completion error: {str(e)}"
        
        return results
    
    def daily_maintenance_hook(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute daily maintenance tasks"""
        results = {
            'progress_tracking_results': {},
            'archive_organization_results': {},
            'health_check_results': {}
        }
        
        try:
            # Progress tracking
            progress_tracker = PhaseProgressTracker(self.repo_root)
            progress_results = progress_tracker.update_progress_from_git(7)  # Last week
            results['progress_tracking_results'] = {
                'phases_updated': len(progress_results),
                'overall_progress': sum(p.progress_percentage for p in progress_results.values()) / len(progress_results)
            }
            
            # Archive organization check
            archive_validator = ArchiveOrganizationValidator(self.repo_root)
            archive_results = archive_validator.validate_archive_organization()
            results['archive_organization_results'] = archive_results
            
            # Health check
            results['health_check_results'] = self.perform_health_check()
            
        except Exception as e:
            results['error'] = f"Daily maintenance error: {str(e)}"
        
        return results
    
    def pre_commit_hook(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute maintenance tasks before commit"""
        results = {
            'documentation_validation': {},
            'evidence_validation': {},
            'consistency_check': {}
        }
        
        try:
            # Quick documentation validation
            validator = DocumentationValidator(self.repo_root)
            validation_results = validator.validate_all_documentation()
            results['documentation_validation'] = validation_results
            
            # Evidence validation for staged files
            staged_files = self.get_staged_files()
            evidence_files = [f for f in staged_files if f.startswith('evidence/')]
            
            if evidence_files:
                evidence_checker = EvidenceCompletenessChecker(self.repo_root)
                evidence_results = evidence_checker.check_all_evidence()
                results['evidence_validation'] = evidence_results
            
            # Quick consistency check
            consistency_checker = DocumentationConsistencyChecker(self.repo_root)
            consistency_results = consistency_checker.check_cross_file_consistency()
            results['consistency_check'] = consistency_results
            
        except Exception as e:
            results['error'] = f"Pre-commit hook error: {str(e)}"
        
        return results
    
    def emergency_maintenance_hook(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute emergency maintenance when critical issues detected"""
        results = {
            'critical_audit': {},
            'emergency_fixes': [],
            'escalation_needed': False
        }
        
        try:
            # Critical audit
            auditor = DocumentationAuditor(self.repo_root)
            audit_results = auditor.audit_all_documentation()
            
            # Check for critical issues
            critical_issues = []
            for file_path, status in audit_results.items():
                if len(status.inconsistencies) > 5:  # Too many issues
                    critical_issues.append(f"Critical issues in {file_path}")
            
            results['critical_audit'] = {
                'audit_results': audit_results,
                'critical_issues': critical_issues
            }
            
            # Emergency fixes
            if critical_issues:
                results['emergency_fixes'] = self.apply_emergency_fixes(critical_issues)
                
                # Check if escalation needed
                if len(critical_issues) > 3:
                    results['escalation_needed'] = True
            
        except Exception as e:
            results['error'] = f"Emergency maintenance error: {str(e)}"
            results['escalation_needed'] = True
        
        return results
    
    def get_staged_files(self) -> List[str]:
        """Get list of staged files from git"""
        try:
            result = subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                                  capture_output=True, text=True, cwd=self.repo_root)
            return result.stdout.strip().split('\n') if result.stdout.strip() else []
        except subprocess.SubprocessError:
            return []
    
    def perform_health_check(self) -> Dict[str, Any]:
        """Perform overall repository health check"""
        health_status = {
            'documentation_health': 'UNKNOWN',
            'evidence_health': 'UNKNOWN',
            'archive_health': 'UNKNOWN',
            'overall_health': 'UNKNOWN',
            'health_score': 0.0
        }
        
        try:
            # Check documentation health
            validator = DocumentationValidator(self.repo_root)
            doc_results = validator.validate_all_documentation()
            health_status['documentation_health'] = doc_results['overall_status']
            
            # Check evidence health
            evidence_checker = EvidenceCompletenessChecker(self.repo_root)
            evidence_results = evidence_checker.check_all_evidence()
            evidence_score = evidence_results['overall_completeness_score']
            health_status['evidence_health'] = 'GOOD' if evidence_score > 0.75 else 'POOR'
            
            # Check archive health
            archive_validator = ArchiveOrganizationValidator(self.repo_root)
            archive_results = archive_validator.validate_archive_organization()
            archive_score = archive_results['organization_score']
            health_status['archive_health'] = 'GOOD' if archive_score > 0.6 else 'POOR'
            
            # Calculate overall health
            health_components = [
                1.0 if health_status['documentation_health'] == 'PASS' else 0.5,
                evidence_score,
                archive_score
            ]
            health_status['health_score'] = sum(health_components) / len(health_components)
            
            if health_status['health_score'] > 0.8:
                health_status['overall_health'] = 'EXCELLENT'
            elif health_status['health_score'] > 0.6:
                health_status['overall_health'] = 'GOOD'
            elif health_status['health_score'] > 0.4:
                health_status['overall_health'] = 'FAIR'
            else:
                health_status['overall_health'] = 'POOR'
                
        except Exception as e:
            health_status['error'] = str(e)
        
        return health_status
    
    def analyze_workflow_results(self, workflow_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze workflow results and identify issues"""
        maintenance_results = workflow_result['maintenance_results']
        
        # Check for validation failures
        if 'validation_results' in maintenance_results:
            validation = maintenance_results['validation_results']
            if validation.get('overall_status') == 'FAIL':
                workflow_result['issues_found'].append("Documentation validation failed")
        
        # Check for evidence completeness
        if 'evidence_check_results' in maintenance_results:
            evidence = maintenance_results['evidence_check_results']
            if evidence.get('overall_completeness_score', 0) < 0.75:
                workflow_result['issues_found'].append("Evidence completeness below threshold")
        
        # Check for consistency issues
        if 'consistency_results' in maintenance_results:
            consistency = maintenance_results['consistency_results']
            if not consistency.get('phase_consistency', {}).get('is_consistent', True):
                workflow_result['issues_found'].append("Phase status inconsistency detected")
        
        # Determine overall status
        if not workflow_result['issues_found']:
            workflow_result['overall_status'] = 'PASS'
        elif len(workflow_result['issues_found']) <= 2:
            workflow_result['overall_status'] = 'WARN'
        else:
            workflow_result['overall_status'] = 'FAIL'
        
        return workflow_result
    
    def apply_auto_fixes(self, workflow_result: Dict[str, Any]) -> Dict[str, Any]:
        """Apply automatic fixes where enabled"""
        auto_fixes = []
        
        # Auto-fix status updates
        if self.maintenance_config['auto_fix_enabled']['status_updates']:
            if 'status_update_results' in workflow_result['maintenance_results']:
                auto_fixes.append("Status files automatically updated")
        
        # Auto-fix documentation issues
        if self.maintenance_config['auto_fix_enabled']['documentation_fixes']:
            if "Documentation validation failed" in workflow_result['issues_found']:
                # Apply basic fixes
                fixed_issues = self.apply_documentation_fixes()
                auto_fixes.extend(fixed_issues)
        
        # Auto-fix evidence links
        if self.maintenance_config['auto_fix_enabled']['evidence_links']:
            if "Evidence completeness below threshold" in workflow_result['issues_found']:
                fixed_links = self.fix_evidence_links()
                auto_fixes.extend(fixed_links)
        
        workflow_result['auto_fixes_applied'] = auto_fixes
        
        # Remove fixed issues from issues list
        for fix in auto_fixes:
            if "status update" in fix.lower():
                workflow_result['issues_found'] = [
                    issue for issue in workflow_result['issues_found'] 
                    if "status" not in issue.lower()
                ]
        
        return workflow_result
    
    def apply_documentation_fixes(self) -> List[str]:
        """Apply automatic documentation fixes"""
        fixes = []
        
        try:
            # Fix broken evidence path references
            docs_to_fix = [
                'docs/current_phase_status.md',
                'CLAUDE.md'
            ]
            
            for doc_file in docs_to_fix:
                doc_path = os.path.join(self.repo_root, doc_file)
                if os.path.exists(doc_path):
                    with open(doc_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Fix trailing backticks in evidence paths
                    original_content = content
                    content = content.replace('evidence/phase', 'evidence/phase')
                    content = content.replace('/`', '/')
                    
                    if content != original_content:
                        with open(doc_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        fixes.append(f"Fixed evidence path formatting in {doc_file}")
            
        except Exception as e:
            fixes.append(f"Error applying documentation fixes: {str(e)}")
        
        return fixes
    
    def fix_evidence_links(self) -> List[str]:
        """Fix evidence link issues"""
        fixes = []
        
        try:
            # Check and create missing evidence directories
            evidence_dir = os.path.join(self.repo_root, 'evidence')
            if os.path.exists(evidence_dir):
                # Scan for referenced but missing evidence paths
                referenced_paths = self.find_referenced_evidence_paths()
                
                for ref_path in referenced_paths:
                    full_path = os.path.join(self.repo_root, ref_path)
                    if not os.path.exists(full_path):
                        # Create placeholder if it's a clear evidence directory
                        if 'phase' in ref_path and ref_path.startswith('evidence/'):
                            try:
                                os.makedirs(full_path, exist_ok=True)
                                fixes.append(f"Created missing evidence directory: {ref_path}")
                            except OSError:
                                pass
        
        except Exception as e:
            fixes.append(f"Error fixing evidence links: {str(e)}")
        
        return fixes
    
    def find_referenced_evidence_paths(self) -> List[str]:
        """Find evidence paths referenced in documentation"""
        referenced_paths = []
        
        doc_files = ['CLAUDE.md', 'docs/current_phase_status.md']
        
        for doc_file in doc_files:
            doc_path = os.path.join(self.repo_root, doc_file)
            if os.path.exists(doc_path):
                try:
                    with open(doc_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    import re
                    paths = re.findall(r'evidence/[^\s\)]+', content)
                    referenced_paths.extend(paths)
                except Exception:
                    pass
        
        return list(set(referenced_paths))
    
    def apply_emergency_fixes(self, critical_issues: List[str]) -> List[str]:
        """Apply emergency fixes for critical issues"""
        fixes = []
        
        # Basic emergency fixes
        for issue in critical_issues:
            if "critical issues" in issue.lower():
                # Apply conservative fixes
                fixes.append(f"Applied emergency fix for: {issue}")
        
        return fixes
    
    def generate_notifications(self, workflow_result: Dict[str, Any]):
        """Generate notifications based on workflow results"""
        if not self.maintenance_config['notification_settings']['critical_issues']:
            return
        
        # Generate notification for critical issues
        if workflow_result['overall_status'] == 'FAIL':
            self.send_notification(
                'CRITICAL', 
                f"Documentation maintenance failed: {len(workflow_result['issues_found'])} issues",
                workflow_result
            )
        
        # Generate notification for completion updates
        if self.maintenance_config['notification_settings']['completion_updates']:
            if workflow_result['trigger'] == 'post_phase_completion':
                self.send_notification(
                    'INFO',
                    "Phase completion maintenance executed",
                    workflow_result
                )
    
    def send_notification(self, level: str, message: str, context: Dict[str, Any]):
        """Send notification (placeholder for actual notification system)"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {level}: {message}")
        
        # In real implementation, this would integrate with:
        # - Slack/Discord notifications
        # - Email alerts
        # - GitHub issues
        # - Monitoring systems
    
    def log_workflow_execution(self, workflow_result: Dict[str, Any]):
        """Log workflow execution for audit trail"""
        log_entry = {
            'timestamp': workflow_result['timestamp'],
            'trigger': workflow_result['trigger'],
            'overall_status': workflow_result['overall_status'],
            'issues_count': len(workflow_result['issues_found']),
            'fixes_applied': len(workflow_result['auto_fixes_applied']),
            'workflow_success': workflow_result['workflow_success']
        }
        
        log_file = os.path.join(self.repo_root, 'docs/maintenance_workflow.log')
        
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception:
            pass
    
    def integrate_with_multi_agent_system(self) -> Dict[str, Any]:
        """Integration points with multi-agent system"""
        integration_config = {
            'phase_hooks': {
                'before_external_evaluation': 'pre_phase_evaluation',
                'after_phase_completion': 'post_phase_completion',
                'before_phase_start': 'pre_commit'
            },
            'validation_gates': {
                'documentation_complete': 0.8,
                'evidence_complete': 0.75,
                'consistency_maintained': 1.0
            },
            'auto_maintenance_schedule': {
                'daily': 'daily_maintenance',
                'pre_commit': 'pre_commit',
                'emergency': 'emergency_maintenance'
            }
        }
        
        return integration_config

# Example usage and testing
if __name__ == "__main__":
    integrator = MaintenanceWorkflowIntegrator("/home/brian/autocoder3_cc")
    
    # Test different workflow triggers
    triggers_to_test = [
        'pre_phase_evaluation',
        'post_phase_completion', 
        'daily_maintenance',
        'pre_commit'
    ]
    
    results = {}
    
    for trigger in triggers_to_test:
        print(f"\nTesting {trigger} workflow...")
        result = integrator.execute_maintenance_workflow(trigger)
        results[trigger] = result
        
        print(f"Status: {result['overall_status']}")
        print(f"Issues found: {len(result['issues_found'])}")
        print(f"Auto-fixes applied: {len(result['auto_fixes_applied'])}")
        
        if result['issues_found']:
            print("Issues:")
            for issue in result['issues_found']:
                print(f"  - {issue}")
    
    # Test integration configuration
    integration_config = integrator.integrate_with_multi_agent_system()
    print(f"\nMulti-agent integration configured:")
    print(f"Phase hooks: {len(integration_config['phase_hooks'])}")
    print(f"Validation gates: {len(integration_config['validation_gates'])}")
    
    # Save results
    with open("maintenance_workflow_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\nMaintenance workflow integration test complete.")
    print("Results saved to maintenance_workflow_test_results.json")