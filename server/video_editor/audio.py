from moviepy.editor import VideoFileClip

# 동영상 파일 경로 설정
video_path = 'data/video2.mp4'

# VideoFileClip을 사용하여 동영상 불러오기
video_clip = VideoFileClip(video_path)

# 오디오 추출
audio_clip = video_clip.audio

# 추출된 오디오를 파일로 저장
audio_output_path = 'data/audio_extracted2.wav'  # 원하는 오디오 파일 형식 및 경로로 수정 가능
audio_clip.write_audiofile(audio_output_path, fps=44100, nbytes=2, codec='pcm_s16le')

# 메모리에서 오디오 클립 제거 (선택 사항)
audio_clip.close()
video_clip.close()