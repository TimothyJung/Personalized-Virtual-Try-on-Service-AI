from src import torch_openpose, util
import numpy as np
import cv2
import json
import os

def get_openpose(img_path_list: list=['datasets/test/image/00891_00.jpg', 'datasets/test/image/03615_00.jpg', 'datasets/test/image/07445_00.jpg', 'datasets/test/image/07573_00.jpg']):
    print('pose start')
    parsing_dir = 'datasets/test/openpose_img' # 최종 폴더
    if not os.path.exists(parsing_dir):
        os.makedirs(parsing_dir)

    parsing_dir = 'datasets/test/openpose_json' # 최종 폴더
    if not os.path.exists(parsing_dir):
        os.makedirs(parsing_dir)

    tp = torch_openpose.torch_openpose('body_25')

    for img_path in img_path_list:
        img = cv2.imread(img_path)
        poses = tp(img)
        canvas = np.zeros_like(img)
        img = util.draw_bodypose(canvas, poses,'body_25')

        pose_keypoints_2d = np.array(poses).reshape(-1)

        data = {
            "version": 1.3,
            "people" : [
                {
                    "person_id" : [-1],
                    "pose_keypoints_2d" : list(pose_keypoints_2d),
                    "face_keypoints_2d" : [],
                    "hand_left_keypoints_2d" : [],
                    "hand_right_keypoints_2d" : [],
                    "pose_keypoints_3d" : [],
                    "face_keypoints_3d" : [],
                    "hand_left_keypoints_3d" : [],
                    "hand_right_keypoints_3d" : []
                }
            ]
        }

        # data json 포맷으로 쓰기
        json_path = img_path.split('image')[0] + 'openpose_json/'+ os.path.splitext(os.path.basename(img_path))[0] + '_keypoints.json'
        sk_img_path = img_path.split('image')[0] + 'openpose_img/'+ os.path.splitext(os.path.basename(img_path))[0] + '_rendered.png'

        with open(json_path, "w")as f:
            json.dump(data, f, indent=4)

        cv2.imwrite(sk_img_path, img)
    print('pose end')