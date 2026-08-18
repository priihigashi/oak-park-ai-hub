"""
sheet_schema.py — Canonical column definitions for Ideas & Inbox spreadsheet tabs.

Source of truth for column names. Scripts must resolve positions at runtime
via header-name lookup (never hardcode indices). Use these constants as the
authoritative column names to pass to the lookup helper.

Usage:
    from scripts.lib.sheet_schema import INSPO_COLS, content_queue_col_names

    headers = lib.row_values(1)
    col_pos = {h.strip().lower(): i for i, h in enumerate(headers)}
    url_idx = col_pos.get(INSPO_COLS["url"])
"""

# ── Inspiration Library (📥 Inspiration Library) ─────────────────────────────
# Canonical schema as of 2026-08-18 (46 columns A–AT).
# A–AH are legacy/content-pipeline fields; AI–AT are the reusable-inspiration
# taxonomy added 2026-08-18. Scripts MUST resolve by header name at runtime so
# future column moves/additions do not silently corrupt data.
INSPO_COLS = {
    "date_added":            "date added",              # A
    "content_hub_link":      "content hub link",        # B
    "platform":              "platform",                # C
    "url":                   "url",                     # D
    "creator":               "creator / account",       # E
    "content_type":          "content type",            # F
    "description":           "description",             # G
    "transcription":         "transcription",           # H
    "original_caption":      "original caption",        # I
    "visual_hook":           "visual hook",             # J
    "hook_type":             "hook type",               # K
    "views":                 "views",                   # L
    "comments":              "engagement comments",     # M
    "saves_shares":          "saves / shares",          # N
    "whats_working":         "what's working",          # O
    "ab_test":               "a/b test",                # P
    "brief_angle":           "brief / angle",           # Q
    "format":                "format",                  # R
    "status":                "status",                  # S
    "topic_title":           "topic / title",           # T
    "niche":                 "niche",                   # U
    "my_comments":           "comments",                # V
    "ai_score":              "ai score (1-5)",          # W
    "date_status_changed":   "date status changed",     # X
    "drive_folder_path":     "drive folder path",       # Y
    "my_raw_notes":          "my raw notes",            # Z
    "series_override":       "series_override",         # AA
    "fake_news_route":       "fake_news_route",         # AB
    "fake_news_confidence":  "fake_news_confidence",    # AC
    "credibility":           "credibility",             # AD
    "manifest_url":          "manifest_url",            # AE
    "pipeline_status":       "status",                  # AF — duplicate legacy header
    "sibling_of":            "sibling_of",              # AG
    "story_id":              "story_id",                # AH
    # Reusable-reference taxonomy — 2026-08-18
    "visual_template":       "visual template?",        # AI
    "font_typography":       "font / typography?",      # AJ
    "sound_audio":           "sound / audio?",          # AK
    "caption_style":         "caption style?",          # AL
    "motion_editing":        "motion / editing?",       # AM
    "duration_bucket":       "duration bucket",         # AN
    "exact_duration_sec":    "exact duration (sec)",     # AO
    "best_placement":        "best placement",           # AP
    "style_tags":            "style tags",               # AQ
    "template_scope":        "template scope",           # AR
    "reference_status":      "reference status",         # AS
    "track_creator_account": "track creator / account?", # AT
}

# Reusable-reference enums. Keep these aligned with the live sheet validation.
INSPO_TRI_STATE = {"yes", "no", "unknown"}
INSPO_DURATION_BUCKETS = {"≤15s", "16–30s", "31–60s", "61–180s", ">180s", "Unknown"}
INSPO_BEST_PLACEMENT = {"Full short", "Intro", "Mid-video impact", "Outro", "Flexible"}
INSPO_TEMPLATE_SCOPE = {"Universal", "News", "OPC", "UGC", "Multiple"}
INSPO_REFERENCE_STATUS = {
    "Link only", "Needs frame capture", "Frames captured", "Analyzed", "Template built"
}

# Valid status values for Inspiration Library Status column
INSPO_SKIP_STATUSES = {
    "captured", "queued", "done", "skip", "duplicate",
    "published", "scheduled", "approved",
}

# ── Content Queue (📋 Content Queue in Ideas & Inbox) ────────────────────────
CONTENT_QUEUE_COLS = {
    "date_created":       "date created",         # A
    "project_name":       "project name",          # B
    "service_type":       "service type",           # C
    "photos_used":        "photo(s) used",         # D
    "content_type":       "content type",           # E
    "hook":               "hook",                   # F
    "caption_body":       "caption body",           # G
    "cta":                "cta",                    # H
    "hashtags":           "hashtags",               # I
    "date_status_changed":"date status changed",   # J
    "status":             "status",                 # K
    "suggested_post_date":"suggested post date",   # L
}

# ── Capture Queue (📲 Capture Queue) ─────────────────────────────────────────
CAPTURE_QUEUE_COLS = {
    "date":              "date",                   # A
    "link":              "link",                   # B
    "comment":           "comment",                # C
    "processed":         "processed",              # D
    "score":             "score",                  # E
    "moved_to":          "moved to",               # F
    "hub_doc_path":      "hub doc path",           # G
    "project":           "project",                # H
    "credits_source":    "credits/source",         # I
    "content_ideas":     "content ideas generated",# J
    "ready_to_build":    "ready to build",         # K
    "cut_windows":       "cut_windows",            # L
    "screenshots":       "screenshots",            # M
    "failed_at_stage":   "failed_at_stage",        # N
    "resume_folder_id":  "resume_folder_id",       # O
    "failed_at_ts":      "failed_at_timestamp",    # P
}

# ── Helper ────────────────────────────────────────────────────────────────────

def make_col_pos(header_row: list) -> dict:
    """Build lowercase header→index map from a row of header strings."""
    return {h.strip().lower(): i for i, h in enumerate(header_row)}


def set_col(row: list, col_pos: dict, col_name: str, value) -> None:
    """Write value into row at the position of col_name. Extends row as needed."""
    idx = col_pos.get(col_name.strip().lower())
    if idx is not None:
        while len(row) <= idx:
            row.append("")
        row[idx] = str(value) if value is not None else ""
