from __future__ import annotations

import asyncio
import os

from config import settings
from core.logger import logger
import json


DEFAULT_FPS = "10/1"
DEFAULT_WIDTH = 360


class FFmpegError(Exception):
    pass


async def probe_resolution(path: str) -> dict:
    # use ffprobe to get resolution
    proc = await asyncio.create_subprocess_exec(
        settings.ffmpeg_path.replace("ffmpeg", "ffprobe"),
        "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height,avg_frame_rate",
        "-of", "json", path,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    out, err = await proc.communicate()
    if proc.returncode != 0:
        raise FFmpegError(err.decode("utf-8", "ignore"))
    data = json.loads(out)
    default_return = {"width": DEFAULT_WIDTH, "avg_frame_rate": DEFAULT_FPS}
    if not data:
        return default_return
    streams = data.get("streams", None)
    if not streams or len(streams) == 0:
        return default_return
    return streams[0]


async def video_to_gif(src: str, dst: str, size_limit_mb: int, timeout_sec: int = 360,
                       dst_fps: int | None = None) -> dict:
    """Convert video to GIF not exceeding size_limit_mb by adjusting fps/scale.
    """
    size_limit_bytes = size_limit_mb * 1024 * 1024

    src_info = await probe_resolution(src)
    src_frame_rate = src_info.get("avg_frame_rate", DEFAULT_FPS)
    src_frame_rate = DEFAULT_FPS if "/0" in src_frame_rate else src_frame_rate

    width = int(max(1, min(src_info.get("width", DEFAULT_WIDTH), 1280)))
    fps = int(max(1, min(eval(src_frame_rate), 30)))
    fps = fps if dst_fps is None else dst_fps
    increased = False
    current_width = 32

    async def run_cmd(cmd: list[str]):
        proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE,
                                                    stderr=asyncio.subprocess.PIPE)
        try:
            out, err = await asyncio.wait_for(proc.communicate(), timeout=timeout_sec)
        except asyncio.TimeoutError:
            proc.kill()
            raise FFmpegError("Timeout")
        if proc.returncode != 0:
            raise FFmpegError(err.decode("utf-8", "ignore"))

    while True:
        # 1) ffmpeg
        vf_use = (f"[0:v]fps={fps},scale={int(current_width)}:-1:flags=lanczos+accurate_rnd+full_chroma_int,"
                  f"split[s0][s1];[s0]palettegen=reserve_transparent=1[p];[s1][p]paletteuse=alpha_threshold=128")
        await run_cmd([settings.ffmpeg_path, "-hide_banner", "-y", "-i", src, "-filter_complex", vf_use,
                       "-gifflags", "-offsetting", "-loop", "0", dst])

        # 2) optimize
        await run_cmd(["gifsicle", "-O3", "--lossy=30", dst, "-o", dst])

        result_size = os.path.getsize(dst)

        log_text = (f"FFmpeg: src: {src}, fps: {fps}, width: {int(current_width)} "
                    f"({round(result_size / 1024 / 1024, 2)} MB)")
        logger.info(log_text)

        file_info = {"width": int(current_width), "fps": fps, "size": result_size}

        if result_size > size_limit_bytes:
            divider = min(max(1.01, (result_size / size_limit_bytes) ** 0.8), 1.3)
            current_width = min(current_width / divider, width)
            increased = True
        elif current_width < width:
            if increased and os.path.exists(dst):
                return file_info
            multiplier = min(max(1.3, (size_limit_bytes / result_size) ** 0.5), 10)
            current_width = min(current_width * multiplier, width)
        elif os.path.exists(dst):
            if current_width > width:
                current_width = width
            else:
                return file_info
        else:
            raise FFmpegError("Cannot create GIF.")
