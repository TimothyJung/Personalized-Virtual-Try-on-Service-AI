import boto3

aws_access_key_id = 'AKIATVK33BK56TQ5E3T6'
aws_secret_access_key = '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'

def delete_file(file_name: str):
    # Boto3를 사용하여 AWS S3에서 파일 삭제하기
    s3 = boto3.client('s3', region_name='us-east-2',
                      aws_access_key_id=aws_access_key_id,
                      aws_secret_access_key=aws_secret_access_key)

    bucket_name = 'bigproject-bucket'

    try:
        # 파일 삭제
        s3.delete_object(Bucket=bucket_name, Key=file_name)
    except Exception as e:
        raise e

# 파일 삭제를 테스트하기 위한 예시
file_name = '0004_4_00/0004_4_00_image.jpg'
delete_file(file_name)