import numpy as np
from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip
import json
import random
import time
from adjust import get_adjusted_clip, vector_interpolation, adjust_vector, find_in_between


begin_time = time.time()

json_file = "data/output-full2.json"
with open(json_file, "r", encoding="utf-8") as file:
    json_string_from_file = file.read()

parameter = json.loads(json_string_from_file)

num_stream = parameter["meta_info"]["num_stream"]
# frame_rate = parameter["meta_info"]["frame_rate"]
init_time = parameter["meta_info"]["init_time"]
total_duration = parameter["meta_info"]["duration"]
current_stream = parameter["meta_info"]["first_stream"]
num_cross = parameter["meta_info"]["num_cross"]
folder_path = parameter["meta_info"]["folder_path"]
cross_list = parameter["cross_points"]
scene_list = parameter["scene_list"]
stream_list = []
target_list = []


streams = parameter["streams"]
if num_stream != len(streams):
    print(f"ALERT!!! invalid stream number. num_stream: {num_stream} vs len(parameter[\"streams\"]): {len(streams)}")


def load_video_clip(filename):
    try:
        clip = VideoFileClip(filename)
        print(filename)
        return clip
    except FileNotFoundError:
        print(f"FileNotFoundError: {filename}")
    except OSError as e:
        print(f"OSError: {e}")
    return None


for stream in streams:
    filename = folder_path + stream["file"]
    clip = load_video_clip(filename)
    if clip:
        stream_list.append(clip)
        # if round(clip.fps, 2) != frame_rate:
        #     print(f"ALERT!!! invalide frame rate in file \"{filename}\" {clip.fps} vs parameter[\"frame_rate\"]: {frame_rate}")
        # else:
        #     print(filename)

        if stream["start"] != 0 or stream["end"] != 0:
            stream_list[-1].subclip(stream["start"], stream["end"])
            print("ALERT!!! we do not support subclip so far")

# clip = stream_list[4].subclip(5.1, 9.5)
# output_path = f'data/test_video_4.mp4'
# clip.write_videofile(output_path, codec='libx264', audio_codec='aac')
#
# clip = stream_list[1].subclip(9.5, 12.3)
# output_path = f'data/test_video_1.mp4'
# clip.write_videofile(output_path, codec='libx264', audio_codec='aac')
# quit()

if num_stream != len(stream_list):
    print(f"ALERT!!! invalid stream number. num_stream: {num_stream} vs len(stream_list): {len(stream_list)}")
    num_stream = len(stream_list)    # can we continue?


frame_rate = stream_list[0].fps
for i in range(num_stream):
    if i == 0:
        frame_rate = stream_list[i].fps
    elif frame_rate != stream_list[i].fps and parameter["meta_info"]["metric"] == "frame":
        print(f"ALERT!!! different frame stream 0: {frame_rate} vs stream {i}: stream_list[i].fps")
        quit()

if "metric" not in parameter["meta_info"] or parameter["meta_info"]["metric"] == "frame":
    frame_gap = 1 / frame_rate
    print("==================")
    for cross in cross_list:
        cross["time_stamp"] = cross["frame_id"] * frame_gap


if json_file not in ["data/output.json", "data/output-8.json", "data/output-30.json", "data/output-60.json", "data/output-full.json", "data/output-full1.json", "data/output-full2.json"]:
    print("VECTOR Conversion to W/H")
    for i in range(len(cross_list)):
        x1, y1, x12, y12 = cross_list[i]["vector_pairs"][0]["vector1"]
        x2, y2, x22, y22 = cross_list[i]["vector_pairs"][0]["vector2"]
        cross_list[i]["vector_pairs"][0]["vector1"] = [x1, y1, x12-x1, y12-y1]
        cross_list[i]["vector_pairs"][0]["vector2"] = [x2, y2, x22-x2, y22-y2]
        # cross_list[i]["vector_pairs"][0]["vector1"] = [x1, y1, x12-x1, 0]
        # cross_list[i]["vector_pairs"][0]["vector2"] = [x2, y2, x22-x2, 0]
        if x12-x1 < 0:
            print(f"!!!ALERT wrong coordination x12 is smaller than x1. x1({x1}), y1({y1}), x12-x1({x12-x1}), y12-y1({y12-y1})")
            quit()


last_cross = {
    "time_stamp": init_time + total_duration,
    "next_stream": cross_list[-1]["next_stream"],
    "vector_pairs": [
        {
            "vector1": [0, 0, 0, 0],
            "vector2": [0, 0, 0, 0]
        }
    ]
}
cross_list.append(last_cross)
if num_cross + 1 != len(cross_list):
    print("ALERT!!! invalid cross number:", num_cross)
    # num_cross = len(cross_list) + 1
else:
    num_cross += 1
# print(cross_list)

if json_file not in ["data/output-jh5.json", "data/output-jh6.json"]:
    print("LOADING extra scene json")
    with open("data/scene_list.json", "r", encoding="utf-8") as file:
        scene_file = file.read()
    scene_json = json.loads(scene_file)
    scene_list = scene_json["scene_list"]
# print(scene_list)
# # for j in range(num_stream):
# for j in range(1):
#     begin = 0
#     for i in range(len(scene_list[j])):
#         end = scene_list[j][i]
#         print(i, j, begin, end)
#         clip = stream_list[j].subclip(begin, end)
#         output_path = f'data/scene_test_{j}_{i}_{end:.4f}.mp4'
#         clip.write_videofile(output_path, codec='libx264', audio_codec='aac')
#         begin = end
# quit()


start_time = init_time
# move_x = 0
# move_y = 0
prev_vector = [0, 0, 0, 0]
curr_vector = [0, 0, 0, 0]
prev_stream = num_stream
num_prop_pre = 0
num_prop_post = 0
num_scen_pre = 0
num_scen_post = 0
max_prop = 0

for i in range(num_cross):
    current_time = cross_list[i]["time_stamp"]

    if prev_vector == curr_vector:
        clip = stream_list[current_stream].subclip(start_time, current_time)
        print(f"{len(target_list)}th clip added without change. stream: {current_stream}, start: {start_time:.2f}, end: {current_time:.2f}, cv: {prev_vector}, nv: {curr_vector}")
        target_list.append(clip)
        prev_vector = cross_list[i]["vector_pairs"][0]["vector1"]
    else:
        if len(target_list) == 0 or prev_stream == num_stream:
            print("ALERT!!! no more prev clip or prev_stream")
            quit()

        print(f"time a {start_time} pre: pv {prev_vector}, cv {curr_vector}")
        intr_vector = vector_interpolation(stream_list[current_stream], prev_vector, curr_vector)
        print(f"time a {start_time} post: iv {intr_vector}, pv {prev_vector}, cv {curr_vector}")

        if prev_vector != intr_vector:
            prev_clip = target_list.pop()
            prev_start = start_time - prev_clip.duration
            # print(f"prev_start: {prev_start}")
            scenes_in_between = find_in_between(scene_list[prev_stream], prev_start, start_time)
            if len(scenes_in_between) == 0:
                prev_clip = get_adjusted_clip(prev_clip, intr_vector, prev_vector)
                print(f"{len(target_list)}th clip re-added with adjust. stream: {prev_stream}, start: {prev_start:.2f}, end: {start_time:.2f}, iv: {intr_vector}, pv: {prev_vector}")
                target_list.append(prev_clip)
                num_prop_pre += 1
            else:
                # print(scenes_in_between)
                scene_time = scenes_in_between[-1]
                nochange_clip = prev_clip.subclip(0, scene_time - prev_start)
                print(f"{len(target_list)}th clip 1st part re-added without change. stream: {prev_stream}, start: {prev_start:.2f}, end: {scene_time:.2f}")
                target_list.append(nochange_clip)

                changed_clip = prev_clip.subclip(scene_time - prev_start, prev_clip.duration)
                changed_clip = get_adjusted_clip(changed_clip, intr_vector, prev_vector)
                print(f"{len(target_list)}th clip 2nd part re-added with adjust. stream: {prev_stream}, start: {scene_time:.2f}, end: {start_time:.2f}, iv: {intr_vector}, pv: {prev_vector}")
                target_list.append(changed_clip)
                num_scen_pre += 1

        curr_clip = stream_list[current_stream].subclip(start_time, current_time)
        if curr_vector == intr_vector:
            print(f"{len(target_list)}th clip added without change. stream: {current_stream}, start: {start_time:.2f}, end: {current_time:.2f}, cv: {prev_vector}, nv: {curr_vector}")
            target_list.append(curr_clip)
            prev_vector = cross_list[i]["vector_pairs"][0]["vector1"]
        else:
            scenes_in_between = find_in_between(scene_list[current_stream], start_time, current_time)
            # print(scenes_in_between)
            if len(scenes_in_between) == 0:
                curr_clip = get_adjusted_clip(curr_clip, intr_vector, curr_vector)
                print(f"{len(target_list)}th clip added with adjust. stream: {current_stream}, start: {start_time:.2f}, end: {current_time:.2f}, iv: {intr_vector}, cv: {curr_vector}")
                target_list.append(curr_clip)
                # print(target_list)
                num_prop_post += 1
                # prev_vector = cross_list[i]["vector_pairs"][0]["vector1"]
                old_prev_vector = prev_vector
                raw_prev_vector = cross_list[i]["vector_pairs"][0]["vector1"]
                prev_vector = adjust_vector(old_prev_vector, curr_vector, raw_prev_vector)
                print(f"new_prev_vector{prev_vector}, raw_prev_vector{raw_prev_vector}, old_prev_vector{old_prev_vector}, curr_vector{curr_vector}")
            else:
                # print(scenes_in_between)
                scene_time = scenes_in_between[0]

                changed_clip = curr_clip.subclip(0, scene_time - start_time)
                changed_clip = get_adjusted_clip(changed_clip, intr_vector, curr_vector)
                print(f"{len(target_list)}th clip 1st part added with adjust. stream: {current_stream}, start: {start_time:.1f}, end: {scene_time:.2f}, iv: {intr_vector}, cv: {curr_vector}")
                target_list.append(changed_clip)

                nochange_clip = curr_clip.subclip(scene_time - start_time, curr_clip.duration)
                print(f"{len(target_list)}th clip 2nd part added without change. stream: {current_stream}, start: {scene_time:.2f}, end: {current_time:.2f}")
                target_list.append(nochange_clip)
                num_scen_post += 1
                prev_vector = cross_list[i]["vector_pairs"][0]["vector1"]

    start_time = current_time
    prev_stream = current_stream
    current_stream = cross_list[i]["next_stream"]
    # prev_vector = cross_list[i]["vector_pairs"][0]["vector1"]
    curr_vector = cross_list[i]["vector_pairs"][0]["vector2"]


print(f"num_prop_pre: {num_prop_pre}")
print(f"num_prop_post: {num_prop_post}")
print(f"num_scen_pre: {num_scen_pre}")
print(f"num_scen_post: {num_scen_post}")
print(f"max_prop: {max_prop}")

print(len(target_list))
for i, clip in enumerate(target_list):
    print(f"Clip {i} duration: {clip.duration}")
# quit()
concatenated_clip = concatenate_videoclips(target_list)
if total_duration == int(stream_list[0].duration):
    final_video = concatenated_clip.set_audio(stream_list[0].audio)
else:
    final_video = concatenated_clip.set_audio(stream_list[0].subclip(0, total_duration).audio)

output_path = f'data/simple_video_{random.randint(0, 999):03d}.mp4'
final_video.write_videofile(output_path, codec='libx264', audio_codec='aac')

for i in range(len(stream_list)):
    stream_list[i].close()
concatenated_clip.close()
final_video.close()

end_time = time.time()
elapsed_time = end_time - begin_time
minutes = int(elapsed_time // 60)
seconds = elapsed_time % 60
print(f"Execution time: {minutes:d} minutes and {seconds:.2f} seconds")