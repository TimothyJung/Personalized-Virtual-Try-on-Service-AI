from fastapi import FastAPI, UploadFile, File
from tempfile import NamedTemporaryFile
import shutil
import subprocess
import torch
import glob
import os
from numba import cuda
from openpose import get_openpose
from cloth_mask import get_colth_mask
from human_parse import get_human_parse
from parse_agnostic import get_parse_agnostic
import time

app = FastAPI()

start_time = time.time()
ID = 'csy'
save_path = [f'datasets/test/archive/image/{ID}.jpg',
             f'datasets/test/archive/cloth/{ID}.jpg',
             f'datasets/test/archive/image-parse-v3/{ID}.png']

load_path = [f'datasets/test/image/{ID}.jpg',
             f'datasets/test/cloth/{ID}.jpg',
             f'datasets/test/image-parse-v3/{ID}.png']

def move_file_path(source_path, destination_path, reverse=False):
    # 정방향 옮김
    if not reverse:
        # 파일이 존재하는지 확인
        if os.path.exists(source_path):
            # 새 디렉토리가 없다면 생성
            destination_dir = os.path.dirname(destination_path)
            if not os.path.exists(destination_dir):
                os.makedirs(destination_dir)

            # 파일 이동
            shutil.move(source_path, destination_path)

            print("File path moved successfully.")
        else:
            print("File does not exist.")

    # 역방향 옮김
    else:
        # 파일이 존재하는지 확인
        if os.path.exists(destination_path):
            # 새 디렉토리가 없다면 생성
            source_dir = os.path.dirname(source_path)
            if not os.path.exists(source_dir):
                os.makedirs(source_dir)

            # 파일 이동
            shutil.move(destination_path, source_path)

            print("파일 경로 이동이 완료되었습니다.")
        else:
            print("파일이 존재하지 않습니다.")

def main():
    for i in range(len(save_path)):
        move_file_path(save_path[i], load_path[i], reverse=False)
    images_list = glob.glob('datasets/test/image/*.jpg')
    cloth_list = glob.glob('datasets/test/cloth/*.jpg')
    get_openpose(images_list) # list // input_files_path
    get_colth_mask(cloth_list) # list // input_files_path_
    torch.cuda.empty_cache()

    # 파일이 존재하는지 확인
    if os.path.exists(load_path[2]):
        print('human parse pass')
    else:
        get_human_parse() # str // input_path, output_path
        device = cuda.get_current_device()
        device.reset()

    get_parse_agnostic() # str // input_path, output_path

    # --------------------------------------------------------------------------------------------------------------
    #                                           DensePose
    # --------------------------------------------------------------------------------------------------------------

    output = subprocess.run(
        '''python -c "import sys; print(sys.executable)"
        source /home/luca/anaconda3/etc/profile.d/conda.sh
        conda activate pipeline_2
        python -c "import sys; print(sys.executable)"
        python pipeline/pipeline_2.py
        python -V''',
        executable='/bin/bash',
        shell=True,
        capture_output=True
    )
    print(bytes.decode(output.stdout))

    # --------------------------------------------------------------------------------------------------------------
    #                                           Get Results
    # --------------------------------------------------------------------------------------------------------------

    # 텍스트 파일 생성 및 내용 저장
    with open('datasets/test_pairs.txt', "w") as file:
        file.write(f'{ID}.jpg {ID}.jpg')
    print("Text file saved.")

    output = subprocess.run(
        '''python -c "import sys; print(sys.executable)"
        source /home/luca/anaconda3/etc/profile.d/conda.sh
        conda activate pipeline_2
        python -c "import sys; print(sys.executable)"
        python test_generator.py --occlusion --cuda True --test_name test_name --tocg_checkpoint ./eval_models/weights/v0.1/mtviton.pth --gpu_ids 0 --gen_checkpoint ./eval_models/weights/v0.1/gen.pth --datasetting unpaired --dataroot ./datasets --data_list test_pairs.txt
        python -V''',
        executable='/bin/bash',
        shell=True,
        capture_output=True
    )
    print(bytes.decode(output.stdout))

    for i in range(len(save_path)):
        move_file_path(save_path[i], load_path[i], reverse=True)

    subprocess.run('python -V', shell=True)

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Code execution time: {execution_time} seconds")

@app.post("/process_images")
async def process_images(image1: UploadFile = File(...), image2: UploadFile = File(...)):
    """두 개의 이미지 파일을 받아 처리한 후, 하나의 이미지 파일을 반환합니다."""
    # 이미지1 저장
    with NamedTemporaryFile(delete=False) as temp_image1:
        shutil.copyfileobj(image1.file, temp_image1)
        image1_path = temp_image1.name

    # 이미지2 저장
    with NamedTemporaryFile(delete=False) as temp_image2:
        shutil.copyfileobj(image2.file, temp_image2)
        image2_path = temp_image2.name

    # 이미지 처리 작업 수행 (예시로 두 이미지를 합치는 작업)
    # 이미지 처리 작업 수행 로직 작성 (image1_path, image2_path를 사용하여 image3_path에 결과 이미지 저장)
    image3_path = "output/{ID}_{ID}.jpg"
    main()  # Call the main function to perform the image processing

    # 처리된 이미지 읽기
    with open(image3_path, "rb") as image3:
        image3_data = image3.read()

    # 처리된 이미지 반환
    return {"image3": image3_data}
