from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip
import random
# #
# # scaled_clip = clip.subclip(5, 15).resize(newsize=(1280, 720))
# #
# # # final_clip = CompositeVideoClip([scaled_clip.set_position("center")], size=(1280, 720))
# #
# # scaled_clip.write_videofile("data/output_video.mp4", codec='libx264')
#
#
input_file = "data/short_video.mp4"
output_file = f"data/output_video_{random.randint(0,999):3d}.mp4"
#
clip = VideoFileClip(input_file)
duration = clip.duration

clip = clip.rotate(5)
# clip = clip.resize(1.7)
# clip = clip.on_color(size=(1920, 1080), color=(0, 0, 0), pos=('center', 'center'))
clip = clip.on_color(size=(1280, 720), color=(0, 0, 0), pos=('center', 'center'))
# clip = clip.on_color(size=(1280, 720), color=(0, 0, 0), pos=(-100, -100))
final_clip = clip.resize(newsize=(1280, 720))
#
# rotated_clip = clip.rotate(5)
# rotated_size = rotated_clip.size
# background = rotated_clip.on_color(size=(1280, 720), color=(0, 0, 0), pos=('center', 'center'))
# final_clip = background.resize(newsize=(1280, 720))
final_clip.write_videofile(output_file, codec='libx264')
#
#
#
# # original_size = clip.size
# #
# # # 1920x1080 크기의 검정색 배경을 만듭니다.
# # background = clip.resize(newsize=(1920, 1080)).on_color(size=(1920, 1080), color=(0, 0, 0))
# #
# # # 원본 동영상을 중앙에 위치시킵니다.
# # final_clip = background.set_position(('center', 'center'))
# #
# # # 변환된 동영상을 파일로 저장합니다.
# # final_clip.write_videofile(output_file, codec='libx264')
#
#
# # final_clip = resize_clip.rotate(30)
#
# final_clip.write_videofile(output_file, codec='libx264')
#
#
