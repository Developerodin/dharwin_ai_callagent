"""
Structured extraction schema for call outcome data
This schema is used by Bolna AI to extract structured data from call transcripts
"""

EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "call_outcome": {
            "type": "string",
            "enum": ["ACCEPTED", "REJECTED", "RESCHEDULED"],
            "description": "The outcome of the call: ACCEPTED (confirmed original slot), REJECTED (declined interview), or RESCHEDULED (changed to new slot)"
        },
        "original_slot": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                    "description": "Date in YYYY-MM-DD format"
                },
                "time": {
                    "type": "string",
                    "pattern": "^\\d{1,2}:\\d{2}\\s(AM|PM)$",
                    "description": "Time in 12-hour format with AM/PM (e.g., '10:00 AM', '02:00 PM')"
                },
                "day_of_week": {
                    "type": "string",
                    "enum": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                    "description": "Day of the week"
                }
            },
            "required": ["date", "time", "day_of_week"],
            "description": "The originally scheduled interview slot"
        },
        "final_slot": {
            "type": ["object", "null"],
            "properties": {
                "date": {
                    "type": "string",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                    "description": "Date in YYYY-MM-DD format"
                },
                "time": {
                    "type": "string",
                    "pattern": "^\\d{1,2}:\\d{2}\\s(AM|PM)$",
                    "description": "Time in 12-hour format with AM/PM (e.g., '10:00 AM', '02:00 PM')"
                },
                "day_of_week": {
                    "type": "string",
                    "enum": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                    "description": "Day of the week"
                }
            },
            "required": ["date", "time", "day_of_week"],
            "description": "Final confirmed slot. If ACCEPTED: same as original_slot. If REJECTED: null. If RESCHEDULED: different from original_slot"
        },
        "notes": {
            "type": "string",
            "description": "Any additional relevant information about the call outcome"
        }
    },
    "required": ["call_outcome", "original_slot", "final_slot", "notes"]
}

EXTRACTION_EXAMPLES = {
    "ACCEPTED": {
        "call_outcome": "ACCEPTED",
        "original_slot": {
            "date": "2024-12-12",
            "time": "10:00 AM",
            "day_of_week": "Thursday"
        },
        "final_slot": {
            "date": "2024-12-12",
            "time": "10:00 AM",
            "day_of_week": "Thursday"
        },
        "notes": "Candidate confirmed without hesitation"
    },
    "REJECTED": {
        "call_outcome": "REJECTED",
        "original_slot": {
            "date": "2024-12-12",
            "time": "10:00 AM",
            "day_of_week": "Thursday"
        },
        "final_slot": None,
        "notes": "Candidate no longer interested in the position"
    },
    "RESCHEDULED": {
        "call_outcome": "RESCHEDULED",
        "original_slot": {
            "date": "2024-12-12",
            "time": "10:00 AM",
            "day_of_week": "Thursday"
        },
        "final_slot": {
            "date": "2024-12-15",
            "time": "02:00 PM",
            "day_of_week": "Sunday"
        },
        "notes": "Candidate had a conflict, selected alternative slot"
    }
}

