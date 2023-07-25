import pandas as pd
from scipy.spatial.distance import cdist


# 사용자 신체 치수 리턴 함수
def physical_size(height, weight, data_path = 'size/size_data.csv') :
    
    data = pd.read_csv(data_path)
    distances = cdist(data[['키', '몸무게']], [[height, weight]], metric='euclidean')

    # 근사값이 가장 작은 행 선택
    closest_row_index = distances.argmin()
    closest_row = data.iloc[closest_row_index].to_dict()
    return {
        'length': closest_row['총장'],
        'shoulderWidth':closest_row['어깨너비'],
        'chestWidth':closest_row['가슴단면'] 
        }


#a = physical_size(176, 68)
#print(a)