# from moviepy.editor import VideoFileClip
#
# # 동영상 파일 경로 설정
# video_path = 'data/video.mp4'
#
# # 동영상 불러오기
# video_clip = VideoFileClip(video_path)
#
# # 동영상을 오른쪽으로 10도 회전
# rotated_clip = video_clip.rotate(10)
#
# # 회전된 클립을 파일로 저장
# output_path = 'data/rotated_video.mp4'
# rotated_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')
#
# # 메모리에서 동영상 클립 제거
# video_clip.close()
# rotated_clip.close()

from moviepy.editor import VideoFileClip, CompositeVideoClip

# 동영상 파일 경로 설정
video_path = 'data/video.mp4'

# 동영상 불러오기
video_clip = VideoFileClip(video_path)

# 회전 중심을 지정하기 위해 비디오 클립을 CompositeVideoClip에 넣습니다.
composite_clip = CompositeVideoClip([video_clip])

# 회전 중심 좌표 설정 (예: 화면 가운데)
center_x = composite_clip.w / 2  # 화면의 가로 중심
# center_y = composite_clip.h / 2  # 화면의 세로 중심
center_y = composite_clip.h  # 화면의 세로 중심

# 회전 중심을 원하는 위치로 이동
translated_clip = composite_clip.set_position((center_x, center_y))

# 동영상을 오른쪽으로 10도 회전
rotated_clip = translated_clip.rotate(10)

# 회전된 클립을 파일로 저장
output_path = 'data/rotated_video.mp4'
rotated_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')

# 메모리에서 동영상 클립 제거
video_clip.close()
composite_clip.close()
translated_clip.close()
rotated_clip.close()