import subprocess
import torch
import glob
from numba import cuda
from openpose import get_openpose
from cloth_mask import get_colth_mask
from human_parse import get_human_parse
from parse_agnostic import get_parse_agnostic

def main():
    #images_list = glob.glob('datasets/test/image/*.jpg')
    #cloth_list = glob.glob('datasets/test/cloth/*.jpg')
    #get_openpose(images_list) # list // input_files_path
    #get_colth_mask(cloth_list) # list // input_files_path_
    #torch.cuda.empty_cache()
    get_human_parse() # str // input_path, output_path
    device = cuda.get_current_device()
    device.reset()
    get_parse_agnostic() # str // input_path, output_path

# --------------------------------------------------------------------------------------------------------------
#                                           DensePose
# --------------------------------------------------------------------------------------------------------------

    #output = subprocess.run('''python -c "import sys; print(sys.executable)"
    #              source /home/luca/anaconda3/etc/profile.d/conda.sh
    #              conda activate pipeline_2
    #              python -c "import sys; print(sys.executable)"
    #              python pipeline/pipeline_2.py
    #              python -V''', executable='/bin/bash', shell=True, capture_output=True)
    #print(bytes.decode(output.stdout))

# --------------------------------------------------------------------------------------------------------------
#                                           결과물 뽑기
# --------------------------------------------------------------------------------------------------------------

    #output = subprocess.run('''python -c "import sys; print(sys.executable)"
    #              source /home/luca/anaconda3/etc/profile.d/conda.sh
    #              conda activate pipeline_2
    #              python -c "import sys; print(sys.executable)"
    #              python test_generator.py --occlusion --cuda True --test_name test_name --tocg_checkpoint ./eval_models/weights/v0.1/mtviton.pth --gpu_ids 0 --gen_checkpoint ./eval_models/weights/v0.1/gen.pth --datasetting unpaired --dataroot ./datasets --data_list test_pairs.txt
    #              python -V''', executable='/bin/bash', shell=True, capture_output=True)
    #print(bytes.decode(output.stdout))

    subprocess.run('python -V', shell=True)


if __name__ == '__main__':
    main()


'''
python -c "import sys; print(sys.executable)"
source /home/luca/anaconda3/etc/profile.d/conda.sh
conda activate pipeline_2
python -c "import sys; print(sys.executable)"
conda env export
python -V
'''

'''
python3 test_generator.py --occlusion --cuda True --test_name test_name --tocg_checkpoint ./eval_models/weights/v0.1/mtviton.pth --gpu_ids 0 --gen_checkpoint ./eval_models/weights/v0.1/gen.pth --datasetting unpaired --dataroot ./datasets --data_list test_pairs.txt
'''