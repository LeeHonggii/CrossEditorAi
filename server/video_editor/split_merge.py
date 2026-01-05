from moviepy.editor import VideoFileClip, concatenate_videoclips

# 동영상 파일 경로 설정
video_path1 = 'data/ive_iam_1.mp4'
video_path2 = 'data/ive_iam_2.mp4'

# 동영상 불러오기
video_clip1 = VideoFileClip(video_path1)
video_clip2 = VideoFileClip(video_path2)

clip_list = []

total_seconds = int(video_clip1.duration)

print(total_seconds)
duration = 5

for i in range (0, total_seconds-duration, duration):
    current = video_clip1 if (i % (duration*2)) == 0 else video_clip2
    start_time = i
    end_time = i + duration
    print(i, i % (duration*2), start_time, end_time)
    video_clip = current.subclip(start_time, end_time)
    clip_list.append(video_clip)


# # 첫 번째 구간 설정 (5초에서 10초)
# start_time1 = 5
# end_time1 = 10
# video_clip1 = video_clip.subclip(start_time1, end_time1)
# clip_list.append(video_clip1)
#
# # 두 번째 구간 설정 (10초에서 15초)
# start_time2 = 15
# end_time2 = 20
# video_clip2 = video_clip.subclip(start_time2, end_time2)
# clip_list.append(video_clip2)
#
# start_time3 = 25
# end_time3 = 30
# video_clip3 = video_clip.subclip(start_time3, end_time3)
# clip_list.append(video_clip3)

# 두 구간을 이어붙이기
concatenated_clip = concatenate_videoclips(clip_list)

# 이어붙인 동영상을 파일로 저장
output_path = 'data/mixedit_video.mp4'
concatenated_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')

# 메모리에서 동영상 클립 제거 (선택 사항)
video_clip.close()
video_clip1.close()
video_clip2.close()
concatenated_clip.close()