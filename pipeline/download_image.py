import albumentations as A
import numpy as np
import boto3
import cv2
import os
from PIL import Image

def image_resize(local_file_name):
    # Albumentations를 사용하여 이미지 크기 변환
    image = Image.open(local_file_name)
    WIDTH = 768
    HEIGHT = 1024
    ORIGINAL_WIDTH, ORIGINAL_HEIGHT = image.size
    width_ratio = WIDTH / ORIGINAL_WIDTH
    height_ratio = HEIGHT / ORIGINAL_HEIGHT
    transform = A.Compose([
            #A.LongestMaxSize(max_size=max(target_width, target_height), always_apply=True),
            #A.PadIfNeeded(min_height=target_height, min_width=target_width, always_apply=True, border_mode=0),
            A.Resize(height=int(ORIGINAL_HEIGHT * height_ratio), width=int(ORIGINAL_WIDTH * width_ratio),
                    always_apply=True),
            A.Resize(height=HEIGHT, width=WIDTH, always_apply=True)
        ])
    transformed = transform(image=np.array(image))["image"]
    transformed_image = Image.fromarray(transformed)
    transformed_image = transformed_image.convert("RGB")
    local_file_name = local_file_name.replace('.png', '.jpg')
    transformed_image.save(local_file_name)

def download_image_cloth(ID, image_url, cloth_url):
    s3 = boto3.client('s3', region_name='us-east-2',
                      aws_access_key_id='AKIATVK33BK56TQ5E3T6',
                      aws_secret_access_key='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')

    bucket_name = 'bigprogect-bucket'
    image_name = image_url.split('/')[-1]
    cloth_name = cloth_url.split('/')[-1]
    file_names = [f'{ID}/{image_name}', f'{ID}/{cloth_name}']

    for file_name in file_names:
        if 'image' in file_name:
            local_file_name = f'datasets/test/archive/image/{ID}.png'  # 다운로드한 파일을 저장할 로컬 경로 및 파일명
        elif 'cloth' in file_name:
            local_file_name = f'datasets/test/archive/cloth/{ID}.png'  # 다운로드한 파일을 저장할 로컬 경로 및 파일명
        s3.download_file(bucket_name, file_name, local_file_name)
        print(f'{file_name} 다운로드 완료')

        # Albumentations를 사용하여 이미지 크기 변환
        image_resize(local_file_name)
        
    file_paths = [f'datasets/test/archive/image/{ID}.png',
                  f'datasets/test/archive/cloth/{ID}.png']

    for file_path in file_paths:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"File '{file_path}' deleted successfully.")
        else:
            print(f"File '{file_path}' does not exist.")

    print('모든 파일 다운로드 및 이미지 사이즈 조절 완료')

def download_image(ID, image_url):
    s3 = boto3.client('s3', region_name='us-east-2',
                      aws_access_key_id='AKIATVK33BK56TQ5E3T6',
                      aws_secret_access_key='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')

    bucket_name = 'bigprogect-bucket'
    image_name = image_url.split('/')[-1]
    file_names = [f'{ID}/{image_name}']

    for file_name in file_names:
        if 'image' in file_name:
            local_file_name = f'datasets/test/archive/image/{ID}.png'  # 다운로드한 파일을 저장할 로컬 경로 및 파일명
        elif 'cloth' in file_name:
            local_file_name = f'datasets/test/archive/cloth/{ID}.png'  # 다운로드한 파일을 저장할 로컬 경로 및 파일명
        s3.download_file(bucket_name, file_name, local_file_name)
        print(f'{file_name} 다운로드 완료')

        # Albumentations를 사용하여 이미지 크기 변환
        image_resize(local_file_name)
        
    file_path = f'datasets/test/archive/image/{ID}.png'

    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"File '{file_path}' deleted successfully.")
    else:
        print(f"File '{file_path}' does not exist.")
        
    print('모든 파일 다운로드 및 이미지 사이즈 조절 완료')