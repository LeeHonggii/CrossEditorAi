import torch
import pandas as pd
import json
from pose.pose_similarity import calculate_similarities
from pose.transformation import find_max_transformation_order
from make_json import generate_json,create_combined_video

def check_cuda():
    if torch.cuda.is_available():
        print("CUDA is available. Device:", torch.cuda.get_device_name(0))
    else:
        print("CUDA is not available.")

# 하이퍼파라미터 설정
WIDTH = 1920
HEIGHT = 1080
THRESHOLD = 8
POSITION_THRESHOLD = 0.05
SIZE_THRESHOLD = 0.05
AVG_SIMILARITY_THRESHOLD = 0.5
RANDOM_POINT = 10

# CSV 파일 및 비디오 파일 설정
csv_files = [
    "sync_bts_fakelove_1.csv",
    "sync_bts_fakelove_2.csv",
    "sync_bts_fakelove_3.csv",
    "sync_bts_fakelove_4.csv",
    "sync_bts_fakelove_5.csv"
]

video_files = [
    "sync_bts_fakelove_1.mp4",
    "sync_bts_fakelove_2.mp4",
    "sync_bts_fakelove_3.mp4",
    "sync_bts_fakelove_4.mp4",
    "sync_bts_fakelove_5.mp4"
]

# 비디오 파일과 CSV 파일 매핑
video_file_mapping = {
    "sync_bts_fakelove_1.csv": "sync_bts_fakelove_1.mp4",
    "sync_bts_fakelove_2.csv": "sync_bts_fakelove_2.mp4",
    "sync_bts_fakelove_3.csv": "sync_bts_fakelove_3.mp4",
    "sync_bts_fakelove_4.csv": "sync_bts_fakelove_4.mp4",
    "sync_bts_fakelove_5.csv": "sync_bts_fakelove_5.mp4"
}

if __name__ == "__main__":
    check_cuda()

    results, verified_matches, frame_similarities, frame_count, best_vectors = calculate_similarities(
        csv_files, WIDTH, HEIGHT, THRESHOLD, POSITION_THRESHOLD, SIZE_THRESHOLD, AVG_SIMILARITY_THRESHOLD
    )

    max_transformation_order = find_max_transformation_order(frame_similarities, frame_count, RANDOM_POINT)

    print("최대 변환 순서:", max_transformation_order)
    print("검증된 매칭 결과:", verified_matches)

    json_data = generate_json(max_transformation_order, verified_matches, video_files, csv_files, video_file_mapping, best_vectors)

    with open('output_pose.json', 'w') as f:
        json.dump(json_data, f, indent=4)

    print("JSON 파일이 생성되었습니다.")

    # JSON 파일을 기반으로 비디오 합치기
    create_combined_video('output_pose.json', 'combined_video.mp4')
    print("최종 비디오가 생성되었습니다.")
