import sys
sys.path.append('pipeline')

import boto3
from pipeline_1 import main
from size.size_recommendation import size
from size.physical_size import physical_size
from size.cloth_size import cloth_size
from botocore.exceptions import ClientError
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from starlette.responses import StreamingResponse

aws_access_key_id = 'AKIATVK33BK56TQ5E3T6'
aws_secret_access_key = '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'

app = FastAPI()

@app.get("/")
def root():
    return {"Hello":"World"}

'''@app.get("/show")
async def read_random_file():
    files = os.listdir(IMAGEDIR)
    random_index = randint(0, len(files)-1)
    path = f'{IMAGEDIR}{files[random_index]}'

    return FileResponse(path)'''

@app.get("/show")
def show(ID):
    # Configure your S3 client
    s3 = boto3.client('s3', region_name='us-east-2',
                      aws_access_key_id=aws_access_key_id,
                      aws_secret_access_key=aws_secret_access_key)
    
    bucket_name = 'bigprogect-bucket'
    file_key = f'{ID}/{ID}.png'  # Specify the key of the image file in your S3 bucket

    try:
        # List objects in the S3 bucket
        response = s3.list_objects(Bucket=bucket_name)
        object_keys = [obj['Key'] for obj in response['Contents']]

        # Select a random file key
        random_file_key = file_key

        # Download the file from S3 to a temporary local path
        local_path = f"/tmp/{random_file_key}"
        s3.download_file(bucket_name, random_file_key, local_path)

        # Return the file as a response
        return FileResponse(local_path)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    '''bucket_name = 'bigproject-bucket'
    file_key = f'{ID}/{ID}.png'  # Specify the key of the image file in your S3 bucket

    try:
        # Get the image file from S3
        response = s3.get_object(Bucket=bucket_name, Key=file_key)
        image_data = response['Body'].read()

        # Return the image as a streaming response
        return StreamingResponse(content=image_data, media_type='image/jpeg')

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))'''

'''@app.get("/s3/{bucket_name}/{file_key}")
def get_image_from_s3(bucket_name: str, file_key: str):
    try:
        response = s3.get_object(Bucket=bucket_name, Key=file_key)
        content_type = response["ContentType"]
        image_data = response["Body"].read()

        return {
            "file_name": file_key,
            "content_type": content_type,
            "image_data": image_data
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))'''
    
@app.post("/run")
def run(ID):
    try:
        print('시작')
        main()
        print('끝')
        return {"message": "Pipeline 실행이 완료되었습니다.",
                'file name': f'https://bigprogect-bucket.s3.amazonaws.com/{ID}/{ID}_{ID}.jpg'}
    except Exception as e:
        print('오류') 
        return {"message": f"Pipeline 실행 중 오류가 발생했습니다: {str(e)}"}

@app.post("/upload2")
async def upload_file2(file: UploadFile = File(...)):
    # Boto3를 사용하여 AWS S3에 파일 업로드하기
    s3 = boto3.client('s3', region_name='us-east-2',
                      aws_access_key_id=aws_access_key_id,
                      aws_secret_access_key=aws_secret_access_key)

    bucket_name = 'bigprogect-bucket'
    file_name = file.filename
    s3.upload_fileobj(file.file, bucket_name, file_name)

    # 이미지 파일에 공개 읽기 권한 부여
    s3.put_object_acl(ACL='public-read', Bucket=bucket_name, Key=file_name)

    # 업로드한 이미지에 대한 URL 생성
    s3_url = f"https://{bucket_name}.s3.amazonaws.com/{file_name}"

    return {"filename": file.filename, "url": s3_url}

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

@app.post("/txt")
async def upload_file(content: str):
    # Boto3를 사용하여 AWS S3에 문자열 저장하기
    s3 = boto3.client('s3', region_name='us-east-2',
                      aws_access_key_id=aws_access_key_id,
                      aws_secret_access_key=aws_secret_access_key)

    bucket_name = 'bigprogect-bucket'
    file_name = 'ID.txt'
    s3.put_object(Body=content.encode('utf-8'), Bucket=bucket_name, Key=file_name)

    # 저장한 문자열에 대한 URL 생성
    s3_url = f"https://{bucket_name}.s3.amazonaws.com/{file_name}"

    return {"filename": file_name, "url": s3_url}


@app.delete("/delete/{file_name}")
async def delete_file(ID, file_name: str):
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
async def get_size(height: int, weight: int):
    size_physical = physical_size(height, weight)

    return {
        "height": height,
        "weight": weight,
        "size": size_physical
        }

@app.get("/cloth_size/")
async def get_size(length: float, shoulderWidth: float, chestWidth: float, imageUrl: str, overfit: bool):
    size_cloth, = cloth_size(length, shoulderWidth, chestWidth, imageUrl, overfit)

    return {
        "length": length,
        "shoulderWidth": shoulderWidth,
        "chestWidth": chestWidth,
        "imageUrl": imageUrl,
        "overfit": overfit,
        "size": size_cloth
        }