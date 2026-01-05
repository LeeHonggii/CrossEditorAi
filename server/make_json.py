import json
from moviepy import VideoFileClip, concatenate_videoclips
import subprocess as sp
from moviepy.config import FFMPEG_BINARY
from moviepy.tools import cross_platform_popen_params, ffmpeg_escape_filename
import moviepy.video.io.ffmpeg_writer

# Monkeypatch FFMPEG_VideoWriter.__init__ to fix preset=None bug
def patched_init(
    self,
    filename,
    size,
    fps,
    codec="libx264",
    audiofile=None,
    audio_codec=None,
    preset="medium",
    bitrate=None,
    with_mask=False,
    logfile=None,
    threads=None,
    ffmpeg_params=None,
    pixel_format=None,
):
    if logfile is None:
        logfile = sp.PIPE
    self.logfile = logfile
    self.filename = filename
    self.codec = codec
    self.audio_codec = audio_codec
    self.ext = self.filename.split(".")[-1]

    pixel_format = "rgba" if with_mask else "rgb24"

    # order is important
    cmd = [
        FFMPEG_BINARY,
        "-y",
        "-loglevel",
        "error" if logfile == sp.PIPE else "info",
        "-f",
        "rawvideo",
        "-vcodec",
        "rawvideo",
        "-s",
        "%dx%d" % (size[0], size[1]),
        "-pix_fmt",
        pixel_format,
        "-r",
        "%.02f" % fps,
        "-an",
        "-i",
        "-",
    ]
    if audiofile is not None:
        if audio_codec is None:
            audio_codec = "copy"
        cmd.extend(["-i", audiofile, "-acodec", audio_codec])

    if codec == "h264_nvenc":
        cmd.extend(["-c:v", codec])
    else:
        cmd.extend(["-vcodec", codec])

    # FIX: Only add preset if it is not None
    if preset is not None:
        cmd.extend(["-preset", preset])

    if ffmpeg_params is not None:
        cmd.extend(ffmpeg_params)

    if bitrate is not None:
        cmd.extend(["-b", bitrate])

    if threads is not None:
        cmd.extend(["-threads", str(threads)])

    # Disable auto alt ref for transparent webm and set pix format yo yuva420p
    if codec == "libvpx" and with_mask:
        cmd.extend(["-pix_fmt", "yuva420p"])
        cmd.extend(["-auto-alt-ref", "0"])
    elif (
        (codec == "libx264" or codec == "h264_nvenc")
        and (size[0] % 2 == 0)
        and (size[1] % 2 == 0)
    ):
        cmd.extend(["-pix_fmt", "yuva420p"])

    cmd.extend([ffmpeg_escape_filename(filename)])

    popen_params = cross_platform_popen_params(
        {"stdout": sp.DEVNULL, "stderr": logfile, "stdin": sp.PIPE}
    )

    self.proc = sp.Popen(cmd, **popen_params)

# Apply monkeypatch
moviepy.video.io.ffmpeg_writer.FFMPEG_VideoWriter.__init__ = patched_init

def generate_json(max_transformation_order, verified_matches, video_files, csv_files, video_file_mapping, best_vectors):
    num_streams = len(video_files)
    fps = [29.97] * num_streams  # 각 비디오의 fps (임시 값)
    total_frames = [774] * num_streams  # 각 비디오의 총 프레임 수 (임시 값)
    duration = [25.8258] * num_streams  # 각 비디오의 길이 (임시 값)

    meta_info = {
        "num_stream": num_streams,
        "metric": "time",
        "frame_rate": fps[0],
        "num_frames": total_frames[0],
        "init_time": 0,
        "duration": duration[0],
        "num_vector_pair": 3,
        "num_cross": len(max_transformation_order),
        "first_stream": 1,
        "folder_path": "",  # 폴더 경로 필요 없음
    }

    streams = [{"file": video_file, "start": 0, "end": 0} for video_file in video_files]

    cross_points = []
    for frame, start_file, end_file in max_transformation_order:
        time_stamp = frame / fps[0]  # 전환되는 프레임 값을 적음
        next_stream = video_files.index(video_file_mapping[end_file])
        vector1, vector2 = best_vectors.get((frame, start_file, end_file), ([0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]))
        vector_pairs = [
            {
                "vector1": vector1,
                "vector2": vector2
            }
        ]
        cross_points.append({
            "time_stamp": time_stamp,
            "next_stream": next_stream,
            "vector_pairs": vector_pairs
        })

    json_data = {
        "meta_info": meta_info,
        "streams": streams,
        "cross_points": cross_points,
        "scene_list": [
        [100, 500, 1000, 1500],
        [200, 500, 1500, 3000],
        [100, 510, 1000, 1500],
        [400, 500, 1000, 1500],
        [150, 500, 1000, 1500],
        [800, 500, 1000, 1500],
    ]
    }

    return json_data

def create_combined_video(json_file, output_file):
    with open(json_file, 'r') as f:
        data = json.load(f)

    streams = data['streams']
    cross_points = data['cross_points']

    video_clips = {stream['file']: VideoFileClip(stream['file']) for stream in streams}

    combined_clips = []
    current_clip_info = cross_points[0]
    current_clip = video_clips[streams[0]['file']].subclipped(0, current_clip_info['time_stamp'])

    combined_clips.append(current_clip)

    for i in range(len(cross_points)):
        cross_point = cross_points[i]
        next_stream_file = streams[cross_point['next_stream']]['file']
        next_clip_start = cross_point['time_stamp']

        if i < len(cross_points) - 1:
            next_clip_end = cross_points[i + 1]['time_stamp']
        else:
            next_clip_end = video_clips[next_stream_file].duration

        next_clip = video_clips[next_stream_file].subclipped(next_clip_start, next_clip_end)
        # Ensure subclip has fps
        if next_clip.fps is None:
             next_clip.fps = 24.0
        combined_clips.append(next_clip)

    print(f"Concatenating {len(combined_clips)} clips...")
    # Use chain method for better performance and stability with same-format clips
    final_clip = concatenate_videoclips(combined_clips, method="chain")
    
    # Use with_fps to ensure it propagates correctly
    final_clip = final_clip.with_fps(24)
    print(f"Final clip FPS: {final_clip.fps}")
    
    import moviepy
    print(f"MoviePy version: {moviepy.__version__}")
    
    # Pass fps as keyword argument
    final_clip.write_videofile(output_file, fps=24, codec='libopenh264', preset=None)

