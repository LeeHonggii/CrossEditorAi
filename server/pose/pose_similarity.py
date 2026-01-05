import numpy as np
from scipy.spatial.distance import euclidean, cosine
from fastdtw import fastdtw
import pandas as pd
from tqdm import tqdm


def calculate_similarities(csv_files, width, height, threshold, position_threshold, size_threshold,
                           avg_similarity_threshold):
    def get_keypoints(row, start_index, count):
        keypoints = []
        for i in range(count):
            x_index = start_index + i * 3 + 1
            y_index = start_index + i * 3 + 2
            if x_index < len(row) and y_index < len(row):
                x = row[x_index]
                y = row[y_index]
                if np.isnan(x) or np.isinf(x):
                    x = 0.0
                if np.isnan(y) or np.isinf(y):
                    y = 0.0
                keypoints.append((x, y))
            else:
                keypoints.append((0.0, 0.0))
        return keypoints

    def normalize_keypoints(keypoints, width, height):
        return [(x / width, y / height) for x, y in keypoints]

    def calculate_dtw_distance(keypoints1, keypoints2):
        distance, _ = fastdtw(keypoints1, keypoints2, dist=euclidean)
        return distance

    def calculate_cosine_similarity(keypoints1, keypoints2):
        flat1 = np.array(keypoints1).flatten()
        flat2 = np.array(keypoints2).flatten()
        uu = np.dot(flat1, flat1)
        vv = np.dot(flat2, flat2)
        if uu == 0 or vv == 0:
            return 1.0
        return cosine(flat1, flat2)

    def calculate_centroid(keypoints):
        x_coords = [x for x, y in keypoints]
        y_coords = [y for x, y in keypoints]
        centroid = (sum(x_coords) / len(x_coords), sum(y_coords) / len(y_coords))
        return centroid

    def calculate_size(keypoints):
        x_coords = [x for x, y in keypoints]
        y_coords = [y for x, y in keypoints]
        width = max(x_coords) - min(x_coords)
        height = max(y_coords) - min(y_coords)
        return width, height

    def filter_by_position_and_size(keypoints1, keypoints2, width, height, position_threshold=0.1, size_threshold=0.1):
        centroid1 = calculate_centroid(keypoints1)
        centroid2 = calculate_centroid(keypoints2)

        size1 = calculate_size(keypoints1)
        size2 = calculate_size(keypoints2)

        norm_centroid1 = (centroid1[0] / width, centroid1[1] / height)
        norm_centroid2 = (centroid2[0] / width, centroid2[1] / height)

        norm_size1 = (size1[0] / width, size1[1] / height)
        norm_size2 = (size2[0] / width, size2[1] / height)

        position_diff = euclidean(norm_centroid1, norm_centroid2)
        size_diff = euclidean(norm_size1, norm_size2)

        is_similar = position_diff < position_threshold and size_diff < size_threshold
        return is_similar, position_diff, size_diff

    def calculate_combined_similarity_with_filter(row1, row2, width, height, position_threshold, size_threshold):
        face1 = get_keypoints(row1, 0, 5)
        face2 = get_keypoints(row2, 0, 5)
        body1 = get_keypoints(row1, 15, 7)
        body2 = get_keypoints(row2, 15, 7)
        leg1 = get_keypoints(row1, 36, 4)
        leg2 = get_keypoints(row2, 36, 4)

        keypoints1 = face1 + body1 + leg1
        keypoints2 = face2 + body2 + leg2

        is_similar, position_diff, size_diff = filter_by_position_and_size(keypoints1, keypoints2, width, height,
                                                                           position_threshold, size_threshold)
        if not is_similar:
            return float('inf'), position_diff, size_diff

        similarity = calculate_combined_similarity(row1, row2, width, height)
        return similarity, position_diff, size_diff

    def calculate_combined_similarity(row1, row2, width, height):
        face1 = get_keypoints(row1, 0, 5)
        body1 = get_keypoints(row1, 15, 7)
        leg1 = get_keypoints(row1, 36, 4)

        face2 = get_keypoints(row2, 0, 5)
        body2 = get_keypoints(row2, 15, 7)
        leg2 = get_keypoints(row2, 36, 4)

        face1 = normalize_keypoints(face1, width, height)
        body1 = normalize_keypoints(body1, width, height)
        leg1 = normalize_keypoints(leg1, width, height)

        face2 = normalize_keypoints(face2, width, height)
        body2 = normalize_keypoints(body2, width, height)
        leg2 = normalize_keypoints(leg2, width, height)

        face_similarity = calculate_dtw_distance(face1, face2) + calculate_cosine_similarity(face1, face2)
        body_similarity = calculate_dtw_distance(body1, body2) + calculate_cosine_similarity(body1, body2)
        leg_similarity = calculate_dtw_distance(leg1, leg2) + calculate_cosine_similarity(leg1, leg2)

        return (face_similarity + body_similarity + leg_similarity) / 3

    def get_similar_frames_dict(results):
        frame_similarities = {}
        for frame_num in results:
            for result in results[frame_num]:
                file_pair = result['similar_files']
                for file in file_pair:
                    if file not in frame_similarities:
                        frame_similarities[file] = []
                    frame_similarities[file].append((frame_num, file_pair))
        return frame_similarities

    data_list = [pd.read_csv(file) for file in csv_files]

    similar_frames = {}
    best_vectors = {}

    all_frame_numbers = set()
    for data in data_list:
        # Ensure frame_number is int
        data.iloc[:, 0] = data.iloc[:, 0].astype(int)
        all_frame_numbers.update(data.iloc[:, 0].unique())

    total_comparisons = sum(
        len(data1[data1.iloc[:, 0] == frame_num]) * len(data2[data2.iloc[:, 0] == frame_num])
        for frame_num in all_frame_numbers
        for i, data1 in enumerate(data_list)
        for j, data2 in enumerate(data_list) if i < j
    )

    progress = tqdm(total=total_comparisons, desc="전환점을 찾고있습니다")

    for frame_num in all_frame_numbers:
        for i, data1 in enumerate(data_list):
            frame1_rows = data1[data1.iloc[:, 0] == frame_num].to_numpy()
            for j, data2 in enumerate(data_list):
                if i >= j:
                    continue

                frame2_rows = data2[data2.iloc[:, 0] == frame_num].to_numpy()

                best_similarity = float('inf')
                best_vector1 = None
                best_vector2 = None

                for row1 in frame1_rows:
                    for row2 in frame2_rows:
                        similarity, position_diff, size_diff = calculate_combined_similarity_with_filter(row1, row2,
                                                                                                         width, height,
                                                                                                         position_threshold,
                                                                                                         size_threshold)

                        if similarity < threshold:
                            key = (frame_num, csv_files[i], csv_files[j])
                            reverse_key = (frame_num, csv_files[j], csv_files[i])
                            if key not in similar_frames:
                                similar_frames[key] = []
                            if reverse_key not in similar_frames:
                                similar_frames[reverse_key] = []
                            similar_frames[key].append((similarity, position_diff, size_diff))
                            similar_frames[reverse_key].append((similarity, position_diff, size_diff))

                        if similarity < best_similarity:
                            best_similarity = similarity
                            best_vector1 = [row1[16], row1[17], row1[19], row1[20]]
                            best_vector2 = [row2[16], row2[17], row2[19], row2[20]]

                            # Ensure the coordinates are in the correct order
                            if best_vector1[0] > best_vector1[2]:
                                best_vector1 = [best_vector1[2], best_vector1[3], best_vector1[0], best_vector1[1]]
                            if best_vector2[0] > best_vector2[2]:
                                best_vector2 = [best_vector2[2], best_vector2[3], best_vector2[0], best_vector2[1]]

                        progress.update(1)

                if best_vector1 is not None and best_vector2 is not None:
                    best_vectors[(frame_num, csv_files[i], csv_files[j])] = (best_vector1, best_vector2)
                    best_vectors[(frame_num, csv_files[j], csv_files[i])] = (best_vector2, best_vector1)

    progress.close()

    results = {}
    verified_matches = []

    for (frame_num, csv_file1, csv_file2), values in similar_frames.items():
        avg_similarity = sum(val[0] for val in values) / len(values)
        avg_position_diff = sum(val[1] for val in values) / len(values)
        avg_size_diff = sum(val[2] for val in values) / len(values)
        if avg_similarity > avg_similarity_threshold:
            continue

        if frame_num not in results:
            results[frame_num] = []

        results[frame_num].append({
            "frame_num": frame_num,
            "similar_files": (csv_file1, csv_file2),
            "avg_similarity": avg_similarity,
            "avg_position_diff": avg_position_diff,
            "avg_size_diff": avg_size_diff,
            "similar_person_count": len(values)
        })
        verified_matches.append((frame_num, csv_file1, csv_file2, avg_similarity))

    frame_similarities = get_similar_frames_dict(results)
    frame_count = max(all_frame_numbers) + 1

    return results, verified_matches, frame_similarities, frame_count, best_vectors
