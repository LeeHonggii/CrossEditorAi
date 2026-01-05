# from moviepy.editor import VideoFileClip
#
# # 동영상 파일 경로 설정
# video_path = 'data/video.mp4'
#
# # 동영상 불러오기
# video_clip = VideoFileClip(video_path)
# # video_clip = video_clip.subclip(15, 35)
# width, height = video_clip.size
#
# # video_clip_resized = video_clip.resize(newsize=(1920, 1080))
# # video_clip_resized = video_clip.resize(0.5)
# # >>> myClip.resize( (460,720) ) # New resolution: (460,720)
# # >>> myClip.resize(0.6) # width and heigth multiplied by 0.6
# # >>> myClip.resize(width=800) # height computed automatically.
# # video_clip_resized = video_clip.resize(lambda t : 1+0.1*t) # slow swelling of the clip
# # video_clip_resized = video_clip.set_position((lambda x : -int(width*0.1*t)), (lambda y : -int(height*0.1*t))).resize(lambda t : 1+0.1*t) # slow swelling of the clip
# # video_clip_resized = video_clip.set_position((lambda x : -int(1*t)), (lambda y : -int(1*t)))
# clip.set_position(lambda t: ('center', 500 + (1080-500)*(t/5)))
#
# # CompositeVideoClip([imgclip],size=(512,512)).write_videofile('./Result.mp4', codec='libx264', fps=24)
#
# video_clip_resized = video_clip_resized.crop(x1=0, y1=0, x2=video_clip.w, y2=video_clip.h)
# # video_clip_resized = video_clip.crop(x1=0, y1=0, x2=video_clip.w*0.5, y2=video_clip.h*0.5)
# # video_clip_resized = video_clip.crop(x1=video_clip.w*0.25, y1=video_clip.h*0.25, x2=video_clip.w*0.75, y2=video_clip.h*0.75)
#
# # 크기가 조정된 비디오 클립을 파일로 저장
# output_path = 'data/resized_video2.mp4'
# video_clip_resized.write_videofile(output_path, codec='libx264', audio_codec='aac')
#
# # 메모리에서 동영상 클립 제거 (선택 사항)
# video_clip.close()
# video_clip_resized.close()


# from moviepy.editor import VideoFileClip, CompositeVideoClip
#
# # 동영상 파일을 로드합니다.
# clip = VideoFileClip("data/video.mp4")
#
# # 동영상을 축소합니다. 예를 들어, 0.5배로 축소한다고 가정합니다.
# scaled_clip = clip.resize(0.5)
#
# # 축소된 동영상을 중앙에 위치시킵니다.
# # CompositeVideoClip을 사용하여 원래 크기인 1280x720 크기의 배경에 축소된 클립을 중앙에 위치시킵니다.
# final_clip = CompositeVideoClip([scaled_clip.set_position("center")], size=(1280, 720))
#
# # 결과를 파일로 저장합니다.
# final_clip.write_videofile("data/output_video.mp4", codec='libx264')

from moviepy.editor import VideoFileClip, CompositeVideoClip

# 동영상 파일을 로드합니다.
clip = VideoFileClip("data/video.mp4")

# 크기 변화 함수: 10초 동안 1.0에서 0.5로 천천히 줄어듭니다.
def scale(t):
    return 1.0 - 0.05 * t if t <= 10 else 0.5

# 축소된 동영상을 시간에 따라 크기를 변경합니다.
scaled_clip = clip.resize(scale)

# 최종 클립을 1280x720 크기의 배경에 중심에 위치시킵니다.
final_clip = CompositeVideoClip([scaled_clip.set_position("center")], size=(1280, 720))

# 결과를 파일로 저장합니다.
final_clip.write_videofile("data/shrinking_video.mp4", codec='libx264')
