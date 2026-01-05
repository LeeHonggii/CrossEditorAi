import numpy as np
from moviepy.editor import VideoFileClip
import cv2
import dlib
import json
import random
import time

begin_time = time.time()

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
landmark_predictor = dlib.shape_predictor("data/shape_predictor_68_face_landmarks.dat")
face_rec_model = dlib.face_recognition_model_v1("data/dlib_face_recognition_resnet_model_v1.dat")
maxx = max

parameter = {
   "meta_info" : {
      "num_stream": 6,
      "metric": "time",         # "time" or "frame" default frame
      "vector": "wh",           #"wh" or "point" defualt points
      "rotation": "NO",         #"YES" or "NO", force surpress rotation for debugging. default YES
      "frame_rate": 29.97,
      "num_frames": 0,         # (2 * 60 + 40 + 0 / 60) * 29.97,
      "init_time": 0,          # start at somewhere in the middle
      "duration": 160,          # 2 * 60 + 40 + 0 / 60,
      "num_vector_pair": 3,    # at least 1, maximum 3 recommended
      "num_cross": 15,         # number of crossedit
      "first_stream": 0,       # first stream can be any integer between 0 and 5
      "folder_path": "data/"
   },
   "streams": [
      {
         "file": "sync_ive_baddie_1.mp4",
         "start": 0,
         "end": 0
      },
      {
         "file": "sync_ive_baddie_2.mp4",
         "start": 0,
         "end": 0
      },
      {
         "file": "sync_ive_baddie_3.mp4",
         "start": 0,
         "end": 0
      },
      {
         "file": "sync_ive_baddie_4.mp4",
         "start": 0,
         "end": 0
      },
      {
         "file": "sync_ive_baddie_5.mp4",
         "start": 0,
         "end": 0
      },
      {
         "file": "sync_ive_baddie_6.mp4",
         "start": 0,
         "end": 0
      }
   ],
   "cross_points": [
   ],
   # "scene_list": [
   #    [100, 500, 1000, 1500],    # scene list for the stream 0
   #    [200, 500, 1500, 3000],    # scene list for the stream 1
   #    [100, 510, 1000, 1500],    # scene list for the stream 2
   #    [400, 500, 1000, 1500],    # scene list for the stream 3
   #    [150, 500, 1000, 1500],    # scene list for the stream 4
   #    [800, 500, 1000, 1500]     # scene list for the stream 5
   # ]
}

num_stream = parameter["meta_info"]["num_stream"]
sclip_list = []

for i in range(num_stream):
    sclip_list.append(VideoFileClip(parameter["meta_info"]["folder_path"] + parameter["streams"][i]["file"]))
    print(parameter["meta_info"]["folder_path"] + parameter["streams"][i]["file"])
    if parameter["streams"][i]["start"] != 0 or parameter["streams"][i]["end"] != 0:
        sclip_list[-1].subclip(parameter["streams"][i]["start"], parameter["streams"][i]["end"])
        print("ALERT!!!")


sclip_rect = [[] for _ in range(num_stream)]        # [[], [], [], [], [], []]
cross_list = []
# current_stream = random.randrange(num_stream)
current_stream = parameter["meta_info"]["first_stream"]    # 0

# iou_threshold = 0.6
# simularity_threshold = 0.6
iou_threshold = 0.7
simularity_threshold = 0.6

parameter["meta_info"]["init_time"] = 0
# parameter["meta_info"]["duration"] = 10
parameter["meta_info"]["duration"] = int(sclip_list[0].duration)
init_time = parameter["meta_info"]["init_time"]
total_duration = parameter["meta_info"]["duration"]
fraction = 0.05
multiply = int(1 / fraction)
t_start = int(init_time * multiply)
t_size = int(total_duration * multiply)
print(f"fraction:{fraction}, multiply:{multiply}, t_size:{t_size}")

skip_min = 1    # sec
skip_max = 1    # sec
skip_end = int(skip_min * multiply)  # fraction
skip_index = skip_end                # fraction
# skip_min = 2
# skip_max = skip_min
# skip_end = skip_min
# skip_index = skip_end

switch_count = 0
face_mismatch_count = 0
face_dectection_fail_count = 0
insufficient_iou_count = 0


def detect_faces(i, t):
    current_time = t / multiply
    frame = sclip_list[i].get_frame(current_time)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # moviepy는 RGB, OpenCV는 BGR
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 얼굴 감지
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    sclip_rect[i].append(faces)


# for t in range(int(sclip_list[0].duration)):
for t in range(t_start, t_size + t_start):
    print(f"time{t / multiply: .2f}")
    for i in range (len(sclip_list)):
        # print(t/multiply, i)
        detect_faces(i, t)


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
    if skip_index < skip_end:
        skip_index += 1
        continue
    # current_time = t // multiply + fraction * (t % multiply)
    current_time = init_time + t / multiply
    current_rect = find_best_rect(current_stream, t)
    max_i = current_stream
    max_iou = 0
    max_rect = (0,0,0,0)
    for i in range(len(sclip_list)):
        if i != current_stream:
            i_rect = find_best_rect(i, t)
            # print(i, t, i_rect)
            if i_rect == (0,0,0,0):
                # print(None)
                pass
            else:
                i_iou = intersection_over_union(current_rect, i_rect)
                if i_iou > max_iou:
                    # print("max iou", i, t, i_iou)
                    max_i = i
                    max_iou = i_iou
                    max_rect = i_rect

    if max_iou > iou_threshold:
        frame = sclip_list[current_stream].get_frame(current_time)
        cx, cy, cw, ch = current_rect
        dlib_rect = dlib.rectangle(int(cx), int(cy), int(cx + cw), int(cy + ch))
        landmarks = landmark_predictor(frame, dlib_rect)
        current_face_embedding = np.array(face_rec_model.compute_face_descriptor(frame, landmarks))

        frame = sclip_list[max_i].get_frame(current_time)
        ix, iy, iw, ih = max_rect
        dlib_rect = dlib.rectangle(int(ix), int(iy), int(ix + iw), int(iy + ih))
        landmarks = landmark_predictor(frame, dlib_rect)
        max_face_embedding = np.array(face_rec_model.compute_face_descriptor(frame, landmarks))

        if current_face_embedding is not None and max_face_embedding is not None:
            distance = np.linalg.norm(current_face_embedding - max_face_embedding)

            if distance < simularity_threshold:
                print(f"!!!SWITCH to {max_i} / max iou: {max_iou:.2f} / simularity: {distance:.2f} at {current_time}")

                cross_point = {}
                cross_point["time_stamp"] = current_time
                cross_point["next_stream"] = max_i
                cross_point["vector_pairs"] = []
                vector_pair = {}
                vector_pair["vector1"] = [int(cx), int(cy), int(cw), int(ch)]
                vector_pair["vector2"] = [int(ix), int(iy), int(iw), int(ih)]
                cross_point["vector_pairs"].append(vector_pair)
                cross_list.append(cross_point)

                # if move_x == 0 and move_y == 0:
                #     tclip_list.append(sclip_list[current_stream].subclip(start_time, current_time))
                # else:
                #     print(f"move x: {move_x} / move y: {move_y}")
                #     temp_clip = sclip_list[current_stream].subclip(start_time, current_time)
                #     moved_clip = temp_clip.set_position((move_x, move_y))
                #     composite_clip = CompositeVideoClip([moved_clip])
                #     # composite_clip = CompositeVideoClip([temp_clip, moved_clip])
                #     tclip_list.append(composite_clip)
                #     # moved_clip = sclip_list[current_stream].subclip(start_time, current_time).set_position(move_x, move_y)
                #     # composite_clip = CompositeVideoClip([video_clip, moved_clip])
                #     # composite_clip = CompositeVideoClip([moved_clip])
                #     # tclip_list.append(CompositeVideoClip([moved_clip]))

                current_stream = max_i
                start_time = current_time
                skip_end = random.randint(skip_min * multiply, skip_max * multiply)
                skip_index = 0

                # print(f"current rect: ({cx}, {cy}, {cw}, {ch}) / next rect: ({ix}, {iy}, {iw}, {ih})")
                # print(f"diff w: {cw-iw} / diff w%:{abs(cw-iw)/min(cw,iw)/100:.4f}%")
                # print(f"diff h: {ch-ih} / diff w%:{abs(ch-ih)/min(ch,ih)/100:.4f}%")
                # print(f"move x: {cx-ix} / move y: {cy-iy}")
                # move_x = cx-ix
                # move_y = cy-iy
                ## move_x = cx-ix - move_x
                ## move_y = cy-iy - move_y

                switch_count += 1
            else:
                print(f"Face mismatch / max iou: {max_iou:.2f} / simularity: {distance:.2f} at {current_time}")
                face_mismatch_count += 1
        else:
            print(f"Face dectection fail / max iou: {max_iou:.2f} / simularity: {distance:.2f} at {current_time}")
            face_dectection_fail_count += 1

    else:
        # print(f"Insufficient iou: {max_iou:.2f} at {current_time}")
        insufficient_iou_count += 1

parameter["cross_points"] = cross_list
parameter["meta_info"]["num_cross"] = len(cross_list)

with open("data/scene_list.json", "r", encoding="utf-8") as file:
    scene_file = file.read()
scene_json = json.loads(scene_file)
parameter["scene_list"] = scene_json["scene_list"]

json_dump = json.dumps(parameter, ensure_ascii=False, indent=4)

# 파일에 저장
with open("data/output.json", "w", encoding="utf-8") as file:
    file.write(json_dump)

# for i in range(len(sclip_list)):
#     sclip_list[i].close()

print(f"switch_count: {switch_count}")
print(f"face_mismatch_count: {face_mismatch_count}")
print(f"face_dectection_fail_count: {face_dectection_fail_count}")
print(f"insufficient_iou_count: {insufficient_iou_count}")

detect_end_time = time.time()
detect_time = detect_end_time - begin_time
minutes = int(detect_time // 60)
seconds = detect_time % 60
print(f"Detection time: {minutes:d} minutes and {seconds:.2f} seconds")

