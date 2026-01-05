# from moviepy.editor import VideoFileClip
#
# # 동영상 파일 경로 설정
# video_path = 'data/video.mp4'
#
# # 동영상 불러오기
# video_clip = VideoFileClip(video_path)
#
# # 확대할 비율 설정
# scale_factor = 0.5  # 10% 확대
#
# # 변환 함수 정의: 크기를 서서히 조절하는 함수
# def gradual_scale(t):
#     return max(0.5, 1.0 + (scale_factor - 1.0) * t / 5)  # 5초 동안 서서히 크기 조절
#
# # 크기를 조절하는 클립 생성
# scaled_clip = video_clip.resize(gradual_scale)
#
# # 클립을 파일로 저장
# output_path = 'data/scaled_video.mp4'
# scaled_clip.write_videofile(output_path, codec='libx264', audio_codec='aac', fps=video_clip.fps)
#
# # 메모리에서 동영상 클립 제거
# video_clip.close()
# scaled_clip.close()

# from moviepy.editor import VideoFileClip
#
# # 동영상 파일 경로 설정
# video_path = 'data/video.mp4'
#
# # 동영상 불러오기
# video_clip = VideoFileClip(video_path)
#
# # 축소할 비율 설정
# scale_factor = 0.5  # 절반으로 축소
#
# # 변환 함수 정의: 크기를 서서히 조절하는 함수
# def gradual_scale(t):
#     print(max(0.5, 1.0 - (1.0 - scale_factor) * t / 5))
#     return max(0.5, 1.0 - (1.0 - scale_factor) * t / 5)  # 5초 동안 서서히 크기 조절
#
# # 크기를 조절하는 클립 생성
# scaled_clip = video_clip.resize(gradual_scale)
#
# # 클립을 파일로 저장
# output_path = 'data/scaled_video.mp4'
# scaled_clip.write_videofile(output_path, codec='libx264', audio_codec='aac', fps=video_clip.fps)
#
# # 메모리에서 동영상 클립 제거
# video_clip.close()
# scaled_clip.close()

# from moviepy.editor import *
#
# # 동영상 파일 경로
# video_path = "data/video.mp4"
#
# # 원본 동영상 불러오기
# video = VideoFileClip(video_path)
#
# # 특정 구간 설정 (시작 시간, 끝 시간)
# start_time = 10
# end_time = 20
#
# # 특정 구간 확대/축소 비율
# zoom_ratio = 2
#
# # 시작 시간부터 끝 시간까지의 구간을 확대/축소
# zoomed_clip = video.subclip(start_time, end_time).fx(vfx.zoom, zoom_ratio)
#
# # 결과 동영상 저장
# output_path = "확대축소된_동영상.mp4"
# zoomed_clip.write_videofile(output_path)


# from moviepy.editor import VideoFileClip
#
# # 비디오 불러오기
# clip = VideoFileClip("data/video.mp4")
#
# # 이미지로 저장할 프레임 범위 설정 (시작 시간과 끝 시간)
# start_time = 1  # 시작 시간 (초)
# end_time = 2    # 끝 시간 (초)
#
# # 시작 시간과 끝 시간에 해당하는 프레임 추출
# selected_frames = [clip.get_frame(t) for t in range(int(start_time * clip.fps), int(end_time * clip.fps))]
#
# # 이미지로 저장
# for i, frame in enumerate(selected_frames):
#     frame.save_frame(f"data/frame_{start_time}_{i}.png")

# from moviepy.editor import VideoFileClip
#
# def save_frame_at_time(video_path, save_path, time):
#     # 비디오 파일 클립을 로드합니다.
#     clip = VideoFileClip(video_path)
#
#     # 지정된 시간으로 이동합니다.
#     # clip = clip.set_duration(1).set_start(time)
#
#     # 해당 시간대의 프레임을 가져옵니다.
#     # frame = clip.get_frame(0)
#
#     # 프레임을 저장합니다.
#     clip.save_frame(save_path, 10)
#
#
# # 사용 예제
# video_path = "data/video.mp4"
# save_path = "data/frame_at_time.jpg"
# time = 10  # 10초
# save_frame_at_time(video_path, save_path, time)

from moviepy.editor import VideoFileClip
from moviepy.video.fx import resize
from PIL import Image


def save_frame_at_time(video_path, save_path, time, scale_factor):
    # 비디오 파일 클립을 로드합니다.
    clip = VideoFileClip(video_path)

    # 지정된 시간으로 이동합니다.
    clip = clip.set_duration(1).set_start(time)

    # 해당 시간대의 프레임을 가져옵니다.
    frame = clip.get_frame(0)

    # 프레임을 확대합니다.
    resized_frame = resize(frame, lambda t: (t[0] * scale_factor, t[1] * scale_factor))

    # 넘파이 배열을 이미지로 변환합니다.
    image = Image.fromarray(resized_frame)

    # 이미지를 저장합니다.
    image.save(save_path)


# 사용 예제
video_path = "data/video.mp4"
save_path = "data/frame_at_5_seconds.jpg"
time = 5  # 5초
scale_factor = 2  # 2배 확대
save_frame_at_time(video_path, save_path, time, scale_factor)
