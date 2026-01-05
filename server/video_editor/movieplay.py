from moviepy.editor import VideoFileClip

# 동영상 파일 경로 설정
video_path = 'data/video1.mp4'

# 동영상 파일 불러오기
clip = VideoFileClip(video_path)

# 동영상과 오디오를 함께 재생
clip.preview()