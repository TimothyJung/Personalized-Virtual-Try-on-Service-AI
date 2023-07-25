import os
import torch
from carvekit.api.high import HiInterface

def get_cloth_mask(file_path_list: list=['datasets/test/cloth/01260_00.jpg', 'datasets/test/cloth/01430_00.jpg', 'datasets/test/cloth/02783_00.jpg']):
    print('mask start')
    interface = HiInterface(object_type="object",
                        batch_size_seg=5,
                        batch_size_matting=1,
                        device='cuda' if torch.cuda.is_available() else 'cpu',
                        seg_mask_size=640,
                        matting_mask_size=2048,
                        trimap_prob_threshold=231,
                        trimap_dilation=30,
                        trimap_erosion_iters=5,
                        fp16=False)
    images_without_background = interface(file_path_list)
    #print(images_without_background)
    mask = []
    parsing_dir = 'datasets/test/cloth-mask' # 최종 폴더
    if not os.path.exists(parsing_dir):
        os.makedirs(parsing_dir)
    for idx, file_path in enumerate(file_path_list):
        mask.append(images_without_background[idx])
        # 알파 채널 추출
        alpha_channel = mask[idx].split()[-1]

        # 알파 채널을 이진화하여 마스크 생성
        mask_image = alpha_channel.point(lambda p: p > 0 and 255)

        # 마스크 이미지 저장
        mask_image.save(file_path.split(f'cloth/{os.path.basename(file_path)}')[0] + 'cloth-mask/' + os.path.splitext(os.path.basename(file_path))[0] + '.jpg')
    print('mask end')
    
def get_image_segm(input_path, output_path):
    interface = HiInterface(object_type="object",
                        batch_size_seg=5,
                        batch_size_matting=1,
                        device='cuda' if torch.cuda.is_available() else 'cpu',
                        seg_mask_size=640,
                        matting_mask_size=2048,
                        trimap_prob_threshold=231,
                        trimap_dilation=30,
                        trimap_erosion_iters=5,
                        fp16=False)
    
    images_without_background = interface([input_path])
    output_img = images_without_background[0]
    output_img.save(output_path)