from moviepy.editor import VideoFileClip, CompositeVideoClip, concatenate_videoclips
import numpy as np
import cv2

clip = VideoFileClip("data/short_video.mp4")
duration = clip.duration

current = [0]
line_list = []


def make_frame(t):
    # global current
    # print(current[0])
    if current[0] == 0:
        line_color = (0, 255, 0)  # Green color
        # start_point = (100, 100)
        # end_point = (220, 100)
        x1, y1, x2, y2 = line_list[0]
        # start_point = (x1, y1)
        # end_point = (x2, y2)
    else:
        line_color = (0, 255, 0)  # Green color
        # line_color = (255, 0, 0)
        # start_point = (130, 150)
        # end_point = (230, 150)
        x1, y1, x2, y2 = line_list[1]
        # start_point = (x1, y1)
        # end_point = (x2, y2)
    start_point = (x1, y1)
    end_point = (x2, y2)
    frame = clip.get_frame(t)  # Get the current frame from the video clip
    frame = np.array(frame)  # Convert frame to numpy array
    cv2.line(frame, start_point, end_point, line_color, 3)  # Increase line thickness to 3
    return frame


def prepare_sample(line1, line2):
    line_list.append(line1)
    line_list.append(line2)

    current[0] = 0

    clip1 = CompositeVideoClip([clip.subclip(0, duration/2).set_make_frame(make_frame)])
    clip1.write_videofile("data/line1.mp4", codec='libx264', audio_codec='aac')

    current[0] = 1

    clip2 = CompositeVideoClip([clip.subclip(duration/2, duration).set_make_frame(make_frame)])
    clip2.write_videofile("data/line2.mp4", codec='libx264', audio_codec='aac')

    # clip3 = VideoFileClip("data/line1.mp4")
    #
    # final_clip = concatenate_videoclips([clip3, clip2])
    #
    # final_clip.write_videofile("data/line0.mp4", codec='libx264', audio_codec='aac')
    #
    # clip3.close()
    # final_clip.close()
    clip1.close()
    clip2.close()


if __name__ == "__main__":
    line1 = (100, 100, 220, 100)
    line2 = (120, 120, 200, 140)
    prepare_sample(line1, line2)

#
# # from moviepy.editor import VideoFileClip, CompositeVideoClip
# # import numpy as np
# # import cv2
# #
# # clip = VideoFileClip("data/video.mp4")
# #
# # # 초기 시작점과 끝점
# # start_point = (100, 100)
# # end_point = (200, 200)
# # line_color = (0, 255, 0)  # Green color
# #
# # # 라인의 이동 속도 및 방향
# # movement_speed = 10  # Adjust as needed
# #
# #
# # def make_frame(t):
# #     # 현재 시작점과 끝점 계산
# #     current_start_point = (start_point[0] + int(movement_speed * t), start_point[1])
# #     current_end_point = (end_point[0] + int(movement_speed * t), end_point[1])
# #
# #     frame = clip.get_frame(t)  # Get the current frame from the video clip
# #     frame = np.array(frame)  # Convert frame to numpy array
# #     cv2.line(frame, current_start_point, current_end_point, line_color, 3)  # Draw line on the frame
# #     return frame
# #
# #
# # final_clip = CompositeVideoClip([clip.set_make_frame(make_frame)])
# #
# # final_clip.write_videofile("data/line_video.mp4", codec='libx264', audio_codec='aac')

# import numpy as np
# import cv2
# from moviepy.editor import VideoFileClip, CompositeVideoClip, concatenate_videoclips
#
# clip = VideoFileClip("data/video.mp4")
# duration = clip.duration
#
# def make_frame(t, current):
#     if current == 0:
#         line_color = (0, 255, 0)  # Green color
#         start_point = (100, 100)
#         end_point = (200, 100)
#         current += 1
#     else:
#         line_color = (255, 0, 0)
#         start_point = (130, 150)
#         end_point = (230, 150)
#     frame = clip.get_frame(t)  # Get the current frame from the video clip
#     frame = np.array(frame)  # Convert frame to numpy array
#     cv2.line(frame, start_point, end_point, line_color, 3)  # Increase line thickness to 3
#     return frame, current
#
# current = 0
# def make_frame_wrapper(t):
#     global current
#     frame, current = make_frame(t, current)
#     return frame
#
# # Clip1 with green and red lines
# clip1 = CompositeVideoClip([clip.subclip(0, duration/2).fl_image(make_frame_wrapper)])
# clip1.write_videofile("data/line1.mp4", codec='libx264', audio_codec='aac')
#
# # Reset current for second part
# current = 0
# # Clip2 with green and red lines
# clip2 = CompositeVideoClip([clip.subclip(duration/2, duration).fl_image(make_frame_wrapper)])
# clip2.write_videofile("data/line2.mp4", codec='libx264', audio_codec='aac')
#
# # Concatenate the two clips
# final_clip = concatenate_videoclips([clip1, clip2])
# final_clip.write_videofile("data/line0.mp4", codec='libx264', audio_codec='aac')