import json
import matplotlib.pyplot as plt
import cv2
import os


def draw_vector(image, vector, color):
    """ Draw a vector on the image """
    x1, y1, x2, y2 = vector
    if x1 != 0.0 or y1 != 0.0 or x2 != 0.0 or y2 != 0.0:
        cv2.line(image, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
        cv2.circle(image, (int(x1), int(y1)), 5, color, -1)
        cv2.circle(image, (int(x2), int(y2)), 5, color, -1)


def visualize_vectors(json_file, video_file_mapping, output_folder='output'):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    with open(json_file, 'r') as f:
        data = json.load(f)

    cross_points = data['cross_points']
    video_files = data['streams']

    for i, point in enumerate(cross_points):
        time_stamp = point['time_stamp']
        next_stream = point['next_stream']
        vector_pairs = point['vector_pairs'][0]

        vector1 = vector_pairs['vector1']
        vector2 = vector_pairs['vector2']

        video_file_before = video_files[i % len(video_files)]['file']
        video_file_after = video_files[next_stream]['file']

        cap_before = cv2.VideoCapture(video_file_before)
        cap_after = cv2.VideoCapture(video_file_after)

        cap_before.set(cv2.CAP_PROP_POS_MSEC, time_stamp * 1000)
        cap_after.set(cv2.CAP_PROP_POS_MSEC, time_stamp * 1000)

        ret_before, frame_before = cap_before.read()
        ret_after, frame_after = cap_after.read()

        if not (ret_before and ret_after):
            continue

        draw_vector(frame_before, vector1, (0, 255, 0))
        draw_vector(frame_after, vector2, (0, 0, 255))

        combined_image = cv2.hconcat([frame_before, frame_after])

        output_path = os.path.join(output_folder, f"frame_{i:04d}.png")
        cv2.imwrite(output_path, combined_image)

        plt.figure(figsize=(12, 6))
        plt.imshow(cv2.cvtColor(combined_image, cv2.COLOR_BGR2RGB))
        plt.title(f"Frame at {time_stamp:.2f}s")
        plt.axis('off')
        plt.savefig(os.path.join(output_folder, f"frame_{i:04d}_plt.png"))
        plt.close()

        cap_before.release()
        cap_after.release()


if __name__ == "__main__":
    json_file = 'output_pose.json'
    video_file_mapping = {
        "ive_baddie_1.csv": "ive_baddie_1.mp4",
        "ive_baddie_2.csv": "ive_baddie_2.mp4",
        "ive_baddie_3.csv": "ive_baddie_3.mp4",
        "ive_baddie_4.csv": "ive_baddie_4.mp4",
        "ive_baddie_5.csv": "ive_baddie_5.mp4"
    }

    visualize_vectors(json_file, video_file_mapping)
