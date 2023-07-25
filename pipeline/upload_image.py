import requests

def upload_image(ID, rand1, rand2):
    url = 'http://34.22.76.240:8080'
    upload_url = f'{url}/upload'  # FastAPI 서버의 업로드 URL
    file_paths = [f'output/{ID}_{ID}_{rand1}_{rand2}.png']

    for file_path in file_paths:
        with open(file_path, 'rb') as file:
            response = requests.post(upload_url, files={'file': file}, params={'ID': ID})

        if response.status_code == 200:
            print(f'{file_path} 이미지 업로드 성공!')
            print(response.json())
        else:
            print(f'{file_path} 이미지 업로드 실패!')
            print(response.text)

    print('모든 이미지 업로드 완료')

if __name__ == '__main__':
    upload_image('csy')