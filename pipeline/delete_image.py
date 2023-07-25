import requests

def delete_image(ID):
    delete_url = 'http://localhost:8000/delete'  # FastAPI 서버의 삭제 URL
    file_names = [f'{ID}_{ID}.jpg']

    for file_name in file_names:
        delete_file_url = delete_url + '/' + file_name
        response = requests.delete(delete_file_url)

        if response.status_code == 200:
            print(f'{file_name} 이미지 삭제 성공!')
        else:
            print(f'{file_name} 이미지 삭제 실패!')
            print(response.text)

    print('모든 이미지 삭제 완료')