from enum import Enum
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, SecretStr
from datetime import datetime

class Status(str, Enum):
    OK = "OK"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"

class FailureCategory(str, Enum):
    NONE = "none"
    UNREACHABLE = "unreachable"
    AUTH_FAILED = "auth_failed"
    TIMEOUT = "timeout"
    CHECK_FAILED = "check_failed"

class Rule(BaseModel):
    type: str  # "contains", "not_contains", "regex"
    pattern: str

class CheckDefinition(BaseModel):
    id: str
    name: str
    type: str  # "time", "disk", "custom"
    command: Optional[str] = None
    params: Dict[str, Any] = Field(default_factory=dict)
    rules: List[Rule] = Field(default_factory=list)

class MonitoredSystem(BaseModel):
    id: str
    name: str
    address: str
    username: str
    password: SecretStr
    checks: List[CheckDefinition] = Field(default_factory=list)

class CheckResult(BaseModel):
    check_id: str
    status: Status
    summary: str
    details: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class SystemStatusSummary(BaseModel):
    system_id: str
    overall_status: Status
    last_checked: Optional[datetime] = None
    check_results: List[CheckResult] = Field(default_factory=list)
    failure_category: FailureCategory = FailureCategory.NONE
