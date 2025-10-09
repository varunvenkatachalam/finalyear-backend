import re
from datetime import datetime
from typing import Dict, Any

def validate_email(email: str) -> bool:
    """Basic email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def format_timestamp(timestamp: datetime) -> str:
    """Format timestamp for display"""
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")

def sanitize_input(text: str) -> str:
    """Basic input sanitization"""
    return text.strip()

def calculate_usage_stats(generations: list) -> Dict[str, Any]:
    """Calculate basic usage statistics"""
    total = len(generations)
    by_type = {}
    
    for gen in generations:
        gen_type = gen.get('type', 'unknown')
        by_type[gen_type] = by_type.get(gen_type, 0) + 1
    
    return {
        "total_generations": total,
        "by_type": by_type,
        "last_activity": format_timestamp(datetime.utcnow()) if total > 0 else "No activity"
    }