import random


def classify_performance(like_rate, comment_rate, engagement_rate, interaction_ratio):
    # Creator-friendly thresholds (all rates are percentages)
    if engagement_rate >= 10 and like_rate >= 6:
        return "Excellent"
    if engagement_rate >= 6 and like_rate >= 3:
        return "Good"
    if engagement_rate >= 3:
        return "Average"
    return "Poor"


def _primary_keyword(keywords):
    words = [w for w, _ in (keywords or []) if isinstance(w, str) and w.strip()]
    return words[0] if words else "this topic"


def _unique_first_n(items, n):
    out = []
    for item in items:
        if item and item not in out:
            out.append(item)
        if len(out) == n:
            break
    return out


def _pick(rng, options):
    options = [o for o in options if o]
    return rng.choice(options) if options else ""


def _reason(like_rate, engagement_rate, interaction_ratio, performance):
    parts = []

    if performance in {"Excellent", "Good"}:
        parts.append(
            f"Strong engagement ({engagement_rate}%) driven by likes ({like_rate}%) shows the reel is resonating and earning reactions."
        )
        if interaction_ratio < 1.0:
            parts.append("Interaction is comparatively low, so it performs more as a quick win than an action-driver.")
        else:
            parts.append("Interaction looks healthy, meaning viewers are taking action beyond passive watching.")
    else:
        parts.append(
            f"Low engagement ({engagement_rate}%) and like rate ({like_rate}%) suggest the hook/value isn’t clear enough early or the pacing is losing viewers."
        )
        if interaction_ratio < 1.0:
            parts.append("Interaction ratio is low, so the CTA/positioning isn’t pulling action.")

    problems = []
    if like_rate < 2.0:
        problems.append("weak hook/value clarity")
    if engagement_rate < 3.0:
        problems.append("low engagement signals (save/share/follow)")
    if interaction_ratio < 1.0:
        problems.append("weak CTA or positioning")
    if problems:
        parts.append("Likely issues: " + ", ".join(problems) + ".")

    return " ".join(parts)


def generate_strategy_report(
    likes,
    views,
    comments,
    like_rate,
    comment_rate,
    engagement_rate,
    interaction_ratio,
    keywords,
    retention_score=None,
    retention_level=None,
):
    performance = classify_performance(like_rate, comment_rate, engagement_rate, interaction_ratio)
    reason = _reason(like_rate, engagement_rate, interaction_ratio, performance)
    kw_hint = _primary_keyword(keywords)

    # Deterministic variety: different reels → different choices (not the same 4 lines)
    seed = int((likes or 0) + (views or 0) + (comments or 0) + int((engagement_rate or 0) * 100))
    rng = random.Random(seed)

    strong = performance in {"Excellent", "Good"}
    low_retention = (retention_level == "Low") or ((retention_score or 0) < 10)

    hook_pool = [
        "Replace the first 2 seconds with a result-first hook (show outcome before explanation).",
        "Open with a pain-point + promise, then deliver the first step immediately.",
        "Start with a bold claim on-screen + quick proof shot, then explain the steps.",
        f"Use a “3 mistakes about {kw_hint}” opener with rapid examples.",
        "Start with a surprising before/after and then reveal the method in 3 steps.",
    ]
    pacing_pool = [
        "Tighten pacing with cuts every 1–2 seconds and bold on-screen text for key points.",
        "Add pattern-interrupts (zoom, b-roll, captions) every 2–3 seconds to prevent swipes.",
        "Use a 3-beat structure: Hook → Proof → Steps, with a visual change at each beat.",
        "Remove filler lines and keep only the 1 strongest example + 1 clear takeaway.",
    ]
    cta_pool = [
        "Add one clear CTA: “Save this” + a reason (template/checklist/steps) to increase saves.",
        "Use an on-screen CTA: “Follow for Part 2” and tease the next outcome in 1 line.",
        "Add a 1-line CTA: “Share this with a friend who needs it” to increase shares.",
        "Pin a follow-up in the caption (“Part 2 here”) to create a binge path.",
    ]
    scale_pool = [
        "Post 2–3 hook variations of the same reel (same body, new first 2 seconds) to scale reach.",
        "Turn this into a 3-part series and pin Part 1 to convert momentum into follows.",
        "Remix into a shorter cut (8–12s) and test as a punchier version.",
        "Repeat the same format on 3 adjacent topics to build bingeable momentum.",
        "Publish a follow-up within 24 hours while the reel is still being pushed.",
    ]
    topic_pool = [
        f"Make a follow-up reel that answers the next step after {kw_hint} and link it via caption/pin.",
        f"Create a “do this, not that” version around {kw_hint} with quick visual examples.",
        f"Turn {kw_hint} into a checklist-style reel with numbered steps on screen.",
        f"Film a common-mistake reel about {kw_hint} and end with the correct fix.",
    ]

    picks = []
    # 1) First suggestion should match performance (scale if good, fix hook if bad)
    picks.append(_pick(rng, scale_pool if strong else hook_pool))
    # 2) Retention/pacing tune
    picks.append(_pick(rng, pacing_pool if low_retention else pacing_pool + hook_pool))
    # 3) Always include a conversion CTA, but vary which one
    picks.append(_pick(rng, cta_pool))
    # 4) Always include a topic/keyword-driven continuation idea
    picks.append(_pick(rng, topic_pool))

    suggestions = _unique_first_n(picks, 4)
    while len(suggestions) < 4:
        suggestions = _unique_first_n(
            suggestions + [_pick(rng, scale_pool + hook_pool + pacing_pool + cta_pool + topic_pool)],
            4,
        )

    return {"performance": performance, "reason": reason, "suggestions": suggestions}