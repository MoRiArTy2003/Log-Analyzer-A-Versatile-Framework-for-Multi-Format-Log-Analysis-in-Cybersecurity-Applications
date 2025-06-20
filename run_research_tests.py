#!/usr/bin/env python3
"""
Research Testing Script for Log Analyzer
Run this script to generate all results needed for your research paper
"""

import os
import sys
import argparse
from pathlib import Path

# Add tests directory to path
tests_dir = Path(__file__).parent / "tests"
sys.path.append(str(tests_dir))

from comprehensive_test_runner import ComprehensiveTestRunner

def main():
    parser = argparse.ArgumentParser(description="Run comprehensive tests for Log Analyzer research paper")
    parser.add_argument("--output-dir", default="research_results", 
                       help="Directory to store test results (default: research_results)")
    parser.add_argument("--quick", action="store_true", 
                       help="Run quick tests with smaller datasets")
    parser.add_argument("--phase", choices=['1', '2', '3', '4', '5'], 
                       help="Run specific phase only (1=data, 2=performance, 3=accuracy, 4=comparison, 5=report)")
    
    args = parser.parse_args()
    
    print("🔬 Log Analyzer Research Testing Suite")
    print("=" * 50)
    print(f"Output Directory: {args.output_dir}")
    print(f"Quick Mode: {'Yes' if args.quick else 'No'}")
    
    if args.phase:
        print(f"Running Phase {args.phase} only")
    else:
        print("Running all phases")
    
    print("=" * 50)
    
    # Initialize test runner
    runner = ComprehensiveTestRunner(args.output_dir)
    
    try:
        if args.phase:
            # Run specific phase
            if args.phase == '1':
                test_files = runner.phase_1_generate_test_data()
                print(f"✅ Phase 1 completed. Generated {len(test_files)} test files.")
                
            elif args.phase == '2':
                # Need test files for performance testing
                test_files_path = Path(args.output_dir) / "test_data"
                if not test_files_path.exists():
                    print("❌ Test data not found. Run Phase 1 first.")
                    return
                
                # Load existing test files
                test_files = {}
                for file_path in test_files_path.glob("*.txt"):
                    if "browsing" in file_path.name:
                        test_files["browsing"] = str(file_path)
                    elif "virus" in file_path.name:
                        test_files["virus"] = str(file_path)
                    elif "mail" in file_path.name:
                        test_files["mail"] = str(file_path)
                
                runner.phase_2_performance_benchmarks(test_files)
                print("✅ Phase 2 completed. Performance benchmarks done.")
                
            elif args.phase == '3':
                # Similar logic for other phases...
                print("✅ Phase 3 would run accuracy tests.")
                
            elif args.phase == '4':
                print("✅ Phase 4 would run comparative analysis.")
                
            elif args.phase == '5':
                report_file = runner.phase_5_generate_research_report()
                print(f"✅ Phase 5 completed. Report: {report_file}")
        
        else:
            # Run comprehensive testing
            report_file = runner.run_comprehensive_testing()
            
            if report_file:
                print("\n🎉 TESTING COMPLETED SUCCESSFULLY!")
                print("=" * 50)
                print(f"📊 Final Report: {report_file}")
                print(f"📁 All Results: {args.output_dir}")
                print("\n📋 What you can use for your research paper:")
                print("  • Performance benchmarks (processing speed, memory usage)")
                print("  • Accuracy metrics (format detection, parsing correctness)")
                print("  • Comparative analysis (vs. existing tools)")
                print("  • Scalability results (concurrent processing, large files)")
                print("  • Error handling and reliability metrics")
                
                # Show key metrics
                print("\n🔍 KEY METRICS FOR YOUR PAPER:")
                try:
                    import json
                    with open(report_file, 'r') as f:
                        results = json.load(f)
                    
                    paper_metrics = results.get('research_paper_metrics', {})
                    if paper_metrics:
                        for category, metrics in paper_metrics.items():
                            print(f"\n{category.replace('_', ' ').title()}:")
                            for key, value in metrics.items():
                                print(f"  • {key.replace('_', ' ').title()}: {value}")
                
                except Exception as e:
                    print(f"  (Could not extract metrics: {e})")
                
                print("\n📝 Next Steps:")
                print("  1. Review the detailed results in the JSON report")
                print("  2. Use the metrics in your research paper")
                print("  3. Create visualizations from the performance data")
                print("  4. Include the comparative analysis in your evaluation section")
                
            else:
                print("❌ Testing failed. Check error messages above.")
                return 1
    
    except KeyboardInterrupt:
        print("\n⚠️  Testing interrupted by user.")
        return 1
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
