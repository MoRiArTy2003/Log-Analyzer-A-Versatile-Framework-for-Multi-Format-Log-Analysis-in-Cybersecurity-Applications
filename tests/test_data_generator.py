"""
Test Data Generator for Log Analyzer Research Paper
Creates diverse test datasets covering all supported log formats and edge cases
"""

import random
import json
import csv
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path
import gzip
import bz2
import zipfile
from typing import List, Dict, Any
import uuid

class TestDataGenerator:
    """
    Generates test data for various log formats and scenarios.
    """
    
    def __init__(self, output_dir: str = "test_data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Common data for realistic log generation
        self.ip_addresses = [
            "192.168.1.100", "10.0.0.50", "172.16.0.25", "203.0.113.10",
            "198.51.100.20", "192.0.2.30", "10.1.1.100", "172.20.0.15"
        ]
        
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X)"
        ]
        
        self.urls = [
            "/index.html", "/login.php", "/dashboard", "/api/users",
            "/admin/panel", "/uploads/file.pdf", "/images/logo.png",
            "/scripts/malicious.js", "/../../etc/passwd", "/admin/../config"
        ]
        
        self.virus_names = [
            "Trojan.Win32.Agent", "Adware.Generic", "Malware.Suspicious",
            "Virus.Boot.Sector", "Ransomware.Locky", "Spyware.Keylogger"
        ]
        
        self.email_domains = [
            "gmail.com", "yahoo.com", "hotmail.com", "company.com",
            "suspicious-domain.ru", "phishing-site.tk", "legitimate.org"
        ]
    
    def generate_browsing_logs(self, num_records: int = 10000, 
                             anomaly_rate: float = 0.05) -> str:
        """Generate browsing logs with optional anomalies."""
        filename = self.output_dir / f"browsing_logs_{num_records}.txt"
        
        with open(filename, 'w') as f:
            for i in range(num_records):
                timestamp = datetime.now() - timedelta(
                    seconds=random.randint(0, 86400 * 7)  # Last 7 days
                )
                
                ip = random.choice(self.ip_addresses)
                username = f"user{random.randint(1, 100)}"
                url = random.choice(self.urls)
                
                # Add anomalies
                if random.random() < anomaly_rate:
                    # Suspicious activity
                    bandwidth = random.randint(100000, 1000000)  # High bandwidth
                    status_code = random.choice([403, 404, 500])  # Error codes
                    url = random.choice(["/admin/../config", "/../../etc/passwd"])
                else:
                    # Normal activity
                    bandwidth = random.randint(1000, 50000)
                    status_code = random.choice([200, 301, 302])
                
                content_type = random.choice(["text/html", "image/png", "application/json"])
                category = random.choice(["Business", "Social", "Entertainment", "Security"])
                device_info = random.choice(self.user_agents)
                
                line = f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')} {ip} {username} {url} {bandwidth} {status_code} {content_type} {category} {device_info}\n"
                f.write(line)
        
        return str(filename)
    
    def generate_virus_logs(self, num_records: int = 5000) -> str:
        """Generate virus/malware detection logs."""
        filename = self.output_dir / f"virus_logs_{num_records}.txt"
        
        with open(filename, 'w') as f:
            for i in range(num_records):
                timestamp = datetime.now() - timedelta(
                    seconds=random.randint(0, 86400 * 30)  # Last 30 days
                )
                
                ip = random.choice(self.ip_addresses)
                username = f"user{random.randint(1, 50)}"
                virus_name = random.choice(self.virus_names)
                file_path = f"C:\\Users\\{username}\\Downloads\\file{random.randint(1, 1000)}.exe"
                action = random.choice(["Quarantined", "Deleted", "Blocked", "Allowed"])
                scan_engine = random.choice(["ClamAV", "Windows Defender", "Kaspersky"])
                severity = random.choice(["Low", "Medium", "High", "Critical"])
                
                line = f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')} {ip} {username} {virus_name} {file_path} {action} {scan_engine} {severity}\n"
                f.write(line)
        
        return str(filename)
    
    def generate_mail_logs(self, num_records: int = 8000) -> str:
        """Generate email server logs."""
        filename = self.output_dir / f"mail_logs_{num_records}.txt"
        
        with open(filename, 'w') as f:
            for i in range(num_records):
                timestamp = datetime.now() - timedelta(
                    seconds=random.randint(0, 86400 * 14)  # Last 14 days
                )
                
                sender_domain = random.choice(self.email_domains)
                recipient_domain = random.choice(self.email_domains)
                
                sender = f"user{random.randint(1, 100)}@{sender_domain}"
                recipient = f"user{random.randint(1, 100)}@{recipient_domain}"
                
                subject = random.choice([
                    "Meeting Reminder", "Invoice Attached", "Urgent: Account Verification",
                    "You've Won $1,000,000!", "Re: Project Update", "Phishing Attempt"
                ])
                
                size = random.randint(1024, 10485760)  # 1KB to 10MB
                status = random.choice(["Delivered", "Bounced", "Spam", "Quarantined"])
                attachment_count = random.randint(0, 5)
                spam_score = random.uniform(0, 10)
                
                line = f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')} {sender} {recipient} {subject} {size} {status} {attachment_count} {spam_score:.2f}\n"
                f.write(line)
        
        return str(filename)
    
    def generate_json_logs(self, num_records: int = 5000) -> str:
        """Generate JSON format logs."""
        filename = self.output_dir / f"json_logs_{num_records}.json"
        
        logs = []
        for i in range(num_records):
            log_entry = {
                "timestamp": (datetime.now() - timedelta(
                    seconds=random.randint(0, 86400 * 7)
                )).isoformat(),
                "level": random.choice(["INFO", "WARN", "ERROR", "DEBUG"]),
                "source": random.choice(["web-server", "database", "auth-service", "api-gateway"]),
                "message": f"Event {i}: " + random.choice([
                    "User login successful",
                    "Database connection established",
                    "API request processed",
                    "Authentication failed",
                    "System error occurred"
                ]),
                "user_id": random.randint(1, 1000),
                "ip_address": random.choice(self.ip_addresses),
                "response_time": random.uniform(0.1, 5.0),
                "status_code": random.choice([200, 201, 400, 401, 403, 404, 500])
            }
            logs.append(log_entry)
        
        with open(filename, 'w') as f:
            for log in logs:
                json.dump(log, f)
                f.write('\n')
        
        return str(filename)
    
    def generate_csv_logs(self, num_records: int = 7000) -> str:
        """Generate CSV format logs."""
        filename = self.output_dir / f"csv_logs_{num_records}.csv"
        
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                'timestamp', 'ip_address', 'user_id', 'action', 
                'resource', 'status', 'bytes_transferred', 'duration'
            ])
            
            for i in range(num_records):
                timestamp = datetime.now() - timedelta(
                    seconds=random.randint(0, 86400 * 7)
                )
                
                row = [
                    timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    random.choice(self.ip_addresses),
                    random.randint(1, 500),
                    random.choice(['GET', 'POST', 'PUT', 'DELETE']),
                    random.choice(self.urls),
                    random.choice([200, 201, 400, 404, 500]),
                    random.randint(100, 100000),
                    random.uniform(0.1, 10.0)
                ]
                writer.writerow(row)
        
        return str(filename)
    
    def generate_syslog_format(self, num_records: int = 6000) -> str:
        """Generate syslog format logs."""
        filename = self.output_dir / f"syslog_{num_records}.log"
        
        facilities = ['kern', 'user', 'mail', 'daemon', 'auth', 'syslog']
        severities = ['emerg', 'alert', 'crit', 'err', 'warning', 'notice', 'info', 'debug']
        
        with open(filename, 'w') as f:
            for i in range(num_records):
                timestamp = datetime.now() - timedelta(
                    seconds=random.randint(0, 86400 * 7)
                )
                
                facility = random.choice(facilities)
                severity = random.choice(severities)
                hostname = f"server{random.randint(1, 10)}"
                process = random.choice(['sshd', 'httpd', 'mysqld', 'kernel'])
                pid = random.randint(1000, 9999)
                
                message = random.choice([
                    "Connection established",
                    "Authentication successful",
                    "Service started",
                    "Error in configuration",
                    "Memory usage high"
                ])
                
                line = f"{timestamp.strftime('%b %d %H:%M:%S')} {hostname} {process}[{pid}]: {message}\n"
                f.write(line)
        
        return str(filename)
    
    def generate_compressed_logs(self, source_file: str, formats: List[str] = ['gzip', 'bz2', 'zip']) -> List[str]:
        """Generate compressed versions of log files."""
        compressed_files = []
        source_path = Path(source_file)
        
        for fmt in formats:
            if fmt == 'gzip':
                output_file = source_path.with_suffix(source_path.suffix + '.gz')
                with open(source_file, 'rb') as f_in:
                    with gzip.open(output_file, 'wb') as f_out:
                        f_out.writelines(f_in)
                compressed_files.append(str(output_file))
                
            elif fmt == 'bz2':
                output_file = source_path.with_suffix(source_path.suffix + '.bz2')
                with open(source_file, 'rb') as f_in:
                    with bz2.open(output_file, 'wb') as f_out:
                        f_out.writelines(f_in)
                compressed_files.append(str(output_file))
                
            elif fmt == 'zip':
                output_file = source_path.with_suffix('.zip')
                with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    zipf.write(source_file, source_path.name)
                compressed_files.append(str(output_file))
        
        return compressed_files
    
    def generate_large_dataset(self, log_type: str, size_mb: int = 100) -> str:
        """Generate large datasets for scalability testing."""
        # Estimate records needed for target size
        if log_type == "browsing":
            # Approximate 200 bytes per record
            num_records = (size_mb * 1024 * 1024) // 200
            return self.generate_browsing_logs(num_records)
        elif log_type == "virus":
            num_records = (size_mb * 1024 * 1024) // 150
            return self.generate_virus_logs(num_records)
        elif log_type == "mail":
            num_records = (size_mb * 1024 * 1024) // 180
            return self.generate_mail_logs(num_records)
        else:
            raise ValueError(f"Unsupported log type: {log_type}")
    
    def generate_all_formats(self, base_records: int = 5000) -> Dict[str, str]:
        """Generate test data for all supported formats."""
        generated_files = {}
        
        print("Generating test data for all formats...")
        
        # Generate each format
        generated_files['browsing'] = self.generate_browsing_logs(base_records)
        generated_files['virus'] = self.generate_virus_logs(base_records)
        generated_files['mail'] = self.generate_mail_logs(base_records)
        generated_files['json'] = self.generate_json_logs(base_records)
        generated_files['csv'] = self.generate_csv_logs(base_records)
        generated_files['syslog'] = self.generate_syslog_format(base_records)
        
        print(f"Generated {len(generated_files)} test files in {self.output_dir}")
        return generated_files

if __name__ == "__main__":
    generator = TestDataGenerator()
    
    # Generate all format test data
    files = generator.generate_all_formats(1000)
    
    # Generate some compressed versions
    for log_type, file_path in files.items():
        if log_type in ['browsing', 'virus']:  # Compress a few examples
            compressed = generator.generate_compressed_logs(file_path, ['gzip'])
            print(f"Generated compressed version: {compressed[0]}")
    
    print("Test data generation complete!")
