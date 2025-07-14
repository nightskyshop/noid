from PIL import Image
from io import BytesIO
import base64
import os

def create(data, frame_name, session):
    # 현재 스크립트의 디렉토리를 기준으로 경로 설정
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    first = Image.open(BytesIO(base64.b64decode(data[0]))).convert('RGBA')
    second = Image.open(BytesIO(base64.b64decode(data[1]))).convert('RGBA')
    third = Image.open(BytesIO(base64.b64decode(data[2]))).convert('RGBA')
    forth = Image.open(BytesIO(base64.b64decode(data[3]))).convert('RGBA')

    photos = [first, second, third, forth]
    frame_path = os.path.join(script_dir, 'frame', f'{frame_name}.png')
    frame = Image.open(frame_path).convert('RGBA')

    coordinates = [(74, 355), (619, 92), (74, 1053), (619, 790)]

    for i, file in enumerate(photos):
        img = file.resize((508, 668))
        frame.paste(img, coordinates[i], img)

    images_dir = os.path.join(script_dir, 'images')
    # images 디렉토리가 없으면 생성
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
    
    output_path = os.path.join(images_dir, f'{session}.png')
    frame.save(output_path)
    
    with open(output_path, 'rb') as f:
            frame_bytes = f.read()
            frame_base64 = base64.b64encode(frame_bytes).decode('utf-8')
            return frame_base64