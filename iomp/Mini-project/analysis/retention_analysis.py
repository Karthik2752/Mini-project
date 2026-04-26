def calculate_retention(likes, views):
    if not views:
        return 0.0, "Low"

    retention_score = round((likes / views) * 100, 2)
    if retention_score > 20:
        level = "High"
    elif retention_score >= 10:
        level = "Medium"
    else:
        level = "Low"
    return retention_score, level