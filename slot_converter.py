"""
Convert between different slot formats
Converts structured extraction format (YYYY-MM-DD, HH:MM AM/PM) to interview format
"""

import re
from typing import Dict, Any, Optional
from datetime import datetime

def convert_slot_to_interview_format(slot_data: Dict[str, Any]) -> Optional[Dict[str, str]]:
    """
    Convert structured slot format to interview format used in candidates.json
    
    Input format (from extraction):
    {
        "date": "2024-12-12",  # YYYY-MM-DD
        "time": "10:00 AM",     # HH:MM AM/PM
        "day_of_week": "Thursday"
    }
    
    Output format (for candidates.json):
    {
        "day": "Thursday",
        "date": "Thursday, the 12th of December",
        "time": "10:00 A.M.",
        "datetime": "Thursday, the 12th of December at 10:00 A.M."
    }
    """
    if not slot_data:
        return None
    
    try:
        date_str = slot_data.get('date', '')
        time_str = slot_data.get('time', '')
        day_of_week = slot_data.get('day_of_week', '')
        
        if not date_str or not time_str:
            return None
        
        # Parse date (YYYY-MM-DD)
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            day_num = date_obj.day
            month_name = date_obj.strftime('%B')  # Full month name
            
            # Format date with ordinal (1st, 2nd, 3rd, etc.)
            def get_ordinal(n):
                if 10 <= n % 100 <= 20:
                    suffix = 'th'
                else:
                    suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
                return f"{n}{suffix}"
            
            ordinal_day = get_ordinal(day_num)
            formatted_date = f"{day_of_week}, the {ordinal_day} of {month_name}"
        except:
            # Fallback if date parsing fails
            formatted_date = f"{day_of_week}, the {day_num}th of {month_name}" if day_of_week else ""
        
        # Convert time format: "10:00 AM" → "10:00 A.M."
        time_formatted = time_str.replace('AM', 'A.M.').replace('PM', 'P.M.')
        
        # Build datetime string
        datetime_str = f"{formatted_date} at {time_formatted}"
        
        return {
            'day': day_of_week or 'Monday',
            'date': formatted_date,
            'time': time_formatted,
            'datetime': datetime_str
        }
    except Exception as e:
        print(f"⚠️  Error converting slot format: {e}")
        return None

def convert_interview_to_slot_format(interview_data: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """
    Convert interview format to structured slot format
    
    Input format (from candidates.json):
    {
        "day": "Thursday",
        "date": "Thursday, the 12th of December",
        "time": "10:00 A.M.",
        "datetime": "Thursday, the 12th of December at 10:00 A.M."
    }
    
    Output format (for extraction):
    {
        "date": "2024-12-12",  # YYYY-MM-DD
        "time": "10:00 AM",     # HH:MM AM/PM
        "day_of_week": "Thursday"
    }
    """
    if not interview_data:
        return None
    
    try:
        date_str = interview_data.get('date', '') or interview_data.get('datetime', '')
        time_str = interview_data.get('time', '')
        day_of_week = interview_data.get('day', '')
        
        # Extract date from string like "Thursday, the 12th of December"
        # Try to parse and convert to YYYY-MM-DD
        date_match = re.search(r'(\d{1,2})(?:st|nd|rd|th)?\s+of\s+(\w+)', date_str, re.IGNORECASE)
        
        if date_match:
            day_num = int(date_match.group(1))
            month_name = date_match.group(2)
            
            # Convert month name to number
            months = {
                'january': 1, 'february': 2, 'march': 3, 'april': 4,
                'may': 5, 'june': 6, 'july': 7, 'august': 8,
                'september': 9, 'october': 10, 'november': 11, 'december': 12
            }
            month_num = months.get(month_name.lower(), 12)
            
            # Use current year (or you can extract from context)
            from datetime import datetime
            current_year = datetime.now().year
            # Try to infer year from context (assuming near future)
            # For now, use current year
            
            date_obj = datetime(current_year, month_num, day_num)
            date_formatted = date_obj.strftime('%Y-%m-%d')
        else:
            # Fallback - can't parse date
            return None
        
        # Convert time: "10:00 A.M." → "10:00 AM"
        time_formatted = time_str.replace('A.M.', 'AM').replace('P.M.', 'PM')
        
        return {
            'date': date_formatted,
            'time': time_formatted,
            'day_of_week': day_of_week
        }
    except Exception as e:
        print(f"⚠️  Error converting interview format: {e}")
        return None

