import cv2

# 합쳐질 동영상 파일 경로 설정
video1_path = 'data/video2.mp4'
video2_path = 'data/video1.mp4'

# 첫 번째 동영상 파일 불러오기
cap1 = cv2.VideoCapture(video1_path)

# 두 번째 동영상 파일 불러오기
cap2 = cv2.VideoCapture(video2_path)

# 첫 번째 동영상 파일이 정상적으로 열렸는지 확인
if not cap1.isOpened():
    print("Error: Could not open first video.")
    exit()

# 두 번째 동영상 파일이 정상적으로 열렸는지 확인
if not cap2.isOpened():
    print("Error: Could not open second video.")
    exit()

# 합쳐질 동영상의 프레임 사이즈 가져오기
width = int(cap1.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap1.get(cv2.CAP_PROP_FRAME_HEIGHT))

# 합쳐질 동영상의 프레임 레이트 가져오기
fps = int(cap1.get(cv2.CAP_PROP_FPS))

# 출력 동영상 파일 설정
output_path = 'data/output_video.mp4'
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

# 첫 번째 동영상 파일의 프레임을 읽어서 출력 동영상에 추가
while True:
    ret1, frame1 = cap1.read()
    if not ret1:
        break
    out.write(frame1)

# 두 번째 동영상 파일의 프레임을 읽어서 출력 동영상에 추가
while True:
    ret2, frame2 = cap2.read()
    if not ret2:
        break
    out.write(frame2)

# 자원 해제
cap1.release()
cap2.release()
out.release()

print('동영상이 성공적으로 합쳐졌습니다.')
