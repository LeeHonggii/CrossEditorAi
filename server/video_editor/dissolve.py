from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip

# 동영상 파일 읽기
clip1 = VideoFileClip("data/video1.mp4")
clip2 = VideoFileClip("data/video2.mp4")
clip1 = clip1.subclip(5, 10)
clip2 = clip2.subclip(5, 10)

# # 페이드 효과 설정 (2초 동안 교차 페이드)
# fade_duration = 0.1
#
# # 첫 번째 클립의 마지막 부분과 두 번째 클립의 첫 부분을 페이드 처리
# clip1 = clip1.crossfadeout(fade_duration)
# clip2 = clip2.crossfadein(fade_duration)
#
# # 클립들을 연결
# final_clip = concatenate_videoclips([clip1, clip2], method="compose")
#
# # 결과를 파일로 저장
# final_clip.write_videofile("data/fade_video.mp4", codec="libx264", fps=24)
#
# from moviepy.editor import VideoFileClip, concatenate_videoclips
#
# # 동영상 파일 읽기
# clip1 = VideoFileClip("video1.mp4")
# clip2 = VideoFileClip("video2.mp4")

# 페이드 효과 설정 (2초 동안 겹쳐서 전환)
# fade_duration = 3
#
# # 첫 번째 클립의 길이
# duration1 = clip1.duration
#
# # 두 번째 클립의 시작 부분을 잘라내어 첫 번째 클립에 겹치기
# clip2 = clip2.set_start(duration1 - fade_duration)
#
# # 두 번째 클립의 길이를 전체 길이로 확장
# final_duration = duration1 + clip2.duration - fade_duration
#
# # CompositeVideoClip을 사용하여 두 클립을 겹쳐서 연결
# final_clip = CompositeVideoClip([clip1, clip2]).set_duration(final_duration)
#
# # 결과를 파일로 저장
# final_clip.write_videofile("data/fade_video.mp4", codec="libx264", fps=24)
#

# from moviepy.editor import VideoFileClip, concatenate_videoclips
#
# # 동영상 파일 읽기
# clip1 = VideoFileClip("video1.mp4")
# clip2 = VideoFileClip("video2.mp4")

# dissolve_duration = 2

# 디졸브 효과를 적용하여 클립들을 연결
# final_clip = concatenate_videoclips([clip1, clip2], method="chain", padding=-dissolve_duration)

# 결과를 파일로 저장
# final_clip.write_videofile("data/desolve_video.mp4", codec="libx264", fps=24)
#

#
# custom_padding = 2
# target_path = "data/fade_video.mp4"
# final_video = concatenate_videoclips(
#     [
#         clip1,
#         clip2.crossfadein(custom_padding),
#         clip1.crossfadein(custom_padding)
#     ],
#     padding=-custom_padding,
#     method="chain"
# )
# final_video.write_videofile("data/fade_video.mp4", codec="libx264", fps=24)

# padding = 2
#
# video_clips = [clip1, clip2]
#
# video_fx_list = [video_clips[0]]
#
# idx = video_clips[0].duration - padding
# for video in video_clips[1:]:
#     video_fx_list.append(video.set_start(idx).crossfadein(padding))
#     idx += video.duration - padding
#
# final_clip = CompositeVideoClip(video_fx_list)
# final_clip.write_videofile("data/fade_video.mp4", codec="libx264", fps=24)

# padding = 1
#
# v_list = []
# v_list.append(clip1)
# v_list.append(clip2.crossfadein(padding).set_opacity(0.5))

# v_list.append(clip2.set_start(v_list[0].duration - padding).crossfadein(-padding))
#
# idx = video_clips[0].duration - padding
# for video in video_clips[1:]:
#     video_fx_list.append(video.set_start(idx).crossfadein(padding))
#     idx += video.duration - padding

# final_clip = concatenate_videoclips(v_list)
# final_clip.write_videofile("data/fade_video.mp4", codec="libx264", fps=24)

dissolve_duration = 0.2

# 첫 번째 클립의 끝 부분을 추출
clip1_end = clip1.subclip(clip1.duration - dissolve_duration, clip1.duration)

# 두 번째 클립의 시작 부분을 추출
clip2_start = clip2.subclip(0, dissolve_duration)

# 두 클립을 겹쳐서 디졸브 효과 적용
dissolve_clip = CompositeVideoClip([clip1_end.set_start(0).set_opacity(0.5).fadeout(dissolve_duration),
                                    clip2_start.set_start(0).set_opacity(0.5).fadein(dissolve_duration, initial_color=None)])

# 디졸브 효과를 포함한 전체 클립
final_clip = concatenate_videoclips([clip1.subclip(0, clip1.duration - dissolve_duration),
                                     dissolve_clip,
                                     clip2.subclip(dissolve_duration, clip2.duration)])
# final_clip = final_clip.without_audio()
# audio = clip1.audio
final_clip = final_clip.set_audio(clip1.audio)
final_clip.write_videofile("data/fade_video.mp4", codec="libx264", fps=24)
