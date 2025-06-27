import os
import shutil
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path

class AutomatedArchiveSystem:
    """Automated system for archiving outdated content and maintaining repository organization"""
    
    def __init__(self, repo_root: str):
        self.repo_root = repo_root
        self.archive_root = os.path.join(repo_root, 'archive')
        self.archive_config = self.load_archive_config()
        self.dry_run = False  # Set to True for testing without actual moves
        
    def load_archive_config(self) -> Dict[str, Any]:
        """Load automated archive configuration"""
        return {
            'archive_rules': {
                'outdated_age_days': 30,
                'temp_file_patterns': ['*.tmp', '*.temp', '*~', '*.bak', '*.swp'],
                'debug_file_patterns': ['debug_*', '*_debug.*', 'test_output.*'],
                'outdated_example_patterns': ['old_*', 'deprecated_*', 'legacy_*'],
                'superseded_doc_patterns': ['*_old.*', '*_backup.*', '*_v1.*'],
                'log_file_patterns': ['*.log', '*.out', 'output_*']
            },
            'archive_categories': {
                'temp_files': 'archive/temp_files',
                'debug_output': 'archive/debug_output', 
                'outdated_docs': 'archive/documentation/outdated',
                'old_examples': 'archive/old_examples',
                'test_outputs': 'archive/test_outputs',
                'superseded_specs': 'archive/old_specs',
                'development_scratch': 'archive/dev_scratch'
            },
            'preservation_rules': {
                'preserve_current_phase_evidence': True,
                'preserve_active_documentation': True,
                'preserve_main_implementation': True,
                'preserve_recent_files_days': 7,
                'preserve_critical_files': [
                    'CLAUDE.md',
                    'README.md',
                    'docs/current_phase_status.md',
                    'docs/MULTI_AGENT_SYSTEM_GUIDE.md'
                ]
            },
            'automation_settings': {
                'auto_archive_enabled': True,
                'manual_approval_required': True,
                'backup_before_archive': True,
                'verification_checks': True,
                'undo_capability': True
            }
        }
    
    def execute_automated_archival(self, target_types: List[str] = None) -> Dict[str, Any]:
        """Execute automated archival process"""
        archival_result = {
            'timestamp': datetime.now().isoformat(),
            'target_types': target_types or ['all'],
            'scan_results': {},
            'archive_operations': [],
            'files_processed': 0,
            'files_archived': 0,
            'errors': [],
            'dry_run': self.dry_run,
            'summary': {}
        }
        
        try:
            if not self.archive_config['automation_settings']['auto_archive_enabled']:
                archival_result['errors'].append("Automated archival is disabled")
                return archival_result
            
            # Scan for archival candidates
            scan_results = self.scan_for_archival_candidates(target_types)
            archival_result['scan_results'] = scan_results
            
            # Process each category
            for category, candidates in scan_results.items():
                if candidates:
                    category_result = self.process_archival_category(category, candidates)
                    archival_result['archive_operations'].append(category_result)
                    
                    archival_result['files_processed'] += category_result['files_processed']
                    archival_result['files_archived'] += category_result['files_archived']
                    archival_result['errors'].extend(category_result['errors'])
            
            # Generate summary
            archival_result['summary'] = self.generate_archival_summary(archival_result)
            
            # Log archival activity
            self.log_archival_activity(archival_result)
            
        except Exception as e:
            archival_result['errors'].append(f"Automated archival failed: {str(e)}")
        
        return archival_result
    
    def scan_for_archival_candidates(self, target_types: List[str] = None) -> Dict[str, List[str]]:
        """Scan repository for files that should be archived"""
        candidates = {
            'temp_files': [],
            'debug_output': [],
            'outdated_docs': [],
            'old_examples': [],
            'test_outputs': [],
            'superseded_specs': [],
            'development_scratch': []
        }
        
        # If specific types requested, only scan those
        if target_types and 'all' not in target_types:
            candidates = {k: v for k, v in candidates.items() if k in target_types}
        
        try:
            # Scan repository for candidates
            for root, dirs, files in os.walk(self.repo_root):
                # Skip .git and archive directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'archive']
                
                rel_root = os.path.relpath(root, self.repo_root)
                
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_file_path = os.path.relpath(file_path, self.repo_root)
                    
                    # Skip preserved files
                    if self.should_preserve_file(rel_file_path):
                        continue
                    
                    # Categorize file for archival
                    category = self.categorize_for_archival(file, file_path, rel_root)
                    if category and category in candidates:
                        candidates[category].append(rel_file_path)
        
        except Exception as e:
            print(f"Error scanning for archival candidates: {e}")
        
        return candidates
    
    def should_preserve_file(self, rel_file_path: str) -> bool:
        """Check if file should be preserved from archival"""
        preserve_rules = self.archive_config['preservation_rules']
        
        # Check critical files
        if rel_file_path in preserve_rules['preserve_critical_files']:
            return True
        
        # Check current phase evidence
        if preserve_rules['preserve_current_phase_evidence']:
            if rel_file_path.startswith('evidence/phase') and self.is_current_phase_evidence(rel_file_path):
                return True
        
        # Check active documentation
        if preserve_rules['preserve_active_documentation']:
            if rel_file_path.startswith('docs/') and not self.is_outdated_doc(rel_file_path):
                return True
        
        # Check main implementation
        if preserve_rules['preserve_main_implementation']:
            if rel_file_path.startswith(('autocoder/', 'blueprint_language/')) and not self.is_deprecated_implementation(rel_file_path):
                return True
        
        # Check recent files
        recent_days = preserve_rules['preserve_recent_files_days']
        if self.is_recent_file(rel_file_path, recent_days):
            return True
        
        return False
    
    def is_current_phase_evidence(self, file_path: str) -> bool:
        """Check if file is current phase evidence"""
        # Get current phase number from documentation
        current_phase = self.get_current_phase_number()
        if current_phase:
            return f'phase{current_phase}' in file_path
        return True  # Preserve if uncertain
    
    def get_current_phase_number(self) -> Optional[int]:
        """Get current phase number from documentation"""
        try:
            claude_md_path = os.path.join(self.repo_root, 'CLAUDE.md')
            if os.path.exists(claude_md_path):
                with open(claude_md_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                import re
                match = re.search(r'ACTIVE PHASE.*?Phase (\d+)', content, re.IGNORECASE)
                if match:
                    return int(match.group(1))
        except Exception:
            pass
        return None
    
    def is_outdated_doc(self, file_path: str) -> bool:
        """Check if documentation file is outdated"""
        outdated_patterns = self.archive_config['archive_rules']['superseded_doc_patterns']
        return any(self.matches_pattern(file_path, pattern) for pattern in outdated_patterns)
    
    def is_deprecated_implementation(self, file_path: str) -> bool:
        """Check if implementation file is deprecated"""
        deprecated_indicators = ['deprecated', 'legacy', 'old', 'backup']
        return any(indicator in file_path.lower() for indicator in deprecated_indicators)
    
    def is_recent_file(self, rel_file_path: str, days: int) -> bool:
        """Check if file was modified recently"""
        try:
            full_path = os.path.join(self.repo_root, rel_file_path)
            if os.path.exists(full_path):
                file_stat = os.stat(full_path)
                file_age = (datetime.now().timestamp() - file_stat.st_mtime) / (24 * 3600)
                return file_age <= days
        except Exception:
            pass
        return True  # Preserve if uncertain
    
    def categorize_for_archival(self, filename: str, file_path: str, rel_root: str) -> Optional[str]:
        """Categorize file for appropriate archival"""
        rules = self.archive_config['archive_rules']
        
        # Check temp files
        if any(self.matches_pattern(filename, pattern) for pattern in rules['temp_file_patterns']):
            return 'temp_files'
        
        # Check debug files
        if any(self.matches_pattern(filename, pattern) for pattern in rules['debug_file_patterns']):
            return 'debug_output'
        
        # Check log files
        if any(self.matches_pattern(filename, pattern) for pattern in rules['log_file_patterns']):
            return 'test_outputs'
        
        # Check outdated examples
        if any(self.matches_pattern(filename, pattern) for pattern in rules['outdated_example_patterns']):
            return 'old_examples'
        
        # Check superseded docs
        if any(self.matches_pattern(filename, pattern) for pattern in rules['superseded_doc_patterns']):
            return 'outdated_docs'
        
        # Check by file age
        if self.is_old_file(file_path, rules['outdated_age_days']):
            # Categorize old files by location
            if rel_root.startswith('examples'):
                return 'old_examples'
            elif rel_root.startswith(('docs', 'documentation')):
                return 'outdated_docs'
            elif rel_root.startswith(('test', 'tests')):
                return 'test_outputs'
            else:
                return 'development_scratch'
        
        return None
    
    def matches_pattern(self, filename: str, pattern: str) -> bool:
        """Check if filename matches pattern"""
        import fnmatch
        return fnmatch.fnmatch(filename, pattern)
    
    def is_old_file(self, file_path: str, max_age_days: int) -> bool:
        """Check if file is older than specified days"""
        try:
            file_stat = os.stat(file_path)
            file_age = (datetime.now().timestamp() - file_stat.st_mtime) / (24 * 3600)
            return file_age > max_age_days
        except Exception:
            return False
    
    def process_archival_category(self, category: str, candidates: List[str]) -> Dict[str, Any]:
        """Process archival for a specific category"""
        category_result = {
            'category': category,
            'candidates_found': len(candidates),
            'files_processed': 0,
            'files_archived': 0,
            'files_skipped': 0,
            'errors': [],
            'archive_location': self.archive_config['archive_categories'].get(category, f'archive/{category}'),
            'operations': []
        }
        
        try:
            # Create archive directory
            archive_dir = os.path.join(self.repo_root, category_result['archive_location'])
            if not self.dry_run:
                os.makedirs(archive_dir, exist_ok=True)
            
            # Process each candidate
            for candidate in candidates:
                category_result['files_processed'] += 1
                
                try:
                    operation_result = self.archive_single_file(candidate, archive_dir, category)
                    category_result['operations'].append(operation_result)
                    
                    if operation_result['archived']:
                        category_result['files_archived'] += 1
                    else:
                        category_result['files_skipped'] += 1
                        
                except Exception as e:
                    error_msg = f"Error archiving {candidate}: {str(e)}"
                    category_result['errors'].append(error_msg)
                    category_result['files_skipped'] += 1
        
        except Exception as e:
            category_result['errors'].append(f"Category processing error: {str(e)}")
        
        return category_result
    
    def archive_single_file(self, rel_file_path: str, archive_dir: str, category: str) -> Dict[str, Any]:
        """Archive a single file"""
        operation = {
            'source_file': rel_file_path,
            'archive_dir': archive_dir,
            'category': category,
            'archived': False,
            'backup_created': False,
            'error': None,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            source_path = os.path.join(self.repo_root, rel_file_path)
            
            if not os.path.exists(source_path):
                operation['error'] = "Source file does not exist"
                return operation
            
            # Generate archive filename
            filename = os.path.basename(rel_file_path)
            archive_filename = self.generate_archive_filename(filename, category)
            archive_path = os.path.join(archive_dir, archive_filename)
            
            # Create backup if required
            if self.archive_config['automation_settings']['backup_before_archive']:
                backup_result = self.create_backup(source_path)
                operation['backup_created'] = backup_result
            
            # Perform verification checks
            if self.archive_config['automation_settings']['verification_checks']:
                verification_result = self.verify_archival_safety(source_path, rel_file_path)
                if not verification_result['safe']:
                    operation['error'] = f"Verification failed: {verification_result['reason']}"
                    return operation
            
            # Perform archival
            if not self.dry_run:
                # Check for manual approval if required
                if self.archive_config['automation_settings']['manual_approval_required']:
                    if not self.get_archival_approval(rel_file_path, category):
                        operation['error'] = "Manual approval not granted"
                        return operation
                
                # Move file to archive
                shutil.move(source_path, archive_path)
                operation['archived'] = True
                operation['archive_path'] = archive_path
            else:
                # Dry run - just log what would happen
                operation['archived'] = True
                operation['archive_path'] = archive_path
                operation['dry_run'] = True
        
        except Exception as e:
            operation['error'] = str(e)
        
        return operation
    
    def generate_archive_filename(self, original_filename: str, category: str) -> str:
        """Generate filename for archived file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name, ext = os.path.splitext(original_filename)
        
        # Add timestamp to avoid conflicts
        return f"{name}_{timestamp}{ext}"
    
    def create_backup(self, source_path: str) -> bool:
        """Create backup of file before archiving"""
        try:
            backup_dir = os.path.join(self.archive_root, 'backups')
            if not self.dry_run:
                os.makedirs(backup_dir, exist_ok=True)
                
                backup_filename = f"{os.path.basename(source_path)}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                backup_path = os.path.join(backup_dir, backup_filename)
                
                shutil.copy2(source_path, backup_path)
            
            return True
        except Exception:
            return False
    
    def verify_archival_safety(self, source_path: str, rel_file_path: str) -> Dict[str, Any]:
        """Verify that archiving this file is safe"""
        verification = {
            'safe': True,
            'reason': None,
            'checks': {}
        }
        
        try:
            # Check if file is referenced in important docs
            if self.is_file_referenced_in_docs(rel_file_path):
                verification['checks']['referenced_in_docs'] = True
                verification['safe'] = False
                verification['reason'] = "File is referenced in documentation"
                return verification
            
            # Check if file is part of active implementation
            if self.is_part_of_active_implementation(rel_file_path):
                verification['checks']['active_implementation'] = True
                verification['safe'] = False
                verification['reason'] = "File is part of active implementation"
                return verification
            
            # Check if file has dependencies
            if self.has_dependencies(source_path):
                verification['checks']['has_dependencies'] = True
                # This is a warning, not a blocker
            
            verification['checks']['all_passed'] = True
            
        except Exception as e:
            verification['safe'] = False
            verification['reason'] = f"Verification error: {str(e)}"
        
        return verification
    
    def is_file_referenced_in_docs(self, rel_file_path: str) -> bool:
        """Check if file is referenced in documentation"""
        important_docs = ['CLAUDE.md', 'docs/current_phase_status.md', 'README.md']
        
        for doc_file in important_docs:
            doc_path = os.path.join(self.repo_root, doc_file)
            if os.path.exists(doc_path):
                try:
                    with open(doc_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if rel_file_path in content or os.path.basename(rel_file_path) in content:
                        return True
                except Exception:
                    continue
        
        return False
    
    def is_part_of_active_implementation(self, rel_file_path: str) -> bool:
        """Check if file is part of active implementation"""
        active_paths = ['autocoder/', 'blueprint_language/', 'phases/']
        
        # Check if in active implementation directories
        if any(rel_file_path.startswith(path) for path in active_paths):
            # Additional check: not deprecated
            if not self.is_deprecated_implementation(rel_file_path):
                return True
        
        return False
    
    def has_dependencies(self, source_path: str) -> bool:
        """Check if file has dependencies (basic check)"""
        try:
            if source_path.endswith('.py'):
                with open(source_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Look for import statements that might indicate dependencies
                import_count = content.count('import ') + content.count('from ')
                return import_count > 5  # Arbitrary threshold
        except Exception:
            pass
        
        return False
    
    def get_archival_approval(self, rel_file_path: str, category: str) -> bool:
        """Get manual approval for archival (simulated for automation)"""
        # In a real implementation, this would:
        # - Check approval database
        # - Send notification for approval
        # - Wait for response
        # - Return approval status
        
        # For automation, we'll approve low-risk categories
        auto_approve_categories = ['temp_files', 'debug_output', 'test_outputs']
        
        if category in auto_approve_categories:
            return True
        
        # For other categories, require explicit approval
        # This could be configured per organization
        return False  # Default to requiring manual approval
    
    def generate_archival_summary(self, archival_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of archival operations"""
        summary = {
            'total_candidates_found': 0,
            'total_files_processed': archival_result['files_processed'],
            'total_files_archived': archival_result['files_archived'],
            'total_errors': len(archival_result['errors']),
            'archival_rate': 0.0,
            'categories_processed': [],
            'space_freed_estimate': 'Unknown',
            'recommendations': []
        }
        
        # Calculate totals
        for category, candidates in archival_result['scan_results'].items():
            summary['total_candidates_found'] += len(candidates)
            if candidates:
                summary['categories_processed'].append(category)
        
        # Calculate archival rate
        if summary['total_files_processed'] > 0:
            summary['archival_rate'] = archival_result['files_archived'] / summary['total_files_processed']
        
        # Generate recommendations
        if summary['total_errors'] > 0:
            summary['recommendations'].append("Review and fix archival errors")
        
        if summary['archival_rate'] < 0.5:
            summary['recommendations'].append("Many files could not be archived - review approval settings")
        
        if summary['total_candidates_found'] > 100:
            summary['recommendations'].append("Large number of candidates found - consider regular cleanup")
        
        return summary
    
    def log_archival_activity(self, archival_result: Dict[str, Any]):
        """Log archival activity for audit trail"""
        log_entry = {
            'timestamp': archival_result['timestamp'],
            'files_processed': archival_result['files_processed'],
            'files_archived': archival_result['files_archived'],
            'errors': len(archival_result['errors']),
            'dry_run': archival_result['dry_run'],
            'categories': list(archival_result['scan_results'].keys())
        }
        
        log_file = os.path.join(self.repo_root, 'docs/automated_archive.log')
        
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception:
            pass
    
    def restore_from_archive(self, archive_filename: str, original_location: str = None) -> Dict[str, Any]:
        """Restore file from archive"""
        restore_result = {
            'archive_filename': archive_filename,
            'original_location': original_location,
            'restored': False,
            'restore_path': None,
            'error': None
        }
        
        try:
            # Find file in archive
            archive_path = self.find_in_archive(archive_filename)
            if not archive_path:
                restore_result['error'] = "File not found in archive"
                return restore_result
            
            # Determine restore location
            if original_location:
                restore_path = os.path.join(self.repo_root, original_location)
            else:
                # Try to infer from archive location
                restore_path = self.infer_restore_location(archive_path)
            
            if not restore_path:
                restore_result['error'] = "Cannot determine restore location"
                return restore_result
            
            # Create restore directory if needed
            os.makedirs(os.path.dirname(restore_path), exist_ok=True)
            
            # Restore file
            shutil.copy2(archive_path, restore_path)
            restore_result['restored'] = True
            restore_result['restore_path'] = restore_path
            
        except Exception as e:
            restore_result['error'] = str(e)
        
        return restore_result
    
    def find_in_archive(self, filename: str) -> Optional[str]:
        """Find file in archive"""
        try:
            for root, dirs, files in os.walk(self.archive_root):
                for file in files:
                    if filename in file:  # Flexible matching
                        return os.path.join(root, file)
        except Exception:
            pass
        
        return None
    
    def infer_restore_location(self, archive_path: str) -> Optional[str]:
        """Infer original location from archive path"""
        # This is a simplified implementation
        # A real system would maintain metadata about original locations
        
        rel_archive_path = os.path.relpath(archive_path, self.archive_root)
        
        if rel_archive_path.startswith('old_examples'):
            return os.path.join(self.repo_root, 'examples', os.path.basename(archive_path))
        elif rel_archive_path.startswith('documentation'):
            return os.path.join(self.repo_root, 'docs', os.path.basename(archive_path))
        
        # Default to root
        return os.path.join(self.repo_root, os.path.basename(archive_path))
    
    def get_archive_statistics(self) -> Dict[str, Any]:
        """Get statistics about archived content"""
        stats = {
            'total_archived_files': 0,
            'archive_size_bytes': 0,
            'categories': {},
            'oldest_archived': None,
            'newest_archived': None
        }
        
        try:
            if os.path.exists(self.archive_root):
                for root, dirs, files in os.walk(self.archive_root):
                    for file in files:
                        file_path = os.path.join(root, file)
                        
                        stats['total_archived_files'] += 1
                        
                        # File size
                        try:
                            stats['archive_size_bytes'] += os.path.getsize(file_path)
                        except OSError:
                            pass
                        
                        # Category
                        category = os.path.relpath(root, self.archive_root).split(os.sep)[0]
                        if category not in stats['categories']:
                            stats['categories'][category] = 0
                        stats['categories'][category] += 1
                        
                        # Dates
                        try:
                            file_stat = os.stat(file_path)
                            file_date = datetime.fromtimestamp(file_stat.st_mtime)
                            
                            if stats['oldest_archived'] is None or file_date < stats['oldest_archived']:
                                stats['oldest_archived'] = file_date
                            
                            if stats['newest_archived'] is None or file_date > stats['newest_archived']:
                                stats['newest_archived'] = file_date
                        except OSError:
                            pass
        
        except Exception:
            pass
        
        return stats

# Example usage and testing
if __name__ == "__main__":
    archive_system = AutomatedArchiveSystem("/home/brian/autocoder3_cc")
    
    # Set to dry run for testing
    archive_system.dry_run = True
    
    print("Testing automated archive system...")
    
    # Execute automated archival
    result = archive_system.execute_automated_archival(['temp_files', 'debug_output'])
    
    print(f"Files scanned for archival:")
    for category, candidates in result['scan_results'].items():
        print(f"  {category}: {len(candidates)} candidates")
        if candidates:
            print(f"    Examples: {candidates[:3]}")
    
    print(f"\nArchival Summary:")
    print(f"  Files processed: {result['files_processed']}")
    print(f"  Files archived: {result['files_archived']}")
    print(f"  Errors: {len(result['errors'])}")
    print(f"  Dry run: {result['dry_run']}")
    
    if result['errors']:
        print(f"\nErrors encountered:")
        for error in result['errors'][:5]:
            print(f"  - {error}")
    
    # Get archive statistics
    stats = archive_system.get_archive_statistics()
    print(f"\nCurrent Archive Statistics:")
    print(f"  Total archived files: {stats['total_archived_files']}")
    print(f"  Archive size: {stats['archive_size_bytes']} bytes")
    print(f"  Categories: {list(stats['categories'].keys())}")
    
    # Save results
    with open("automated_archive_test_results.json", "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"\nAutomated archive system test complete.")
    print("Results saved to automated_archive_test_results.json")