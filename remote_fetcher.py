"""
Remote log fetcher module for retrieving logs from remote systems.
"""
import os
import io
import tempfile
import streamlit as st
import paramiko
import requests
import ftplib
from urllib.parse import urlparse
from typing import Optional, Tuple, List, Dict, Any, BinaryIO, Union

class RemoteLogFetcher:
    """Class for fetching logs from remote systems."""

    def __init__(self):
        """Initialize the remote log fetcher."""
        # Create a temporary directory for storing fetched logs
        self.temp_dir = tempfile.mkdtemp(prefix="log_analyzer_")

    def __del__(self):
        """Clean up temporary files on deletion."""
        try:
            # Clean up temporary files
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except:
            pass

    def fetch_log(self, source_url: str, credentials: Optional[Dict[str, str]] = None) -> Tuple[bool, str, Optional[str]]:
        """
        Fetch a log file from a remote source.

        Args:
            source_url: URL or path to the remote log file
            credentials: Optional dictionary with authentication credentials

        Returns:
            Tuple containing:
                - Success flag (True/False)
                - Local path to the fetched file or error message
                - Optional content type
        """
        try:
            # Parse the URL to determine the protocol
            parsed_url = urlparse(source_url)
            protocol = parsed_url.scheme.lower()

            # Handle different protocols
            if protocol in ['ssh', 'scp']:
                return self._fetch_via_ssh(source_url, credentials)
            elif protocol in ['http', 'https']:
                return self._fetch_via_http(source_url, credentials)
            elif protocol in ['ftp', 'sftp', 'ftps']:
                return self._fetch_via_ftp(source_url, credentials)
            else:
                return False, f"Unsupported protocol: {protocol}", None

        except Exception as e:
            return False, f"Error fetching log: {str(e)}", None

    def _fetch_via_ssh(self, source_url: str, credentials: Optional[Dict[str, str]]) -> Tuple[bool, str, Optional[str]]:
        """
        Fetch a log file via SSH/SCP.

        Args:
            source_url: SSH URL (ssh://user@host:port/path/to/file)
            credentials: Dictionary with 'username', 'password' or 'key_file'

        Returns:
            Tuple containing success flag, local path or error message, and content type
        """
        try:
            # Parse the SSH URL
            parsed_url = urlparse(source_url)
            host = parsed_url.netloc.split('@')[-1].split(':')[0]
            port = int(parsed_url.netloc.split(':')[-1]) if ':' in parsed_url.netloc else 22
            path = parsed_url.path

            # Get username from URL or credentials
            username = parsed_url.netloc.split('@')[0] if '@' in parsed_url.netloc else None
            if not username and credentials and 'username' in credentials:
                username = credentials['username']
            if not username:
                return False, "Username not provided for SSH connection", None

            # Create SSH client
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Connect with password or key file
            if credentials and 'key_file' in credentials:
                key = paramiko.RSAKey.from_private_key_file(credentials['key_file'])
                client.connect(host, port=port, username=username, pkey=key)
            elif credentials and 'password' in credentials:
                client.connect(host, port=port, username=username, password=credentials['password'])
            else:
                return False, "No password or key file provided for SSH connection", None

            # Create a temporary file to store the log
            local_path = os.path.join(self.temp_dir, os.path.basename(path))

            # Use SCP to download the file
            with client.open_sftp() as sftp:
                sftp.get(path, local_path)

            # Close the connection
            client.close()

            return True, local_path, "text/plain"

        except Exception as e:
            return False, f"SSH error: {str(e)}", None

    def _fetch_via_http(self, source_url: str, credentials: Optional[Dict[str, str]]) -> Tuple[bool, str, Optional[str]]:
        """
        Fetch a log file via HTTP/HTTPS.

        Args:
            source_url: HTTP URL (http://host/path/to/file)
            credentials: Dictionary with 'username' and 'password' for basic auth

        Returns:
            Tuple containing success flag, local path or error message, and content type
        """
        try:
            # Prepare authentication if provided
            auth = None
            if credentials and 'username' in credentials and 'password' in credentials:
                auth = (credentials['username'], credentials['password'])

            # Make the HTTP request
            response = requests.get(source_url, auth=auth, stream=True, timeout=30)

            # Check if the request was successful
            if response.status_code != 200:
                return False, f"HTTP error: {response.status_code} - {response.reason}", None

            # Create a temporary file to store the log
            local_path = os.path.join(self.temp_dir, os.path.basename(urlparse(source_url).path) or "http_log.txt")

            # Save the content to the file
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            # Get the content type
            content_type = response.headers.get('Content-Type', 'text/plain')

            return True, local_path, content_type

        except Exception as e:
            return False, f"HTTP error: {str(e)}", None

    def _fetch_via_ftp(self, source_url: str, credentials: Optional[Dict[str, str]]) -> Tuple[bool, str, Optional[str]]:
        """
        Fetch a log file via FTP/SFTP/FTPS.

        Args:
            source_url: FTP URL (ftp://user:pass@host:port/path/to/file)
            credentials: Dictionary with 'username' and 'password'

        Returns:
            Tuple containing success flag, local path or error message, and content type
        """
        try:
            # Parse the FTP URL
            parsed_url = urlparse(source_url)
            protocol = parsed_url.scheme.lower()
            host = parsed_url.netloc.split('@')[-1].split(':')[0]
            port = int(parsed_url.netloc.split(':')[-1]) if ':' in parsed_url.netloc else 21
            path = parsed_url.path

            # Get username and password from URL or credentials
            username = parsed_url.username
            password = parsed_url.password

            if not username and credentials and 'username' in credentials:
                username = credentials['username']
            if not password and credentials and 'password' in credentials:
                password = credentials['password']

            # Default username for anonymous FTP
            if not username:
                username = 'anonymous'
                password = 'anonymous@'

            # Create a temporary file to store the log
            local_path = os.path.join(self.temp_dir, os.path.basename(path) or "ftp_log.txt")

            if protocol == 'sftp':
                # Use paramiko for SFTP
                transport = paramiko.Transport((host, port))
                transport.connect(username=username, password=password)
                sftp = paramiko.SFTPClient.from_transport(transport)
                sftp.get(path, local_path)
                sftp.close()
                transport.close()
            else:
                # Use ftplib for FTP/FTPS
                if protocol == 'ftps':
                    ftp = ftplib.FTP_TLS()
                    ftp.connect(host, port)
                    ftp.login(username, password)
                    ftp.prot_p()  # Set up secure data connection
                else:
                    ftp = ftplib.FTP()
                    ftp.connect(host, port)
                    ftp.login(username, password)

                # Download the file
                with open(local_path, 'wb') as f:
                    ftp.retrbinary(f'RETR {path}', f.write)

                ftp.quit()

            return True, local_path, "text/plain"

        except Exception as e:
            return False, f"FTP error: {str(e)}", None

    def fetch_syslog(self, host: str, port: int = 22, username: str = None,
                    password: str = None, key_file: str = None,
                    log_path: str = "/var/log/syslog") -> Tuple[bool, str, Optional[str]]:
        """
        Fetch syslog from a Linux system.

        Args:
            host: Hostname or IP address
            port: SSH port (default: 22)
            username: SSH username
            password: SSH password (optional if key_file is provided)
            key_file: Path to SSH private key file (optional if password is provided)
            log_path: Path to the syslog file (default: /var/log/syslog)

        Returns:
            Tuple containing success flag, local path or error message, and content type
        """
        # Construct SSH URL
        source_url = f"ssh://{username}@{host}:{port}{log_path}"

        # Prepare credentials
        credentials = {}
        if username:
            credentials['username'] = username
        if password:
            credentials['password'] = password
        if key_file:
            credentials['key_file'] = key_file

        # Use the SSH fetcher
        return self._fetch_via_ssh(source_url, credentials)

    def fetch_windows_event_log(self, host: str, username: str, password: str,
                               log_name: str = "System") -> Tuple[bool, str, Optional[str]]:
        """
        Fetch Windows Event Log via WinRM.

        Args:
            host: Hostname or IP address
            username: Windows username (domain\\username format for domain accounts)
            password: Windows password
            log_name: Name of the event log (System, Application, Security, etc.)

        Returns:
            Tuple containing success flag, local path or error message, and content type
        """
        try:
            # This requires pywinrm which is Windows-specific
            import winrm

            # Create WinRM session
            session = winrm.Session(host, auth=(username, password))

            # PowerShell command to export event log
            ps_command = f"Get-EventLog -LogName {log_name} | ConvertTo-Csv -NoTypeInformation"

            # Execute the command
            result = session.run_ps(ps_command)

            if result.status_code != 0:
                return False, f"WinRM error: {result.std_err.decode('utf-8')}", None

            # Create a temporary file to store the log
            local_path = os.path.join(self.temp_dir, f"{log_name}_event_log.csv")

            # Save the content to the file
            with open(local_path, 'wb') as f:
                f.write(result.std_out)

            return True, local_path, "text/csv"

        except ImportError:
            return False, "WinRM support not available. Install pywinrm package.", None
        except Exception as e:
            return False, f"Windows Event Log error: {str(e)}", None

    def fetch_from_api(self, api_url: str, api_key: Optional[str] = None,
                      headers: Optional[Dict[str, str]] = None) -> Tuple[bool, str, Optional[str]]:
        """
        Fetch logs from a REST API.

        Args:
            api_url: URL of the API endpoint
            api_key: Optional API key for authentication
            headers: Optional additional headers

        Returns:
            Tuple containing success flag, local path or error message, and content type
        """
        try:
            # Prepare headers
            request_headers = headers or {}
            if api_key:
                request_headers['Authorization'] = f"Bearer {api_key}"

            # Make the API request
            response = requests.get(api_url, headers=request_headers, timeout=30)

            # Check if the request was successful
            if response.status_code != 200:
                return False, f"API error: {response.status_code} - {response.reason}", None

            # Create a temporary file to store the log
            local_path = os.path.join(self.temp_dir, "api_log.json")

            # Save the content to the file
            with open(local_path, 'wb') as f:
                f.write(response.content)

            # Get the content type
            content_type = response.headers.get('Content-Type', 'application/json')

            return True, local_path, content_type

        except Exception as e:
            return False, f"API error: {str(e)}", None

def fetch_remote_log(source_type: str, source_params: Dict[str, Any]) -> Tuple[bool, str, Optional[str]]:
    """
    Fetch a log file from a remote source.

    Args:
        source_type: Type of remote source ('ssh', 'http', 'ftp', 'syslog', 'windows_event', 'api')
        source_params: Parameters for the specific source type

    Returns:
        Tuple containing success flag, local path or error message, and content type
    """
    fetcher = RemoteLogFetcher()

    if source_type == 'ssh':
        # Construct SSH URL
        source_url = f"ssh://{source_params.get('username', '')}@{source_params.get('host', '')}:{source_params.get('port', 22)}{source_params.get('path', '')}"

        # Prepare credentials
        credentials = {
            'username': source_params.get('username', ''),
            'password': source_params.get('password', ''),
            'key_file': source_params.get('key_file', '')
        }

        return fetcher._fetch_via_ssh(source_url, credentials)
    elif source_type == 'http':
        return fetcher._fetch_via_http(
            source_params.get('url', ''),
            {'username': source_params.get('username', ''),
             'password': source_params.get('password', '')}
            if source_params.get('username') else None
        )
    elif source_type == 'ftp':
        return fetcher._fetch_via_ftp(
            source_params.get('url', ''),
            {'username': source_params.get('username', ''),
             'password': source_params.get('password', '')}
        )
    elif source_type == 'syslog':
        return fetcher.fetch_syslog(
            source_params.get('host', ''),
            source_params.get('port', 22),
            source_params.get('username', ''),
            source_params.get('password', ''),
            source_params.get('key_file', ''),
            source_params.get('log_path', '/var/log/syslog')
        )
    elif source_type == 'windows_event':
        return fetcher.fetch_windows_event_log(
            source_params.get('host', ''),
            source_params.get('username', ''),
            source_params.get('password', ''),
            source_params.get('log_name', 'System')
        )
    elif source_type == 'api':
        return fetcher.fetch_from_api(
            source_params.get('url', ''),
            source_params.get('api_key', ''),
            source_params.get('headers', {})
        )
    else:
        return False, f"Unsupported source type: {source_type}", None
