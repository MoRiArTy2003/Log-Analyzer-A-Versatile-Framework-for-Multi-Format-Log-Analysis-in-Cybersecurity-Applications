"""
Data models for the Log Analyzer application.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

@dataclass
class User:
    """User model for authentication and authorization."""
    email: str
    username: str
    role: str = "analyst"  # Default role
    last_login: Optional[datetime] = None
    preferences: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the user to a dictionary."""
        return {
            "email": self.email,
            "username": self.username,
            "role": self.role,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "preferences": self.preferences
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create a user from a dictionary."""
        last_login = None
        if data.get("last_login"):
            try:
                last_login = datetime.fromisoformat(data["last_login"])
            except (ValueError, TypeError):
                pass

        return cls(
            email=data.get("email", ""),
            username=data.get("username", ""),
            role=data.get("role", "analyst"),
            last_login=last_login,
            preferences=data.get("preferences", {})
        )

@dataclass
class LogEntry:
    """Base class for log entries."""
    timestamp: Union[int, str]
    formatted_timestamp: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert the log entry to a dictionary."""
        return {
            "timestamp": self.timestamp,
            "formatted_timestamp": self.formatted_timestamp
        }

@dataclass
class BrowsingLogEntry(LogEntry):
    """Model for browsing log entries."""
    ip_address: str = ""
    username: str = ""
    url: str = ""
    bandwidth: int = 0
    status_code: int = 0
    content_type: str = ""
    category: str = ""
    device_info: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert the browsing log entry to a dictionary."""
        return {
            **super().to_dict(),
            "ip_address": self.ip_address,
            "username": self.username,
            "url": self.url,
            "bandwidth": self.bandwidth,
            "status_code": self.status_code,
            "content_type": self.content_type,
            "category": self.category,
            "device_info": self.device_info
        }

@dataclass
class VirusLogEntry(LogEntry):
    """Model for virus log entries."""
    ip_address: str = ""
    username: str = ""
    virus_name: str = ""
    file_path: str = ""
    action_taken: str = ""
    scan_engine: str = ""
    severity: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert the virus log entry to a dictionary."""
        return {
            **super().to_dict(),
            "ip_address": self.ip_address,
            "username": self.username,
            "virus_name": self.virus_name,
            "file_path": self.file_path,
            "action_taken": self.action_taken,
            "scan_engine": self.scan_engine,
            "severity": self.severity
        }

@dataclass
class MailLogEntry(LogEntry):
    """Model for mail log entries."""
    sender: str = ""
    recipient: str = ""
    subject: str = ""
    size: int = 0
    status: str = ""
    attachment_count: int = 0
    spam_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert the mail log entry to a dictionary."""
        return {
            **super().to_dict(),
            "sender": self.sender,
            "recipient": self.recipient,
            "subject": self.subject,
            "size": self.size,
            "status": self.status,
            "attachment_count": self.attachment_count,
            "spam_score": self.spam_score
        }

@dataclass
class Report:
    """Model for generated reports."""
    title: str
    description: str
    created_at: datetime = field(default_factory=datetime.now)
    created_by: Optional[str] = None
    log_type: str = "browsing"
    filters: Dict[str, Any] = field(default_factory=dict)
    charts: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the report to a dictionary."""
        return {
            "title": self.title,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
            "log_type": self.log_type,
            "filters": self.filters,
            "charts": self.charts
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Report':
        """Create a report from a dictionary."""
        created_at = datetime.now()
        if data.get("created_at"):
            try:
                created_at = datetime.fromisoformat(data["created_at"])
            except (ValueError, TypeError):
                pass

        return cls(
            title=data.get("title", ""),
            description=data.get("description", ""),
            created_at=created_at,
            created_by=data.get("created_by"),
            log_type=data.get("log_type", "browsing"),
            filters=data.get("filters", {}),
            charts=data.get("charts", [])
        )
