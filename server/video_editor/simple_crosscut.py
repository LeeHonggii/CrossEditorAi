import numpy as np
import cv2
from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip
import dlib
import random
import time

begin_time = time.time()

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
landmark_predictor = dlib.shape_predictor("data/shape_predictor_68_face_landmarks.dat")
face_rec_model = dlib.face_recognition_model_v1("data/dlib_face_recognition_resnet_model_v1.dat")
maxx = max

sclip_list = [VideoFileClip("data/sync_ive_baddie_1.mp4"),
             VideoFileClip("data/sync_ive_baddie_2.mp4"),
             VideoFileClip("data/sync_ive_baddie_3.mp4"),
             VideoFileClip("data/sync_ive_baddie_4.mp4"),
             VideoFileClip("data/sync_ive_baddie_5.mp4"),
             VideoFileClip("data/sync_ive_baddie_6.mp4")]
# random.shuffle(sclip_list)

sclip_rect = [[], [], [], [], [], []]
tclip_list = []
current = 0

iou_threshold = 0.3
simularity_threshold = 0.6
dissolve = 0.0

# init_time = 0
# total_duration = int(sclip_list[0].duration)
# fraction = 0.1
init_time = 20
total_duration = 10
fraction = 0.1
multiply = int(1 / fraction)
t_start = int(init_time * multiply)
t_size = int(total_duration * multiply)
print(f"fraction:{fraction}, multiply:{multiply}, t_size:{t_size}")

# skip_min = 2
# skip_max = 3
# skip_end = skip_max * 2 * multiply
# skip_index = 0
skip_min = 0
skip_max = skip_min
skip_end = skip_min
skip_index = skip_end

switch_count = 0
face_mismatch_count = 0
face_dectection_fail_count = 0
insufficient_iou_count = 0

start_time = init_time
move_x = 0
move_y = 0

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
    current_rect = find_best_rect(current, t)
    max_i = current
    max_iou = 0
    max_rect = (0,0,0,0)
    for i in range(len(sclip_list)):
        if i != current:
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
        frame = sclip_list[current].get_frame(current_time)
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

                if dissolve == 0:
                    # if True:
                    if move_x == 0 and move_y == 0:
                        tclip_list.append(sclip_list[current].subclip(start_time, current_time))
                    else:
                        print(f"move x: {move_x} / move y: {move_y}")
                        temp_clip = sclip_list[current].subclip(start_time, current_time)
                        moved_clip = temp_clip.set_position((move_x, move_y))
                        composite_clip = CompositeVideoClip([moved_clip])
                        # composite_clip = CompositeVideoClip([temp_clip, moved_clip])
                        tclip_list.append(composite_clip)
                        # moved_clip = sclip_list[current].subclip(start_time, current_time).set_position(move_x, move_y)
                        # composite_clip = CompositeVideoClip([video_clip, moved_clip])
                        # composite_clip = CompositeVideoClip([moved_clip])
                        # tclip_list.append(CompositeVideoClip([moved_clip]))
                else:
                    pre_end = sclip_list[current].subclip(current_time - dissolve, current_time)
                    post_start = sclip_list[max_i].subclip(current_time - dissolve, current_time)
                    dissolve_clip = CompositeVideoClip(
                        [pre_end.set_opacity(0.5).fadeout(dissolve),
                         post_start.set_opacity(0.3).fadein(dissolve, initial_color=None)])
                    tclip_list.append(sclip_list[current].subclip(start_time, current_time - dissolve))
                    tclip_list.append(dissolve_clip)
                current = max_i
                start_time = current_time
                skip_end = random.randint(skip_min * multiply, skip_max * multiply)
                skip_index = 0

                print(f"current rect: ({cx}, {cy}, {cw}, {ch}) / next rect: ({ix}, {iy}, {iw}, {ih})")
                print(f"diff w: {cw-iw} / diff w%:{abs(cw-iw)/min(cw,iw)/100:.4f}%")
                print(f"diff h: {ch-ih} / diff w%:{abs(ch-ih)/min(ch,ih)/100:.4f}%")
                print(f"move x: {cx-ix} / move y: {cy-iy}")
                move_x = cx-ix
                move_y = cy-iy
                # move_x = cx-ix - move_x
                # move_y = cy-iy - move_y

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

tclip_list.append(sclip_list[current].subclip(start_time, init_time + total_duration))

# print("final clip", start_time, total_duration)

print(f"switch_count: {switch_count}")
print(f"face_mismatch_count: {face_mismatch_count}")
print(f"face_dectection_fail_count: {face_dectection_fail_count}")
print(f"insufficient_iou_count: {insufficient_iou_count}")

print(len(tclip_list))
for i, clip in enumerate(tclip_list):
    print(f"Clip {i} duration: {clip.duration}")

concatenated_clip = concatenate_videoclips(tclip_list)
if total_duration == int(sclip_list[0].duration):
    final_video = concatenated_clip.set_audio(sclip_list[0].audio)
else:
    final_video = concatenated_clip.set_audio(sclip_list[0].subclip(0, total_duration).audio)

# total_duration
# tclip = sclip_list[0].subclip(0, total_duration)
# final_video = concatenated_clip.set_audio(sclip_list[0].subclip(0, total_duration).audio)
# final_video = concatenated_clip.set_audio(sclip_list[0].audio)

output_path = f'data/simple_video_{multiply:.2f}_{iou_threshold:.2f}_{simularity_threshold:.2f}_{dissolve:.2f}_{random.randint(0, 999):3d}.mp4'
final_video.write_videofile(output_path, codec='libx264', audio_codec='aac')

for i in range(len(sclip_list)):
    sclip_list[i].close()
concatenated_clip.close()
final_video.close()

end_time = time.time()
elapsed_time = end_time - begin_time
minutes = int(elapsed_time // 60)
seconds = elapsed_time % 60
print(f"Execution time: {minutes:d} minutes and {seconds:.2f} seconds")