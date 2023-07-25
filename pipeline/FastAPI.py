import sys
sys.path.append('pipeline')

import boto3
import pipeline_1
from pipeline_1 import main
from pipeline_1 import human_parse
from size.physical_size import physical_size
from size.cloth_size import cloth_size
from fastapi import FastAPI, HTTPException, UploadFile, File

aws_access_key_id = 'AKIATVK33BK56TQ5E3T6'
aws_secret_access_key = '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'

app = FastAPI()

@app.get("/")
def root():
    return {"Hello":"World"}
    
@app.post("/run")
def run(ID: str, image_url: str, cloth_url: str):
    try:
        print('시작')
        main(ID, image_url, cloth_url)
        print('끝')
        return {"message": "Pipeline 실행이 완료되었습니다.",
                "success": True,
                "file_name": f"https://bigprogect-bucket.s3.amazonaws.com/{ID}/{ID}_{ID}_{pipeline_1.rand1}_{pipeline_1.rand2}.png"}
    except Exception as e:
        print(f'오류: {str(e)}') 
        return {"message": f"Pipeline 실행 중 오류가 발생했습니다: {str(e)}",
                "success": False}
    
@app.post("/parse")
def parse(ID: str, image_url: str):
    try:
        print('시작')
        human_parse(ID, image_url)
        print('끝')
        return {"message": "human parse 실행이 완료되었습니다.",
               "error": False}
    except Exception as e:
        print(f'오류: {str(e)}') 
        return {"message": f"human parse 실행 중 오류가 발생했습니다: {str(e)}",
                "error": True}

@app.post("/upload")
async def upload_file(ID: str, file: UploadFile = File(...)):
    # Boto3를 사용하여 AWS S3에 파일 업로드하기
    s3 = boto3.client('s3', region_name='us-east-2',
                      aws_access_key_id=aws_access_key_id,
                      aws_secret_access_key=aws_secret_access_key)

    bucket_name = 'bigprogect-bucket'
    file_name = f'{ID}/{file.filename}'
    s3.upload_fileobj(file.file, bucket_name, file_name)

    # 이미지 파일에 공개 읽기 권한 부여
    s3.put_object_acl(ACL='public-read', Bucket=bucket_name, Key=file_name)

    # 업로드한 이미지에 대한 URL 생성
    s3_url = f"https://{bucket_name}.s3.amazonaws.com/{file_name}"

    return {"filename": file.filename, "url": s3_url}

@app.delete("/delete/{file_name}")
async def delete_file(ID: str, file_name: str):
    # Boto3를 사용하여 AWS S3에서 파일 삭제하기
    s3 = boto3.client('s3', region_name='us-east-2',
                      aws_access_key_id=aws_access_key_id,
                      aws_secret_access_key=aws_secret_access_key)

    bucket_name = 'bigprogect-bucket'

    try:
        # 이미지 파일 삭제
        s3.delete_object(Bucket=bucket_name, Key=f'{ID}/{file_name}')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": "File deleted successfully"}

@app.get("/physical_size/")
async def get_size(height: float, weight: float):
    size_physical = physical_size(height, weight)

    return {
        "height": height,
        "weight": weight,
        "size": size_physical
        }

@app.get("/cloth_size/")
async def get_size(length: float, shoulderWidth: float, chestWidth: float, imageUrl: str, overfit: str):
    if overfit == '오버핏':
        overfit = True
    else:
        overfit = False
    size_cloth, = cloth_size(length, shoulderWidth, chestWidth, imageUrl, overfit)

    return {
        "length": length,
        "shoulderWidth": shoulderWidth,
        "chestWidth": chestWidth,
        "imageUrl": imageUrl,
        "overfit": overfit,
        "size": size_cloth
        }