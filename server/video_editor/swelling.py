# from moviepy.editor import VideoFileClip, CompositeVideoClip
#
# # 동영상 파일을 로드합니다.
# clip = VideoFileClip("data/video.mp4")
#
# # 크기 변화 함수: 처음 10초 동안 0.5에서 1.0으로 증가, 다음 10초 동안 1.0에서 0.5로 감소.
# def scale(t):
#     if t <= 10:
#         return 0.5 + 0.05 * t  # 10초 동안 0.5 -> 1.0
#     elif 10 < t <= 20:
#         return 1.0 - 0.05 * (t - 10)  # 10초 동안 1.0 -> 0.5
#     else:
#         return 0.5  # 이후에는 0.5로 유지
#
# # 위치 변화 함수: 처음 10초 동안 좌상단에서 중앙으로 이동, 다음 10초 동안 중앙에서 우하단으로 이동.
# def position(t):
#     if t <= 10:
#         return ("left", "top") if t == 0 else (640 * t / 10 - 320, 360 * t / 10 - 180)
#     elif 10 < t <= 20:
#         t -= 10
#         return (320 + 320 * t / 10, 180 + 180 * t / 10)
#     else:
#         return ("right", "bottom")
#
# # 축소된 동영상을 시간에 따라 크기와 위치를 변경합니다.
# scaled_and_moved_clip = clip.resize(scale).set_position(position)
#
# # 최종 클립을 1280x720 크기의 배경에 위치시킵니다.
# final_clip = CompositeVideoClip([scaled_and_moved_clip], size=(1280, 720))
#
# # 결과를 파일로 저장합니다.
# final_clip.write_videofile("data/swelling_video.mp4", codec='libx264')

# from moviepy.editor import VideoFileClip, CompositeVideoClip
#
# # 동영상 파일을 로드합니다.
# clip = VideoFileClip("data/video.mp4")
#
# # 크기 변화 함수: 처음 10초 동안 0.5에서 1.0으로 증가, 다음 10초 동안 1.0에서 0.5로 감소.
# def scale(t):
#     if t <= 10:
#         return 0.5 + 0.05 * t  # 10초 동안 0.5 -> 1.0
#     elif 10 < t <= 20:
#         return 1.0 - 0.05 * (t - 10)  # 10초 동안 1.0 -> 0.5
#     else:
#         return 0.5  # 이후에는 0.5로 유지
#
# # 위치 변화 함수: 처음 10초 동안 좌상단에서 중앙으로 이동, 다음 10초 동안 중앙에서 우하단으로 이동.
# def position(t):
#     if t <= 10:
#         return ("left", "top") if t == 0 else (640 * t / 10 - 320, 360 * t / 10 - 180)
#     elif 10 < t <= 20:
#         t -= 10
#         return (320 + 320 * t / 10, 180 + 180 * t / 10)
#     else:
#         return ("right", "bottom")
#
# # 회전 변화 함수: 처음 10초 동안 0도에서 90도로 회전, 다음 10초 동안 90도에서 180도로 회전.
# def rotate(t):
#     if t <= 10:
#         return 9 * t  # 10초 동안 0 -> 90도
#     elif 10 < t <= 20:
#         return 90 + 9 * (t - 10)  # 10초 동안 90 -> 180도
#     else:
#         return 180  # 이후에는 180도 유지
#
# # 축소된 동영상을 시간에 따라 크기, 위치, 회전을 변경합니다.
# transformed_clip = clip.resize(scale).set_position(position).rotate(rotate)
#
# # 최종 클립을 1280x720 크기의 배경에 위치시킵니다.
# final_clip = CompositeVideoClip([transformed_clip], size=(1280, 720))
#
# # 결과를 파일로 저장합니다.
# final_clip.write_videofile("data/moving_video.mp4", codec='libx264')

# from moviepy.editor import VideoFileClip, CompositeVideoClip
#
# # 동영상 파일을 로드합니다.
# clip = VideoFileClip("data/video.mp4")
#
# # 크기 변화 함수: 처음 10초 동안 0.5에서 1.0으로 증가, 다음 10초 동안 1.0에서 0.5로 감소.
# def scale(t):
#     if t <= 10:
#         return 0.5 + 0.05 * t  # 10초 동안 0.5 -> 1.0
#     elif 10 < t <= 20:
#         return 1.0 - 0.05 * (t - 10)  # 10초 동안 1.0 -> 0.5
#     else:
#         return 0.5  # 이후에는 0.5로 유지
#
# # 위치 변화 함수: 처음 10초 동안 좌상단에서 중앙으로 이동, 다음 10초 동안 중앙에서 우하단으로 이동.
# def position(t):
#     if t <= 10:
#         return ("left", "top") if t == 0 else (640 * t / 10 - 320, 360 * t / 10 - 180)
#     elif 10 < t <= 20:
#         t -= 10
#         return (320 + 320 * t / 10, 180 + 180 * t / 10)
#     else:
#         return ("right", "bottom")
#
# # 회전 변화 함수: 처음 10초 동안 0도에서 90도로 회전, 다음 10초 동안 90도에서 180도로 회전.
# def rotate(t):
#     if t <= 10:
#         return 9 * t  # 10초 동안 0 -> 90도
#     elif 10 < t <= 20:
#         return 90 + 9 * (t - 10)  # 10초 동안 90 -> 180도
#     else:
#         return 180  # 이후에는 180도 유지
#
# # 회전 중심 설정: 좌측에서 4분의 1, 위에서 2분의 1
# def rotation_center(w, h):
#     return (w * 0.25, h * 0.5)
#
# # 축소된 동영상을 시간에 따라 크기, 위치, 회전을 변경합니다.
# transformed_clip = clip.resize(scale).set_position(position).rotate(lambda t: rotate(t), center=rotation_center(clip.w, clip.h))
#
# # 최종 클립을 1280x720 크기의 배경에 위치시킵니다.
# final_clip = CompositeVideoClip([transformed_clip], size=(1280, 720))
#
# # 결과를 파일로 저장합니다.
# final_clip.write_videofile("data/moving_video.mp4", codec='libx264')
#
#
from moviepy.editor import VideoFileClip, CompositeVideoClip
import cv2
import numpy as np

# 동영상 파일을 로드합니다.
clip = VideoFileClip("data/video.mp4")

# 크기 변화 함수: 처음 10초 동안 0.5에서 1.0으로 증가, 다음 10초 동안 1.0에서 0.5로 감소.
def scale(t):
    if t <= 10:
        return 0.5 + 0.05 * t  # 10초 동안 0.5 -> 1.0
    elif 10 < t <= 20:
        return 1.0 - 0.05 * (t - 10)  # 10초 동안 1.0 -> 0.5
    else:
        return 0.5  # 이후에는 0.5로 유지

# 위치 변화 함수: 처음 10초 동안 좌상단에서 중앙으로 이동, 다음 10초 동안 중앙에서 우하단으로 이동.
def position(t):
    if t <= 10:
        return (640 * t / 10 - 320, 360 * t / 10 - 180)
    elif 10 < t <= 20:
        t -= 10
        return (320 + 320 * t / 10, 180 + 180 * t / 10)
    else:
        return (640, 360)

# 회전 변화 함수: 처음 10초 동안 0도에서 90도로 회전, 다음 10초 동안 90도에서 180도로 회전.
def rotate(t):
    if t <= 10:
        return 9 * t  # 10초 동안 0 -> 90도
    elif 10 < t <= 20:
        return 90 + 9 * (t - 10)  # 10초 동안 90 -> 180도
    else:
        return 180  # 이후에는 180도 유지

# 회전 중심 설정: 좌측에서 4분의 1, 위에서 2분의 1
rotation_center = (clip.w * 0.25, clip.h * 0.5)

# 프레임에 변형을 적용하는 함수
def apply_transforms(get_frame, t):
    frame = get_frame(t)
    frame_center = np.array(frame.shape[1::-1]) / 2
    translation_to_center = np.array(rotation_center) - frame_center
    translation_back = -translation_to_center

    # 1. 원래 위치에서 회전 중심으로 이동
    M_to_center = np.float32([[1, 0, translation_to_center[0]], [0, 1, translation_to_center[1]]])
    frame = cv2.warpAffine(frame, M_to_center, (frame.shape[1], frame.shape[0]))

    # 2. 회전
    angle = rotate(t)
    M_rotate = cv2.getRotationMatrix2D(rotation_center, angle, 1)
    frame = cv2.warpAffine(frame, M_rotate, (frame.shape[1], frame.shape[0]))

    # 3. 다시 원래 위치로 이동
    M_back = np.float32([[1, 0, translation_back[0]], [0, 1, translation_back[1]]])
    frame = cv2.warpAffine(frame, M_back, (frame.shape[1], frame.shape[0]))

    return frame

# 변형된 클립을 반환하는 함수
transformed_clip = clip.fl(apply_transforms)

# 크기와 위치 변환을 적용한 클립
transformed_clip = transformed_clip.resize(scale).set_position(position)

# 최종 클립을 1280x720 크기의 배경에 위치시킵니다.
final_clip = CompositeVideoClip([transformed_clip], size=(1280, 720))

# 결과를 파일로 저장합니다.
final_clip.write_videofile("data/moving_video.mp4", codec='libx264')
