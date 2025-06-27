import os
import json
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
from pathlib import Path

class ArchiveOrganizationValidator:
    """Validate proper organization and archival of repository content"""
    
    def __init__(self, repo_root: str):
        self.repo_root = repo_root
        self.archive_dir = os.path.join(repo_root, 'archive')
        self.organization_rules = self.load_organization_rules()
    
    def load_organization_rules(self) -> Dict[str, Any]:
        """Load rules for proper archive organization"""
        return {
            'archive_structure': {
                'required_subdirs': [
                    'documentation',
                    'old_examples', 
                    'test_scripts',
                    'old_docs'
                ],
                'optional_subdirs': [
                    'analysis',
                    'claude_md_archive',
                    'dev',
                    'old_specs',
                    'todo_nextsteps'
                ]
            },
            'archival_criteria': {
                'outdated_age_days': 30,
                'superseded_versions': True,
                'deprecated_examples': True,
                'old_test_scripts': True
            },
            'content_categories': {
                'documentation': {
                    'patterns': ['*.md', '*.txt'],
                    'keywords': ['doc', 'readme', 'guide', 'spec'],
                    'archive_location': 'archive/documentation/'
                },
                'examples': {
                    'patterns': ['examples/*', 'demo*', 'sample*'],
                    'keywords': ['example', 'demo', 'sample', 'tutorial'],
                    'archive_location': 'archive/old_examples/'
                },
                'test_scripts': {
                    'patterns': ['test_*', '*_test.py', 'tests/*'],
                    'keywords': ['test', 'validation', 'check'],
                    'archive_location': 'archive/test_scripts/'
                },
                'specifications': {
                    'patterns': ['*_spec.md', '*_specification.*'],
                    'keywords': ['spec', 'specification', 'requirement'],
                    'archive_location': 'archive/old_specs/'
                }
            },
            'active_content_indicators': {
                'current_phase_evidence': True,
                'main_implementation': True,
                'active_documentation': True,
                'recent_modifications': 7  # days
            }
        }
    
    def validate_archive_organization(self) -> Dict[str, Any]:
        """Validate overall archive organization"""
        validation_result = {
            'timestamp': datetime.now().isoformat(),
            'archive_exists': os.path.exists(self.archive_dir),
            'structure_validation': {},
            'content_analysis': {},
            'archival_recommendations': [],
            'misplaced_content': [],
            'orphaned_content': [],
            'organization_score': 0.0
        }
        
        if not validation_result['archive_exists']:
            validation_result['archival_recommendations'].append(
                "Create archive directory to organize historical content"
            )
            return validation_result
        
        # Validate archive structure
        validation_result['structure_validation'] = self.validate_archive_structure()
        
        # Analyze content organization
        validation_result['content_analysis'] = self.analyze_content_organization()
        
        # Find misplaced content
        validation_result['misplaced_content'] = self.find_misplaced_content()
        
        # Find orphaned content
        validation_result['orphaned_content'] = self.find_orphaned_content()
        
        # Generate recommendations
        validation_result['archival_recommendations'] = self.generate_archival_recommendations(validation_result)
        
        # Calculate organization score
        validation_result['organization_score'] = self.calculate_organization_score(validation_result)
        
        return validation_result
    
    def validate_archive_structure(self) -> Dict[str, Any]:
        """Validate the structure of the archive directory"""
        structure_result = {
            'required_dirs_present': {},
            'optional_dirs_present': {},
            'unexpected_dirs': [],
            'total_subdirs': 0,
            'structure_score': 0.0
        }
        
        try:
            archive_items = os.listdir(self.archive_dir)
            subdirs = [item for item in archive_items 
                      if os.path.isdir(os.path.join(self.archive_dir, item))]
            
            structure_result['total_subdirs'] = len(subdirs)
            
            # Check required directories
            required_dirs = self.organization_rules['archive_structure']['required_subdirs']
            for required_dir in required_dirs:
                is_present = required_dir in subdirs
                structure_result['required_dirs_present'][required_dir] = is_present
            
            # Check optional directories
            optional_dirs = self.organization_rules['archive_structure']['optional_subdirs']
            for optional_dir in optional_dirs:
                is_present = optional_dir in subdirs
                structure_result['optional_dirs_present'][optional_dir] = is_present
            
            # Find unexpected directories
            expected_dirs = set(required_dirs + optional_dirs)
            structure_result['unexpected_dirs'] = [
                d for d in subdirs if d not in expected_dirs
            ]
            
            # Calculate structure score
            required_present = sum(structure_result['required_dirs_present'].values())
            structure_result['structure_score'] = required_present / len(required_dirs)
            
        except OSError as e:
            structure_result['error'] = f"Error scanning archive directory: {e}"
        
        return structure_result
    
    def analyze_content_organization(self) -> Dict[str, Any]:
        """Analyze how content is organized within the archive"""
        content_analysis = {
            'content_by_category': {},
            'file_counts_by_location': {},
            'organization_issues': [],
            'well_organized_sections': []
        }
        
        categories = self.organization_rules['content_categories']
        
        try:
            for category, rules in categories.items():
                content_analysis['content_by_category'][category] = self.analyze_category_content(
                    category, rules
                )
            
            # Analyze file distribution
            content_analysis['file_counts_by_location'] = self.count_files_by_location()
            
            # Identify organization issues
            content_analysis['organization_issues'] = self.identify_organization_issues()
            
            # Identify well-organized sections
            content_analysis['well_organized_sections'] = self.identify_well_organized_sections()
            
        except Exception as e:
            content_analysis['error'] = f"Error analyzing content: {e}"
        
        return content_analysis
    
    def analyze_category_content(self, category: str, rules: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content for a specific category"""
        category_analysis = {
            'expected_location': rules['archive_location'],
            'files_in_expected_location': [],
            'files_in_wrong_location': [],
            'total_category_files': 0,
            'organization_score': 0.0
        }
        
        expected_location = os.path.join(self.repo_root, rules['archive_location'].rstrip('/'))
        
        # Find all files matching this category
        category_files = self.find_category_files(rules)
        category_analysis['total_category_files'] = len(category_files)
        
        for file_path in category_files:
            if file_path.startswith(expected_location):
                rel_path = os.path.relpath(file_path, expected_location)
                category_analysis['files_in_expected_location'].append(rel_path)
            else:
                rel_path = os.path.relpath(file_path, self.repo_root)
                category_analysis['files_in_wrong_location'].append(rel_path)
        
        # Calculate organization score
        if category_analysis['total_category_files'] > 0:
            correctly_placed = len(category_analysis['files_in_expected_location'])
            category_analysis['organization_score'] = correctly_placed / category_analysis['total_category_files']
        
        return category_analysis
    
    def find_category_files(self, rules: Dict[str, Any]) -> List[str]:
        """Find files matching a category's rules"""
        matching_files = []
        
        try:
            for root, dirs, files in os.walk(self.repo_root):
                # Skip .git and other special directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # Check patterns
                    if self.file_matches_patterns(file, rules.get('patterns', [])):
                        matching_files.append(file_path)
                        continue
                    
                    # Check keywords
                    if self.file_matches_keywords(file, rules.get('keywords', [])):
                        matching_files.append(file_path)
        
        except Exception:
            pass
        
        return matching_files
    
    def file_matches_patterns(self, filename: str, patterns: List[str]) -> bool:
        """Check if file matches any of the given patterns"""
        import fnmatch
        
        for pattern in patterns:
            if fnmatch.fnmatch(filename, pattern):
                return True
        return False
    
    def file_matches_keywords(self, filename: str, keywords: List[str]) -> bool:
        """Check if file matches any of the given keywords"""
        filename_lower = filename.lower()
        return any(keyword.lower() in filename_lower for keyword in keywords)
    
    def count_files_by_location(self) -> Dict[str, int]:
        """Count files in different archive locations"""
        file_counts = {}
        
        if not os.path.exists(self.archive_dir):
            return file_counts
        
        try:
            for root, dirs, files in os.walk(self.archive_dir):
                rel_path = os.path.relpath(root, self.archive_dir)
                if rel_path == '.':
                    rel_path = 'archive_root'
                
                file_counts[rel_path] = len(files)
        
        except OSError:
            pass
        
        return file_counts
    
    def identify_organization_issues(self) -> List[str]:
        """Identify organization issues in the archive"""
        issues = []
        
        # Check for files in archive root
        if os.path.exists(self.archive_dir):
            try:
                root_files = [f for f in os.listdir(self.archive_dir) 
                             if os.path.isfile(os.path.join(self.archive_dir, f))]
                if root_files:
                    issues.append(f"Files in archive root should be categorized: {len(root_files)} files")
            except OSError:
                pass
        
        # Check for overly deep directory structures
        max_depth = 0
        try:
            for root, dirs, files in os.walk(self.archive_dir):
                depth = root[len(self.archive_dir):].count(os.sep)
                max_depth = max(max_depth, depth)
            
            if max_depth > 4:
                issues.append(f"Directory structure too deep: {max_depth} levels")
        except OSError:
            pass
        
        # Check for inconsistent naming
        try:
            archive_subdirs = [d for d in os.listdir(self.archive_dir) 
                             if os.path.isdir(os.path.join(self.archive_dir, d))]
            
            naming_patterns = set()
            for subdir in archive_subdirs:
                if '_' in subdir:
                    naming_patterns.add('underscore')
                if '-' in subdir:
                    naming_patterns.add('hyphen')
                if subdir.islower():
                    naming_patterns.add('lowercase')
                if subdir.isupper():
                    naming_patterns.add('uppercase')
            
            if len(naming_patterns) > 2:
                issues.append("Inconsistent directory naming conventions")
        except OSError:
            pass
        
        return issues
    
    def identify_well_organized_sections(self) -> List[str]:
        """Identify well-organized sections of the archive"""
        well_organized = []
        
        if not os.path.exists(self.archive_dir):
            return well_organized
        
        try:
            for subdir in os.listdir(self.archive_dir):
                subdir_path = os.path.join(self.archive_dir, subdir)
                if os.path.isdir(subdir_path):
                    if self.is_well_organized_section(subdir_path):
                        well_organized.append(subdir)
        except OSError:
            pass
        
        return well_organized
    
    def is_well_organized_section(self, section_path: str) -> bool:
        """Check if a section is well organized"""
        try:
            # Count files and subdirectories
            total_files = 0
            total_subdirs = 0
            
            for root, dirs, files in os.walk(section_path):
                total_files += len(files)
                if root == section_path:
                    total_subdirs = len(dirs)
            
            # Well-organized criteria:
            # 1. Has some structure (subdirectories)
            # 2. Not too many files in root
            # 3. Reasonable file count
            root_files = len([f for f in os.listdir(section_path) 
                            if os.path.isfile(os.path.join(section_path, f))])
            
            return (
                total_subdirs > 0 and  # Has structure
                root_files <= 5 and   # Not cluttered
                5 <= total_files <= 100  # Reasonable size
            )
        except OSError:
            return False
    
    def find_misplaced_content(self) -> List[Dict[str, str]]:
        """Find content that should be archived but isn't"""
        misplaced = []
        
        # Look for old/outdated content in active areas
        active_areas = [
            'examples',
            'tests',
            'docs'
        ]
        
        for area in active_areas:
            area_path = os.path.join(self.repo_root, area)
            if os.path.exists(area_path):
                misplaced.extend(self.find_outdated_content_in_area(area_path, area))
        
        return misplaced
    
    def find_outdated_content_in_area(self, area_path: str, area_name: str) -> List[Dict[str, str]]:
        """Find outdated content in a specific area"""
        outdated = []
        cutoff_date = datetime.now() - timedelta(days=30)
        
        try:
            for root, dirs, files in os.walk(area_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # Check file age
                    file_stat = os.stat(file_path)
                    file_date = datetime.fromtimestamp(file_stat.st_mtime)
                    
                    # Check for outdated indicators in filename
                    outdated_indicators = ['old', 'deprecated', 'legacy', 'backup', 'test_']
                    
                    if (file_date < cutoff_date or 
                        any(indicator in file.lower() for indicator in outdated_indicators)):
                        
                        rel_path = os.path.relpath(file_path, self.repo_root)
                        outdated.append({
                            'file_path': rel_path,
                            'area': area_name,
                            'reason': 'outdated_or_deprecated',
                            'last_modified': file_date.isoformat()
                        })
        
        except OSError:
            pass
        
        return outdated
    
    def find_orphaned_content(self) -> List[Dict[str, str]]:
        """Find content that appears to be orphaned or unclear purpose"""
        orphaned = []
        
        # Look for files with unclear purpose in root
        try:
            root_files = [f for f in os.listdir(self.repo_root) 
                         if os.path.isfile(os.path.join(self.repo_root, f))]
            
            for file in root_files:
                if self.is_potentially_orphaned(file):
                    orphaned.append({
                        'file_path': file,
                        'location': 'repository_root',
                        'reason': 'unclear_purpose_in_root'
                    })
        except OSError:
            pass
        
        return orphaned
    
    def is_potentially_orphaned(self, filename: str) -> bool:
        """Check if a file appears to be orphaned"""
        # Skip important root files
        important_files = {
            'claude.md', 'readme.md', 'license', 'gitignore',
            'requirements.txt', 'setup.py', 'pyproject.toml'
        }
        
        if filename.lower() in important_files:
            return False
        
        # Check for unclear file types
        unclear_patterns = [
            'temp', 'tmp', 'backup', 'copy', 'untitled',
            'new', 'test', 'debug', 'scratch'
        ]
        
        return any(pattern in filename.lower() for pattern in unclear_patterns)
    
    def generate_archival_recommendations(self, validation_result: Dict[str, Any]) -> List[str]:
        """Generate recommendations for improving archive organization"""
        recommendations = []
        
        # Structure recommendations
        structure = validation_result.get('structure_validation', {})
        missing_required = [dir_name for dir_name, present in structure.get('required_dirs_present', {}).items() 
                           if not present]
        
        if missing_required:
            recommendations.append(f"Create missing required archive directories: {', '.join(missing_required)}")
        
        # Content organization recommendations
        content = validation_result.get('content_analysis', {})
        for category, analysis in content.get('content_by_category', {}).items():
            if analysis.get('organization_score', 0) < 0.5:
                wrong_location_count = len(analysis.get('files_in_wrong_location', []))
                if wrong_location_count > 0:
                    recommendations.append(f"Move {wrong_location_count} {category} files to {analysis['expected_location']}")
        
        # Misplaced content recommendations
        misplaced = validation_result.get('misplaced_content', [])
        if misplaced:
            recommendations.append(f"Archive {len(misplaced)} outdated files from active directories")
        
        # Orphaned content recommendations
        orphaned = validation_result.get('orphaned_content', [])
        if orphaned:
            recommendations.append(f"Review and archive {len(orphaned)} potentially orphaned files")
        
        return recommendations
    
    def calculate_organization_score(self, validation_result: Dict[str, Any]) -> float:
        """Calculate overall organization score"""
        score_components = []
        
        # Structure score
        structure = validation_result.get('structure_validation', {})
        if 'structure_score' in structure:
            score_components.append(structure['structure_score'])
        
        # Content organization scores
        content = validation_result.get('content_analysis', {})
        for analysis in content.get('content_by_category', {}).values():
            if 'organization_score' in analysis:
                score_components.append(analysis['organization_score'])
        
        # Penalty for misplaced/orphaned content
        misplaced_count = len(validation_result.get('misplaced_content', []))
        orphaned_count = len(validation_result.get('orphaned_content', []))
        
        penalty = min((misplaced_count + orphaned_count) * 0.1, 0.5)
        
        if score_components:
            base_score = sum(score_components) / len(score_components)
            return max(0.0, base_score - penalty)
        
        return 0.0
    
    def generate_organization_report(self, validation_result: Dict[str, Any]) -> str:
        """Generate human-readable organization report"""
        report = f"""# Archive Organization Validation Report
Generated: {validation_result['timestamp']}
Overall Organization Score: {validation_result['organization_score']:.1%}

## Archive Structure
"""
        
        if validation_result['archive_exists']:
            report += "✅ Archive directory exists\n\n"
            
            structure = validation_result['structure_validation']
            
            # Required directories
            report += "### Required Directories\n"
            for dir_name, present in structure['required_dirs_present'].items():
                status = '✅' if present else '❌'
                report += f"{status} {dir_name}\n"
            
            # Organization issues
            if validation_result['content_analysis'].get('organization_issues'):
                report += "\n### Organization Issues\n"
                for issue in validation_result['content_analysis']['organization_issues']:
                    report += f"- {issue}\n"
        else:
            report += "❌ Archive directory does not exist\n\n"
        
        # Content organization
        report += "\n## Content Organization\n"
        content = validation_result['content_analysis']
        
        for category, analysis in content.get('content_by_category', {}).items():
            score = analysis.get('organization_score', 0)
            status = '✅' if score >= 0.75 else '⚠️' if score >= 0.5 else '❌'
            
            report += f"\n### {status} {category.title()}\n"
            report += f"- Organization score: {score:.1%}\n"
            report += f"- Files in correct location: {len(analysis.get('files_in_expected_location', []))}\n"
            report += f"- Files in wrong location: {len(analysis.get('files_in_wrong_location', []))}\n"
        
        # Recommendations
        if validation_result['archival_recommendations']:
            report += "\n## Recommendations\n"
            for i, rec in enumerate(validation_result['archival_recommendations'], 1):
                report += f"{i}. {rec}\n"
        
        return report

# Example usage and testing
if __name__ == "__main__":
    validator = ArchiveOrganizationValidator("/home/brian/autocoder3_cc")
    results = validator.validate_archive_organization()
    
    # Generate report
    report = validator.generate_organization_report(results)
    
    # Save results
    with open("archive_organization_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    with open("archive_organization_report.md", "w") as f:
        f.write(report)
    
    print(f"Archive organization validation complete.")
    print(f"Archive exists: {results['archive_exists']}")
    print(f"Organization score: {results['organization_score']:.1%}")
    print(f"Recommendations: {len(results['archival_recommendations'])}")
    print("Detailed results saved to archive_organization_results.json")
    print("Human-readable report saved to archive_organization_report.md")