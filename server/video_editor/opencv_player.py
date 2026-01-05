import cv2

# 동영상 파일 경로 설정
video_path = 'data/resized_video.mp4'

# 동영상 파일 불러오기
cap = cv2.VideoCapture(video_path)

# 동영상 파일이 정상적으로 열렸는지 확인
if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

# 동영상의 프레임 레이트 가져오기
fps = cap.get(cv2.CAP_PROP_FPS)

# 딜레이 계산 (프레임 간의 시간)
delay = int(1000 / fps)  # 밀리초 단위로 변환

# 동영상 재생 루프
while True:
    # 동영상 프레임 읽기
    ret, frame = cap.read()

    # 더 이상 읽을 프레임이 없으면 종료
    if not ret:
        print("Reached end of video.")
        break

    # 프레임을 창에 표시
    cv2.imshow('Video Playback', frame)

    # 딜레이 추가
    key = cv2.waitKey(delay) & 0xFF

    # 'q' 키를 누르면 종료
    if key == ord('q'):
        break

# 자원 해제
cap.release()
cv2.destroyAllWindows()
