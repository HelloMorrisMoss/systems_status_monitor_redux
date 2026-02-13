import re
import logging
from systems_status_monitor_redux.models.entities import CheckResult, Status, CheckDefinition

logger = logging.getLogger(__name__)

def evaluate_time(check_def: CheckDefinition, stdout: str, stderr: str, exit_status: int) -> CheckResult:
    """
    Evaluates the output of 'time /T' or '%DATE% %TIME%'.
    """
    if exit_status != 0:
        return CheckResult(
            check_id=check_def.id,
            status=Status.CRITICAL,
            summary="Command failed",
            details=stderr
        )
    
    output = stdout.strip()
    if not output:
        return CheckResult(
            check_id=check_def.id,
            status=Status.UNKNOWN,
            summary="No output from time command"
        )

    # Typical 'time /T' output: 02:45 PM
    # Typical '%DATE% %TIME%' output: Wed 02/11/2026 14:45:01.23
    return CheckResult(
        check_id=check_def.id,
        status=Status.OK,
        summary=f"System time: {output}"
    )

def evaluate_disk(check_def: CheckDefinition, stdout: str, stderr: str, exit_status: int) -> CheckResult:
    """
    Evaluates WMIC disk output.
    Expected format:
    Caption  FreeSpace     Size
    C:       1234567890    2345678901
    """
    if exit_status != 0:
        return CheckResult(
            check_id=check_def.id,
            status=Status.CRITICAL,
            summary="WMIC command failed",
            details=stderr
        )

    lines = [line.strip() for line in stdout.splitlines() if line.strip()]
    if len(lines) < 2:
        return CheckResult(
            check_id=check_def.id,
            status=Status.UNKNOWN,
            summary="Unexpected WMIC output format"
        )

    # Parse headers and find columns
    header = lines[0]
    data_lines = lines[1:]
    
    target_drive = check_def.params.get("drive", "C:").upper()
    if ":" not in target_drive:
        target_drive += ":"

    warning_threshold_gb = check_def.params.get("warning_gb", 10)
    critical_threshold_gb = check_def.params.get("critical_gb", 5)

    for line in data_lines:
        parts = line.split()
        if len(parts) >= 3:
            caption = parts[0].upper()
            if caption == target_drive:
                try:
                    free_bytes = int(parts[1])
                    total_bytes = int(parts[2])
                    
                    free_gb = free_bytes / (1024**3)
                    total_gb = total_bytes / (1024**3)
                    
                    status = Status.OK
                    if free_gb <= critical_threshold_gb:
                        status = Status.CRITICAL
                    elif free_gb <= warning_threshold_gb:
                        status = Status.WARNING
                    
                    return CheckResult(
                        check_id=check_def.id,
                        status=status,
                        summary=f"Drive {caption}: {free_gb:.1f}GB free of {total_gb:.1f}GB"
                    )
                except (ValueError, IndexError):
                    continue

    return CheckResult(
        check_id=check_def.id,
        status=Status.UNKNOWN,
        summary=f"Drive {target_drive} not found"
    )

def evaluate_custom(check_def: CheckDefinition, stdout: str, stderr: str, exit_status: int) -> CheckResult:
    """
    Evaluates custom command based on exit status and rules.
    """
    # 1. Check exit status
    if exit_status != 0:
        return CheckResult(
            check_id=check_def.id,
            status=Status.CRITICAL,
            summary=f"Command failed with exit status {exit_status}",
            details=stderr or stdout
        )

    # 2. Evaluate rules
    for rule in check_def.rules:
        match = False
        if rule.type == "contains":
            match = rule.pattern in stdout
        elif rule.type == "not_contains":
            match = rule.pattern not in stdout
        elif rule.type == "regex":
            try:
                match = bool(re.search(rule.pattern, stdout))
            except Exception as e:
                logger.error(f"Invalid regex '{rule.pattern}': {e}")
                continue
        
        if not match:
            # Redact/Truncate large output to avoid dashboard issues
            details = stdout[:1000]
            return CheckResult(
                check_id=check_def.id,
                status=Status.CRITICAL,
                summary=f"Rule failed: {rule.type} '{rule.pattern}'",
                details=details
            )

    return CheckResult(
        check_id=check_def.id,
        status=Status.OK,
        summary="Command check passed",
        details=stdout[:1000]
    )

def get_evaluator(check_type: str):
    evaluators = {
        "time": evaluate_time,
        "disk": evaluate_disk,
        "custom": evaluate_custom
    }
    return evaluators.get(check_type)
