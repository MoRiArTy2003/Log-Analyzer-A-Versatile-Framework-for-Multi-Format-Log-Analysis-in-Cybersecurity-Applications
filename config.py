"""
Configuration settings for the Log Analyzer application.
"""
import os

# Application settings
APP_NAME = "Log Analyzer"
APP_VERSION = "1.0.0"
DEBUG = True

# File paths
DEFAULT_LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "misc")
EXAMPLE_LOG_FILE = os.path.join(DEFAULT_LOG_DIR, "browsinglogs_20240924.txt")

# Log types and their column definitions
LOG_TYPES = {
    "browsing": {
        "columns": [
            "timestamp", "ip_address", "username", "url",
            "bandwidth", "status_code", "content_type",
            "category", "device_info"
        ],
        "datetime_format": "%Y%m%d%H%M%S",  # If timestamp needs parsing
        "separator": " ",
        "description": "Web browsing logs with URLs and HTTP status codes"
    },
    "virus": {
        "columns": [
            "timestamp", "ip_address", "username", "virus_name",
            "file_path", "action_taken", "scan_engine", "severity"
        ],
        "datetime_format": "%Y%m%d%H%M%S",
        "separator": " ",
        "description": "Antivirus detection logs with virus information"
    },
    "mail": {
        "columns": [
            "timestamp", "sender", "recipient", "subject",
            "size", "status", "attachment_count", "spam_score"
        ],
        "datetime_format": "%Y%m%d%H%M%S",
        "separator": " ",
        "description": "Email server logs with message details"
    },
    "firewall": {
        "columns": [
            "timestamp", "action", "protocol", "src_ip",
            "src_port", "dst_ip", "dst_port", "interface",
            "rule_id", "description"
        ],
        "datetime_format": "%Y%m%d%H%M%S",
        "separator": " ",
        "description": "Firewall logs with connection information"
    },
    "auth": {
        "columns": [
            "timestamp", "username", "source_ip", "service",
            "status", "auth_method", "details"
        ],
        "datetime_format": "%Y%m%d%H%M%S",
        "separator": " ",
        "description": "Authentication logs with login attempts"
    },
    "system": {
        "columns": [
            "timestamp", "hostname", "service", "pid",
            "level", "message"
        ],
        "datetime_format": "%Y%m%d%H%M%S",
        "separator": " ",
        "description": "System logs with service information"
    },
    "application": {
        "columns": [
            "timestamp", "app_name", "level", "component",
            "thread_id", "request_id", "message"
        ],
        "datetime_format": "%Y%m%d%H%M%S",
        "separator": " ",
        "description": "Application logs with debug information"
    },
    "ids": {
        "columns": [
            "timestamp", "alert_id", "severity", "category",
            "src_ip", "dst_ip", "protocol", "signature",
            "description"
        ],
        "datetime_format": "%Y%m%d%H%M%S",
        "separator": " ",
        "description": "Intrusion detection system logs"
    },
    "vpn": {
        "columns": [
            "timestamp", "username", "client_ip", "session_id",
            "event_type", "duration", "bytes_in", "bytes_out"
        ],
        "datetime_format": "%Y%m%d%H%M%S",
        "separator": " ",
        "description": "VPN connection logs with session details"
    },
    "syslog": {
        "columns": [
            "timestamp", "hostname", "process", "pid", "message"
        ],
        "datetime_format": "%b %d %H:%M:%S",
        "separator": " ",
        "description": "Standard syslog format logs"
    },
    "clf": {
        "columns": [
            "host", "ident", "authuser", "timestamp", "method",
            "path", "protocol", "status", "bytes_sent", "url"
        ],
        "datetime_format": "%d/%b/%Y:%H:%M:%S %z",
        "separator": " ",
        "description": "Common Log Format (CLF) web server logs"
    },
    "elf": {
        "columns": [],  # Columns are determined from the #Fields directive
        "datetime_format": "%Y-%m-%d %H:%M:%S",
        "separator": " ",
        "description": "Extended Log Format (ELF) web server logs"
    },
    "json": {
        "columns": [],  # Columns are determined from the JSON structure
        "datetime_format": "%Y-%m-%d %H:%M:%S",
        "separator": "",
        "description": "JSON structured logs"
    },
    "xml": {
        "columns": [],  # Columns are determined from the XML structure
        "datetime_format": "%Y-%m-%d %H:%M:%S",
        "separator": "",
        "description": "XML structured logs"
    },
    "csv": {
        "columns": [],  # Columns are determined from the CSV header
        "datetime_format": "%Y-%m-%d %H:%M:%S",
        "separator": ",",
        "description": "CSV structured logs"
    }
}

# Chart settings
CHART_WIDTH = 700
CHART_HEIGHT = 400
COLOR_SCHEME = "category10"  # Altair color scheme

# Authentication settings
AUTH_TIMEOUT = 3600  # Session timeout in seconds (1 hour)
MIN_PASSWORD_LENGTH = 8

# UI settings
THEME_COLORS = {
    "light": {
        "background": "#ffffff",
        "text": "#333333",
        "primary": "#007acc",
        "secondary": "#6c757d",
        "success": "#28a745",
        "danger": "#dc3545",
        "warning": "#ffc107",
        "info": "#17a2b8"
    },
    "dark": {
        "background": "#2c2c2c",
        "text": "#ffffff",
        "primary": "#007acc",
        "secondary": "#6c757d",
        "success": "#28a745",
        "danger": "#dc3545",
        "warning": "#ffc107",
        "info": "#17a2b8"
    }
}

# Default settings
DEFAULT_THEME = "dark"
DEFAULT_CHART_TYPE = "bar"
DEFAULT_LOG_TYPE = "browsing"

# Cache settings
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cache")
CACHE_EXPIRATION = 3600  # Cache expiration time in seconds (1 hour)
MAX_CACHE_SIZE = 100 * 1024 * 1024  # Maximum cache size in bytes (100 MB)
