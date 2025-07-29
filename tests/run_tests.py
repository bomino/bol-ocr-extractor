"""
Comprehensive test runner for BOL OCR Extractor
"""

import subprocess
import sys
import os
import argparse
import time
from pathlib import Path
from typing import List, Dict, Optional

class TestRunner:
    """Comprehensive test execution and reporting"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_dir = Path(__file__).parent
        
    def run_command(self, cmd: List[str], capture_output: bool = True) -> subprocess.CompletedProcess:
        """Run a command and return the result"""
        print(f"Running: {' '.join(cmd)}")
        return subprocess.run(cmd, capture_output=capture_output, text=True, cwd=self.project_root)
    
    def run_unit_tests(self, verbose: bool = False) -> bool:
        """Run unit tests"""
        print("\n" + "="*60)
        print("RUNNING UNIT TESTS")
        print("="*60)
        
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.test_dir / "unit"),
            "--cov=app",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov/unit",
            "-v" if verbose else "-q",
            "--tb=short",
            "-m", "unit"
        ]
        
        result = self.run_command(cmd, capture_output=False)
        success = result.returncode == 0
        
        if success:
            print("✅ Unit tests PASSED")
        else:
            print("❌ Unit tests FAILED")
        
        return success
    
    def run_integration_tests(self, verbose: bool = False) -> bool:
        """Run integration tests"""
        print("\n" + "="*60)
        print("RUNNING INTEGRATION TESTS")
        print("="*60)
        
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.test_dir / "integration"),
            "--cov=app",
            "--cov-append",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov/integration",
            "-v" if verbose else "-q",
            "--tb=short",
            "-m", "integration"
        ]
        
        result = self.run_command(cmd, capture_output=False)
        success = result.returncode == 0
        
        if success:
            print("✅ Integration tests PASSED")
        else:
            print("❌ Integration tests FAILED")
        
        return success
    
    def run_performance_tests(self, verbose: bool = False, quick: bool = False) -> bool:
        """Run performance tests"""
        print("\n" + "="*60)
        print("RUNNING PERFORMANCE TESTS")
        print("="*60)
        
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.test_dir / "performance"),
            "-v" if verbose else "-q",
            "--tb=short",
            "-m", "performance"
        ]
        
        if quick:
            # Skip slow performance tests for quick runs
            cmd.extend(["-k", "not slow"])
        
        result = self.run_command(cmd, capture_output=False)
        success = result.returncode == 0
        
        if success:
            print("✅ Performance tests PASSED")
        else:
            print("❌ Performance tests FAILED")
        
        return success
    
    def run_coverage_analysis(self) -> bool:
        """Run comprehensive coverage analysis"""
        print("\n" + "="*60)
        print("RUNNING COVERAGE ANALYSIS")
        print("="*60)
        
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.test_dir),
            "--cov=app",
            "--cov-report=term",
            "--cov-report=html:htmlcov/complete",
            "--cov-report=xml:coverage.xml",
            "--cov-fail-under=80",
            "-q"
        ]
        
        result = self.run_command(cmd, capture_output=False)
        success = result.returncode == 0
        
        if success:
            print("✅ Coverage requirements MET (≥80%)")
            print("📊 Detailed coverage report: htmlcov/complete/index.html")
        else:
            print("❌ Coverage requirements NOT MET (<80%)")
        
        return success
    
    def generate_synthetic_test_data(self, count: int = 50) -> bool:
        """Generate synthetic test data"""
        print("\n" + "="*60)
        print(f"GENERATING SYNTHETIC TEST DATA ({count} BOLs)")
        print("="*60)
        
        try:
            # Import and run the synthetic data generator
            sys.path.insert(0, str(self.test_dir / "utils"))
            from synthetic_data_generator import SyntheticBOLGenerator
            
            generator = SyntheticBOLGenerator()
            
            # Create output directory
            fixtures_dir = self.test_dir / "fixtures"
            fixtures_dir.mkdir(exist_ok=True)
            
            # Generate test dataset
            dataset = generator.generate_test_dataset(count, str(fixtures_dir / "synthetic_dataset"))
            print(f"✅ Generated {len(dataset)} synthetic BOL PDFs")
            
            # Generate edge cases
            edge_cases = generator.generate_edge_case_dataset(str(fixtures_dir / "edge_cases"))
            print(f"✅ Generated {len(edge_cases)} edge case BOL PDFs")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to generate synthetic test data: {e}")
            return False
    
    def run_accuracy_validation(self) -> bool:
        """Run accuracy validation against synthetic data"""
        print("\n" + "="*60)
        print("RUNNING ACCURACY VALIDATION")
        print("="*60)
        
        try:
            # Check if synthetic data exists
            fixtures_dir = self.test_dir / "fixtures" / "synthetic_dataset"
            if not fixtures_dir.exists():
                print("⚠️  Synthetic test data not found. Generating...")
                if not self.generate_synthetic_test_data(20):
                    return False
            
            # Import required modules
            sys.path.insert(0, str(self.project_root))
            sys.path.insert(0, str(self.test_dir / "utils"))
            
            from app import BOLOCRApp
            from accuracy_calculator import AccuracyCalculator, evaluate_against_criteria
            from synthetic_data_generator import SyntheticBOLData
            import json
            
            # Load ground truth data
            ground_truth_file = fixtures_dir / "ground_truth.json"
            with open(ground_truth_file, 'r') as f:
                ground_truth_list = json.load(f)
            
            ground_truth = [SyntheticBOLData(**item) for item in ground_truth_list]
            
            # Process PDFs with BOL OCR app
            app = BOLOCRApp()
            extracted_results = []
            
            pdfs_dir = fixtures_dir / "pdfs"
            pdf_files = list(pdfs_dir.glob("*.pdf"))[:10]  # Process first 10 for validation
            
            print(f"Processing {len(pdf_files)} PDFs for accuracy validation...")
            
            for pdf_file in pdf_files:
                with open(pdf_file, 'rb') as f:
                    result = app.process_single_pdf(f, pdf_file.name)
                    extracted_results.append(result)
            
            # Calculate accuracy
            calculator = AccuracyCalculator()
            
            # Match extracted results with ground truth
            matched_ground_truth = []
            for result in extracted_results:
                matching_gt = next((gt for gt in ground_truth if gt.filename == result.filename), None)
                if matching_gt:
                    matched_ground_truth.append(matching_gt)
            
            if len(matched_ground_truth) != len(extracted_results):
                print(f"⚠️  Could only match {len(matched_ground_truth)} of {len(extracted_results)} results")
            
            # Calculate dataset accuracy
            dataset_results = calculator.calculate_dataset_accuracy(
                extracted_results[:len(matched_ground_truth)], 
                matched_ground_truth
            )
            
            # Generate report
            report = calculator.generate_accuracy_report(
                dataset_results, 
                str(self.project_root / "accuracy_report.txt")
            )
            
            print("📊 ACCURACY VALIDATION SUMMARY")
            print("-" * 40)
            overall_acc = dataset_results['summary_statistics']['overall_accuracy']['mean']
            print(f"Overall Mean Accuracy: {overall_acc:.1%}")
            
            # Evaluate against criteria
            evaluation = evaluate_against_criteria(dataset_results)
            overall_success = evaluation.get('overall_success', False)
            
            if overall_success:
                print("✅ Accuracy validation PASSED - meets all criteria")
            else:
                print("❌ Accuracy validation FAILED - does not meet all criteria")
                failed_criteria = [k for k, v in evaluation.items() if not v and k != 'overall_success']
                print(f"Failed criteria: {failed_criteria}")
            
            print(f"📄 Detailed report saved to: accuracy_report.txt")
            
            return overall_success
            
        except Exception as e:
            print(f"❌ Accuracy validation failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_all_tests(self, verbose: bool = False, quick: bool = False, 
                     skip_accuracy: bool = False) -> Dict[str, bool]:
        """Run all test suites"""
        print("🚀 STARTING COMPREHENSIVE BOL OCR TESTING SUITE")
        print("=" * 80)
        
        start_time = time.time()
        results = {}
        
        # Generate synthetic data if needed
        if not skip_accuracy:
            results['synthetic_data'] = self.generate_synthetic_test_data(30 if quick else 50)
        
        # Run test suites
        results['unit_tests'] = self.run_unit_tests(verbose)
        results['integration_tests'] = self.run_integration_tests(verbose)
        
        if not quick:
            results['performance_tests'] = self.run_performance_tests(verbose, quick)
        
        results['coverage_analysis'] = self.run_coverage_analysis()
        
        if not skip_accuracy:
            results['accuracy_validation'] = self.run_accuracy_validation()
        
        # Summary
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "="*80)
        print("TEST EXECUTION SUMMARY")
        print("="*80)
        print(f"Total execution time: {duration:.1f} seconds")
        print()
        
        passed_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        for test_type, success in results.items():
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"{test_type.replace('_', ' ').title():<25} {status}")
        
        print()
        overall_success = all(results.values())
        if overall_success:
            print("🎉 ALL TESTS PASSED - System ready for production!")
        else:
            print(f"⚠️  {total_count - passed_count} of {total_count} test suites failed")
            print("🔧 Please review failed tests before deployment")
        
        return results

def main():
    """Main entry point for test runner"""
    parser = argparse.ArgumentParser(description="BOL OCR Extractor Test Runner")
    
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Run tests in verbose mode")
    parser.add_argument("--quick", "-q", action="store_true",
                       help="Run quick test suite (skip slow tests)")
    parser.add_argument("--unit-only", action="store_true",
                       help="Run only unit tests")
    parser.add_argument("--integration-only", action="store_true", 
                       help="Run only integration tests")
    parser.add_argument("--performance-only", action="store_true",
                       help="Run only performance tests")
    parser.add_argument("--coverage-only", action="store_true",
                       help="Run only coverage analysis")
    parser.add_argument("--accuracy-only", action="store_true",
                       help="Run only accuracy validation")
    parser.add_argument("--skip-accuracy", action="store_true",
                       help="Skip accuracy validation")
    parser.add_argument("--generate-data", action="store_true",
                       help="Generate synthetic test data only")
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    # Check for single test suite runs
    if args.unit_only:
        success = runner.run_unit_tests(args.verbose)
        sys.exit(0 if success else 1)
    
    if args.integration_only:
        success = runner.run_integration_tests(args.verbose)
        sys.exit(0 if success else 1)
    
    if args.performance_only:
        success = runner.run_performance_tests(args.verbose, args.quick)
        sys.exit(0 if success else 1)
    
    if args.coverage_only:
        success = runner.run_coverage_analysis()
        sys.exit(0 if success else 1)
    
    if args.accuracy_only:
        success = runner.run_accuracy_validation()
        sys.exit(0 if success else 1)
    
    if args.generate_data:
        success = runner.generate_synthetic_test_data(100)
        sys.exit(0 if success else 1)
    
    # Run full test suite
    results = runner.run_all_tests(args.verbose, args.quick, args.skip_accuracy)
    overall_success = all(results.values())
    
    sys.exit(0 if overall_success else 1)

if __name__ == "__main__":
    main()