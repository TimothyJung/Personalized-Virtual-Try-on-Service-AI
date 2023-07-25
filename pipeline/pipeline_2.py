import torch
import glob
from densepose_segm import get_densepose

def main():
    input_path = 'datasets/test/image'
    get_densepose(input_path) # ser // input_path
    torch.cuda.empty_cache()

if __name__ == '__main__':
    main()