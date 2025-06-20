"""
Accuracy and Effectiveness Testing Suite for Log Analyzer Research Paper
Measures format detection accuracy, parsing correctness, and analysis quality
"""

import os
import sys
import pandas as pd
import numpy as np
import json
from datetime import datetime
from typing import Dict, List, Tuple, Any
from pathlib import Path
import re

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from log_parser import LogParser
from ml_engine import detect_anomalies, cluster_logs

class AccuracyTester:
    """
    Comprehensive accuracy testing suite for the log analyzer.
    """
    
    def __init__(self, results_dir: str = "test_results"):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
        self.results = []
    
    def test_format_detection_accuracy(self, test_files: Dict[str, str]) -> Dict[str, Any]:
        """
        Test the accuracy of automatic format detection.
        
        Args:
            test_files: Dictionary mapping expected format to file path
            
        Returns:
            Dictionary with format detection accuracy metrics
        """
        print("Testing format detection accuracy...")
        
        correct_detections = 0
        total_files = len(test_files)
        detection_results = {}
        
        for expected_format, file_path in test_files.items():
            parser = LogParser()
            detected_format = parser._detect_file_format(file_path)
            
            is_correct = detected_format == expected_format
            if is_correct:
                correct_detections += 1
            
            detection_results[file_path] = {
                'expected': expected_format,
                'detected': detected_format,
                'correct': is_correct
            }
            
            print(f"  {file_path}: Expected {expected_format}, Detected {detected_format} {'✓' if is_correct else '✗'}")
        
        accuracy = correct_detections / total_files * 100 if total_files > 0 else 0
        
        result = {
            'test_type': 'format_detection_accuracy',
            'total_files': total_files,
            'correct_detections': correct_detections,
            'accuracy_percent': accuracy,
            'detection_details': detection_results,
            'timestamp': datetime.now().isoformat()
        }
        
        self.results.append(result)
        return result
    
    def test_parsing_correctness(self, file_path: str, log_type: str, 
                               expected_columns: List[str] = None) -> Dict[str, Any]:
        """
        Test the correctness of log parsing.
        
        Args:
            file_path: Path to the log file
            log_type: Expected log type
            expected_columns: Expected column names
            
        Returns:
            Dictionary with parsing correctness metrics
        """
        print(f"Testing parsing correctness for {log_type} logs...")
        
        parser = LogParser(log_type=log_type)
        
        try:
            df = parser.parse_file(file_path)
            
            # Basic validation
            parsing_success = not df.empty
            total_records = len(df)
            
            # Column validation
            if expected_columns:
                expected_cols = set(expected_columns)
                actual_cols = set(df.columns)
                missing_cols = expected_cols - actual_cols
                extra_cols = actual_cols - expected_cols
                column_match = len(missing_cols) == 0 and len(extra_cols) == 0
            else:
                missing_cols = set()
                extra_cols = set()
                column_match = True
            
            # Data quality checks
            null_percentages = {}
            data_type_issues = {}
            
            for col in df.columns:
                null_pct = df[col].isnull().sum() / len(df) * 100
                null_percentages[col] = null_pct
                
                # Check for data type consistency
                if col in ['timestamp', 'datetime']:
                    # Check if timestamp parsing worked
                    try:
                        pd.to_datetime(df[col].dropna().iloc[0] if not df[col].dropna().empty else None)
                        data_type_issues[col] = False
                    except:
                        data_type_issues[col] = True
                elif col in ['bandwidth', 'size', 'status_code', 'bytes_sent']:
                    # Check if numeric fields are numeric
                    numeric_count = pd.to_numeric(df[col], errors='coerce').notna().sum()
                    data_type_issues[col] = numeric_count < len(df) * 0.9  # Allow 10% tolerance
            
            # Calculate overall data quality score
            avg_null_pct = np.mean(list(null_percentages.values()))
            type_error_pct = sum(data_type_issues.values()) / len(data_type_issues) * 100 if data_type_issues else 0
            data_quality_score = max(0, 100 - avg_null_pct - type_error_pct)
            
        except Exception as e:
            parsing_success = False
            total_records = 0
            column_match = False
            missing_cols = set()
            extra_cols = set()
            null_percentages = {}
            data_type_issues = {}
            data_quality_score = 0
            error_message = str(e)
        
        result = {
            'test_type': 'parsing_correctness',
            'log_type': log_type,
            'file_path': file_path,
            'parsing_success': parsing_success,
            'total_records': total_records,
            'column_match': column_match,
            'missing_columns': list(missing_cols),
            'extra_columns': list(extra_cols),
            'null_percentages': null_percentages,
            'data_type_issues': data_type_issues,
            'data_quality_score': data_quality_score,
            'timestamp': datetime.now().isoformat()
        }
        
        if not parsing_success:
            result['error_message'] = error_message
        
        self.results.append(result)
        return result
    
    def test_anomaly_detection_accuracy(self, file_path: str, log_type: str,
                                      known_anomalies: List[int] = None) -> Dict[str, Any]:
        """
        Test the accuracy of anomaly detection.
        
        Args:
            file_path: Path to the log file
            log_type: Type of log
            known_anomalies: List of indices of known anomalous records
            
        Returns:
            Dictionary with anomaly detection accuracy metrics
        """
        print(f"Testing anomaly detection accuracy for {log_type} logs...")
        
        parser = LogParser(log_type=log_type)
        df = parser.parse_file(file_path)
        
        if df.empty:
            return {
                'test_type': 'anomaly_detection_accuracy',
                'error': 'Failed to parse log file',
                'timestamp': datetime.now().isoformat()
            }
        
        # Run anomaly detection
        try:
            result_df = detect_anomalies(df, contamination=0.1)
            
            if known_anomalies:
                # Calculate precision, recall, F1-score
                predicted_anomalies = set(result_df[result_df['is_anomaly'] == 'Anomaly'].index)
                true_anomalies = set(known_anomalies)
                
                true_positives = len(predicted_anomalies & true_anomalies)
                false_positives = len(predicted_anomalies - true_anomalies)
                false_negatives = len(true_anomalies - predicted_anomalies)
                
                precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
                recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
                f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
                
                accuracy_metrics = {
                    'precision': precision,
                    'recall': recall,
                    'f1_score': f1_score,
                    'true_positives': true_positives,
                    'false_positives': false_positives,
                    'false_negatives': false_negatives
                }
            else:
                # Without ground truth, calculate basic statistics
                total_anomalies = len(result_df[result_df['is_anomaly'] == 'Anomaly'])
                anomaly_rate = total_anomalies / len(result_df) * 100
                
                accuracy_metrics = {
                    'total_anomalies_detected': total_anomalies,
                    'anomaly_rate_percent': anomaly_rate,
                    'note': 'No ground truth provided for precision/recall calculation'
                }
            
            detection_success = True
            
        except Exception as e:
            detection_success = False
            accuracy_metrics = {'error': str(e)}
        
        result = {
            'test_type': 'anomaly_detection_accuracy',
            'log_type': log_type,
            'file_path': file_path,
            'total_records': len(df),
            'detection_success': detection_success,
            'accuracy_metrics': accuracy_metrics,
            'timestamp': datetime.now().isoformat()
        }
        
        self.results.append(result)
        return result
    
    def test_data_integrity(self, file_path: str, log_type: str) -> Dict[str, Any]:
        """
        Test data integrity during parsing and processing.
        
        Args:
            file_path: Path to the log file
            log_type: Type of log
            
        Returns:
            Dictionary with data integrity metrics
        """
        print(f"Testing data integrity for {log_type} logs...")
        
        # Count original lines
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            original_lines = sum(1 for line in f if line.strip())
        
        # Parse and count processed records
        parser = LogParser(log_type=log_type)
        df = parser.parse_file(file_path)
        processed_records = len(df)
        
        # Calculate data loss
        data_loss_rate = (original_lines - processed_records) / original_lines * 100 if original_lines > 0 else 0
        
        # Check for duplicate records
        duplicate_count = df.duplicated().sum()
        duplicate_rate = duplicate_count / len(df) * 100 if len(df) > 0 else 0
        
        # Check for data consistency
        consistency_issues = []
        
        # Check timestamp consistency
        if 'timestamp' in df.columns or 'datetime' in df.columns:
            timestamp_col = 'timestamp' if 'timestamp' in df.columns else 'datetime'
            try:
                timestamps = pd.to_datetime(df[timestamp_col], errors='coerce')
                invalid_timestamps = timestamps.isnull().sum()
                if invalid_timestamps > 0:
                    consistency_issues.append(f"{invalid_timestamps} invalid timestamps")
            except:
                consistency_issues.append("Timestamp parsing failed")
        
        # Check for empty critical fields
        critical_fields = ['ip_address', 'username', 'url'] if log_type == 'browsing' else []
        for field in critical_fields:
            if field in df.columns:
                empty_count = df[field].isnull().sum() + (df[field] == '').sum()
                if empty_count > len(df) * 0.1:  # More than 10% empty
                    consistency_issues.append(f"{field} has {empty_count} empty values")
        
        result = {
            'test_type': 'data_integrity',
            'log_type': log_type,
            'file_path': file_path,
            'original_lines': original_lines,
            'processed_records': processed_records,
            'data_loss_rate_percent': data_loss_rate,
            'duplicate_count': duplicate_count,
            'duplicate_rate_percent': duplicate_rate,
            'consistency_issues': consistency_issues,
            'integrity_score': max(0, 100 - data_loss_rate - duplicate_rate - len(consistency_issues) * 5),
            'timestamp': datetime.now().isoformat()
        }
        
        self.results.append(result)
        return result
    
    def test_edge_cases(self, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Test handling of edge cases and malformed data.
        
        Args:
            test_cases: List of test case dictionaries with 'data', 'log_type', 'expected_behavior'
            
        Returns:
            Dictionary with edge case handling results
        """
        print("Testing edge case handling...")
        
        edge_case_results = []
        
        for i, test_case in enumerate(test_cases):
            test_data = test_case['data']
            log_type = test_case['log_type']
            expected_behavior = test_case.get('expected_behavior', 'graceful_handling')
            
            # Create temporary test file
            temp_file = self.results_dir / f"edge_case_{i}.txt"
            with open(temp_file, 'w') as f:
                f.write(test_data)
            
            try:
                parser = LogParser(log_type=log_type)
                df = parser.parse_file(str(temp_file))
                
                result = {
                    'test_case': i,
                    'success': True,
                    'records_parsed': len(df),
                    'behavior': 'graceful_handling' if not df.empty else 'empty_result'
                }
                
            except Exception as e:
                result = {
                    'test_case': i,
                    'success': False,
                    'error': str(e),
                    'behavior': 'exception_thrown'
                }
            
            # Check if behavior matches expectation
            result['meets_expectation'] = result.get('behavior', 'exception_thrown') == expected_behavior
            edge_case_results.append(result)
            
            # Clean up
            temp_file.unlink()
        
        success_rate = sum(1 for r in edge_case_results if r['meets_expectation']) / len(edge_case_results) * 100
        
        result = {
            'test_type': 'edge_case_handling',
            'total_test_cases': len(test_cases),
            'success_rate_percent': success_rate,
            'detailed_results': edge_case_results,
            'timestamp': datetime.now().isoformat()
        }
        
        self.results.append(result)
        return result
    
    def save_results(self, filename: str = None) -> str:
        """Save accuracy test results to JSON file."""
        if filename is None:
            filename = f"accuracy_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = self.results_dir / filename
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"Results saved to: {filepath}")
        return str(filepath)
    
    def generate_accuracy_summary(self) -> Dict[str, Any]:
        """Generate a summary of all accuracy test results."""
        if not self.results:
            return {"error": "No results available"}
        
        summary = {
            'total_tests': len(self.results),
            'test_types': list(set(r['test_type'] for r in self.results)),
            'timestamp': datetime.now().isoformat()
        }
        
        # Format detection accuracy
        format_tests = [r for r in self.results if r['test_type'] == 'format_detection_accuracy']
        if format_tests:
            summary['format_detection'] = {
                'average_accuracy': np.mean([r['accuracy_percent'] for r in format_tests])
            }
        
        # Parsing correctness
        parsing_tests = [r for r in self.results if r['test_type'] == 'parsing_correctness']
        if parsing_tests:
            summary['parsing_correctness'] = {
                'success_rate': sum(1 for r in parsing_tests if r['parsing_success']) / len(parsing_tests) * 100,
                'average_data_quality': np.mean([r['data_quality_score'] for r in parsing_tests])
            }
        
        # Data integrity
        integrity_tests = [r for r in self.results if r['test_type'] == 'data_integrity']
        if integrity_tests:
            summary['data_integrity'] = {
                'average_integrity_score': np.mean([r['integrity_score'] for r in integrity_tests]),
                'average_data_loss': np.mean([r['data_loss_rate_percent'] for r in integrity_tests])
            }
        
        return summary

if __name__ == "__main__":
    # Example usage
    tester = AccuracyTester()
    
    # Test with example files if available
    test_files = {
        'browsing': 'browsinglogs_20240924.txt'
    }
    
    existing_files = {k: v for k, v in test_files.items() if os.path.exists(v)}
    
    if existing_files:
        print("Running accuracy tests...")
        
        # Test format detection
        tester.test_format_detection_accuracy(existing_files)
        
        # Test parsing correctness
        for log_type, file_path in existing_files.items():
            tester.test_parsing_correctness(file_path, log_type)
            tester.test_data_integrity(file_path, log_type)
        
        # Save results
        tester.save_results()
        
        # Generate summary
        summary = tester.generate_accuracy_summary()
        print("\nAccuracy Summary:")
        print(json.dumps(summary, indent=2))
    else:
        print("No test files found. Please generate test data first.")
