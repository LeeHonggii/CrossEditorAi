import numpy as np
import cv2
from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

sclip_list = [VideoFileClip("data/sync_ive_baddie_1.mp4"),
             VideoFileClip("data/sync_ive_baddie_2.mp4"),
             VideoFileClip("data/sync_ive_baddie_3.mp4"),
             VideoFileClip("data/sync_ive_baddie_4.mp4"),
             VideoFileClip("data/sync_ive_baddie_5.mp4"),
             VideoFileClip("data/sync_ive_baddie_6.mp4")]
sclip_rect = [[], [], [], [], [], []]

tclip_list = []

current = 0
start_time = 0

# t_size = 30
total_duration = int(sclip_list[0].duration)
fraction = 0.25
multiply = int(1 / fraction)
t_size = total_duration * multiply
print(fraction, multiply, t_size)
iou_threshold = 0.5
skip_time = 2
skip_max = skip_time * multiply
skip_index = skip_max

maxx = max

def detect_faces(i, t):
    current_time = t / multiply
    frame = sclip_list[i].get_frame(current_time)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # moviepy는 RGB, OpenCV는 BGR
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 얼굴 감지
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    sclip_rect[i].append(faces)

# for t in range(int(sclip_list[0].duration)):
for t in range(t_size):
    for i in range (len(sclip_list)):
        print(t/multiply, i)
        detect_faces(i, t)

# for t in range(t_size):
# for i in range(len(sclip_rect)):
#     print(sclip_rect[i])

def find_best_rect(i, t):
    r_list = sclip_rect[i][t]
    # print(len(r_list))
    # print(type(r_list))
    # print(r_list)
    if len(r_list) == 0:
        max_row = (0,0,0,0)
    else:
        products = r_list[:, 2] * r_list[:, 3]
        max_index = np.argmax(products)
        max_row = r_list[max_index]
        # print(max_row)
    return tuple(max_row)

def intersection_over_union(rect1, rect2):
    x1, y1, w1, h1 = rect1
    x2, y2, w2, h2 = rect2

    x1_max = x1 + w1
    y1_max = y1 + h1
    x2_max = x2 + w2
    y2_max = y2 + h2

    inter_x1 = maxx(x1, x2)
    inter_y1 = maxx(y1, y2)
    inter_x2 = min(x1_max, x2_max)
    inter_y2 = min(y1_max, y2_max)
    inter_w = maxx(0, inter_x2 - inter_x1)
    inter_h = maxx(0, inter_y2 - inter_y1)

    inter_area = inter_w * inter_h
    rect1_area = w1 * h1
    rect2_area = w2 * h2
    union_area = rect1_area + rect2_area - inter_area

    iou = inter_area / union_area

    return iou

# for t in range(int(sclip_list[0].duration)):
for t in range(t_size):
    if skip_index < skip_max:
        skip_index += 1
        continue
    # current_time = t // multiply + fraction * (t % multiply)
    current_time = t / multiply
    current_rect = find_best_rect(current, t)
    max_i = current
    max_iou = 0
    for i in range(len(sclip_list)):
        if i != current:
            i_rect = find_best_rect(i, t)
            print(i, t, i_rect)
            if i_rect == (0,0,0,0):
                print(None)
            else:
                i_iou = intersection_over_union(current_rect, i_rect)
                print("iou", i, t, i_iou)
                if i_iou > max_iou:
                    max_i = i
                    max_iou = i_iou

    if max_iou > iou_threshold:
        print("!!!max iou:", max_i, max_iou, "switch to", max_i)
        tclip_list.append(sclip_list[current].subclip(start_time, current_time))
        current = max_i
        start_time = current_time
        skip_index = 0
    else:
        rint(f"Insufficient iou: {max_iou} at {current_time}")

concatenated_clip = concatenate_videoclips(tclip_list)

# 이어붙인 동영상을 파일로 저장
output_path = f'data/opencv_video_{multiply:.2f}_{iou_threshold:.1f}.mp4'
concatenated_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')

# 메모리에서 동영상 클립 제거 (선택 사항)
for i in range(len(sclip_list)):
    sclip_list[i].close()
concatenated_clip.close()
