def calculate_retention(likes, comments_count, views):
    if views == 0:
        return 0, "Low"

    retention_score = (likes + comments_count) / views

    if retention_score < 0.02:
        level = "Low"
    elif retention_score < 0.05:
        level = "Medium"
    else:
        level = "High"

    return round(retention_score, 4), level