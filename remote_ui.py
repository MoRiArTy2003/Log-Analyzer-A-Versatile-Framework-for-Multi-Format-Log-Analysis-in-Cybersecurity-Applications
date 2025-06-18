"""
UI components for remote log fetching.
"""
import streamlit as st
import os
from typing import Optional, Dict, Any, Tuple

from remote_fetcher import RemoteLogFetcher

def show_remote_fetch_ui() -> Optional[str]:
    """
    Display UI for fetching logs from remote sources.

    Returns:
        Optional[str]: Path to the fetched log file if successful, None otherwise
    """
    st.subheader("Fetch Remote Logs")

    # Source type selection
    source_type = st.selectbox(
        "Source Type",
        options=[
            "Linux Syslog (SSH)",
            "Windows Event Log",
            "HTTP/HTTPS URL",
            "FTP/SFTP Server",
            "REST API",
            "Custom SSH Command"
        ],
        index=0
    )

    # Parameters based on source type
    params = {}

    if source_type == "Linux Syslog (SSH)":
        col1, col2 = st.columns(2)
        with col1:
            params['host'] = st.text_input("Hostname/IP", placeholder="e.g., 192.168.1.100")
            params['username'] = st.text_input("Username", placeholder="e.g., admin")
            params['auth_method'] = st.radio("Authentication Method", ["Password", "SSH Key"])

        with col2:
            params['port'] = st.number_input("SSH Port", value=22, min_value=1, max_value=65535)
            if params['auth_method'] == "Password":
                params['password'] = st.text_input("Password", type="password")
            else:
                params['key_file'] = st.text_input("SSH Key File Path", placeholder="e.g., ~/.ssh/id_rsa")

        params['log_path'] = st.text_input("Log File Path", value="/var/log/syslog")

    elif source_type == "Windows Event Log":
        col1, col2 = st.columns(2)
        with col1:
            params['host'] = st.text_input("Hostname/IP", placeholder="e.g., 192.168.1.100")
            params['username'] = st.text_input("Username", placeholder="e.g., Administrator")

        with col2:
            params['password'] = st.text_input("Password", type="password")
            params['log_name'] = st.selectbox(
                "Event Log",
                options=["System", "Application", "Security", "Setup", "ForwardedEvents"],
                index=0
            )

    elif source_type == "HTTP/HTTPS URL":
        params['url'] = st.text_input("URL", placeholder="e.g., https://example.com/logs/access.log")

        auth_required = st.checkbox("Authentication Required")
        if auth_required:
            col1, col2 = st.columns(2)
            with col1:
                params['username'] = st.text_input("Username")
            with col2:
                params['password'] = st.text_input("Password", type="password")

    elif source_type == "FTP/SFTP Server":
        col1, col2 = st.columns(2)
        with col1:
            params['protocol'] = st.selectbox("Protocol", options=["FTP", "SFTP", "FTPS"], index=1)
            params['host'] = st.text_input("Hostname/IP", placeholder="e.g., ftp.example.com")
            params['username'] = st.text_input("Username", placeholder="e.g., anonymous")

        with col2:
            params['port'] = st.number_input(
                "Port",
                value=22 if params.get('protocol') == "SFTP" else 21,
                min_value=1,
                max_value=65535
            )
            params['password'] = st.text_input("Password", type="password")
            params['path'] = st.text_input("File Path", placeholder="e.g., /logs/access.log")

    elif source_type == "REST API":
        params['url'] = st.text_input("API URL", placeholder="e.g., https://api.example.com/logs")

        auth_type = st.selectbox("Authentication Type", options=["None", "API Key", "Bearer Token", "Basic Auth"])

        if auth_type == "API Key":
            col1, col2 = st.columns(2)
            with col1:
                params['api_key_name'] = st.text_input("API Key Name", placeholder="e.g., X-API-Key")
            with col2:
                params['api_key'] = st.text_input("API Key", type="password")

        elif auth_type == "Bearer Token":
            params['token'] = st.text_input("Bearer Token", type="password")

        elif auth_type == "Basic Auth":
            col1, col2 = st.columns(2)
            with col1:
                params['username'] = st.text_input("Username")
            with col2:
                params['password'] = st.text_input("Password", type="password")

        params['headers'] = st.text_area("Additional Headers (JSON)", placeholder='{"Content-Type": "application/json"}')

    elif source_type == "Custom SSH Command":
        col1, col2 = st.columns(2)
        with col1:
            params['host'] = st.text_input("Hostname/IP", placeholder="e.g., 192.168.1.100")
            params['username'] = st.text_input("Username", placeholder="e.g., admin")
            params['auth_method'] = st.radio("Authentication Method", ["Password", "SSH Key"])

        with col2:
            params['port'] = st.number_input("SSH Port", value=22, min_value=1, max_value=65535)
            if params['auth_method'] == "Password":
                params['password'] = st.text_input("Password", type="password")
            else:
                params['key_file'] = st.text_input("SSH Key File Path", placeholder="e.g., ~/.ssh/id_rsa")

        params['command'] = st.text_area("SSH Command", placeholder="e.g., cat /var/log/syslog | grep ERROR")

    # Fetch button
    if st.button("Fetch Log"):
        if not _validate_params(source_type, params):
            st.error("Please fill in all required fields.")
            return None

        # Create a progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Show initial status
        status_text.text("Initializing connection...")
        progress_bar.progress(10)

        # Fetch the log with progress updates
        try:
            # Update progress
            status_text.text("Establishing connection...")
            progress_bar.progress(30)

            # Fetch the log
            success, result, content_type = _fetch_log(source_type, params)

            # Update progress
            status_text.text("Processing data...")
            progress_bar.progress(80)

            # Small delay for visual feedback
            import time
            time.sleep(0.5)

            # Complete the progress
            progress_bar.progress(100)
            status_text.text("Completed!" if success else "Failed!")

        except Exception as e:
            # Show error in progress
            progress_bar.progress(100)
            status_text.text(f"Error: {str(e)}")
            success = False
            result = str(e)
            content_type = None

        if success:
            st.success(f"Log file fetched successfully: {os.path.basename(result)}")
            return result
        else:
            st.error(f"Failed to fetch log file: {result}")
            return None

    return None

def _validate_params(source_type: str, params: Dict[str, Any]) -> bool:
    """
    Validate parameters for the selected source type.

    Args:
        source_type: Type of remote source
        params: Parameters for the source

    Returns:
        bool: True if parameters are valid, False otherwise
    """
    if source_type == "Linux Syslog (SSH)":
        if not params.get('host') or not params.get('username') or not params.get('log_path'):
            return False
        if params.get('auth_method') == "Password" and not params.get('password'):
            return False
        if params.get('auth_method') == "SSH Key" and not params.get('key_file'):
            return False

    elif source_type == "Windows Event Log":
        if not params.get('host') or not params.get('username') or not params.get('password'):
            return False

    elif source_type == "HTTP/HTTPS URL":
        if not params.get('url'):
            return False

    elif source_type == "FTP/SFTP Server":
        if not params.get('host') or not params.get('path'):
            return False

    elif source_type == "REST API":
        if not params.get('url'):
            return False

    elif source_type == "Custom SSH Command":
        if not params.get('host') or not params.get('username') or not params.get('command'):
            return False
        if params.get('auth_method') == "Password" and not params.get('password'):
            return False
        if params.get('auth_method') == "SSH Key" and not params.get('key_file'):
            return False

    return True

def _fetch_log(source_type: str, params: Dict[str, Any]) -> Tuple[bool, str, Optional[str]]:
    """
    Fetch log file from the remote source.

    Args:
        source_type: Type of remote source
        params: Parameters for the source

    Returns:
        Tuple containing success flag, result (path or error message), and content type
    """
    fetcher = RemoteLogFetcher()

    try:
        if source_type == "Linux Syslog (SSH)":
            return fetcher.fetch_syslog(
                host=params['host'],
                port=params.get('port', 22),
                username=params['username'],
                password=params.get('password'),
                key_file=params.get('key_file'),
                log_path=params['log_path']
            )

        elif source_type == "Windows Event Log":
            return fetcher.fetch_windows_event_log(
                host=params['host'],
                username=params['username'],
                password=params['password'],
                log_name=params['log_name']
            )

        elif source_type == "HTTP/HTTPS URL":
            credentials = None
            if params.get('username') and params.get('password'):
                credentials = {
                    'username': params['username'],
                    'password': params['password']
                }
            return fetcher._fetch_via_http(params['url'], credentials)

        elif source_type == "FTP/SFTP Server":
            protocol = params.get('protocol', 'SFTP').lower()
            url = f"{protocol}://{params.get('username', 'anonymous')}:{params.get('password', '')}@{params['host']}:{params.get('port', 21 if protocol != 'sftp' else 22)}{params['path']}"
            return fetcher._fetch_via_ftp(url, {
                'username': params.get('username', 'anonymous'),
                'password': params.get('password', '')
            })

        elif source_type == "REST API":
            headers = {}

            # Parse additional headers if provided
            if params.get('headers'):
                import json
                try:
                    headers = json.loads(params['headers'])
                except:
                    pass

            # Add authentication headers
            auth_type = params.get('auth_type', 'None')
            if auth_type == "API Key" and params.get('api_key'):
                headers[params.get('api_key_name', 'X-API-Key')] = params['api_key']
            elif auth_type == "Bearer Token" and params.get('token'):
                headers['Authorization'] = f"Bearer {params['token']}"

            # For Basic Auth, we pass credentials separately
            credentials = None
            if auth_type == "Basic Auth" and params.get('username') and params.get('password'):
                credentials = {
                    'username': params['username'],
                    'password': params['password']
                }

            return fetcher._fetch_via_http(params['url'], credentials, headers)

        elif source_type == "Custom SSH Command":
            # Create a temporary script to execute the command and capture output
            import tempfile

            script_content = f"#!/bin/bash\n{params['command']}"
            script_file = tempfile.NamedTemporaryFile(delete=False, suffix='.sh')
            script_file.write(script_content.encode('utf-8'))
            script_file.close()

            # Make the script executable
            os.chmod(script_file.name, 0o755)

            # Upload and execute the script via SSH
            credentials = {}
            if params.get('auth_method') == "Password":
                credentials['password'] = params['password']
            else:
                credentials['key_file'] = params['key_file']

            # Construct SSH URL for the script
            remote_script_path = f"/tmp/log_analyzer_script_{os.path.basename(script_file.name)}"
            source_url = f"ssh://{params['username']}@{params['host']}:{params.get('port', 22)}{remote_script_path}"

            # Use paramiko to upload and execute the script
            import paramiko

            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Connect with password or key file
            if params.get('auth_method') == "Password":
                client.connect(
                    params['host'],
                    port=params.get('port', 22),
                    username=params['username'],
                    password=params['password']
                )
            else:
                key = paramiko.RSAKey.from_private_key_file(params['key_file'])
                client.connect(
                    params['host'],
                    port=params.get('port', 22),
                    username=params['username'],
                    pkey=key
                )

            # Upload the script
            with client.open_sftp() as sftp:
                sftp.put(script_file.name, remote_script_path)

            # Execute the script
            stdin, stdout, stderr = client.exec_command(f"chmod +x {remote_script_path} && {remote_script_path}")

            # Read the output
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')

            # Clean up
            client.exec_command(f"rm {remote_script_path}")
            client.close()
            os.unlink(script_file.name)

            if error:
                return False, f"SSH command error: {error}", None

            # Save the output to a file
            output_file = os.path.join(fetcher.temp_dir, "ssh_command_output.log")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output)

            return True, output_file, "text/plain"

        else:
            return False, f"Unsupported source type: {source_type}", None

    except Exception as e:
        import traceback
        return False, f"Error fetching log: {str(e)}\n{traceback.format_exc()}", None
