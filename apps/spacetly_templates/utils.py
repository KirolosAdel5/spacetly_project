from datetime import datetime, timezone


def time_since(dt):
    """
    Returns string representing "time since" e.g.
    """
    now = datetime.now(timezone.utc)
    diff = now - dt

    seconds = diff.total_seconds()
    minutes = int(seconds // 60)
    hours = int(minutes // 60)
    days = int(hours // 24)
    months = int(days // 30)
    years = int(days // 365)

    if years > 0:
        return f"منذ {years} {'سنوات' if years > 1 else 'سنة'} "
    elif months > 0:
        return f"منذ{months} {'اشهر' if months > 1 else 'شهر'} "
    elif days > 0:
        return f"منذ {days} {'ايام' if days > 1 else 'يوم'} "
    elif hours > 0:
        return f"منذ {hours} {'ساعات' if hours > 1 else 'ساعة'} "
    elif minutes > 0:
        return f"منذ {minutes} {'دقائق' if minutes > 1 else 'دقيقة'} "
    else:
        return f"منذ {int(seconds)} {'ثواني' if seconds > 1 else 'ثانية'} "
