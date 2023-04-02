from datetime import datetime, date


def get_date_from_str(value: str) -> date:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except ValueError:
        pass
    try:
        return datetime.strptime(value, '%a, %d %b %Y %H:%M:%S %z').date()
    except ValueError:
        pass
