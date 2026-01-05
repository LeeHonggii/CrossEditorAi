from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip

# 소리 없는 동영상 파일 경로 설정
video_path = 'data/output_video.mp4'

# 오디오 파일 경로 설정 (여러 개)
audio_paths = ['data/audio1.wav', 'data/audio2.wav']

# 동영상 불러오기
video_clip = VideoFileClip(video_path)

# 빈 CompositeAudioClip 객체 생성
composite_audio = CompositeAudioClip([])

# 각 오디오 파일을 CompositeAudioClip에 추가
for audio_path in audio_paths:
    audio_clip = AudioFileClip(audio_path)
    composite_audio = composite_audio.set_duration(max(composite_audio.duration, audio_clip.duration))
    composite_audio = composite_audio.set_channels(audio_clip.nchannels)
    composite_audio = composite_audio.set_fps(audio_clip.fps)
    composite_audio = composite_audio.add_audioclip(audio_clip)

# 소리 없는 동영상에 오디오 추가
video_clip = video_clip.set_audio(composite_audio)

# 합쳐진 동영상 파일로 저장
output_path = 'video_with_audio.mp4'
video_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')

# 메모리에서 동영상 클립 제거 (선택 사항)
video_clip.close()
