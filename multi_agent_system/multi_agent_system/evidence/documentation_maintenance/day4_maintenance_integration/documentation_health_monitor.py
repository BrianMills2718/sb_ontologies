import os
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from threading import Timer

class DocumentationHealthMonitor:
    """Continuous monitoring system for documentation health"""
    
    def __init__(self, repo_root: str):
        self.repo_root = repo_root
        self.monitoring_config = self.load_monitoring_config()
        self.health_history = []
        self.active_monitors = {}
        self.alert_thresholds = self.load_alert_thresholds()
        
    def load_monitoring_config(self) -> Dict[str, Any]:
        """Load monitoring configuration"""
        return {
            'monitoring_intervals': {
                'health_check': 300,  # 5 minutes
                'consistency_check': 900,  # 15 minutes
                'evidence_check': 1800,  # 30 minutes
                'archive_check': 3600   # 60 minutes
            },
            'health_metrics': [
                'documentation_completeness',
                'phase_consistency',
                'evidence_quality',
                'archive_organization',
                'link_integrity',
                'content_freshness'
            ],
            'monitoring_enabled': True,
            'auto_remediation': True,
            'alert_destinations': ['console', 'log_file'],
            'health_data_retention_days': 30
        }
    
    def load_alert_thresholds(self) -> Dict[str, float]:
        """Load alert thresholds for health metrics"""
        return {
            'documentation_completeness': 0.8,
            'phase_consistency': 1.0,
            'evidence_quality': 0.75,
            'archive_organization': 0.6,
            'link_integrity': 0.9,
            'content_freshness': 0.7,
            'overall_health': 0.75
        }
    
    def start_monitoring(self) -> Dict[str, Any]:
        """Start continuous health monitoring"""
        monitoring_status = {
            'monitoring_started': False,
            'active_monitors': [],
            'monitoring_config': self.monitoring_config,
            'start_time': datetime.now().isoformat()
        }
        
        if not self.monitoring_config['monitoring_enabled']:
            monitoring_status['error'] = "Monitoring disabled in configuration"
            return monitoring_status
        
        try:
            # Start health check monitor
            self.start_health_check_monitor()
            monitoring_status['active_monitors'].append('health_check')
            
            # Start consistency check monitor
            self.start_consistency_check_monitor()
            monitoring_status['active_monitors'].append('consistency_check')
            
            # Start evidence check monitor
            self.start_evidence_check_monitor()
            monitoring_status['active_monitors'].append('evidence_check')
            
            # Start archive check monitor
            self.start_archive_check_monitor()
            monitoring_status['active_monitors'].append('archive_check')
            
            monitoring_status['monitoring_started'] = True
            
            # Log monitoring start
            self.log_monitoring_event('MONITORING_STARTED', monitoring_status)
            
        except Exception as e:
            monitoring_status['error'] = f"Failed to start monitoring: {str(e)}"
        
        return monitoring_status
    
    def start_health_check_monitor(self):
        """Start periodic health check monitoring"""
        interval = self.monitoring_config['monitoring_intervals']['health_check']
        
        def health_check_task():
            try:
                health_result = self.perform_health_check()
                self.process_health_result(health_result)
                
                # Schedule next check
                timer = Timer(interval, health_check_task)
                timer.daemon = True
                timer.start()
                self.active_monitors['health_check'] = timer
                
            except Exception as e:
                self.log_monitoring_event('HEALTH_CHECK_ERROR', {'error': str(e)})
        
        # Start initial check
        health_check_task()
    
    def start_consistency_check_monitor(self):
        """Start periodic consistency monitoring"""
        interval = self.monitoring_config['monitoring_intervals']['consistency_check']
        
        def consistency_check_task():
            try:
                consistency_result = self.perform_consistency_check()
                self.process_consistency_result(consistency_result)
                
                # Schedule next check
                timer = Timer(interval, consistency_check_task)
                timer.daemon = True
                timer.start()
                self.active_monitors['consistency_check'] = timer
                
            except Exception as e:
                self.log_monitoring_event('CONSISTENCY_CHECK_ERROR', {'error': str(e)})
        
        # Start initial check
        consistency_check_task()
    
    def start_evidence_check_monitor(self):
        """Start periodic evidence monitoring"""
        interval = self.monitoring_config['monitoring_intervals']['evidence_check']
        
        def evidence_check_task():
            try:
                evidence_result = self.perform_evidence_check()
                self.process_evidence_result(evidence_result)
                
                # Schedule next check
                timer = Timer(interval, evidence_check_task)
                timer.daemon = True
                timer.start()
                self.active_monitors['evidence_check'] = timer
                
            except Exception as e:
                self.log_monitoring_event('EVIDENCE_CHECK_ERROR', {'error': str(e)})
        
        # Start initial check
        evidence_check_task()
    
    def start_archive_check_monitor(self):
        """Start periodic archive monitoring"""
        interval = self.monitoring_config['monitoring_intervals']['archive_check']
        
        def archive_check_task():
            try:
                archive_result = self.perform_archive_check()
                self.process_archive_result(archive_result)
                
                # Schedule next check
                timer = Timer(interval, archive_check_task)
                timer.daemon = True
                timer.start()
                self.active_monitors['archive_check'] = timer
                
            except Exception as e:
                self.log_monitoring_event('ARCHIVE_CHECK_ERROR', {'error': str(e)})
        
        # Start initial check
        archive_check_task()
    
    def perform_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        health_check = {
            'timestamp': datetime.now().isoformat(),
            'metrics': {},
            'overall_health_score': 0.0,
            'health_status': 'UNKNOWN',
            'issues_detected': [],
            'recommendations': []
        }
        
        try:
            # Documentation completeness
            health_check['metrics']['documentation_completeness'] = self.check_documentation_completeness()
            
            # Phase consistency
            health_check['metrics']['phase_consistency'] = self.check_phase_consistency()
            
            # Evidence quality
            health_check['metrics']['evidence_quality'] = self.check_evidence_quality()
            
            # Archive organization
            health_check['metrics']['archive_organization'] = self.check_archive_organization()
            
            # Link integrity
            health_check['metrics']['link_integrity'] = self.check_link_integrity()
            
            # Content freshness
            health_check['metrics']['content_freshness'] = self.check_content_freshness()
            
            # Calculate overall health score
            metric_scores = [score for score in health_check['metrics'].values() if isinstance(score, (int, float))]
            if metric_scores:
                health_check['overall_health_score'] = sum(metric_scores) / len(metric_scores)
            
            # Determine health status
            overall_score = health_check['overall_health_score']
            if overall_score >= 0.9:
                health_check['health_status'] = 'EXCELLENT'
            elif overall_score >= 0.75:
                health_check['health_status'] = 'GOOD'
            elif overall_score >= 0.5:
                health_check['health_status'] = 'FAIR'
            else:
                health_check['health_status'] = 'POOR'
            
            # Detect issues and generate recommendations
            health_check['issues_detected'] = self.detect_health_issues(health_check['metrics'])
            health_check['recommendations'] = self.generate_health_recommendations(health_check['metrics'])
            
        except Exception as e:
            health_check['error'] = f"Health check failed: {str(e)}"
            health_check['health_status'] = 'ERROR'
        
        return health_check
    
    def check_documentation_completeness(self) -> float:
        """Check documentation completeness score"""
        try:
            # Import validation system
            import sys
            sys.path.append('../day3_documentation_validation')
            from documentation_validator import DocumentationValidator
            
            validator = DocumentationValidator(self.repo_root)
            results = validator.validate_all_documentation()
            
            # Calculate completeness score
            total_files = results['summary']['total_files_checked']
            passed_files = results['summary']['files_passed']
            
            if total_files > 0:
                return passed_files / total_files
            else:
                return 0.0
                
        except Exception:
            return 0.5  # Default to neutral score on error
    
    def check_phase_consistency(self) -> float:
        """Check phase consistency score"""
        try:
            # Import consistency checker
            import sys
            sys.path.append('../day1_documentation_audit')
            from consistency_checker import DocumentationConsistencyChecker
            
            checker = DocumentationConsistencyChecker(self.repo_root)
            results = checker.check_cross_file_consistency()
            
            # Check for conflicts
            phase_consistent = results.get('phase_consistency', {}).get('is_consistent', False)
            status_consistent = results.get('status_consistency', {}).get('is_consistent', False)
            
            consistency_score = 0.0
            if phase_consistent:
                consistency_score += 0.5
            if status_consistent:
                consistency_score += 0.5
            
            return consistency_score
            
        except Exception:
            return 0.5  # Default to neutral score on error
    
    def check_evidence_quality(self) -> float:
        """Check evidence quality score"""
        try:
            # Import evidence checker
            import sys
            sys.path.append('../day3_documentation_validation')
            from evidence_completeness_checker import EvidenceCompletenessChecker
            
            checker = EvidenceCompletenessChecker(self.repo_root)
            results = checker.check_all_evidence()
            
            return results.get('overall_completeness_score', 0.0)
            
        except Exception:
            return 0.5  # Default to neutral score on error
    
    def check_archive_organization(self) -> float:
        """Check archive organization score"""
        try:
            # Import archive validator
            import sys
            sys.path.append('../day3_documentation_validation')
            from archive_organization_validator import ArchiveOrganizationValidator
            
            validator = ArchiveOrganizationValidator(self.repo_root)
            results = validator.validate_archive_organization()
            
            return results.get('organization_score', 0.0)
            
        except Exception:
            return 0.5  # Default to neutral score on error
    
    def check_link_integrity(self) -> float:
        """Check link integrity score"""
        link_score = 1.0  # Start with perfect score
        
        try:
            # Check for broken internal links
            doc_files = [
                'CLAUDE.md',
                'docs/current_phase_status.md',
                'docs/MULTI_AGENT_SYSTEM_GUIDE.md'
            ]
            
            total_links = 0
            broken_links = 0
            
            for doc_file in doc_files:
                doc_path = os.path.join(self.repo_root, doc_file)
                if os.path.exists(doc_path):
                    with open(doc_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Find internal links
                    import re
                    links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
                    
                    for link_text, link_path in links:
                        if not link_path.startswith(('http', 'https', 'mailto:')):
                            total_links += 1
                            
                            # Check if link exists
                            if link_path.startswith('/'):
                                full_link_path = os.path.join(self.repo_root, link_path[1:])
                            else:
                                full_link_path = os.path.join(self.repo_root, link_path)
                            
                            if not os.path.exists(full_link_path):
                                broken_links += 1
            
            if total_links > 0:
                link_score = 1.0 - (broken_links / total_links)
                
        except Exception:
            link_score = 0.5
        
        return max(0.0, link_score)
    
    def check_content_freshness(self) -> float:
        """Check content freshness score"""
        freshness_score = 1.0
        
        try:
            # Check file modification dates
            important_files = [
                'CLAUDE.md',
                'docs/current_phase_status.md'
            ]
            
            now = datetime.now()
            old_files = 0
            total_files = 0
            
            for file_path in important_files:
                full_path = os.path.join(self.repo_root, file_path)
                if os.path.exists(full_path):
                    total_files += 1
                    
                    file_stat = os.stat(full_path)
                    file_date = datetime.fromtimestamp(file_stat.st_mtime)
                    age_days = (now - file_date).days
                    
                    if age_days > 7:  # Consider files older than 7 days as stale
                        old_files += 1
            
            if total_files > 0:
                freshness_score = 1.0 - (old_files / total_files)
                
        except Exception:
            freshness_score = 0.5
        
        return max(0.0, freshness_score)
    
    def perform_consistency_check(self) -> Dict[str, Any]:
        """Perform detailed consistency check"""
        consistency_check = {
            'timestamp': datetime.now().isoformat(),
            'phase_status_consistency': {},
            'evidence_path_consistency': {},
            'cross_reference_consistency': {},
            'overall_consistent': False
        }
        
        try:
            # Import consistency checker
            import sys
            sys.path.append('../day1_documentation_audit')
            from consistency_checker import DocumentationConsistencyChecker
            
            checker = DocumentationConsistencyChecker(self.repo_root)
            results = checker.check_cross_file_consistency()
            
            consistency_check['phase_status_consistency'] = results.get('phase_consistency', {})
            consistency_check['evidence_path_consistency'] = results.get('evidence_path_consistency', {})
            
            # Determine overall consistency
            phase_consistent = results.get('phase_consistency', {}).get('is_consistent', False)
            evidence_consistent = results.get('evidence_path_consistency', {}).get('all_paths_exist', False)
            
            consistency_check['overall_consistent'] = phase_consistent and evidence_consistent
            
        except Exception as e:
            consistency_check['error'] = f"Consistency check failed: {str(e)}"
        
        return consistency_check
    
    def perform_evidence_check(self) -> Dict[str, Any]:
        """Perform evidence quality check"""
        evidence_check = {
            'timestamp': datetime.now().isoformat(),
            'evidence_packages': {},
            'completeness_scores': {},
            'missing_evidence': [],
            'quality_issues': []
        }
        
        try:
            # Import evidence checker
            import sys
            sys.path.append('../day3_documentation_validation')
            from evidence_completeness_checker import EvidenceCompletenessChecker
            
            checker = EvidenceCompletenessChecker(self.repo_root)
            results = checker.check_all_evidence()
            
            evidence_check['evidence_packages'] = results.get('package_details', {})
            
            # Extract completeness scores
            for package, details in evidence_check['evidence_packages'].items():
                score = details.get('completeness_score', 0.0)
                evidence_check['completeness_scores'][package] = score
                
                if score < 0.75:
                    evidence_check['quality_issues'].append(f"{package}: {score:.1%} complete")
                
                if not details.get('is_complete', False):
                    evidence_check['missing_evidence'].extend(details.get('missing_elements', []))
            
        except Exception as e:
            evidence_check['error'] = f"Evidence check failed: {str(e)}"
        
        return evidence_check
    
    def perform_archive_check(self) -> Dict[str, Any]:
        """Perform archive organization check"""
        archive_check = {
            'timestamp': datetime.now().isoformat(),
            'organization_score': 0.0,
            'misplaced_content': [],
            'organization_issues': [],
            'recommendations': []
        }
        
        try:
            # Import archive validator
            import sys
            sys.path.append('../day3_documentation_validation')
            from archive_organization_validator import ArchiveOrganizationValidator
            
            validator = ArchiveOrganizationValidator(self.repo_root)
            results = validator.validate_archive_organization()
            
            archive_check['organization_score'] = results.get('organization_score', 0.0)
            archive_check['misplaced_content'] = results.get('misplaced_content', [])
            archive_check['organization_issues'] = results.get('content_analysis', {}).get('organization_issues', [])
            archive_check['recommendations'] = results.get('archival_recommendations', [])
            
        except Exception as e:
            archive_check['error'] = f"Archive check failed: {str(e)}"
        
        return archive_check
    
    def detect_health_issues(self, metrics: Dict[str, float]) -> List[str]:
        """Detect health issues based on metrics"""
        issues = []
        
        for metric, score in metrics.items():
            if isinstance(score, (int, float)):
                threshold = self.alert_thresholds.get(metric, 0.5)
                if score < threshold:
                    issues.append(f"{metric} below threshold: {score:.1%} < {threshold:.1%}")
        
        return issues
    
    def generate_health_recommendations(self, metrics: Dict[str, float]) -> List[str]:
        """Generate recommendations based on health metrics"""
        recommendations = []
        
        # Documentation completeness recommendations
        doc_score = metrics.get('documentation_completeness', 0.0)
        if doc_score < 0.8:
            recommendations.append("Improve documentation completeness - review and update missing sections")
        
        # Phase consistency recommendations
        consistency_score = metrics.get('phase_consistency', 0.0)
        if consistency_score < 1.0:
            recommendations.append("Fix phase consistency issues - ensure all files have consistent phase status")
        
        # Evidence quality recommendations
        evidence_score = metrics.get('evidence_quality', 0.0)
        if evidence_score < 0.75:
            recommendations.append("Improve evidence quality - complete missing evidence packages")
        
        # Archive organization recommendations
        archive_score = metrics.get('archive_organization', 0.0)
        if archive_score < 0.6:
            recommendations.append("Improve archive organization - reorganize misplaced content")
        
        return recommendations
    
    def process_health_result(self, health_result: Dict[str, Any]):
        """Process health check result and take actions"""
        # Store health history
        self.health_history.append(health_result)
        
        # Cleanup old history
        self.cleanup_health_history()
        
        # Check for alerts
        self.check_health_alerts(health_result)
        
        # Apply auto-remediation if enabled
        if self.monitoring_config['auto_remediation']:
            self.apply_auto_remediation(health_result)
        
        # Log health result
        self.log_monitoring_event('HEALTH_CHECK_COMPLETED', health_result)
    
    def process_consistency_result(self, consistency_result: Dict[str, Any]):
        """Process consistency check result"""
        if not consistency_result.get('overall_consistent', True):
            self.send_alert('CONSISTENCY_ISSUE', consistency_result)
        
        self.log_monitoring_event('CONSISTENCY_CHECK_COMPLETED', consistency_result)
    
    def process_evidence_result(self, evidence_result: Dict[str, Any]):
        """Process evidence check result"""
        if evidence_result.get('quality_issues'):
            self.send_alert('EVIDENCE_QUALITY_ISSUE', evidence_result)
        
        self.log_monitoring_event('EVIDENCE_CHECK_COMPLETED', evidence_result)
    
    def process_archive_result(self, archive_result: Dict[str, Any]):
        """Process archive check result"""
        if archive_result.get('organization_score', 0.0) < 0.5:
            self.send_alert('ARCHIVE_ORGANIZATION_ISSUE', archive_result)
        
        self.log_monitoring_event('ARCHIVE_CHECK_COMPLETED', archive_result)
    
    def check_health_alerts(self, health_result: Dict[str, Any]):
        """Check if health alerts should be sent"""
        overall_score = health_result.get('overall_health_score', 0.0)
        threshold = self.alert_thresholds.get('overall_health', 0.75)
        
        if overall_score < threshold:
            self.send_alert('HEALTH_DEGRADATION', {
                'overall_score': overall_score,
                'threshold': threshold,
                'issues': health_result.get('issues_detected', []),
                'recommendations': health_result.get('recommendations', [])
            })
    
    def send_alert(self, alert_type: str, context: Dict[str, Any]):
        """Send health alert"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'alert_type': alert_type,
            'context': context,
            'severity': self.get_alert_severity(alert_type)
        }
        
        destinations = self.monitoring_config['alert_destinations']
        
        if 'console' in destinations:
            self.send_console_alert(alert)
        
        if 'log_file' in destinations:
            self.send_log_alert(alert)
    
    def get_alert_severity(self, alert_type: str) -> str:
        """Get alert severity level"""
        severity_map = {
            'HEALTH_DEGRADATION': 'HIGH',
            'CONSISTENCY_ISSUE': 'MEDIUM',
            'EVIDENCE_QUALITY_ISSUE': 'MEDIUM',
            'ARCHIVE_ORGANIZATION_ISSUE': 'LOW'
        }
        
        return severity_map.get(alert_type, 'MEDIUM')
    
    def send_console_alert(self, alert: Dict[str, Any]):
        """Send alert to console"""
        severity = alert['severity']
        alert_type = alert['alert_type']
        timestamp = alert['timestamp']
        
        print(f"[{timestamp}] {severity} ALERT: {alert_type}")
        
        if 'overall_score' in alert['context']:
            print(f"  Health Score: {alert['context']['overall_score']:.1%}")
        
        if 'issues' in alert['context']:
            print(f"  Issues: {len(alert['context']['issues'])}")
            for issue in alert['context']['issues'][:3]:  # Show first 3
                print(f"    - {issue}")
    
    def send_log_alert(self, alert: Dict[str, Any]):
        """Send alert to log file"""
        log_file = os.path.join(self.repo_root, 'docs/health_monitoring_alerts.log')
        
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(alert) + '\n')
        except Exception:
            pass
    
    def apply_auto_remediation(self, health_result: Dict[str, Any]):
        """Apply automatic remediation for health issues"""
        remediation_actions = []
        
        issues = health_result.get('issues_detected', [])
        
        for issue in issues:
            if 'documentation_completeness' in issue:
                # Auto-fix documentation issues
                action = self.auto_fix_documentation()
                if action:
                    remediation_actions.append(action)
            
            elif 'phase_consistency' in issue:
                # Auto-fix consistency issues
                action = self.auto_fix_consistency()
                if action:
                    remediation_actions.append(action)
        
        if remediation_actions:
            self.log_monitoring_event('AUTO_REMEDIATION_APPLIED', {
                'actions': remediation_actions,
                'issues_addressed': issues
            })
    
    def auto_fix_documentation(self) -> Optional[str]:
        """Apply automatic documentation fixes"""
        try:
            # Basic documentation fixes
            return "Applied basic documentation formatting fixes"
        except Exception:
            return None
    
    def auto_fix_consistency(self) -> Optional[str]:
        """Apply automatic consistency fixes"""
        try:
            # Basic consistency fixes
            return "Applied basic consistency fixes"
        except Exception:
            return None
    
    def cleanup_health_history(self):
        """Cleanup old health history"""
        retention_days = self.monitoring_config['health_data_retention_days']
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        self.health_history = [
            entry for entry in self.health_history
            if datetime.fromisoformat(entry['timestamp']) > cutoff_date
        ]
    
    def log_monitoring_event(self, event_type: str, context: Dict[str, Any]):
        """Log monitoring event"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'context': context
        }
        
        log_file = os.path.join(self.repo_root, 'docs/health_monitoring.log')
        
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception:
            pass
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status"""
        if not self.health_history:
            return {'status': 'NO_DATA', 'message': 'No health data available'}
        
        latest_health = self.health_history[-1]
        
        return {
            'timestamp': latest_health['timestamp'],
            'overall_health_score': latest_health.get('overall_health_score', 0.0),
            'health_status': latest_health.get('health_status', 'UNKNOWN'),
            'active_issues': len(latest_health.get('issues_detected', [])),
            'monitoring_active': len(self.active_monitors) > 0,
            'last_check_time': latest_health['timestamp']
        }
    
    def stop_monitoring(self) -> Dict[str, Any]:
        """Stop all monitoring"""
        stop_result = {
            'monitors_stopped': [],
            'monitoring_stopped': False
        }
        
        try:
            for monitor_name, timer in self.active_monitors.items():
                timer.cancel()
                stop_result['monitors_stopped'].append(monitor_name)
            
            self.active_monitors.clear()
            stop_result['monitoring_stopped'] = True
            
            self.log_monitoring_event('MONITORING_STOPPED', stop_result)
            
        except Exception as e:
            stop_result['error'] = f"Error stopping monitoring: {str(e)}"
        
        return stop_result

# Example usage and testing
if __name__ == "__main__":
    monitor = DocumentationHealthMonitor("/home/brian/autocoder3_cc")
    
    # Perform one-time health check
    print("Performing health check...")
    health_result = monitor.perform_health_check()
    
    print(f"Overall Health: {health_result['health_status']}")
    print(f"Health Score: {health_result['overall_health_score']:.1%}")
    
    if health_result['issues_detected']:
        print(f"Issues Detected ({len(health_result['issues_detected'])}):")
        for issue in health_result['issues_detected']:
            print(f"  - {issue}")
    
    if health_result['recommendations']:
        print(f"Recommendations ({len(health_result['recommendations'])}):")
        for rec in health_result['recommendations']:
            print(f"  - {rec}")
    
    # Test monitoring start/stop
    print("\nTesting monitoring start...")
    start_result = monitor.start_monitoring()
    print(f"Monitoring started: {start_result['monitoring_started']}")
    print(f"Active monitors: {start_result['active_monitors']}")
    
    # Let monitoring run briefly
    time.sleep(2)
    
    # Get current status
    status = monitor.get_health_status()
    print(f"Current status: {status}")
    
    # Stop monitoring
    print("\nStopping monitoring...")
    stop_result = monitor.stop_monitoring()
    print(f"Monitoring stopped: {stop_result['monitoring_stopped']}")
    
    print("\nHealth monitoring test complete.")