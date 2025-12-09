"""
Time formatter for natural speech output
Converts times like "2:00 P.M." to "2 o'clock in the afternoon"
"""

import re
from typing import Optional

def format_time_for_speech(time_str: str) -> str:
    """
    Convert time format to natural speech format for TTS
    
    Examples:
        "10:00 A.M." → "10 o'clock in the morning"
        "2:00 P.M." → "2 o'clock in the afternoon"
        "11:00 P.M." → "11 o'clock at night"
        "12:00 A.M." → "12 o'clock at night" (midnight)
        "12:00 P.M." → "12 o'clock in the afternoon" (noon)
    
    Args:
        time_str: Time string in format like "10:00 A.M." or "2:00 P.M."
    
    Returns:
        Natural speech format string
    """
    if not time_str:
        return time_str
    
    # Remove extra spaces and normalize
    time_str = time_str.strip()
    
    # Pattern to match time formats: "10:00 A.M.", "2:00 PM", etc.
    time_pattern = r'(\d{1,2}):(\d{2})\s*(A\.M\.|P\.M\.|AM|PM|am|pm)'
    match = re.search(time_pattern, time_str, re.IGNORECASE)
    
    if not match:
        # If no match, try to return as-is or extract hour
        return time_str
    
    hour = int(match.group(1))
    minute = int(match.group(2))
    period = match.group(3).upper()
    
    # Handle 12-hour format edge cases
    is_am = 'A.M.' in period or 'AM' in period
    is_pm = 'P.M.' in period or 'PM' in period
    
    # Determine time of day description
    if is_am:
        if hour == 12:  # Midnight (12:00 AM)
            time_of_day = "at night"
        elif hour < 6:  # Early morning (1-5 AM)
            time_of_day = "in the early morning"
        else:  # Morning (6-11 AM)
            time_of_day = "in the morning"
    else:  # PM
        if hour == 12:  # Noon (12:00 PM)
            time_of_day = "in the afternoon"
        elif hour < 6:  # Afternoon (1-5 PM)
            time_of_day = "in the afternoon"
        elif hour < 9:  # Evening (6-8 PM)
            time_of_day = "in the evening"
        else:  # Night (9-11 PM)
            time_of_day = "at night"
    
    # Format the hour (remove leading zero, handle 12-hour format)
    display_hour = hour if hour <= 12 else hour - 12
    
    # Handle minutes
    if minute == 0:
        time_str_formatted = f"{display_hour} o'clock {time_of_day}"
    elif minute < 10:
        time_str_formatted = f"{display_hour} oh {minute} {time_of_day}"
    else:
        time_str_formatted = f"{display_hour} {minute} {time_of_day}"
    
    return time_str_formatted


def format_datetime_for_speech(datetime_str: str) -> str:
    """
    Format a full datetime string for natural speech
    
    Example:
        "Friday, the 12th of December at 2:00 P.M." 
        → "Friday, the 12th of December at 2 o'clock in the afternoon"
    
    Args:
        datetime_str: Full datetime string
    
    Returns:
        Formatted datetime string with natural time
    """
    if not datetime_str:
        return datetime_str
    
    # Pattern to find time in datetime string
    time_pattern = r'(\d{1,2}):(\d{2})\s*(A\.M\.|P\.M\.|AM|PM|am|pm)'
    match = re.search(time_pattern, datetime_str, re.IGNORECASE)
    
    if match:
        # Extract the time part
        time_part = match.group(0)
        # Format it
        formatted_time = format_time_for_speech(time_part)
        # Replace in original string
        return datetime_str.replace(time_part, formatted_time)
    
    return datetime_str


def format_slots_for_speech(slots: list) -> list:
    """
    Format a list of datetime slot strings for natural speech
    
    Args:
        slots: List of datetime strings like ["Monday, the 15th at 2:00 P.M."]
    
    Returns:
        List of formatted datetime strings
    """
    if not slots:
        return slots
    
    return [format_datetime_for_speech(slot) for slot in slots]


# Test function
if __name__ == "__main__":
    test_times = [
        "10:00 A.M.",
        "2:00 P.M.",
        "11:00 P.M.",
        "12:00 A.M.",
        "12:00 P.M.",
        "6:30 A.M.",
        "9:15 P.M.",
        "1:00 P.M.",
        "11:30 A.M."
    ]
    
    print("Time Formatting Tests:")
    print("=" * 60)
    for time_str in test_times:
        formatted = format_time_for_speech(time_str)
        print(f"{time_str:15} → {formatted}")
    
    print("\n" + "=" * 60)
    print("\nDatetime Formatting Tests:")
    print("=" * 60)
    
    test_datetimes = [
        "Friday, the 12th of December at 10:00 A.M.",
        "Monday, the 15th of December at 2:00 P.M.",
        "Tuesday, the 16th of December at 11:00 P.M.",
        "Wednesday, the 17th of December at 12:00 P.M."
    ]
    
    for dt_str in test_datetimes:
        formatted = format_datetime_for_speech(dt_str)
        print(f"Original: {dt_str}")
        print(f"Formatted: {formatted}\n")

