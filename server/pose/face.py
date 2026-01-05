import cv2
import numpy as np
import os
from insightface.app import FaceAnalysis
import csv
from collections import defaultdict, deque
from multiprocessing import Pool, cpu_count

def initialize_face_analysis():
    app = FaceAnalysis(allowed_modules=["detection", "landmark_2d_106"], providers=["CUDAExecutionProvider"])
    app.prepare(ctx_id=0, det_size=(640, 640))
    return app

def process_video_frames(video_path):
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"No file found at {video_path}")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise Exception("Failed to open video file.")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps else 0

    app = initialize_face_analysis()

    window_name = "Video"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    line1_x = int(width * 0.35)
    line2_x = int(width * 0.65)
    line1_y = int(height * 0.25)
    line2_y = int(height * 0.6)
    target_x = (line1_x + line2_x) // 2
    target_y = (line1_y + line2_y) // 2

    frame_count = 0
    face_positions = []
    face_recognitions = []
    eye_endpoint = []

    while frame_count < total_frames:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % 5 != 0:
            continue
        display_frame = frame.copy()

        cv2.line(display_frame, (line1_x, 0), (line1_x, height), (255, 255, 0), 2)
        cv2.line(display_frame, (line2_x, 0), (line2_x, height), (255, 255, 0), 2)
        cv2.line(display_frame, (0, line1_y), (width, line1_y), (255, 255, 0), 2)
        cv2.line(display_frame, (0, line2_y), (width, line2_y), (255, 255, 0), 2)

        best_face = None
        largest_face = None
        largest_face_size = 0  # To track the largest face size

        faces = app.get(frame)
        for face in faces:
            bbox = face["bbox"].astype(int)
            face_size = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
            # Update largest face if this face is bigger
            if face_size > largest_face_size:
                largest_face_size = face_size
                largest_face = face

            face_center_x = bbox[0] + (bbox[2] - bbox[0]) // 2
            face_center_y = bbox[1] + (bbox[3] - bbox[1]) // 2

            if (
                line1_x <= face_center_x <= line2_x
                and line1_y <= face_center_y <= line2_y
            ):
                distance = abs(face_center_x - target_x) + abs(face_center_y - target_y)
                if best_face is None or distance < best_face[1]:
                    best_face = (face, distance)

        if best_face is None and largest_face is not None:
            best_face = (
                largest_face,
                0,
            )  # Use the largest face if no face found in area

        if best_face:
            face = best_face[0]
            bbox = face["bbox"].astype(int)
            cv2.rectangle(
                display_frame,
                (bbox[0], bbox[1]),
                (bbox[2], bbox[3]),
                (0, 255, 0),
                2,
            )
            if "landmark_2d_106" in face:
                lmk = face["landmark_2d_106"]
                lmk = np.round(lmk).astype(np.int64)
                for point in lmk:
                    cv2.circle(
                        display_frame, tuple(point), 2, (0, 0, 255), -1, cv2.LINE_AA
                    )
                current_frame_positions = [
                    (bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1])
                ]
                current_frame_face_data = [lmk.tolist()]
                eye_point1 = tuple(lmk[35])
                eye_point2 = tuple(lmk[93])
                current_frame_eye_data = [(eye_point1, eye_point2)]

                face_positions.append(current_frame_positions)
                eye_endpoint.append(current_frame_eye_data)
                face_recognitions.append(current_frame_face_data)

        else:
            # Append zeros if no face is detected
            # Ensure that the structure matches the expected unpacking structure in CSV writing.
            face_positions.append(
                [(0, 0, 0, 0)]
            )  # Enclose in an additional list to match structure
            eye_endpoint.append([((0, 0), (0, 0))])  # Use tuple of tuples
            face_recognitions.append([[]])  # This already matches expected structure

        cv2.imshow(window_name, display_frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    return video_path, duration, face_positions, eye_endpoint

def save_results_to_csv(results):
    for result in results:
        video_path, duration, face_positions, eye_endpoint = result
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        output_csv = f"output_{base_name}.csv"

        with open(output_csv, "w", newline="") as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(["frame", "x", "y", "w", "h", "eye_point1", "eye_point2"])
            for i, (positions, eye_points) in enumerate(zip(face_positions, eye_endpoint)):
                for position, eye_point in zip(positions, eye_points):
                    x, y, w, h = position  # Unpack position
                    eye_point1, eye_point2 = eye_point  # Unpack eye points
                    csvwriter.writerow([i * 5, x, y, w, h, eye_point1, eye_point2])

def process_video_multiprocessing(video_files):
    with Pool(cpu_count()) as pool:
        results = pool.map(process_video_frames, video_files)
    save_results_to_csv(results)
    return results

def intersection_over_union(x1, y1, w1, h1, x2, y2, w2, h2):
    x1_max = x1 + w1
    y1_max = y1 + h1
    x2_max = x2 + w2
    y2_max = y2 + h2

    inter_x1 = max(x1, x2)
    inter_y1 = max(y1, y2)
    inter_x2 = min(x1_max, x2_max)
    inter_y2 = min(y1_max, y2_max)

    inter_w = max(0, inter_x2 - inter_x1)
    inter_h = max(0, inter_y2 - inter_y1)

    inter_area = inter_w * inter_h
    rect1_area = w1 * h1
    rect2_area = w2 * h2
    union_area = rect1_area + rect2_area - inter_area

    if union_area == 0:
        return 0.0  # Return 0 IOU to indicate no overlap or undefined case

    iou = inter_area / union_area
    return iou

def load_csv_data(file_path):
    face_positions = []
    eye_endpoints = []
    with open(file_path, "r") as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)  # Skip header
        for row in csvreader:
            video_path, duration, frame, x, y, w, h, eye_point1, eye_point2 = row
            face_positions.append([(int(x), int(y), int(w), int(h))])
            eye_endpoints.append(
                [
                    (
                        (
                            int(eye_point1[1:-1].split(", ")[0]),
                            int(eye_point1[1:-1].split(", ")[1]),
                        ),
                        (
                            int(eye_point2[1:-1].split(", ")[0]),
                            int(eye_point2[1:-1].split(", ")[1]),
                        ),
                    )
                ]
            )
    return face_positions, eye_endpoints

def find_matching_faces(csv_files, THRESHOLD = 0.6):
    all_face_positions = []
    all_eye_endpoints = []
    for csv_file in csv_files:
        face_positions, eye_endpoints = load_csv_data(csv_file)
        all_face_positions.append(face_positions)
        all_eye_endpoints.append(eye_endpoints)

    matched_faces = []
    min_length = min(len(positions) for positions in all_face_positions)
    last_matched_index = 0  # Track the last matched file index

    for frame_index in range(min_length):
        frame_faces = [
            face_positions[frame_index] for face_positions in all_face_positions
        ]
        frame_eyes = [eye_endpoints[frame_index] for eye_endpoints in all_eye_endpoints]

        if not all(frame_eyes):
            continue  # Skip frames without valid eye endpoint data

        current_frame = frame_index * 5

        # Re-arrange faces to start matching from the last matched index
        arranged_faces = (
            frame_faces[last_matched_index:] + frame_faces[:last_matched_index]
        )
        arranged_eyes = (
            frame_eyes[last_matched_index:] + frame_eyes[:last_matched_index]
        )

        face_pairs = []
        for i, faces in enumerate(arranged_faces):
            adjusted_index = (last_matched_index + i) % len(csv_files)
            for face in faces:
                face_pairs.append((adjusted_index, face))

        face_pairs_count = len(face_pairs)
        for i in range(face_pairs_count):
            for j in range(i + 1, face_pairs_count):
                index1, face1 = face_pairs[i]
                index2, face2 = face_pairs[j]

                eye1 = arranged_eyes[index1 - last_matched_index][0]
                eye2 = arranged_eyes[index2 - last_matched_index][0]

                # Check if the faces or eyes are zero (no detection)
                if (
                    face1 == [(0, 0, 0, 0)]
                    or face2 == [(0, 0, 0, 0)]
                    or eye1 == [((0, 0), (0, 0))]
                    or eye2 == [((0, 0), (0, 0))]
                ):
                    continue  # Skip processing for zero data

                if eye1 and eye2:
                    x1, y1, w1, h1 = face1
                    x2, y2, w2, h2 = face2

                    area1 = w1 * h1
                    area2 = w2 * h2

                    if area1 > 0 and area2 > 0:
                        area_ratio = max(area1, area2) / min(area1, area2)
                        if area_ratio > 1.5:
                            continue  # Skip this frame if area size difference is more than 1.5

                    iou_score = intersection_over_union(x1, y1, w1, h1, x2, y2, w2, h2)
                    if iou_score > THRESHOLD:
                        eye1_vector = [eye1[0][0], eye1[0][1], eye1[1][0], eye1[1][1]]
                        eye2_vector = [eye2[0][0], eye2[0][1], eye2[1][0], eye2[1][1]]
                        matched_faces.append(
                            (
                                current_frame,
                                index1,
                                index2,
                                iou_score,
                                eye1_vector,
                                eye2_vector,
                            )
                        )
                        last_matched_index = index2  # Update last matched index
                        print(
                            f"Matched Face at Frame {current_frame}: IOU {iou_score:.2f}"
                        )
                        break  # Exit loop once a match is found in this frame
                else:
                    continue
                break

    return matched_faces

def build_transition_graph(matched_faces, csv_files):

    graph = defaultdict(list)
    for frame, index1, index2, iou_score, eye1, eye2 in matched_faces:
        graph[(frame, index1)].append(index2)
        graph[(frame, index2)].append(index1)  # Assuming bidirectional interest

    return graph

def process_matches(matched_faces, video_files):
    graph = build_transition_graph(matched_faces, video_files)
    # Assuming the matches include frame numbers and IOU scores now
    verified_matches = [
        (frame, video_files[index1], video_files[index2], iou, eye1, eye2)
        for frame, index1, index2, iou, eye1, eye2 in matched_faces
    ]

    return verified_matches

def save_verified_matches(verified_matches, filename="verified_matches.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["검증된 매칭 결과:"])
        for match in verified_matches:
            writer.writerow(match)


def frame_difference_detection(
    video_path, threshold=20, resize_factor=1, aggregation_window=18
):
    frame_list = []
    cap = cv2.VideoCapture(video_path)
    transition_count = 0
    total_frames = 0
    added_frames = 0  # To keep track of how many times we've added an extra frame

    ret, frame1 = cap.read()
    if not ret:
        print("Error: Failed to read video file.")
        return 0

    # Resize frame to speed up processing
    frame1 = cv2.resize(frame1, (0, 0), fx=resize_factor, fy=resize_factor)
    prev_gray = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    last_cut_frame = (
        -aggregation_window
    )  # Initialize to a value outside possible frame index

    while True:
        ret, frame2 = cap.read()
        if not ret:
            break

        frame2 = cv2.resize(frame2, (0, 0), fx=resize_factor, fy=resize_factor)
        total_frames += 1
        gray = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

        # Compute the absolute difference between the current frame and the previous frame
        frame_diff = cv2.absdiff(prev_gray, gray)
        mean_diff = np.mean(frame_diff)

        # Correct frame count at every 1000th frame
        if total_frames % 1000 == 0 and total_frames // 1000 > added_frames:
            total_frames += 1
            added_frames += 1  # Update the counter for added frames

        # If the average intensity difference exceeds the threshold, it's likely a cut
        if mean_diff > threshold:
            # Aggregate close detections as a single cut
            if total_frames - last_cut_frame > aggregation_window:
                transition_count += 1
                last_cut_frame = total_frames

                # print(
                #     f"Cut detected at frame {total_frames} with average frame difference {mean_diff}"
                # )

                frame_list.append(total_frames)
                print((total_frames) * (1 / 29.97))
        prev_gray = gray

    cap.release()
    return frame_list
