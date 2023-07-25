import requests

url = 'http://172.30.1.20:8000' # http://localhost:8000
url = f"{url}/run"  # FastAPI 서버의 주소와 포트 번호에 맞게 수정해주세요.

response = requests.post(url)

if response.status_code == 200:
    print("Pipeline 실행 요청이 성공적으로 전송되었습니다.")
else:
    print("Pipeline 실행 요청을 보내는 중에 오류가 발생했습니다.")
    print(f"오류 코드: {response.status_code}")
    print(f"오류 메시지: {response.text}")