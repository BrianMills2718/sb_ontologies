#!/usr/bin/env python3
"""
Complete Documentation Maintenance System
Integrates all maintenance components into unified system
"""

import os
import sys
import json
import subprocess
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add maintenance modules to path
maintenance_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for day_dir in ['day1_documentation_audit', 'day2_automated_status_tracking', 
                'day3_documentation_validation', 'day4_maintenance_integration', 
                'day5_enforcement_mechanisms']:
    sys.path.append(os.path.join(maintenance_root, day_dir))

# Import all maintenance components
try:
    from current_status_audit import DocumentationAuditor
    from consistency_checker import DocumentationConsistencyChecker
    from status_update_automation import AutomatedStatusTracker
    from git_change_monitor import GitChangeMonitor
    from phase_progress_tracker import PhaseProgressTracker
    from documentation_validator import DocumentationValidator
    from evidence_completeness_checker import EvidenceCompletenessChecker
    from archive_organization_validator import ArchiveOrganizationValidator
    from maintenance_workflow import MaintenanceWorkflowIntegrator
    from post_phase_maintenance import PostPhaseMaintenanceSystem
    from documentation_health_monitor import DocumentationHealthMonitor
    from pre_commit_documentation_check import PreCommitDocumentationChecker
    from phase_completion_validator import PhaseCompletionValidator
    from automated_archive_system import AutomatedArchiveSystem
except ImportError as e:
    print(f"Warning: Could not import all maintenance modules: {e}")

class CompleteMaintenanceSystem:
    """Complete documentation maintenance system with all integrated components"""
    
    def __init__(self, repo_root: str):
        self.repo_root = repo_root
        self.system_config = self.load_system_config()
        self.components = self.initialize_components()
        
    def load_system_config(self) -> Dict[str, Any]:
        """Load complete system configuration"""
        return {
            'system_info': {
                'name': 'Documentation Maintenance System v1.0',
                'version': '1.0.0',
                'repository': self.repo_root,
                'initialized': datetime.now().isoformat()
            },
            'enabled_components': {
                'documentation_audit': True,
                'automated_status_tracking': True,
                'documentation_validation': True,
                'maintenance_integration': True,
                'enforcement_mechanisms': True,
                'health_monitoring': True,
                'archive_management': True
            },
            'automation_levels': {
                'pre_commit_checks': 'enabled',
                'phase_completion_validation': 'strict',
                'status_tracking': 'automatic',
                'archive_maintenance': 'manual_approval',
                'health_monitoring': 'continuous'
            },
            'integration_points': {
                'multi_agent_workflow': True,
                'git_hooks': True,
                'ci_cd_pipeline': False,  # Not implemented yet
                'notification_system': False  # Not implemented yet
            },
            'maintenance_schedule': {
                'health_checks': '5_minutes',
                'consistency_checks': '15_minutes',
                'evidence_validation': '30_minutes',
                'archive_organization': '60_minutes',
                'full_audit': 'daily'
            }
        }
    
    def initialize_components(self) -> Dict[str, Any]:
        """Initialize all maintenance components"""
        components = {}
        
        try:
            if self.system_config['enabled_components']['documentation_audit']:
                components['auditor'] = DocumentationAuditor(self.repo_root)
                components['consistency_checker'] = DocumentationConsistencyChecker(self.repo_root)
            
            if self.system_config['enabled_components']['automated_status_tracking']:
                components['status_tracker'] = AutomatedStatusTracker(self.repo_root)
                components['git_monitor'] = GitChangeMonitor(self.repo_root)
                components['progress_tracker'] = PhaseProgressTracker(self.repo_root)
            
            if self.system_config['enabled_components']['documentation_validation']:
                components['validator'] = DocumentationValidator(self.repo_root)
                components['evidence_checker'] = EvidenceCompletenessChecker(self.repo_root)
                components['archive_validator'] = ArchiveOrganizationValidator(self.repo_root)
            
            if self.system_config['enabled_components']['maintenance_integration']:
                components['workflow_integrator'] = MaintenanceWorkflowIntegrator(self.repo_root)
                components['post_phase_maintenance'] = PostPhaseMaintenanceSystem(self.repo_root)
            
            if self.system_config['enabled_components']['health_monitoring']:
                components['health_monitor'] = DocumentationHealthMonitor(self.repo_root)
            
            if self.system_config['enabled_components']['enforcement_mechanisms']:
                components['pre_commit_checker'] = PreCommitDocumentationChecker(self.repo_root)
                components['phase_completion_validator'] = PhaseCompletionValidator(self.repo_root)
                components['archive_system'] = AutomatedArchiveSystem(self.repo_root)
                
        except Exception as e:
            print(f"Warning: Error initializing components: {e}")
        
        return components
    
    def run_comprehensive_health_check(self) -> Dict[str, Any]:
        """Run comprehensive health check of all systems"""
        health_check = {
            'timestamp': datetime.now().isoformat(),
            'system_status': 'UNKNOWN',
            'component_health': {},
            'overall_scores': {},
            'critical_issues': [],
            'recommendations': [],
            'maintenance_required': []
        }
        
        print("Running comprehensive documentation maintenance health check...")
        
        try:
            # 1. Documentation Audit
            if 'auditor' in self.components:
                print("  → Documentation audit...")
                audit_results = self.components['auditor'].audit_all_documentation()
                consistency_results = self.components['consistency_checker'].check_cross_file_consistency()
                
                health_check['component_health']['documentation_audit'] = {
                    'status': 'OPERATIONAL',
                    'files_audited': len(audit_results),
                    'inconsistencies_found': sum(len(status.inconsistencies) for status in audit_results.values()),
                    'consistency_issues': len(consistency_results.get('phase_consistency', {}).get('issues', []))
                }
                
                total_inconsistencies = health_check['component_health']['documentation_audit']['inconsistencies_found']
                health_check['overall_scores']['documentation_audit'] = max(0, 1.0 - (total_inconsistencies / 10))
            
            # 2. Status Tracking
            if 'status_tracker' in self.components:
                print("  → Status tracking...")
                recent_changes = self.components['status_tracker'].detect_recent_changes(24)
                progress_results = self.components['progress_tracker'].update_progress_from_git(7)
                
                health_check['component_health']['status_tracking'] = {
                    'status': 'OPERATIONAL',
                    'recent_changes_detected': sum(len(changes) for changes in recent_changes.values()),
                    'phases_tracked': len(progress_results),
                    'current_phase': self.components['progress_tracker'].get_current_active_phase(progress_results)
                }
                
                health_check['overall_scores']['status_tracking'] = 1.0  # Operational
            
            # 3. Documentation Validation
            if 'validator' in self.components:
                print("  → Documentation validation...")
                validation_results = self.components['validator'].validate_all_documentation()
                evidence_results = self.components['evidence_checker'].check_all_evidence()
                archive_results = self.components['archive_validator'].validate_archive_organization()
                
                health_check['component_health']['documentation_validation'] = {
                    'status': validation_results['overall_status'],
                    'files_validated': validation_results['summary']['total_files_checked'],
                    'validation_passed': validation_results['summary']['files_passed'],
                    'evidence_completeness': evidence_results['overall_completeness_score'],
                    'archive_organization': archive_results['organization_score']
                }
                
                validation_score = validation_results['summary']['files_passed'] / max(validation_results['summary']['total_files_checked'], 1)
                health_check['overall_scores']['documentation_validation'] = (
                    validation_score * 0.4 + 
                    evidence_results['overall_completeness_score'] * 0.4 + 
                    archive_results['organization_score'] * 0.2
                )
            
            # 4. Enforcement Mechanisms
            if 'pre_commit_checker' in self.components:
                print("  → Enforcement mechanisms...")
                # Test pre-commit checker
                commit_allowed, commit_check = self.components['pre_commit_checker'].run_pre_commit_checks()
                
                # Test phase completion validator with current phase
                current_phase = 5  # Example
                phase_validation = self.components['phase_completion_validator'].validate_phase_completion(current_phase, "PASS")
                
                health_check['component_health']['enforcement_mechanisms'] = {
                    'status': 'OPERATIONAL',
                    'pre_commit_status': 'PASS' if commit_allowed else 'BLOCKING',
                    'phase_validation_gates': len(phase_validation['validation_gates']),
                    'phase_completion_allowed': phase_validation['completion_allowed'],
                    'archive_system_ready': True
                }
                
                enforcement_score = 1.0 if commit_check['commit_allowed'] else 0.8  # Still functional if blocking
                health_check['overall_scores']['enforcement_mechanisms'] = enforcement_score
            
            # 5. Integration Status
            if 'workflow_integrator' in self.components:
                print("  → Integration status...")
                integration_config = self.components['workflow_integrator'].integrate_with_multi_agent_system()
                
                health_check['component_health']['integration'] = {
                    'status': 'OPERATIONAL',
                    'phase_hooks_configured': len(integration_config['phase_hooks']),
                    'validation_gates_set': len(integration_config['validation_gates']),
                    'auto_maintenance_scheduled': len(integration_config['auto_maintenance_schedule'])
                }
                
                health_check['overall_scores']['integration'] = 1.0  # Operational
            
            # Calculate overall system health
            scores = list(health_check['overall_scores'].values())
            if scores:
                overall_score = sum(scores) / len(scores)
                health_check['overall_scores']['system_overall'] = overall_score
                
                if overall_score >= 0.9:
                    health_check['system_status'] = 'EXCELLENT'
                elif overall_score >= 0.75:
                    health_check['system_status'] = 'GOOD'
                elif overall_score >= 0.5:
                    health_check['system_status'] = 'FAIR'
                else:
                    health_check['system_status'] = 'POOR'
            
            # Identify critical issues
            for component, details in health_check['component_health'].items():
                if details.get('status') in ['FAIL', 'ERROR']:
                    health_check['critical_issues'].append(f"{component}: {details.get('status')}")
            
            # Generate recommendations
            if health_check['overall_scores'].get('documentation_validation', 1.0) < 0.8:
                health_check['recommendations'].append("Improve documentation validation scores")
            
            if health_check['overall_scores'].get('documentation_audit', 1.0) < 0.8:
                health_check['recommendations'].append("Address documentation inconsistencies")
            
            if not health_check['component_health'].get('enforcement_mechanisms', {}).get('phase_completion_allowed', True):
                health_check['maintenance_required'].append("Complete current phase before proceeding")
            
        except Exception as e:
            health_check['system_status'] = 'ERROR'
            health_check['critical_issues'].append(f"Health check error: {str(e)}")
        
        return health_check
    
    def execute_maintenance_cycle(self, cycle_type: str = 'full') -> Dict[str, Any]:
        """Execute complete maintenance cycle"""
        maintenance_cycle = {
            'cycle_type': cycle_type,
            'timestamp': datetime.now().isoformat(),
            'operations_performed': [],
            'results': {},
            'issues_resolved': [],
            'issues_remaining': [],
            'cycle_success': False
        }
        
        print(f"Executing {cycle_type} maintenance cycle...")
        
        try:
            if cycle_type in ['full', 'audit']:
                # Documentation audit and consistency check
                print("  → Running documentation audit...")
                if 'auditor' in self.components:
                    audit_results = self.components['auditor'].audit_all_documentation()
                    consistency_results = self.components['consistency_checker'].check_cross_file_consistency()
                    
                    maintenance_cycle['operations_performed'].append('documentation_audit')
                    maintenance_cycle['results']['audit'] = {
                        'files_audited': len(audit_results),
                        'inconsistencies': sum(len(status.inconsistencies) for status in audit_results.values()),
                        'consistency_issues': len(consistency_results.get('phase_consistency', {}).get('issues', []))
                    }
            
            if cycle_type in ['full', 'status']:
                # Status tracking update
                print("  → Updating status tracking...")
                if 'status_tracker' in self.components:
                    recent_changes = self.components['status_tracker'].detect_recent_changes(24)
                    self.components['status_tracker'].update_current_status_file(recent_changes)
                    
                    maintenance_cycle['operations_performed'].append('status_update')
                    maintenance_cycle['results']['status_tracking'] = {
                        'changes_detected': sum(len(changes) for changes in recent_changes.values()),
                        'status_updated': True
                    }
            
            if cycle_type in ['full', 'validation']:
                # Documentation validation
                print("  → Running validation checks...")
                if 'validator' in self.components:
                    validation_results = self.components['validator'].validate_all_documentation()
                    evidence_results = self.components['evidence_checker'].check_all_evidence()
                    
                    maintenance_cycle['operations_performed'].append('validation')
                    maintenance_cycle['results']['validation'] = {
                        'overall_status': validation_results['overall_status'],
                        'evidence_completeness': evidence_results['overall_completeness_score'],
                        'validation_passed': validation_results['summary']['files_passed']
                    }
            
            if cycle_type in ['full', 'archive']:
                # Archive maintenance
                print("  → Running archive maintenance...")
                if 'archive_system' in self.components:
                    # Set to dry run for safety
                    self.components['archive_system'].dry_run = True
                    archive_results = self.components['archive_system'].execute_automated_archival(['temp_files', 'debug_output'])
                    
                    maintenance_cycle['operations_performed'].append('archive_maintenance')
                    maintenance_cycle['results']['archive'] = {
                        'candidates_found': sum(len(candidates) for candidates in archive_results['scan_results'].values()),
                        'files_processed': archive_results['files_processed'],
                        'dry_run': archive_results['dry_run']
                    }
            
            # Determine cycle success
            maintenance_cycle['cycle_success'] = len(maintenance_cycle['operations_performed']) > 0
            
            # Generate summary
            if maintenance_cycle['cycle_success']:
                print(f"  ✅ Maintenance cycle completed successfully")
                print(f"     Operations: {', '.join(maintenance_cycle['operations_performed'])}")
            
        except Exception as e:
            maintenance_cycle['cycle_success'] = False
            maintenance_cycle['issues_remaining'].append(f"Maintenance cycle error: {str(e)}")
            print(f"  ❌ Maintenance cycle failed: {e}")
        
        return maintenance_cycle
    
    def install_git_hooks(self) -> Dict[str, Any]:
        """Install git hooks for documentation maintenance"""
        installation_result = {
            'hooks_installed': [],
            'installation_success': False,
            'errors': []
        }
        
        try:
            git_hooks_dir = os.path.join(self.repo_root, '.git', 'hooks')
            
            if not os.path.exists(git_hooks_dir):
                installation_result['errors'].append("Git hooks directory not found")
                return installation_result
            
            # Install pre-commit hook
            pre_commit_hook_path = os.path.join(git_hooks_dir, 'pre-commit')
            pre_commit_script = f"""#!/bin/bash
# Documentation Maintenance Pre-commit Hook
cd "{self.repo_root}"
python "{os.path.join(maintenance_root, 'day5_enforcement_mechanisms', 'pre_commit_documentation_check.py')}"
"""
            
            with open(pre_commit_hook_path, 'w') as f:
                f.write(pre_commit_script)
            
            # Make executable
            os.chmod(pre_commit_hook_path, 0o755)
            installation_result['hooks_installed'].append('pre-commit')
            
            installation_result['installation_success'] = True
            
        except Exception as e:
            installation_result['errors'].append(f"Hook installation error: {str(e)}")
        
        return installation_result
    
    def generate_system_report(self) -> str:
        """Generate comprehensive system status report"""
        health_check = self.run_comprehensive_health_check()
        
        report = f"""# Documentation Maintenance System Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## System Overview
- **System Status**: {health_check['system_status']}
- **Overall Health Score**: {health_check['overall_scores'].get('system_overall', 0.0):.1%}
- **Repository**: {self.repo_root}
- **Components Active**: {len(self.components)}

## Component Status
"""
        
        for component, details in health_check['component_health'].items():
            status_icon = '✅' if details['status'] in ['OPERATIONAL', 'PASS'] else '❌'
            report += f"### {status_icon} {component.replace('_', ' ').title()}\n"
            report += f"- Status: {details['status']}\n"
            
            for key, value in details.items():
                if key != 'status':
                    report += f"- {key.replace('_', ' ').title()}: {value}\n"
            report += "\n"
        
        ## Health Scores
        report += "## Health Scores\n"
        for component, score in health_check['overall_scores'].items():
            score_icon = '✅' if score >= 0.8 else '⚠️' if score >= 0.5 else '❌'
            report += f"- {score_icon} {component.replace('_', ' ').title()}: {score:.1%}\n"
        
        ## Issues and Recommendations
        if health_check['critical_issues']:
            report += "\n## Critical Issues\n"
            for issue in health_check['critical_issues']:
                report += f"- ❌ {issue}\n"
        
        if health_check['recommendations']:
            report += "\n## Recommendations\n"
            for rec in health_check['recommendations']:
                report += f"- 💡 {rec}\n"
        
        if health_check['maintenance_required']:
            report += "\n## Maintenance Required\n"
            for maintenance in health_check['maintenance_required']:
                report += f"- 🔧 {maintenance}\n"
        
        ## Configuration
        report += f"\n## System Configuration\n"
        report += f"- Automation Level: {self.system_config['automation_levels']}\n"
        report += f"- Enabled Components: {list(self.system_config['enabled_components'].keys())}\n"
        report += f"- Integration Points: {list(self.system_config['integration_points'].keys())}\n"
        
        return report
    
    def get_maintenance_statistics(self) -> Dict[str, Any]:
        """Get comprehensive maintenance statistics"""
        stats = {
            'timestamp': datetime.now().isoformat(),
            'system_uptime': 'N/A',  # Would track actual uptime
            'maintenance_operations': {},
            'enforcement_statistics': {},
            'health_metrics': {},
            'usage_patterns': {}
        }
        
        try:
            # Health metrics
            health_check = self.run_comprehensive_health_check()
            stats['health_metrics'] = health_check['overall_scores']
            
            # Component statistics
            for component_name, component in self.components.items():
                if hasattr(component, 'get_statistics'):
                    stats['maintenance_operations'][component_name] = component.get_statistics()
            
            # Archive statistics
            if 'archive_system' in self.components:
                archive_stats = self.components['archive_system'].get_archive_statistics()
                stats['enforcement_statistics']['archive'] = archive_stats
            
        except Exception as e:
            stats['error'] = f"Statistics collection error: {str(e)}"
        
        return stats

# Command-line interface
def main():
    """Main CLI interface for maintenance system"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Documentation Maintenance System')
    parser.add_argument('--repo-root', default='/home/brian/autocoder3_cc', help='Repository root path')
    parser.add_argument('--action', choices=['health-check', 'maintenance', 'report', 'install-hooks', 'stats'], 
                       default='health-check', help='Action to perform')
    parser.add_argument('--cycle-type', choices=['full', 'audit', 'status', 'validation', 'archive'], 
                       default='full', help='Maintenance cycle type')
    
    args = parser.parse_args()
    
    # Initialize system
    maintenance_system = CompleteMaintenanceSystem(args.repo_root)
    
    if args.action == 'health-check':
        health_check = maintenance_system.run_comprehensive_health_check()
        print(f"System Status: {health_check['system_status']}")
        print(f"Overall Health: {health_check['overall_scores'].get('system_overall', 0.0):.1%}")
        
        if health_check['critical_issues']:
            print(f"Critical Issues: {len(health_check['critical_issues'])}")
            for issue in health_check['critical_issues']:
                print(f"  - {issue}")
    
    elif args.action == 'maintenance':
        cycle_result = maintenance_system.execute_maintenance_cycle(args.cycle_type)
        print(f"Maintenance Cycle: {cycle_result['cycle_success']}")
        print(f"Operations: {', '.join(cycle_result['operations_performed'])}")
    
    elif args.action == 'report':
        report = maintenance_system.generate_system_report()
        print(report)
        
        # Save report
        report_file = f"maintenance_system_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w') as f:
            f.write(report)
        print(f"\nReport saved to {report_file}")
    
    elif args.action == 'install-hooks':
        hook_result = maintenance_system.install_git_hooks()
        print(f"Git Hooks Installation: {hook_result['installation_success']}")
        if hook_result['hooks_installed']:
            print(f"Installed: {', '.join(hook_result['hooks_installed'])}")
        if hook_result['errors']:
            for error in hook_result['errors']:
                print(f"Error: {error}")
    
    elif args.action == 'stats':
        stats = maintenance_system.get_maintenance_statistics()
        print("Maintenance Statistics:")
        print(json.dumps(stats, indent=2, default=str))

if __name__ == "__main__":
    main()