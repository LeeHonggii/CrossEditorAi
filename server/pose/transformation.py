import numpy as np
def find_max_transformation_order(frame_similarities, frame_count, random_point):
    frames = sorted(frame_similarities.keys())
    n = len(frames)

    # DP 테이블 초기화: 전환 횟수를 저장하는 테이블
    dp = np.zeros(n)
    path = [None] * n

    for i in range(n):
        for j in range(i):
            if frames[i] - frames[j] >= random_point:
                for transition in frame_similarities[frames[i]]:
                    if transition[0] in [pair[1] for pair in frame_similarities[frames[j]]]:
                        if dp[i] < dp[j] + 1:
                            dp[i] = dp[j] + 1
                            path[i] = (frames[j], transition[0], transition[1])

    # 최대 전환 횟수 및 해당 경로 추적
    max_transitions = max(dp)
    max_index = np.argmax(dp)

    # 경로 재구성
    optimal_path = []
    while max_index is not None and path[max_index] is not None:
        frame, start_csv, end_csv = frames[max_index], path[max_index][1], path[max_index][2]
        optimal_path.append((frame, start_csv, end_csv))
        next_frame = path[max_index][0]
        max_index = frames.index(next_frame) if next_frame in frames else None

    optimal_path.reverse()

    return optimal_path

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