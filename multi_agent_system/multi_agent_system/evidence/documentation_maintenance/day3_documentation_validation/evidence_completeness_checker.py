import os
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path

class EvidenceCompletenessChecker:
    """Check completeness of evidence packages for phases"""
    
    def __init__(self, repo_root: str):
        self.repo_root = repo_root
        self.evidence_dir = os.path.join(repo_root, 'evidence')
        self.evidence_standards = self.load_evidence_standards()
    
    def load_evidence_standards(self) -> Dict[str, Any]:
        """Load standards for what constitutes complete evidence"""
        return {
            'phase_evidence_requirements': {
                'implementation_days': {
                    'required_structure': ['day1_*', 'day2_*', 'day3_*', 'day4_*', 'day5_*'],
                    'optional_structure': ['completion/', 'documentation/'],
                    'required_files_per_day': {
                        'python_files': 1,  # At least 1 .py file per day
                        'output_files': 1   # At least 1 output/demo file per day
                    }
                },
                'completion_evidence': {
                    'required_files': [
                        '*_completion.py',
                        '*_summary.md',
                        'implementation_summary.md',
                        'external_evaluator_test.md'
                    ],
                    'required_content': [
                        'working code',
                        'test results',
                        'evaluation criteria'
                    ]
                },
                'file_types': {
                    'required': ['.py', '.md'],
                    'optional': ['.json', '.yaml', '.txt'],
                    'evidence': ['.json', '.txt', '.log']
                }
            },
            'quality_indicators': {
                'min_files_per_phase': 10,
                'min_python_files': 5,
                'min_markdown_files': 3,
                'min_evidence_files': 2
            },
            'phase_specific_requirements': {
                'phase5_database_integration': {
                    'required_components': ['database', 'schema', 'migration', 'orm'],
                    'required_evidence': ['database_tests', 'performance_results']
                },
                'phase6_harness': {
                    'required_components': ['execution', 'harness', 'component'],
                    'required_evidence': ['execution_tests', 'integration_results']
                },
                'phase7_generation': {
                    'required_components': ['generation', 'pipeline', 'templates'],
                    'required_evidence': ['generation_tests', 'pipeline_results']
                }
            }
        }
    
    def check_all_evidence(self) -> Dict[str, Any]:
        """Check completeness of all evidence packages"""
        if not os.path.exists(self.evidence_dir):
            return {
                'evidence_dir_exists': False,
                'error': 'Evidence directory does not exist',
                'timestamp': datetime.now().isoformat()
            }
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'evidence_dir_exists': True,
            'total_evidence_packages': 0,
            'complete_packages': 0,
            'incomplete_packages': 0,
            'package_details': {},
            'overall_completeness_score': 0.0,
            'recommendations': []
        }
        
        # Scan for evidence packages
        evidence_packages = self.discover_evidence_packages()
        results['total_evidence_packages'] = len(evidence_packages)
        
        # Check each package
        for package_name in evidence_packages:
            package_path = os.path.join(self.evidence_dir, package_name)
            package_result = self.check_evidence_package(package_path, package_name)
            results['package_details'][package_name] = package_result
            
            if package_result['is_complete']:
                results['complete_packages'] += 1
            else:
                results['incomplete_packages'] += 1
        
        # Calculate overall score
        if results['total_evidence_packages'] > 0:
            completeness_scores = [
                details['completeness_score'] 
                for details in results['package_details'].values()
            ]
            results['overall_completeness_score'] = sum(completeness_scores) / len(completeness_scores)
        
        # Generate recommendations
        results['recommendations'] = self.generate_recommendations(results)
        
        return results
    
    def discover_evidence_packages(self) -> List[str]:
        """Discover evidence packages in the evidence directory"""
        packages = []
        
        try:
            for item in os.listdir(self.evidence_dir):
                item_path = os.path.join(self.evidence_dir, item)
                if os.path.isdir(item_path):
                    packages.append(item)
        except OSError:
            pass
        
        return sorted(packages)
    
    def check_evidence_package(self, package_path: str, package_name: str) -> Dict[str, Any]:
        """Check completeness of a single evidence package"""
        result = {
            'package_name': package_name,
            'package_path': package_path,
            'exists': os.path.exists(package_path),
            'is_phase_evidence': self.is_phase_evidence(package_name),
            'structure_analysis': {},
            'file_analysis': {},
            'content_analysis': {},
            'completeness_score': 0.0,
            'is_complete': False,
            'missing_elements': [],
            'quality_indicators': {}
        }
        
        if not result['exists']:
            result['missing_elements'].append('Package directory does not exist')
            return result
        
        # Analyze structure
        result['structure_analysis'] = self.analyze_package_structure(package_path)
        
        # Analyze files
        result['file_analysis'] = self.analyze_package_files(package_path)
        
        # Analyze content
        result['content_analysis'] = self.analyze_package_content(package_path, package_name)
        
        # Calculate completeness
        result['completeness_score'] = self.calculate_completeness_score(result)
        result['is_complete'] = result['completeness_score'] >= 0.75  # 75% threshold
        
        # Identify missing elements
        result['missing_elements'] = self.identify_missing_elements(result, package_name)
        
        # Quality indicators
        result['quality_indicators'] = self.assess_quality_indicators(result)
        
        return result
    
    def is_phase_evidence(self, package_name: str) -> bool:
        """Check if package is phase evidence"""
        return 'phase' in package_name.lower()
    
    def analyze_package_structure(self, package_path: str) -> Dict[str, Any]:
        """Analyze the structure of an evidence package"""
        structure = {
            'subdirectories': [],
            'has_day_structure': False,
            'has_completion_dir': False,
            'day_directories': [],
            'total_subdirs': 0
        }
        
        try:
            for item in os.listdir(package_path):
                item_path = os.path.join(package_path, item)
                if os.path.isdir(item_path):
                    structure['subdirectories'].append(item)
                    structure['total_subdirs'] += 1
                    
                    if item.startswith('day') and any(c.isdigit() for c in item):
                        structure['day_directories'].append(item)
                    
                    if 'completion' in item.lower():
                        structure['has_completion_dir'] = True
            
            structure['has_day_structure'] = len(structure['day_directories']) >= 3
            
        except OSError:
            pass
        
        return structure
    
    def analyze_package_files(self, package_path: str) -> Dict[str, Any]:
        """Analyze files in the evidence package"""
        file_analysis = {
            'total_files': 0,
            'python_files': [],
            'markdown_files': [],
            'json_files': [],
            'txt_files': [],
            'other_files': [],
            'file_counts_by_type': {},
            'files_by_directory': {}
        }
        
        try:
            for root, dirs, files in os.walk(package_path):
                rel_dir = os.path.relpath(root, package_path)
                if rel_dir == '.':
                    rel_dir = 'root'
                
                file_analysis['files_by_directory'][rel_dir] = []
                
                for file in files:
                    file_analysis['total_files'] += 1
                    file_analysis['files_by_directory'][rel_dir].append(file)
                    
                    if file.endswith('.py'):
                        file_analysis['python_files'].append(os.path.join(rel_dir, file))
                    elif file.endswith('.md'):
                        file_analysis['markdown_files'].append(os.path.join(rel_dir, file))
                    elif file.endswith('.json'):
                        file_analysis['json_files'].append(os.path.join(rel_dir, file))
                    elif file.endswith('.txt'):
                        file_analysis['txt_files'].append(os.path.join(rel_dir, file))
                    else:
                        file_analysis['other_files'].append(os.path.join(rel_dir, file))
            
            # Count by type
            file_analysis['file_counts_by_type'] = {
                'python': len(file_analysis['python_files']),
                'markdown': len(file_analysis['markdown_files']),
                'json': len(file_analysis['json_files']),
                'txt': len(file_analysis['txt_files']),
                'other': len(file_analysis['other_files'])
            }
            
        except OSError:
            pass
        
        return file_analysis
    
    def analyze_package_content(self, package_path: str, package_name: str) -> Dict[str, Any]:
        """Analyze content quality of the evidence package"""
        content_analysis = {
            'has_implementation_code': False,
            'has_test_results': False,
            'has_documentation': False,
            'has_completion_summary': False,
            'executable_files': [],
            'demo_files': [],
            'result_files': [],
            'content_indicators': {}
        }
        
        try:
            for root, dirs, files in os.walk(package_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # Check Python files for implementation
                    if file.endswith('.py'):
                        if self.is_implementation_file(file_path):
                            content_analysis['has_implementation_code'] = True
                            content_analysis['executable_files'].append(file)
                        
                        if 'demo' in file.lower() or 'test' in file.lower():
                            content_analysis['demo_files'].append(file)
                    
                    # Check for test results
                    if any(keyword in file.lower() for keyword in ['result', 'output', 'demo', 'test']):
                        if file.endswith(('.txt', '.json', '.md')):
                            content_analysis['result_files'].append(file)
                            content_analysis['has_test_results'] = True
                    
                    # Check for documentation
                    if file.endswith('.md'):
                        content_analysis['has_documentation'] = True
                        
                        if 'completion' in file.lower() or 'summary' in file.lower():
                            content_analysis['has_completion_summary'] = True
            
            # Content quality indicators
            content_analysis['content_indicators'] = {
                'implementation_to_demo_ratio': len(content_analysis['executable_files']) / max(len(content_analysis['demo_files']), 1),
                'documentation_coverage': len(content_analysis['result_files']) > 0,
                'has_external_evaluator_info': any('evaluator' in f.lower() for f in content_analysis['result_files'])
            }
            
        except OSError:
            pass
        
        return content_analysis
    
    def is_implementation_file(self, file_path: str) -> bool:
        """Check if a Python file contains implementation code"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for implementation indicators
            indicators = [
                'class ', 'def ', 'import ', 'from ',
                'if __name__ == "__main__"',
                'def main(', 'def run('
            ]
            
            return any(indicator in content for indicator in indicators) and len(content) > 500
        except:
            return False
    
    def calculate_completeness_score(self, package_result: Dict[str, Any]) -> float:
        """Calculate completeness score for a package"""
        score = 0.0
        max_score = 10.0
        
        # Structure scoring (3 points)
        if package_result['structure_analysis']['has_day_structure']:
            score += 1.5
        if package_result['structure_analysis']['has_completion_dir']:
            score += 1.0
        if package_result['structure_analysis']['total_subdirs'] >= 3:
            score += 0.5
        
        # File quantity scoring (3 points)
        file_counts = package_result['file_analysis']['file_counts_by_type']
        if file_counts['python'] >= 5:
            score += 1.5
        elif file_counts['python'] >= 3:
            score += 1.0
        elif file_counts['python'] >= 1:
            score += 0.5
            
        if file_counts['markdown'] >= 3:
            score += 1.0
        elif file_counts['markdown'] >= 1:
            score += 0.5
            
        if package_result['file_analysis']['total_files'] >= 10:
            score += 0.5
        
        # Content quality scoring (4 points)
        content = package_result['content_analysis']
        if content['has_implementation_code']:
            score += 1.5
        if content['has_test_results']:
            score += 1.0
        if content['has_documentation']:
            score += 1.0
        if content['has_completion_summary']:
            score += 0.5
        
        return min(score / max_score, 1.0)
    
    def identify_missing_elements(self, package_result: Dict[str, Any], package_name: str) -> List[str]:
        """Identify missing elements in the evidence package"""
        missing = []
        
        # Structure requirements
        if not package_result['structure_analysis']['has_day_structure']:
            missing.append("Day-based directory structure (day1_*, day2_*, etc.)")
        
        if not package_result['structure_analysis']['has_completion_dir']:
            missing.append("Completion directory with final evidence")
        
        # File requirements
        file_counts = package_result['file_analysis']['file_counts_by_type']
        if file_counts['python'] < 3:
            missing.append(f"Insufficient Python files ({file_counts['python']}/3 minimum)")
        
        if file_counts['markdown'] < 2:
            missing.append(f"Insufficient documentation files ({file_counts['markdown']}/2 minimum)")
        
        # Content requirements
        content = package_result['content_analysis']
        if not content['has_implementation_code']:
            missing.append("Working implementation code")
        
        if not content['has_test_results']:
            missing.append("Test results or demonstration output")
        
        if not content['has_completion_summary']:
            missing.append("Completion summary documentation")
        
        # Phase-specific requirements
        if package_result['is_phase_evidence']:
            phase_requirements = self.get_phase_specific_requirements(package_name)
            for requirement in phase_requirements:
                if not self.check_phase_requirement(package_result, requirement):
                    missing.append(f"Phase-specific requirement: {requirement}")
        
        return missing
    
    def get_phase_specific_requirements(self, package_name: str) -> List[str]:
        """Get phase-specific requirements"""
        phase_reqs = self.evidence_standards['phase_specific_requirements']
        
        for phase_key, requirements in phase_reqs.items():
            if phase_key in package_name.lower():
                return requirements.get('required_evidence', [])
        
        return []
    
    def check_phase_requirement(self, package_result: Dict[str, Any], requirement: str) -> bool:
        """Check if a phase-specific requirement is met"""
        # Look for requirement in file names
        all_files = []
        for file_list in package_result['file_analysis']['files_by_directory'].values():
            all_files.extend(file_list)
        
        return any(requirement.lower() in file.lower() for file in all_files)
    
    def assess_quality_indicators(self, package_result: Dict[str, Any]) -> Dict[str, Any]:
        """Assess quality indicators for the package"""
        quality = {
            'meets_minimum_files': package_result['file_analysis']['total_files'] >= 10,
            'has_diverse_file_types': len([k for k, v in package_result['file_analysis']['file_counts_by_type'].items() if v > 0]) >= 3,
            'good_implementation_coverage': package_result['content_analysis']['has_implementation_code'],
            'good_documentation_coverage': package_result['file_analysis']['file_counts_by_type']['markdown'] >= 3,
            'has_working_demos': len(package_result['content_analysis']['demo_files']) > 0
        }
        
        quality['overall_quality'] = sum(quality.values()) / len(quality)
        
        return quality
    
    def generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations for improving evidence completeness"""
        recommendations = []
        
        if results['overall_completeness_score'] < 0.5:
            recommendations.append("Overall evidence quality is low - focus on improving package completeness")
        
        incomplete_packages = [
            name for name, details in results['package_details'].items() 
            if not details['is_complete']
        ]
        
        if incomplete_packages:
            recommendations.append(f"Complete evidence packages for: {', '.join(incomplete_packages)}")
        
        # Analyze common missing elements
        all_missing = []
        for details in results['package_details'].values():
            all_missing.extend(details['missing_elements'])
        
        from collections import Counter
        common_missing = Counter(all_missing).most_common(3)
        
        for missing_element, count in common_missing:
            if count > 1:
                recommendations.append(f"Common issue across {count} packages: {missing_element}")
        
        return recommendations
    
    def generate_completeness_report(self, results: Dict[str, Any]) -> str:
        """Generate human-readable completeness report"""
        report = f"""# Evidence Completeness Report
Generated: {results['timestamp']}

## Summary
- Total evidence packages: {results['total_evidence_packages']}
- Complete packages: {results['complete_packages']}
- Incomplete packages: {results['incomplete_packages']}
- Overall completeness score: {results['overall_completeness_score']:.1%}

## Package Details
"""
        
        for package_name, details in results['package_details'].items():
            status_icon = '✅' if details['is_complete'] else '❌'
            report += f"\n### {status_icon} {package_name}\n"
            report += f"- Completeness score: {details['completeness_score']:.1%}\n"
            report += f"- Total files: {details['file_analysis']['total_files']}\n"
            report += f"- Python files: {details['file_analysis']['file_counts_by_type']['python']}\n"
            report += f"- Documentation files: {details['file_analysis']['file_counts_by_type']['markdown']}\n"
            
            if details['missing_elements']:
                report += f"- Missing elements ({len(details['missing_elements'])}):\n"
                for missing in details['missing_elements']:
                    report += f"  - {missing}\n"
        
        if results['recommendations']:
            report += "\n## Recommendations\n"
            for i, rec in enumerate(results['recommendations'], 1):
                report += f"{i}. {rec}\n"
        
        return report

# Example usage and testing
if __name__ == "__main__":
    checker = EvidenceCompletenessChecker("/home/brian/autocoder3_cc")
    results = checker.check_all_evidence()
    
    # Generate report
    report = checker.generate_completeness_report(results)
    
    # Save results
    with open("evidence_completeness_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    with open("evidence_completeness_report.md", "w") as f:
        f.write(report)
    
    print(f"Evidence completeness check complete.")
    print(f"Total packages: {results['total_evidence_packages']}")
    print(f"Complete packages: {results['complete_packages']}")
    print(f"Overall score: {results['overall_completeness_score']:.1%}")
    print("Detailed results saved to evidence_completeness_results.json")
    print("Human-readable report saved to evidence_completeness_report.md")