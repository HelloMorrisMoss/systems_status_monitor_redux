from typing import Dict

# Command presets for Windows/legacy hosts
COMMAND_PRESETS: Dict[str, str] = {
    "time": "time /T",
    "time_fallback": "echo %DATE% %TIME%",
    "disk": "wmic logicaldisk get caption,freespace,size",
}

def get_check_command(check_type: str, custom_command: str = None) -> str:
    """
    Returns the command string for a given check type.
    """
    if check_type == "custom":
        return custom_command or ""
    return COMMAND_PRESETS.get(check_type, "")
