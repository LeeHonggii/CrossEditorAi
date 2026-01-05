from moviepy.editor import VideoFileClip, CompositeVideoClip, concatenate_videoclips
import numpy as np
import random
import cv2


def make_frame(t):
    line_color = (0, 255, 0)  # Green color
    x1, y1, x2, y2 = line1
    start_point = (x1, y1)
    end_point = (x2, y2)
    frame = clip1.get_frame(t)  # Get the current frame from the video clip
    frame = np.array(frame)  # Convert frame to numpy array
    cv2.line(frame, start_point, end_point, line_color, 3)  # Increase line thickness to 3
    return frame


def make_frame2(t):
    line_color = (0, 255, 0)  # Green color
    x1, y1, x2, y2 = line2
    start_point = (x1, y1)
    end_point = (x2, y2)
    frame = clip2.get_frame(t)  # Get the current frame from the video clip
    frame = np.array(frame)  # Convert frame to numpy array
    cv2.line(frame, start_point, end_point, line_color, 3)  # Increase line thickness to 3
    return frame

file1 = "test_video_4"
file2 = "test_video_1"

vector1 = (1323, 484, 78, 78)
vector2 = (1302, 474, 70, 70)
# vector_test(file1, file2, vector1, vector2)

# def vector_test(file1, file2, vector1, vector2):
x1, y1, w1, h1 = vector1
x2, y2, w2, h2 = vector2
line1 = x1, y1, x1+w1, y1+h1
line2 = x2, y2, x2+w2, y2+h2
# line_list.append(line1)
# line_list.append(line2)

test_path1 = f"data/{file1}.mp4"
test_path2 = f"data/{file2}.mp4"
test_out1 = f"data/{file1}_out.mp4"
test_out2 = f"data/{file2}_out.mp4"
# print(test_path1)
# print(test_path2)
# quit()

clip1 = VideoFileClip(test_path1)
clip2 = VideoFileClip(test_path2)

fclip1 = CompositeVideoClip([clip1.set_make_frame(make_frame)])
fclip1.write_videofile(test_out1, codec='libx264', audio_codec='aac')

fclip2 = CompositeVideoClip([clip2.set_make_frame(make_frame2)])
fclip2.write_videofile(test_out2, codec='libx264', audio_codec='aac')

final_clip = concatenate_videoclips([fclip1, fclip2])
output_path = f'data/vector_test_{random.randint(0, 999):03d}.mp4'
final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')

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
fclip1.close()
fclip2.close()
final_clip.close()


if __name__ == "__main__":
    pass
    # file1 = "test_video_4"
    # file2 = "test_video_1"
    #
    # vector1 = (1253, 243, 164, 164)
    # vector2 = (1197, 205, 234, 234)
    # vector_test(file1, file2, vector1, vector2)


    # line1 = (100, 100, 220, 100)
    # line2 = (120, 120, 200, 140)
    # vector_test(file1, file2, vector1, vector2)
    #
