from __future__ import annotations

import re
from typing import Iterable

SAFE_NAME_RE = re.compile(r"[^A-Za-z0-9._-]+")

VIDEO_MIME_PREFIXES: tuple[str, ...] = ("video/",)

ALLOWED_EXTENSIONS = {"mp4", "mov", "mkv", "webm", "avi"}


def sanitize_filename(name: str) -> str:
    name = name.replace(" ", "_")[:80]
    return SAFE_NAME_RE.sub("", name)


def has_only_one_video(attachments: Iterable[tuple[str, int | None]]) -> bool:
    # attachments: iterable of (mime_type, file_size)
    videos = [a for a in attachments if a[0].startswith("video/")]
    non_videos = [a for a in attachments if not a[0].startswith("video/")]
    return len(videos) == 1 and len(non_videos) == 0
