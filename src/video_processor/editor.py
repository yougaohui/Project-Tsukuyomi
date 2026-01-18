"""
视频编辑器 - 使用 MoviePy 处理视频
"""
from pathlib import Path
from typing import Optional, Tuple, List
import moviepy.editor as mp
from moviepy.video.fx import all as vfx

from src.config.settings import (
    VIDEO_CROP_ENABLED,
    VIDEO_MAX_DURATION,
    VIDEO_MIN_DURATION,
    WATERMARK_ENABLED,
    WATERMARK_POSITION,
    WATERMARK_OPACITY,
    WATERMARK_DURATION,
    WATERMARK_DIR,
    SUBTITLE_ENABLED,
    SUBTITLE_FONT_SIZE,
    SUBTITLE_COLOR,
    SUBTITLE_POSITION,
    MUSIC_ENABLED,
    MUSIC_VOLUME,
    MUSIC_FADE_DURATION,
    MUSIC_DIR,
    PROCESSED_DIR
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


class VideoEditor:
    """视频编辑器"""

    def __init__(self):
        self.watermark_path = WATERMARK_DIR / "watermark.png" if WATERMARK_ENABLED else None

    def crop_video(
        self,
        video_path: Path,
        max_duration: int = VIDEO_MAX_DURATION,
        min_duration: int = VIDEO_MIN_DURATION
    ) -> Path:
        """
        裁剪视频时长

        Args:
            video_path: 视频文件路径
            max_duration: 最大时长（秒）
            min_duration: 最小时长（秒）

        Returns:
            裁剪后的视频路径
        """
        if not VIDEO_CROP_ENABLED:
            return video_path

        video = mp.VideoFileClip(str(video_path))

        if video.duration <= max_duration and video.duration >= min_duration:
            logger.info(f"Video duration {video.duration:.2f}s is within limits")
            video.close()
            return video_path

        if video.duration > max_duration:
            logger.info(f"Cropping video from {video.duration:.2f}s to {max_duration}s")
            video = video.subclip(0, max_duration)

        output_path = PROCESSED_DIR / f"cropped_{video_path.name}"
        video.write_videofile(
            str(output_path),
            codec="libx264",
            audio_codec="aac",
            verbose=False,
            logger=None
        )

        video.close()
        logger.info(f"Video cropped and saved to {output_path}")

        return output_path

    def add_watermark(
        self,
        video_path: Path,
        watermark_path: Path = None,
        position: Tuple[str, str] = WATERMARK_POSITION,
        opacity: float = WATERMARK_OPACITY,
        duration: int = WATERMARK_DURATION
    ) -> Path:
        """
        添加水印

        Args:
            video_path: 视频文件路径
            watermark_path: 水印图片路径
            position: 水印位置
            opacity: 透明度 (0-1)
            duration: 水印显示时长（秒），None 表示全程显示

        Returns:
            添加水印后的视频路径
        """
        if not WATERMARK_ENABLED:
            return video_path

        watermark_path = watermark_path or self.watermark_path
        if not watermark_path or not watermark_path.exists():
            logger.warning(f"Watermark file not found, skipping watermark")
            return video_path

        video = mp.VideoFileClip(str(video_path))
        watermark = (mp.ImageClip(str(watermark_path))
                   .set_duration(duration if duration else video.duration)
                   .resize(height=50)
                   .set_position(position)
                   .set_opacity(opacity))

        final = mp.CompositeVideoClip([video, watermark])
        output_path = PROCESSED_DIR / f"watermarked_{video_path.name}"

        final.write_videofile(
            str(output_path),
            codec="libx264",
            audio_codec="aac",
            verbose=False,
            logger=None
        )

        video.close()
        final.close()
        logger.info(f"Watermark added to {output_path}")

        return output_path

    def add_subtitle(
        self,
        video_path: Path,
        text: str,
        font_size: int = SUBTITLE_FONT_SIZE,
        color: str = SUBTITLE_COLOR,
        position: str = SUBTITLE_POSITION,
        duration: int = 5
    ) -> Path:
        """
        添加字幕

        Args:
            video_path: 视频文件路径
            text: 字幕文本
            font_size: 字体大小
            color: 字体颜色
            position: 字幕位置
            duration: 字幕显示时长（秒）

        Returns:
            添加字幕后的视频路径
        """
        if not SUBTITLE_ENABLED:
            return video_path

        video = mp.VideoFileClip(str(video_path))

        txt_clip = (mp.TextClip(
            text,
            fontsize=font_size,
            color=color,
            stroke_color='black',
            stroke_width=2
        )
        .set_position(position)
        .set_duration(min(duration, video.duration)))

        final = mp.CompositeVideoClip([video, txt_clip])
        output_path = PROCESSED_DIR / f"subtitled_{video_path.name}"

        final.write_videofile(
            str(output_path),
            codec="libx264",
            audio_codec="aac",
            verbose=False,
            logger=None
        )

        video.close()
        final.close()
        logger.info(f"Subtitle added to {output_path}")

        return output_path

    def add_background_music(
        self,
        video_path: Path,
        music_path: Path = None,
        volume: float = MUSIC_VOLUME,
        fade_duration: int = MUSIC_FADE_DURATION
    ) -> Path:
        """
        添加背景音乐

        Args:
            video_path: 视频文件路径
            music_path: 音乐文件路径
            volume: 音乐音量 (0-1)
            fade_duration: 淡入淡出时长（秒）

        Returns:
            添加音乐后的视频路径
        """
        if not MUSIC_ENABLED:
            return video_path

        if not music_path or not music_path.exists():
            musics = list(MUSIC_DIR.glob("*.mp3"))
            if not musics:
                logger.warning("No background music found, skipping")
                return video_path
            music_path = musics[0]

        video = mp.VideoFileClip(str(video_path))
        music = mp.AudioFileClip(str(music_path))

        if music.duration > video.duration:
            music = music.subclip(0, video.duration)
        else:
            music = music.fx(vfx.audio_loop, duration=video.duration)

        music = music.fx(vfx.audio_fadein, fade_duration)
        music = music.fx(vfx.audio_fadeout, fade_duration)
        music = music.volumex(volume)

        final_audio = mp.CompositeAudioClip([video.audio, music])
        final_video = video.set_audio(final_audio)

        output_path = PROCESSED_DIR / f"music_{video_path.name}"

        final_video.write_videofile(
            str(output_path),
            codec="libx264",
            audio_codec="aac",
            verbose=False,
            logger=None
        )

        video.close()
        music.close()
        final_video.close()
        logger.info(f"Background music added to {output_path}")

        return output_path

    def process_video(
        self,
        video_path: Path,
        crop: bool = None,
        add_watermark_flag: bool = None,
        add_music_flag: bool = None,
        subtitle_text: str = None
    ) -> Path:
        """
        综合处理视频（裁剪、水印、字幕、音乐）

        Args:
            video_path: 原始视频路径
            crop: 是否裁剪
            add_watermark_flag: 是否添加水印
            add_music_flag: 是否添加音乐
            subtitle_text: 字幕文本

        Returns:
            处理后的视频路径
        """
        current_path = video_path

        if crop if crop is not None else VIDEO_CROP_ENABLED:
            current_path = self.crop_video(current_path)

        if add_watermark_flag if add_watermark_flag is not None else WATERMARK_ENABLED:
            current_path = self.add_watermark(current_path)

        if add_music_flag if add_music_flag is not None else MUSIC_ENABLED:
            current_path = self.add_background_music(current_path)

        if subtitle_text and SUBTITLE_ENABLED:
            current_path = self.add_subtitle(current_path, subtitle_text)

        logger.info(f"Video processing completed: {current_path}")
        return current_path

    def extract_frame(
        self,
        video_path: Path,
        timestamp: float,
        output_path: Path = None
    ) -> Path:
        """
        提取视频帧

        Args:
            video_path: 视频路径
            timestamp: 时间戳（秒）
            output_path: 输出路径

        Returns:
            提取的图片路径
        """
        video = mp.VideoFileClip(str(video_path))

        if output_path is None:
            output_path = PROCESSED_DIR / f"frame_{int(timestamp)}.jpg"

        video.save_frame(str(output_path), t=timestamp)
        video.close()

        logger.info(f"Frame extracted to {output_path}")
        return output_path

    def concatenate_videos(
        self,
        video_paths: List[Path],
        output_path: Path = None
    ) -> Path:
        """
        拼接多个视频

        Args:
            video_paths: 视频路径列表
            output_path: 输出路径

        Returns:
            拼接后的视频路径
        """
        if len(video_paths) < 2:
            raise ValueError("At least 2 videos required for concatenation")

        clips = [mp.VideoFileClip(str(path)) for path in video_paths]

        if output_path is None:
            output_path = PROCESSED_DIR / "concatenated.mp4"

        final = mp.concatenate_videoclips(clips, method="compose")
        final.write_videofile(
            str(output_path),
            codec="libx264",
            audio_codec="aac",
            verbose=False,
            logger=None
        )

        for clip in clips:
            clip.close()
        final.close()

        logger.info(f"Videos concatenated to {output_path}")
        return output_path
