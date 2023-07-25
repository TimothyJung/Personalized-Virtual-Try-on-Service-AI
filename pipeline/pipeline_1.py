import subprocess
import shutil
import random
import torch
import glob
import time
import os
from numba import cuda
from openpose import get_openpose
from upload_image import upload_image
from human_parse import get_human_parse
from download_image import download_image
from parse_agnostic import get_parse_agnostic
from download_image import download_image_cloth
from cloth_mask import get_cloth_mask, get_image_segm

# --------------------------------------------------------------------------------------------------------------
#                                           Functions
# --------------------------------------------------------------------------------------------------------------

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

            print("파일 경로 이동이 완료되었습니다.")
        else:
            print("파일이 존재하지 않습니다.")

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

def human_parse(ID, image_url):
    start_time = time.time()

    download_image(ID, image_url)

    save_path = [f'datasets/test/archive/image/{ID}.jpg',
                f'datasets/test/archive/image-parse-v3/{ID}.png']

    load_path = [f'datasets/test/image/{ID}.jpg',
                f'datasets/test/image-parse-v3/{ID}.png']
    
    for i in range(len(save_path)):
        move_file_path(save_path[i], load_path[i], reverse=False)

    get_human_parse(ID) # str // input_path, output_path
    #device = cuda.get_current_device()
    #device.reset()

    for i in range(len(save_path)):
        move_file_path(save_path[i], load_path[i], reverse=True)

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"코드 실행 시간: {execution_time}초")

# --------------------------------------------------------------------------------------------------------------
#                                           Main function
# --------------------------------------------------------------------------------------------------------------

def main(ID, image_url, cloth_url):
    start_time = time.time()

    save_path = [f'datasets/test/archive/image/{ID}.jpg',
                f'datasets/test/archive/cloth/{ID}.jpg',
                f'datasets/test/archive/image-parse-v3/{ID}.png']

    load_path = [f'datasets/test/image/{ID}.jpg',
                f'datasets/test/cloth/{ID}.jpg',
                f'datasets/test/image-parse-v3/{ID}.png']

# --------------------------------------------------------------------------------------------------------------
#                                           Download Image to AWS s3
# --------------------------------------------------------------------------------------------------------------
    
    download_image_cloth(ID, image_url, cloth_url)

# --------------------------------------------------------------------------------------------------------------
#                                           Move files to a dataset
# --------------------------------------------------------------------------------------------------------------

    for i in range(len(save_path)):
        move_file_path(save_path[i], load_path[i], reverse=False)

    #images_list = glob.glob('datasets/test/image/*.jpg')

    #cloth_list = glob.glob('datasets/test/cloth/*.jpg')
    
    images_list = [f'datasets/test/image/{ID}.jpg']

    cloth_list = [f'datasets/test/cloth/{ID}.jpg']

# --------------------------------------------------------------------------------------------------------------
#                                           OpenPose
# --------------------------------------------------------------------------------------------------------------

    get_openpose(images_list) # list // input_files_path
    torch.cuda.empty_cache()

# --------------------------------------------------------------------------------------------------------------
#                                           Cloth Mask
# --------------------------------------------------------------------------------------------------------------

    get_cloth_mask(cloth_list) # list // input_files_path
    torch.cuda.empty_cache()

# --------------------------------------------------------------------------------------------------------------
#                                           Human Parse
# --------------------------------------------------------------------------------------------------------------

    # 파일이 존재하는지 확인
    if os.path.exists(load_path[2]):
        print('human parse pass')
    else:
        get_human_parse(ID=ID) # str // input_path, output_path
        #device = cuda.get_current_device()
        #device.reset()

# --------------------------------------------------------------------------------------------------------------
#                                           Parse Agnostic
# --------------------------------------------------------------------------------------------------------------

    get_parse_agnostic(ID=ID) # str // input_path, output_path

# --------------------------------------------------------------------------------------------------------------
#                                           DensePose
# --------------------------------------------------------------------------------------------------------------

    output = subprocess.run('''python -c "import sys; print(sys.executable)"
                  source ~/anaconda3/etc/profile.d/conda.sh
                  conda activate pipeline_2
                  python -c "import sys; print(sys.executable)"
                  python pipeline/pipeline_2.py
                  python -V''', executable='/bin/bash', shell=True, capture_output=True)
    print(bytes.decode(output.stdout))

# --------------------------------------------------------------------------------------------------------------
#                                           결과물 뽑기
# --------------------------------------------------------------------------------------------------------------
    
    # 텍스트 파일 생성 및 내용 저장
    with open('datasets/test_pairs.txt', "w") as file:
        file.write(f'{ID}.jpg {ID}.jpg')
    print("텍스트 파일 저장이 완료되었습니다.")

    output = subprocess.run('''python -c "import sys; print(sys.executable)"
                  source ~/anaconda3/etc/profile.d/conda.sh
                  conda activate pipeline_2
                  python -c "import sys; print(sys.executable)"
                  python test_generator.py --occlusion --cuda True --test_name test_name --tocg_checkpoint ./eval_models/weights/v0.1/mtviton.pth --gpu_ids 0 --gen_checkpoint ./eval_models/weights/v0.1/gen.pth --datasetting unpaired --dataroot ./datasets --data_list test_pairs.txt
                  python -V''', executable='/bin/bash', shell=True, capture_output=True)
    print(bytes.decode(output.stdout))
    torch.cuda.empty_cache()
    
    global rand1
    global rand2
    rand1 = random.randint(1, 1000)
    rand2 = random.randint(1, 1000)
    
    get_image_segm(f'output/{ID}_{ID}.jpg', f'output/{ID}_{ID}_{rand1}_{rand2}.png')

# --------------------------------------------------------------------------------------------------------------
#                                           Move files to archive
# --------------------------------------------------------------------------------------------------------------

    for i in range(len(save_path)):
        move_file_path(save_path[i], load_path[i], reverse=True)

    folders = ['cloth', 'cloth-mask', 'image', 'image-densepose', 'image-parse-agnostic-v3.2', 'image-parse-v3', 'openpose_img', 'openpose_json']
    for folder in folders:
        path = os.path.join('datasets', 'test', folder)
        for root, dirs, files in os.walk(path):
            for file in files:
                if ID in file:
                    file_path = os.path.join(root, file)
                    os.remove(file_path)

    subprocess.run('python -V', shell=True)
    
# --------------------------------------------------------------------------------------------------------------
#                                           Uploading an Image to AWS s3
# --------------------------------------------------------------------------------------------------------------

    upload_image(ID, rand1, rand2)

# --------------------------------------------------------------------------------------------------------------
#                                           End
# --------------------------------------------------------------------------------------------------------------

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"코드 실행 시간: {execution_time}초")

if __name__ == '__main__':
    main()