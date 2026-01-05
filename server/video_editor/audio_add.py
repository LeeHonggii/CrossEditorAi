from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip

# 소리 없는 동영상 파일 경로 설정
video_path = 'data/output_video.mp4'

# 소리 파일 경로 설정
audio_path = 'data/audio2.wav'

# 동영상 불러오기
video_clip = VideoFileClip(video_path)

# 오디오 불러오기
audio_clip = AudioFileClip(audio_path)

# 동영상에 오디오 추가
video_clip = video_clip.set_audio(audio_clip)

# 합쳐진 동영상 파일로 저장
output_path = 'data/video_with_audio.mp4'
video_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')

# 메모리에서 동영상 클립 제거 (선택 사항)
video_clip.close()
