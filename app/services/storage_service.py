import boto3
from botocore.exceptions import ClientError
from config import Config

class S3StorageService:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=Config.AWS_ACCESS_KEY,
            aws_secret_access_key=Config.AWS_SECRET_KEY
        )

        self.bucket_name = Config.AWS_BUCKET_NAME

    def upload_file(self, file_obj, file_name):
        """Upload a file to an S3 bucket

        :param file_obj: File object to upload
        :param file_name: File to upload  
        :return: True if file was uploaded, else False
        """
        try:
            self.s3_client.upload_fileobj(file_obj, self.bucket_name, file_name)
        except ClientError as e:
            print(f"Error uploading file: {e}")
            return False
        return True

    def download_file(self, file_name):
        """Download a file from an S3 bucket

        :param file_name: Name of the file to download
        :return: File content if successful, else False
        """
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=file_name)
            return response['Body']
        except ClientError as e:
            print(f"Error downloading file: {e}")           
            return False