"""
Performance Benchmarking Suite for Log Analyzer Research Paper
Measures processing speed, memory usage, scalability, and resource utilization
"""

import time
import psutil
import os
import sys
import pandas as pd
import numpy as np
import json
import tracemalloc
from datetime import datetime
from typing import Dict, List, Tuple, Any
import threading
import concurrent.futures
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from log_parser import LogParser
from performance import optimized_parse_file

class PerformanceBenchmark:
    """
    Comprehensive performance benchmarking suite for the log analyzer.
    """
    
    def __init__(self, results_dir: str = "test_results"):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
        self.results = []
        
    def measure_system_resources(self) -> Dict[str, float]:
        """Measure current system resource usage."""
        process = psutil.Process()
        return {
            'cpu_percent': process.cpu_percent(),
            'memory_mb': process.memory_info().rss / 1024 / 1024,
            'memory_percent': process.memory_percent(),
            'disk_io_read': psutil.disk_io_counters().read_bytes if psutil.disk_io_counters() else 0,
            'disk_io_write': psutil.disk_io_counters().write_bytes if psutil.disk_io_counters() else 0,
        }
    
    def benchmark_parsing_speed(self, file_path: str, log_type: str, iterations: int = 3) -> Dict[str, Any]:
        """
        Benchmark parsing speed for different log formats.
        
        Args:
            file_path: Path to the log file
            log_type: Type of log (browsing, virus, mail, etc.)
            iterations: Number of iterations to average
            
        Returns:
            Dictionary with performance metrics
        """
        print(f"Benchmarking parsing speed for {log_type} logs...")
        
        file_size = os.path.getsize(file_path) / 1024 / 1024  # MB
        
        times = []
        memory_usage = []
        
        for i in range(iterations):
            # Start memory tracking
            tracemalloc.start()
            start_resources = self.measure_system_resources()
            
            # Measure parsing time
            start_time = time.time()
            
            parser = LogParser(log_type=log_type)
            df = parser.parse_file(file_path)
            
            end_time = time.time()
            
            # Measure memory usage
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            end_resources = self.measure_system_resources()
            
            parse_time = end_time - start_time
            times.append(parse_time)
            memory_usage.append(peak / 1024 / 1024)  # Convert to MB
            
            print(f"  Iteration {i+1}: {parse_time:.2f}s, {len(df)} records, {peak/1024/1024:.1f}MB peak memory")
        
        # Calculate statistics
        avg_time = np.mean(times)
        std_time = np.std(times)
        avg_memory = np.mean(memory_usage)
        
        # Calculate throughput metrics
        total_records = len(df) if 'df' in locals() else 0
        records_per_second = total_records / avg_time if avg_time > 0 else 0
        mb_per_second = file_size / avg_time if avg_time > 0 else 0
        
        result = {
            'test_type': 'parsing_speed',
            'log_type': log_type,
            'file_size_mb': file_size,
            'total_records': total_records,
            'avg_parse_time': avg_time,
            'std_parse_time': std_time,
            'avg_memory_mb': avg_memory,
            'records_per_second': records_per_second,
            'mb_per_second': mb_per_second,
            'timestamp': datetime.now().isoformat()
        }
        
        self.results.append(result)
        return result
    
    def benchmark_memory_optimization(self, file_path: str, log_type: str) -> Dict[str, Any]:
        """
        Benchmark memory optimization techniques.
        
        Args:
            file_path: Path to the log file
            log_type: Type of log
            
        Returns:
            Dictionary with memory optimization metrics
        """
        print(f"Benchmarking memory optimization for {log_type} logs...")
        
        # Test without optimization
        tracemalloc.start()
        start_time = time.time()
        
        parser = LogParser(log_type=log_type)
        df_normal = parser.parse_file(file_path)
        
        normal_time = time.time() - start_time
        normal_current, normal_peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Test with optimization
        tracemalloc.start()
        start_time = time.time()
        
        df_optimized = optimized_parse_file(file_path, log_type)
        
        optimized_time = time.time() - start_time
        optimized_current, optimized_peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Calculate improvements
        memory_reduction = (normal_peak - optimized_peak) / normal_peak * 100
        time_improvement = (normal_time - optimized_time) / normal_time * 100
        
        result = {
            'test_type': 'memory_optimization',
            'log_type': log_type,
            'normal_memory_mb': normal_peak / 1024 / 1024,
            'optimized_memory_mb': optimized_peak / 1024 / 1024,
            'memory_reduction_percent': memory_reduction,
            'normal_time': normal_time,
            'optimized_time': optimized_time,
            'time_improvement_percent': time_improvement,
            'timestamp': datetime.now().isoformat()
        }
        
        self.results.append(result)
        return result
    
    def benchmark_concurrent_processing(self, file_paths: List[str], log_types: List[str], 
                                      max_workers: int = 4) -> Dict[str, Any]:
        """
        Benchmark concurrent processing capabilities.
        
        Args:
            file_paths: List of file paths to process
            log_types: Corresponding log types
            max_workers: Maximum number of worker threads
            
        Returns:
            Dictionary with concurrency metrics
        """
        print(f"Benchmarking concurrent processing with {max_workers} workers...")
        
        def process_file(file_path: str, log_type: str) -> Tuple[float, int]:
            start_time = time.time()
            parser = LogParser(log_type=log_type)
            df = parser.parse_file(file_path)
            end_time = time.time()
            return end_time - start_time, len(df)
        
        # Sequential processing
        start_time = time.time()
        sequential_results = []
        for file_path, log_type in zip(file_paths, log_types):
            result = process_file(file_path, log_type)
            sequential_results.append(result)
        sequential_time = time.time() - start_time
        
        # Concurrent processing
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(process_file, fp, lt) for fp, lt in zip(file_paths, log_types)]
            concurrent_results = [future.result() for future in concurrent.futures.as_completed(futures)]
        concurrent_time = time.time() - start_time
        
        # Calculate metrics
        speedup = sequential_time / concurrent_time if concurrent_time > 0 else 0
        efficiency = speedup / max_workers * 100
        
        result = {
            'test_type': 'concurrent_processing',
            'num_files': len(file_paths),
            'max_workers': max_workers,
            'sequential_time': sequential_time,
            'concurrent_time': concurrent_time,
            'speedup': speedup,
            'efficiency_percent': efficiency,
            'timestamp': datetime.now().isoformat()
        }
        
        self.results.append(result)
        return result
    
    def benchmark_large_file_processing(self, file_path: str, log_type: str, 
                                      chunk_sizes: List[int] = [1000, 5000, 10000]) -> Dict[str, Any]:
        """
        Benchmark processing of large files with different chunk sizes.
        
        Args:
            file_path: Path to large log file
            log_type: Type of log
            chunk_sizes: Different chunk sizes to test
            
        Returns:
            Dictionary with large file processing metrics
        """
        print(f"Benchmarking large file processing for {log_type} logs...")
        
        file_size = os.path.getsize(file_path) / 1024 / 1024  # MB
        results_by_chunk = {}
        
        for chunk_size in chunk_sizes:
            print(f"  Testing chunk size: {chunk_size}")
            
            tracemalloc.start()
            start_time = time.time()
            
            # Process file in chunks
            parser = LogParser(log_type=log_type)
            chunks = []
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = []
                for i, line in enumerate(f):
                    lines.append(line)
                    if len(lines) >= chunk_size:
                        chunk_df = parser._parse_browsing_logs(lines) if log_type == "browsing" else pd.DataFrame()
                        chunks.append(len(chunk_df))
                        lines = []
                
                # Process remaining lines
                if lines:
                    chunk_df = parser._parse_browsing_logs(lines) if log_type == "browsing" else pd.DataFrame()
                    chunks.append(len(chunk_df))
            
            end_time = time.time()
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            total_records = sum(chunks)
            processing_time = end_time - start_time
            
            results_by_chunk[chunk_size] = {
                'processing_time': processing_time,
                'peak_memory_mb': peak / 1024 / 1024,
                'total_records': total_records,
                'records_per_second': total_records / processing_time if processing_time > 0 else 0
            }
        
        result = {
            'test_type': 'large_file_processing',
            'log_type': log_type,
            'file_size_mb': file_size,
            'chunk_results': results_by_chunk,
            'timestamp': datetime.now().isoformat()
        }
        
        self.results.append(result)
        return result
    
    def save_results(self, filename: str = None) -> str:
        """Save benchmark results to JSON file."""
        if filename is None:
            filename = f"performance_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = self.results_dir / filename
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"Results saved to: {filepath}")
        return str(filepath)
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """Generate a summary report of all benchmark results."""
        if not self.results:
            return {"error": "No results available"}
        
        summary = {
            'total_tests': len(self.results),
            'test_types': list(set(r['test_type'] for r in self.results)),
            'log_types_tested': list(set(r.get('log_type', 'unknown') for r in self.results)),
            'timestamp': datetime.now().isoformat()
        }
        
        # Aggregate parsing speed results
        parsing_results = [r for r in self.results if r['test_type'] == 'parsing_speed']
        if parsing_results:
            summary['parsing_performance'] = {
                'avg_records_per_second': np.mean([r['records_per_second'] for r in parsing_results]),
                'avg_mb_per_second': np.mean([r['mb_per_second'] for r in parsing_results]),
                'avg_memory_usage_mb': np.mean([r['avg_memory_mb'] for r in parsing_results])
            }
        
        # Aggregate memory optimization results
        memory_results = [r for r in self.results if r['test_type'] == 'memory_optimization']
        if memory_results:
            summary['memory_optimization'] = {
                'avg_memory_reduction_percent': np.mean([r['memory_reduction_percent'] for r in memory_results]),
                'avg_time_improvement_percent': np.mean([r['time_improvement_percent'] for r in memory_results])
            }
        
        return summary

if __name__ == "__main__":
    # Example usage
    benchmark = PerformanceBenchmark()
    
    # Test with example log file if available
    example_file = "browsinglogs_20240924.txt"
    if os.path.exists(example_file):
        print("Running performance benchmarks...")
        
        # Benchmark parsing speed
        benchmark.benchmark_parsing_speed(example_file, "browsing")
        
        # Benchmark memory optimization
        benchmark.benchmark_memory_optimization(example_file, "browsing")
        
        # Save results
        benchmark.save_results()
        
        # Generate summary
        summary = benchmark.generate_summary_report()
        print("\nSummary Report:")
        print(json.dumps(summary, indent=2))
    else:
        print(f"Example file {example_file} not found. Please provide log files for testing.")
