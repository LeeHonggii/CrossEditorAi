import cv2
from ultralytics import YOLO
import csv
import os
from multiprocessing import Pool, cpu_count

fourcc = cv2.VideoWriter_fourcc(*'mp4v')

def split_data(data):
    faces = []
    bodies = []
    legs = []

    for person in data:
        face = person[:5].tolist()
        body = person[5:12].tolist()
        leg = person[12:16].tolist()

        faces.append(face)
        bodies.append(body)
        legs.append(leg)

    return faces, bodies, legs

def save_to_csv(filename, frame_data):
    headers = [
        'frame_number',
        'face_x0', 'face_y0', 'face_conf0', 'face_x1', 'face_y1', 'face_conf1', 'face_x2', 'face_y2', 'face_conf2', 'face_x3', 'face_y3', 'face_conf3', 'face_x4', 'face_y4', 'face_conf4',
        'body_x5', 'body_y5', 'body_conf5', 'body_x6', 'body_y6', 'body_conf6', 'body_x7', 'body_y7', 'body_conf7', 'body_x8', 'body_y8', 'body_conf8', 'body_x9', 'body_y9', 'body_conf9',
        'body_x10', 'body_y10', 'body_conf10', 'body_x11', 'body_y11', 'body_conf11',
        'leg_x12', 'leg_y12', 'leg_conf12', 'leg_x13', 'leg_y13', 'leg_conf13', 'leg_x14', 'leg_y14', 'leg_conf14', 'leg_x15', 'leg_y15', 'leg_conf15'
    ]

    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        for frame_number, faces, bodies, legs in frame_data:
            for face, body, leg in zip(faces, bodies, legs):
                flattened_row = [frame_number] + [item for sublist in face + body + leg for item in sublist]
                writer.writerow(flattened_row)

def process_video(video_path):
    model = YOLO("yolov8n-pose.pt")
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        # print(f"Error: Could not open video {video_path}.")
        return None

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    video_name = os.path.splitext(os.path.basename(video_path))[0]
    output_video_path = f"{video_name}_output.mp4"
    output_csv_path = f"{video_name}.csv"

    out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))

    frame_number = 0
    frame_data = []

    while cap.isOpened():
        success, frame = cap.read()
        if success:
            results = model.track(frame, conf=0.5,verbose=False)

            if results:
                annotated_frame = results[0].plot()
                data = results[0].keypoints.data
                faces, bodies, legs = split_data(data)

                frame_data.append((frame_number, faces, bodies, legs))
                out.write(annotated_frame)
                # cv2.imshow("YOLOv8 Tracking", annotated_frame)
            # else:
                # print(f"Warning: No results found for frame {frame_number}.")

            frame_number += 1

            # if cv2.waitKey(1) & 0xFF == ord("q"):
            #     break
        else:
            break

    cap.release()
    out.release()
    # cv2.destroyAllWindows()

    save_to_csv(output_csv_path, frame_data)
    # print(f"Processed {video_path} and saved to {output_csv_path} and {output_video_path}.")

    return output_csv_path

def process_videos(video_files):
    with Pool(processes=cpu_count()) as pool:
        csv_files = pool.map(process_video, video_files)
    return {video_files[i]: csv_files[i] for i in range(len(video_files)) if csv_files[i] is not None}
