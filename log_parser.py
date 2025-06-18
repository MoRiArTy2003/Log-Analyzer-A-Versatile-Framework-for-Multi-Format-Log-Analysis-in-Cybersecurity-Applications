"""
Log parser module for handling different types of log files.
"""
import pandas as pd
import streamlit as st
import re
import io
import os
import gzip
import bz2
import zipfile
import json
import xml.etree.ElementTree as ET
import csv
from datetime import datetime
from typing import List, Optional

from config import LOG_TYPES, DEFAULT_LOG_TYPE
from utils import detect_log_type, format_timestamp

class LogParser:
    """Class for parsing and processing log files of different formats."""

    def __init__(self, log_type: Optional[str] = None):
        """
        Initialize the log parser.

        Args:
            log_type: Type of log to parse (browsing, virus, mail, etc.)
                     If None, the parser will attempt to detect the log type.
        """
        self.log_type = log_type or DEFAULT_LOG_TYPE
        self.columns = LOG_TYPES.get(self.log_type, {}).get("columns", [])
        self.separator = LOG_TYPES.get(self.log_type, {}).get("separator", " ")
        self.datetime_format = LOG_TYPES.get(self.log_type, {}).get("datetime_format", "%Y%m%d%H%M%S")

    def parse_file(self, file_path: str) -> pd.DataFrame:
        """
        Parse a log file and return a DataFrame.

        Args:
            file_path: Path to the log file

        Returns:
            pd.DataFrame: DataFrame containing the parsed log data
        """
        try:
            # If log_type wasn't specified, try to detect it
            if self.log_type == DEFAULT_LOG_TYPE:
                detected_type = detect_log_type(file_path)
                if detected_type != self.log_type:
                    self.log_type = detected_type
                    self.columns = LOG_TYPES.get(self.log_type, {}).get("columns", [])
                    self.separator = LOG_TYPES.get(self.log_type, {}).get("separator", " ")
                    self.datetime_format = LOG_TYPES.get(self.log_type, {}).get("datetime_format", "%Y%m%d%H%M%S")

            # Detect file format and read accordingly
            file_format = self._detect_file_format(file_path)
            lines = self._read_file_by_format(file_path, file_format)

            # Try to detect log format from content if not already specified
            if self.log_type == DEFAULT_LOG_TYPE:
                self._detect_log_format_from_content(lines[:10])

            # Parse the lines based on the log type
            if self.log_type == "browsing":
                return self._parse_browsing_logs(lines)
            elif self.log_type == "virus":
                return self._parse_virus_logs(lines)
            elif self.log_type == "mail":
                return self._parse_mail_logs(lines)
            elif self.log_type == "firewall":
                return self._parse_firewall_logs(lines)
            elif self.log_type == "auth":
                return self._parse_auth_logs(lines)
            elif self.log_type == "system":
                return self._parse_system_logs(lines)
            elif self.log_type == "ids":
                return self._parse_ids_logs(lines)
            elif self.log_type == "vpn":
                return self._parse_vpn_logs(lines)
            elif self.log_type == "syslog":
                return self._parse_syslog_format(lines)
            elif self.log_type == "clf":
                return self._parse_common_log_format(lines)
            elif self.log_type == "elf":
                return self._parse_extended_log_format(lines)
            elif self.log_type == "json":
                return self._parse_json_format(lines)
            elif self.log_type == "xml":
                return self._parse_xml_format(lines)
            elif self.log_type == "csv":
                return self._parse_csv_format(lines)
            else:
                # Generic parsing for unknown log types
                return self._parse_generic_logs(lines)

        except Exception as e:
            st.error(f"Error parsing log file: {e}")
            import traceback
            st.error(traceback.format_exc())
            return pd.DataFrame(columns=self.columns)

    def parse_uploaded_file(self, uploaded_file) -> pd.DataFrame:
        """
        Parse an uploaded file and return a DataFrame.

        Args:
            uploaded_file: Streamlit uploaded file object

        Returns:
            pd.DataFrame: DataFrame containing the parsed log data
        """
        try:
            # Detect file format from file name and content
            file_format = self._detect_uploaded_file_format(uploaded_file)

            # Read the file content based on its format
            lines = self._read_uploaded_file_by_format(uploaded_file, file_format)

            # Try to detect log format from content
            self._detect_log_format_from_content(lines[:10])

            # Parse the lines based on the log type
            if self.log_type == "browsing":
                return self._parse_browsing_logs(lines)
            elif self.log_type == "virus":
                return self._parse_virus_logs(lines)
            elif self.log_type == "mail":
                return self._parse_mail_logs(lines)
            elif self.log_type == "firewall":
                return self._parse_firewall_logs(lines)
            elif self.log_type == "auth":
                return self._parse_auth_logs(lines)
            elif self.log_type == "system":
                return self._parse_system_logs(lines)
            elif self.log_type == "application":
                return self._parse_application_logs(lines)
            elif self.log_type == "ids":
                return self._parse_ids_logs(lines)
            elif self.log_type == "vpn":
                return self._parse_vpn_logs(lines)
            elif self.log_type == "syslog":
                return self._parse_syslog_format(lines)
            elif self.log_type == "clf":
                return self._parse_common_log_format(lines)
            elif self.log_type == "elf":
                return self._parse_extended_log_format(lines)
            elif self.log_type == "json":
                return self._parse_json_format(lines)
            elif self.log_type == "xml":
                return self._parse_xml_format(lines)
            elif self.log_type == "csv":
                return self._parse_csv_format(lines)
            else:
                # Generic parsing for unknown log types
                return self._parse_generic_logs(lines)

        except Exception as e:
            st.error(f"Error parsing uploaded file: {e}")
            import traceback
            st.error(traceback.format_exc())
            return pd.DataFrame(columns=self.columns)

    def _detect_file_format(self, file_path: str) -> str:
        """
        Detect the format of a file based on its extension and content.

        Args:
            file_path: Path to the file

        Returns:
            str: Detected file format (plain, gzip, bz2, zip, binary, json, xml, csv)
        """
        # Check file extension first
        file_ext = os.path.splitext(file_path)[1].lower()

        if file_ext in ['.gz', '.gzip']:
            return 'gzip'
        elif file_ext in ['.bz2', '.bzip2']:
            return 'bz2'
        elif file_ext in ['.zip']:
            return 'zip'
        elif file_ext in ['.json']:
            return 'json'
        elif file_ext in ['.xml']:
            return 'xml'
        elif file_ext in ['.csv']:
            return 'csv'

        # If extension doesn't give a clear answer, check content
        try:
            # Try to read the first few bytes to check if it's binary
            with open(file_path, 'rb') as f:
                header = f.read(8)

            # Check for common binary file signatures
            if header.startswith(b'\x1f\x8b'):  # gzip
                return 'gzip'
            elif header.startswith(b'BZh'):     # bzip2
                return 'bz2'
            elif header.startswith(b'PK\x03\x04'):  # zip
                return 'zip'

            # Check if it's a binary file by looking for null bytes and control characters
            text_chars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7f})
            is_binary = bool(header.translate(None, text_chars))
            if is_binary:
                return 'binary'

            # Try to read the first line to check for structured formats
            with open(file_path, 'r', errors='ignore') as f:
                first_line = f.readline().strip()

            # Check for JSON format
            if first_line.startswith('{') or first_line.startswith('['):
                try:
                    json.loads(first_line)
                    return 'json'
                except:
                    pass

            # Check for XML format
            if first_line.startswith('<?xml') or first_line.startswith('<'):
                return 'xml'

            # Check for CSV format
            if ',' in first_line and len(first_line.split(',')) > 1:
                return 'csv'

            # Default to plain text
            return 'plain'

        except Exception:
            # If any error occurs, default to plain text
            return 'plain'

    def _read_file_by_format(self, file_path: str, file_format: str) -> List[str]:
        """
        Read a file based on its detected format.

        Args:
            file_path: Path to the file
            file_format: Format of the file

        Returns:
            List[str]: Lines from the file
        """
        lines = []

        try:
            if file_format == 'gzip':
                with gzip.open(file_path, 'rt', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
            elif file_format == 'bz2':
                with bz2.open(file_path, 'rt', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
            elif file_format == 'zip':
                with zipfile.ZipFile(file_path) as zf:
                    # Get the first file in the archive
                    first_file = zf.namelist()[0]
                    with zf.open(first_file) as f:
                        lines = [line.decode('utf-8', errors='ignore') for line in f.readlines()]
            elif file_format == 'json':
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    json_data = json.load(f)
                    # Convert JSON to lines
                    if isinstance(json_data, list):
                        lines = [json.dumps(item) for item in json_data]
                    else:
                        lines = [json.dumps(json_data)]
            elif file_format == 'xml':
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    xml_content = f.read()
                    # Parse XML and convert to lines
                    root = ET.fromstring(xml_content)
                    lines = [ET.tostring(elem, encoding='unicode') for elem in root.findall('.//*')]
            elif file_format == 'csv':
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    csv_reader = csv.reader(f)
                    lines = [','.join(row) for row in csv_reader]
            elif file_format == 'binary':
                # For binary files, try to extract text content
                with open(file_path, 'rb') as f:
                    binary_data = f.read()
                    # Try to decode as utf-8, ignoring errors
                    text_content = binary_data.decode('utf-8', errors='ignore')
                    lines = text_content.splitlines()
            else:  # plain text
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
        except Exception as e:
            st.warning(f"Error reading file with format {file_format}: {e}. Falling back to plain text.")
            try:
                # Fallback to plain text
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
            except Exception as e2:
                st.error(f"Error reading file as plain text: {e2}")
                lines = []

        return lines

    def _detect_uploaded_file_format(self, uploaded_file) -> str:
        """
        Detect the format of an uploaded file.

        Args:
            uploaded_file: Streamlit uploaded file object

        Returns:
            str: Detected file format
        """
        # Check file name extension
        file_name = uploaded_file.name.lower()
        file_ext = os.path.splitext(file_name)[1].lower()

        if file_ext in ['.gz', '.gzip']:
            return 'gzip'
        elif file_ext in ['.bz2', '.bzip2']:
            return 'bz2'
        elif file_ext in ['.zip']:
            return 'zip'
        elif file_ext in ['.json']:
            return 'json'
        elif file_ext in ['.xml']:
            return 'xml'
        elif file_ext in ['.csv']:
            return 'csv'

        # If extension doesn't give a clear answer, check content
        try:
            # Read the first few bytes
            header = uploaded_file.read(8)
            uploaded_file.seek(0)  # Reset position

            # Check for common binary file signatures
            if header.startswith(b'\x1f\x8b'):  # gzip
                return 'gzip'
            elif header.startswith(b'BZh'):     # bzip2
                return 'bz2'
            elif header.startswith(b'PK\x03\x04'):  # zip
                return 'zip'

            # Check if it's a binary file
            text_chars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7f})
            is_binary = bool(header.translate(None, text_chars))
            if is_binary:
                return 'binary'

            # Default to plain text
            return 'plain'

        except Exception:
            # If any error occurs, default to plain text
            return 'plain'

    def _read_uploaded_file_by_format(self, uploaded_file, file_format: str) -> List[str]:
        """
        Read an uploaded file based on its detected format.

        Args:
            uploaded_file: Streamlit uploaded file object
            file_format: Format of the file

        Returns:
            List[str]: Lines from the file
        """
        lines = []

        try:
            if file_format == 'gzip':
                content = uploaded_file.read()
                with gzip.open(io.BytesIO(content), 'rt', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
            elif file_format == 'bz2':
                content = uploaded_file.read()
                with bz2.open(io.BytesIO(content), 'rt', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
            elif file_format == 'zip':
                content = uploaded_file.read()
                with zipfile.ZipFile(io.BytesIO(content)) as zf:
                    # Get the first file in the archive
                    first_file = zf.namelist()[0]
                    with zf.open(first_file) as f:
                        lines = [line.decode('utf-8', errors='ignore') for line in f.readlines()]
            elif file_format == 'json':
                content = uploaded_file.read().decode('utf-8', errors='ignore')
                json_data = json.loads(content)
                # Convert JSON to lines
                if isinstance(json_data, list):
                    lines = [json.dumps(item) for item in json_data]
                else:
                    lines = [json.dumps(json_data)]
            elif file_format == 'xml':
                content = uploaded_file.read().decode('utf-8', errors='ignore')
                # Parse XML and convert to lines
                root = ET.fromstring(content)
                lines = [ET.tostring(elem, encoding='unicode') for elem in root.findall('.//*')]
            elif file_format == 'csv':
                content = uploaded_file.read().decode('utf-8', errors='ignore')
                csv_reader = csv.reader(io.StringIO(content))
                lines = [','.join(row) for row in csv_reader]
            elif file_format == 'binary':
                # For binary files, try to extract text content
                binary_data = uploaded_file.read()
                # Try to decode as utf-8, ignoring errors
                text_content = binary_data.decode('utf-8', errors='ignore')
                lines = text_content.splitlines()
            else:  # plain text
                content = uploaded_file.read().decode('utf-8', errors='ignore')
                lines = content.splitlines()
        except Exception as e:
            st.warning(f"Error reading uploaded file with format {file_format}: {e}. Falling back to plain text.")
            try:
                # Fallback to plain text
                uploaded_file.seek(0)  # Reset position
                content = uploaded_file.read().decode('utf-8', errors='ignore')
                lines = content.splitlines()
            except Exception as e2:
                st.error(f"Error reading uploaded file as plain text: {e2}")
                lines = []

        return lines

    def _detect_log_format_from_content(self, sample_lines: List[str]) -> None:
        """
        Detect log format from content and update parser settings.

        Args:
            sample_lines: Sample lines from the log file
        """
        # First check for structured formats
        if sample_lines and sample_lines[0].strip().startswith('{'):
            try:
                json.loads(sample_lines[0])
                self.log_type = "json"
                return
            except:
                pass

        # Check for Common Log Format (CLF)
        clf_pattern = r'^\S+ \S+ \S+ \[\d+/\w+/\d+:\d+:\d+:\d+ [+-]\d+\] "\S+ \S+ \S+" \d+ \d+$'
        if sample_lines and re.match(clf_pattern, sample_lines[0].strip()):
            self.log_type = "clf"
            return

        # Check for Extended Log Format (ELF)
        if sample_lines and sample_lines[0].strip().startswith('#Fields:'):
            self.log_type = "elf"
            return

        # Check for Syslog format
        syslog_pattern = r'^\w{3} [ 0-9]\d \d{2}:\d{2}:\d{2} \S+ \S+(\[\d+\])?:'
        if sample_lines and re.match(syslog_pattern, sample_lines[0].strip()):
            self.log_type = "syslog"
            return

        # If no structured format detected, fall back to content-based detection for log types
        for line in sample_lines:
            # Check for browsing log patterns (URLs, HTTP status codes)
            if re.search(r'https?://|www\.|\.(com|org|net|edu|gov)', line) and re.search(r'\b[1-5][0-9]{2}\b', line):
                self.log_type = "browsing"
                break

            # Check for virus log patterns
            if re.search(r'virus|malware|trojan|infected|quarantine', line, re.IGNORECASE):
                self.log_type = "virus"
                break

            # Check for mail log patterns
            if re.search(r'@|sender|recipient|subject|spam|mail', line, re.IGNORECASE):
                self.log_type = "mail"
                break

            # Check for firewall log patterns
            if re.search(r'firewall|allow|deny|block|accept|drop|src|dst|port', line, re.IGNORECASE):
                self.log_type = "firewall"
                break

            # Check for authentication log patterns
            if re.search(r'login|logout|auth|failed|success|user|password|session', line, re.IGNORECASE):
                self.log_type = "auth"
                break

            # Check for system log patterns
            if re.search(r'system|kernel|daemon|cron|service|start|stop|restart', line, re.IGNORECASE):
                self.log_type = "system"
                break

            # Check for application log patterns
            if re.search(r'error|warning|info|debug|trace|exception|stack', line, re.IGNORECASE):
                self.log_type = "application"
                break

            # Check for IDS/IPS log patterns
            if re.search(r'intrusion|detection|prevention|alert|signature|attack', line, re.IGNORECASE):
                self.log_type = "ids"
                break

            # Check for VPN log patterns
            if re.search(r'vpn|tunnel|connect|disconnect|remote|client', line, re.IGNORECASE):
                self.log_type = "vpn"
                break

        # Update parser settings based on detected log type
        self.columns = LOG_TYPES.get(self.log_type, {}).get("columns", [])
        self.separator = LOG_TYPES.get(self.log_type, {}).get("separator", " ")
        self.datetime_format = LOG_TYPES.get(self.log_type, {}).get("datetime_format", "%Y%m%d%H%M%S")

    def _detect_log_type_from_content(self, sample_lines: List[str]) -> None:
        """
        Detect log type from content and update parser settings.

        Args:
            sample_lines: Sample lines from the log file
        """
        # Check for patterns in the sample lines
        for line in sample_lines:
            # Check for browsing log patterns (URLs, HTTP status codes)
            if re.search(r'https?://|www\.|\.(com|org|net|edu|gov)', line) and re.search(r'\b[1-5][0-9]{2}\b', line):
                self.log_type = "browsing"
                break

            # Check for virus log patterns
            if re.search(r'virus|malware|trojan|infected|quarantine', line, re.IGNORECASE):
                self.log_type = "virus"
                break

            # Check for mail log patterns
            if re.search(r'@|sender|recipient|subject|spam|mail', line, re.IGNORECASE):
                self.log_type = "mail"
                break

            # Check for firewall log patterns
            if re.search(r'firewall|allow|deny|block|accept|drop|src|dst|port', line, re.IGNORECASE):
                self.log_type = "firewall"
                break

            # Check for authentication log patterns
            if re.search(r'login|logout|auth|failed|success|user|password|session', line, re.IGNORECASE):
                self.log_type = "auth"
                break

            # Check for system log patterns
            if re.search(r'system|kernel|daemon|cron|service|start|stop|restart', line, re.IGNORECASE):
                self.log_type = "system"
                break

            # Check for application log patterns
            if re.search(r'error|warning|info|debug|trace|exception|stack', line, re.IGNORECASE):
                self.log_type = "application"
                break

            # Check for IDS/IPS log patterns
            if re.search(r'intrusion|detection|prevention|alert|signature|attack', line, re.IGNORECASE):
                self.log_type = "ids"
                break

            # Check for VPN log patterns
            if re.search(r'vpn|tunnel|connect|disconnect|remote|client', line, re.IGNORECASE):
                self.log_type = "vpn"
                break

        # Update parser settings based on detected log type
        self.columns = LOG_TYPES.get(self.log_type, {}).get("columns", [])
        self.separator = LOG_TYPES.get(self.log_type, {}).get("separator", " ")
        self.datetime_format = LOG_TYPES.get(self.log_type, {}).get("datetime_format", "%Y%m%d%H%M%S")

    def _parse_browsing_logs(self, lines: List[str]) -> pd.DataFrame:
        """
        Parse browsing logs.

        Args:
            lines: Lines from the log file

        Returns:
            pd.DataFrame: DataFrame containing the parsed browsing log data
        """
        data = []

        for line in lines:
            # Split the line into parts
            parts = line.strip().split(maxsplit=8)  # Split into 9 parts max

            if len(parts) >= 9:
                # Extract the parts into variables
                timestamp, ip_address, username, url, bandwidth, status_code, content_type, category, device_info = parts

                # Format the timestamp
                formatted_timestamp = format_timestamp(timestamp, "browsing")

                # Add the data to the list
                data.append({
                    "timestamp": formatted_timestamp,
                    "raw_timestamp": timestamp,
                    "ip_address": ip_address,
                    "username": username,
                    "url": url,
                    "bandwidth": bandwidth,
                    "status_code": status_code,
                    "content_type": content_type,
                    "category": category,
                    "device_info": device_info
                })

        # Create a DataFrame from the data
        df = pd.DataFrame(data)

        # Convert numeric columns
        if not df.empty:
            df["bandwidth"] = pd.to_numeric(df["bandwidth"], errors="coerce")
            df["status_code"] = pd.to_numeric(df["status_code"], errors="coerce")
            df["datetime"] = pd.to_datetime(df["raw_timestamp"].astype(int), unit='s', errors='coerce')

        return df

    def _parse_virus_logs(self, lines: List[str]) -> pd.DataFrame:
        """
        Parse virus logs.

        Args:
            lines: Lines from the log file

        Returns:
            pd.DataFrame: DataFrame containing the parsed virus log data
        """
        # Placeholder for virus log parsing
        # This would be implemented based on the actual virus log format
        data = []

        for line in lines:
            # Split the line into parts
            parts = line.strip().split(maxsplit=7)  # Adjust based on actual format

            if len(parts) >= 8:
                # Extract the parts into variables
                timestamp, ip_address, username, virus_name, file_path, action_taken, scan_engine, severity = parts

                # Format the timestamp
                formatted_timestamp = format_timestamp(timestamp, "virus")

                # Add the data to the list
                data.append({
                    "timestamp": formatted_timestamp,
                    "raw_timestamp": timestamp,
                    "ip_address": ip_address,
                    "username": username,
                    "virus_name": virus_name,
                    "file_path": file_path,
                    "action_taken": action_taken,
                    "scan_engine": scan_engine,
                    "severity": severity
                })

        # Create a DataFrame from the data
        df = pd.DataFrame(data)

        return df

    def _parse_mail_logs(self, lines: List[str]) -> pd.DataFrame:
        """
        Parse mail logs.

        Args:
            lines: Lines from the log file

        Returns:
            pd.DataFrame: DataFrame containing the parsed mail log data
        """
        # Placeholder for mail log parsing
        # This would be implemented based on the actual mail log format
        data = []

        for line in lines:
            # Split the line into parts
            parts = line.strip().split(maxsplit=7)  # Adjust based on actual format

            if len(parts) >= 8:
                # Extract the parts into variables
                timestamp, sender, recipient, subject, size, status, attachment_count, spam_score = parts

                # Format the timestamp
                formatted_timestamp = format_timestamp(timestamp, "mail")

                # Add the data to the list
                data.append({
                    "timestamp": formatted_timestamp,
                    "raw_timestamp": timestamp,
                    "sender": sender,
                    "recipient": recipient,
                    "subject": subject,
                    "size": size,
                    "status": status,
                    "attachment_count": attachment_count,
                    "spam_score": spam_score
                })

        # Create a DataFrame from the data
        df = pd.DataFrame(data)

        return df

    def _parse_firewall_logs(self, lines: List[str]) -> pd.DataFrame:
        """
        Parse firewall logs.

        Args:
            lines: Lines from the log file

        Returns:
            pd.DataFrame: DataFrame containing the parsed firewall log data
        """
        data = []

        for line in lines:
            # Split the line into parts
            parts = line.strip().split(maxsplit=9)  # Adjust based on actual format

            if len(parts) >= 10:
                # Extract the parts into variables
                timestamp, action, protocol, src_ip, src_port, dst_ip, dst_port, interface, rule_id, description = parts

                # Format the timestamp
                formatted_timestamp = format_timestamp(timestamp, "firewall")

                # Add the data to the list
                data.append({
                    "timestamp": formatted_timestamp,
                    "raw_timestamp": timestamp,
                    "action": action,
                    "protocol": protocol,
                    "src_ip": src_ip,
                    "src_port": src_port,
                    "dst_ip": dst_ip,
                    "dst_port": dst_port,
                    "interface": interface,
                    "rule_id": rule_id,
                    "description": description
                })

        # Create a DataFrame from the data
        df = pd.DataFrame(data)

        return df

    def _parse_auth_logs(self, lines: List[str]) -> pd.DataFrame:
        """
        Parse authentication logs.

        Args:
            lines: Lines from the log file

        Returns:
            pd.DataFrame: DataFrame containing the parsed authentication log data
        """
        data = []

        for line in lines:
            # Split the line into parts
            parts = line.strip().split(maxsplit=6)  # Adjust based on actual format

            if len(parts) >= 7:
                # Extract the parts into variables
                timestamp, username, source_ip, service, status, auth_method, details = parts

                # Format the timestamp
                formatted_timestamp = format_timestamp(timestamp, "auth")

                # Add the data to the list
                data.append({
                    "timestamp": formatted_timestamp,
                    "raw_timestamp": timestamp,
                    "username": username,
                    "source_ip": source_ip,
                    "service": service,
                    "status": status,
                    "auth_method": auth_method,
                    "details": details
                })

        # Create a DataFrame from the data
        df = pd.DataFrame(data)

        return df

    def _parse_system_logs(self, lines: List[str]) -> pd.DataFrame:
        """
        Parse system logs.

        Args:
            lines: Lines from the log file

        Returns:
            pd.DataFrame: DataFrame containing the parsed system log data
        """
        data = []

        for line in lines:
            # Split the line into parts
            parts = line.strip().split(maxsplit=5)  # Adjust based on actual format

            if len(parts) >= 6:
                # Extract the parts into variables
                timestamp, hostname, service, pid, level, message = parts

                # Format the timestamp
                formatted_timestamp = format_timestamp(timestamp, "system")

                # Add the data to the list
                data.append({
                    "timestamp": formatted_timestamp,
                    "raw_timestamp": timestamp,
                    "hostname": hostname,
                    "service": service,
                    "pid": pid,
                    "level": level,
                    "message": message
                })

        # Create a DataFrame from the data
        df = pd.DataFrame(data)

        return df

    def _parse_application_logs(self, lines: List[str]) -> pd.DataFrame:
        """
        Parse application logs.

        Args:
            lines: Lines from the log file

        Returns:
            pd.DataFrame: DataFrame containing the parsed application log data
        """
        data = []

        for line in lines:
            # Split the line into parts
            parts = line.strip().split(maxsplit=6)  # Adjust based on actual format

            if len(parts) >= 7:
                # Extract the parts into variables
                timestamp, app_name, level, component, thread_id, request_id, message = parts

                # Format the timestamp
                formatted_timestamp = format_timestamp(timestamp, "application")

                # Add the data to the list
                data.append({
                    "timestamp": formatted_timestamp,
                    "raw_timestamp": timestamp,
                    "app_name": app_name,
                    "level": level,
                    "component": component,
                    "thread_id": thread_id,
                    "request_id": request_id,
                    "message": message
                })

        # Create a DataFrame from the data
        df = pd.DataFrame(data)

        return df

    def _parse_ids_logs(self, lines: List[str]) -> pd.DataFrame:
        """
        Parse IDS/IPS logs.

        Args:
            lines: Lines from the log file

        Returns:
            pd.DataFrame: DataFrame containing the parsed IDS/IPS log data
        """
        data = []

        for line in lines:
            # Split the line into parts
            parts = line.strip().split(maxsplit=8)  # Adjust based on actual format

            if len(parts) >= 9:
                # Extract the parts into variables
                timestamp, alert_id, severity, category, src_ip, dst_ip, protocol, signature, description = parts

                # Format the timestamp
                formatted_timestamp = format_timestamp(timestamp, "ids")

                # Add the data to the list
                data.append({
                    "timestamp": formatted_timestamp,
                    "raw_timestamp": timestamp,
                    "alert_id": alert_id,
                    "severity": severity,
                    "category": category,
                    "src_ip": src_ip,
                    "dst_ip": dst_ip,
                    "protocol": protocol,
                    "signature": signature,
                    "description": description
                })

        # Create a DataFrame from the data
        df = pd.DataFrame(data)

        return df

    def _parse_vpn_logs(self, lines: List[str]) -> pd.DataFrame:
        """
        Parse VPN logs.

        Args:
            lines: Lines from the log file

        Returns:
            pd.DataFrame: DataFrame containing the parsed VPN log data
        """
        data = []

        for line in lines:
            # Split the line into parts
            parts = line.strip().split(maxsplit=7)  # Adjust based on actual format

            if len(parts) >= 8:
                # Extract the parts into variables
                timestamp, username, client_ip, session_id, event_type, duration, bytes_in, bytes_out = parts

                # Format the timestamp
                formatted_timestamp = format_timestamp(timestamp, "vpn")

                # Add the data to the list
                data.append({
                    "timestamp": formatted_timestamp,
                    "raw_timestamp": timestamp,
                    "username": username,
                    "client_ip": client_ip,
                    "session_id": session_id,
                    "event_type": event_type,
                    "duration": duration,
                    "bytes_in": bytes_in,
                    "bytes_out": bytes_out
                })

        # Create a DataFrame from the data
        df = pd.DataFrame(data)

        return df

    def _parse_syslog_format(self, lines: List[str]) -> pd.DataFrame:
        """
        Parse syslog format logs.

        Args:
            lines: Lines from the log file

        Returns:
            pd.DataFrame: DataFrame containing the parsed log data
        """
        data = []

        # Syslog pattern: Month Day Time Hostname Process[PID]: Message
        syslog_pattern = r'^(\w{3} [ 0-9]\d \d{2}:\d{2}:\d{2}) (\S+) (\S+)(?:\[(\d+)\])?: (.*)$'

        for line in lines:
            match = re.match(syslog_pattern, line.strip())
            if match:
                timestamp, hostname, process, pid, message = match.groups()

                # Add the data to the list
                data.append({
                    "timestamp": timestamp,
                    "hostname": hostname,
                    "process": process,
                    "pid": pid if pid else "",
                    "message": message
                })

        # Create a DataFrame from the data
        df = pd.DataFrame(data)

        return df

    def _parse_common_log_format(self, lines: List[str]) -> pd.DataFrame:
        """
        Parse Common Log Format (CLF) logs.

        Args:
            lines: Lines from the log file

        Returns:
            pd.DataFrame: DataFrame containing the parsed log data
        """
        data = []

        # CLF pattern: host ident authuser [date] "request" status bytes
        clf_pattern = r'^(\S+) (\S+) (\S+) \[([^]]+)\] "([^"]*)" (\d+) (\d+)$'

        for line in lines:
            match = re.match(clf_pattern, line.strip())
            if match:
                host, ident, authuser, date, request, status, bytes_sent = match.groups()

                # Parse the request into method, path, and protocol
                request_parts = request.split()
                method = request_parts[0] if len(request_parts) > 0 else ""
                path = request_parts[1] if len(request_parts) > 1 else ""
                protocol = request_parts[2] if len(request_parts) > 2 else ""

                # Add the data to the list
                data.append({
                    "host": host,
                    "ident": ident,
                    "authuser": authuser,
                    "timestamp": date,
                    "method": method,
                    "path": path,
                    "protocol": protocol,
                    "status": status,
                    "bytes_sent": bytes_sent,
                    "url": path  # Add URL field for compatibility with browsing logs
                })

        # Create a DataFrame from the data
        df = pd.DataFrame(data)

        return df

    def _parse_extended_log_format(self, lines: List[str]) -> pd.DataFrame:
        """
        Parse Extended Log Format (ELF) logs.

        Args:
            lines: Lines from the log file

        Returns:
            pd.DataFrame: DataFrame containing the parsed log data
        """
        data = []
        fields = []

        # Process the lines
        for line in lines:
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Process directive lines
            if line.startswith('#'):
                if line.startswith('#Fields:'):
                    # Extract field names
                    fields = line[8:].strip().split()
                continue

            # Process data lines if we have fields
            if fields:
                parts = line.split()

                # Create a dictionary with the parts
                row = {}
                for i, part in enumerate(parts):
                    if i < len(fields):
                        row[fields[i]] = part
                    else:
                        # If there are more parts than fields, add them to the last field
                        if fields:
                            row[fields[-1]] = row.get(fields[-1], "") + " " + part

                # Add the row to the data
                if row:
                    # Add URL field for compatibility with browsing logs if cs-uri-stem exists
                    if 'cs-uri-stem' in row:
                        row['url'] = row['cs-uri-stem']

                    data.append(row)

        # Create a DataFrame from the data
        df = pd.DataFrame(data)

        return df

    def _parse_json_format(self, lines: List[str]) -> pd.DataFrame:
        """
        Parse JSON format logs.

        Args:
            lines: Lines from the log file

        Returns:
            pd.DataFrame: DataFrame containing the parsed log data
        """
        data = []

        for line in lines:
            try:
                # Parse the JSON object
                json_obj = json.loads(line.strip())

                # Add the object to the data
                data.append(json_obj)
            except json.JSONDecodeError:
                # Skip invalid JSON
                continue

        # Create a DataFrame from the data
        df = pd.DataFrame(data)

        return df

    def _parse_xml_format(self, lines: List[str]) -> pd.DataFrame:
        """
        Parse XML format logs.

        Args:
            lines: Lines from the log file

        Returns:
            pd.DataFrame: DataFrame containing the parsed log data
        """
        data = []

        for line in lines:
            try:
                # Parse the XML element
                elem = ET.fromstring(line.strip())

                # Convert element to dictionary
                row = {}
                for child in elem:
                    row[child.tag] = child.text

                # Add the row to the data
                if row:
                    data.append(row)
            except ET.ParseError:
                # Skip invalid XML
                continue

        # Create a DataFrame from the data
        df = pd.DataFrame(data)

        return df

    def _parse_csv_format(self, lines: List[str]) -> pd.DataFrame:
        """
        Parse CSV format logs.

        Args:
            lines: Lines from the log file

        Returns:
            pd.DataFrame: DataFrame containing the parsed log data
        """
        # Create a CSV reader
        csv_reader = csv.reader(lines)

        # Get the header row
        header = next(csv_reader, None)

        # If no header, use default column names
        if not header:
            return pd.DataFrame()

        # Process the data rows
        data = []
        for row in csv_reader:
            # Create a dictionary with the row values
            row_dict = {}
            for i, value in enumerate(row):
                if i < len(header):
                    row_dict[header[i]] = value

            # Add the row to the data
            if row_dict:
                data.append(row_dict)

        # Create a DataFrame from the data
        df = pd.DataFrame(data)

        return df

    def _parse_generic_logs(self, lines: List[str]) -> pd.DataFrame:
        """
        Parse generic logs when the format is unknown.

        Args:
            lines: Lines from the log file

        Returns:
            pd.DataFrame: DataFrame containing the parsed log data
        """
        data = []

        for line in lines:
            # Split the line into parts
            parts = line.strip().split(self.separator)

            # Create a dictionary with the parts
            row = {}
            for i, part in enumerate(parts):
                if i < len(self.columns):
                    row[self.columns[i]] = part
                else:
                    # If there are more parts than columns, add them to the last column
                    if self.columns:
                        row[self.columns[-1]] = row.get(self.columns[-1], "") + " " + part

            # Add the row to the data
            if row:
                data.append(row)

        # Create a DataFrame from the data
        df = pd.DataFrame(data)

        return df
