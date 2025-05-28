from PIL import Image
from io import BytesIO
import base64, os

def create(data, frame_name, session):
    first = Image.open(BytesIO(base64.b64decode(data[0]))).convert('RGBA')
    second = Image.open(BytesIO(base64.b64decode(data[1]))).convert('RGBA')
    third = Image.open(BytesIO(base64.b64decode(data[2]))).convert('RGBA')
    forth = Image.open(BytesIO(base64.b64decode(data[3]))).convert('RGBA')

    photos = [first, second, third, forth]
    frame = Image.open(f'./frame/{frame_name}.png').convert('RGBA')

    if frame_name == 'dankook_b' or frame_name == 'dankook_w' or frame_name == 'seoulddp':
        coordinates = [(74, 338), (608, 81), (74, 1016), (608, 759)]
    elif frame_name == 'dwyl' or frame_name == 'blue' or frame_name == 'green':
        coordinates = [(70, 80), (609, 80), (70, 760), (609, 760)]

    for i, file in enumerate(photos):
        img = file.resize((500, 650))
        frame.paste(img, coordinates[i], img)

    frame.save(f'./images/{session}.png')
    
    with open(f'./images/{session}.png', 'rb') as f:
            frame_bytes = f.read()
            frame_base64 = base64.b64encode(frame_bytes).decode('utf-8')
            return frame_base64