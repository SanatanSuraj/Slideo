import boto3
import os
import uuid
from typing import Optional
from botocore.exceptions import ClientError, NoCredentialsError
from utils.get_env import get_env_variable
from dotenv import load_dotenv

# Load environment variables if not already loaded
if not os.getenv("AWS_S3_ACCESS_KEY"):
    load_dotenv()


class S3Service:
    def __init__(self):
        self.access_key = get_env_variable("AWS_S3_ACCESS_KEY")
        self.secret_key = get_env_variable("AWS_S3_SECRET_KEY")
        self.region = get_env_variable("AWS_S3_REGION", "us-east-1")
        self.bucket = get_env_variable("AWS_S3_BUCKET")
        
        if not all([self.access_key, self.secret_key, self.bucket]):
            raise ValueError("AWS S3 credentials not properly configured")
        
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region
        )
    
    def upload_file(self, file_path: str, s3_key: Optional[str] = None) -> str:
        """
        Upload a file to S3 and return the public URL
        
        Args:
            file_path: Local path to the file to upload
            s3_key: Optional S3 key (path) for the file. If not provided, generates one
            
        Returns:
            Public URL of the uploaded file
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Generate S3 key if not provided
            if not s3_key:
                filename = os.path.basename(file_path)
                # Generate unique filename with UUID
                name, ext = os.path.splitext(filename)
                unique_filename = f"{name}-{uuid.uuid4()}{ext}"
                s3_key = f"images/{unique_filename}"
            
            print(f"🔄 S3 UPLOAD: Uploading {file_path} to s3://{self.bucket}/{s3_key}")
            
            # Upload file to S3
            self.s3_client.upload_file(
                file_path,
                self.bucket,
                s3_key,
                ExtraArgs={
                    'ContentType': self._get_content_type(file_path),
                    'ACL': 'public-read'  # Make the file publicly accessible
                }
            )
            
            # Generate public URL
            public_url = f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{s3_key}"
            print(f"✅ S3 UPLOAD: Successfully uploaded to {public_url}")
            
            return public_url
            
        except NoCredentialsError:
            raise Exception("AWS credentials not found")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchBucket':
                raise Exception(f"S3 bucket '{self.bucket}' does not exist")
            elif error_code == 'AccessDenied':
                raise Exception("Access denied to S3 bucket")
            else:
                raise Exception(f"S3 upload failed: {e}")
        except Exception as e:
            raise Exception(f"Failed to upload file to S3: {e}")
    
    def upload_file_from_bytes(self, file_bytes: bytes, filename: str, content_type: str = "image/png") -> str:
        """
        Upload file bytes directly to S3
        
        Args:
            file_bytes: File content as bytes
            filename: Original filename
            content_type: MIME type of the file
            
        Returns:
            Public URL of the uploaded file
        """
        try:
            # Generate unique filename
            name, ext = os.path.splitext(filename)
            unique_filename = f"{name}-{uuid.uuid4()}{ext}"
            s3_key = f"images/{unique_filename}"
            
            print(f"🔄 S3 UPLOAD: Uploading bytes to s3://{self.bucket}/{s3_key}")
            
            # Upload bytes to S3
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=s3_key,
                Body=file_bytes,
                ContentType=content_type,
                ACL='public-read'
            )
            
            # Generate public URL
            public_url = f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{s3_key}"
            print(f"✅ S3 UPLOAD: Successfully uploaded to {public_url}")
            
            return public_url
            
        except NoCredentialsError:
            raise Exception("AWS credentials not found")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchBucket':
                raise Exception(f"S3 bucket '{self.bucket}' does not exist")
            elif error_code == 'AccessDenied':
                raise Exception("Access denied to S3 bucket")
            else:
                raise Exception(f"S3 upload failed: {e}")
        except Exception as e:
            raise Exception(f"Failed to upload bytes to S3: {e}")
    
    def delete_file(self, s3_key: str) -> bool:
        """
        Delete a file from S3
        
        Args:
            s3_key: S3 key (path) of the file to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"🗑️ S3 DELETE: Deleting s3://{self.bucket}/{s3_key}")
            
            self.s3_client.delete_object(Bucket=self.bucket, Key=s3_key)
            
            print(f"✅ S3 DELETE: Successfully deleted {s3_key}")
            return True
            
        except ClientError as e:
            print(f"❌ S3 DELETE: Failed to delete {s3_key}: {e}")
            return False
        except Exception as e:
            print(f"❌ S3 DELETE: Unexpected error deleting {s3_key}: {e}")
            return False
    
    def get_file_url(self, s3_key: str) -> str:
        """
        Get the public URL for an S3 object
        
        Args:
            s3_key: S3 key (path) of the file
            
        Returns:
            Public URL of the file
        """
        return f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{s3_key}"
    
    def extract_s3_key_from_url(self, url: str) -> Optional[str]:
        """
        Extract S3 key from a public S3 URL
        
        Args:
            url: Public S3 URL
            
        Returns:
            S3 key if URL is valid S3 URL, None otherwise
        """
        try:
            if f"{self.bucket}.s3.{self.region}.amazonaws.com" in url:
                # Extract the key part after the domain
                key = url.split(f"{self.bucket}.s3.{self.region}.amazonaws.com/")[-1]
                return key
            return None
        except Exception:
            return None
    
    def _get_content_type(self, file_path: str) -> str:
        """
        Get content type based on file extension
        
        Args:
            file_path: Path to the file
            
        Returns:
            MIME type string
        """
        ext = os.path.splitext(file_path)[1].lower()
        content_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.svg': 'image/svg+xml',
            '.bmp': 'image/bmp',
            '.tiff': 'image/tiff',
            '.ico': 'image/x-icon'
        }
        return content_types.get(ext, 'application/octet-stream')
    
    def is_s3_url(self, url: str) -> bool:
        """
        Check if a URL is an S3 URL
        
        Args:
            url: URL to check
            
        Returns:
            True if it's an S3 URL, False otherwise
        """
        return f"{self.bucket}.s3.{self.region}.amazonaws.com" in url


# Global instance - lazy initialization
_s3_service_instance = None

def get_s3_service():
    """Get the global S3 service instance with lazy initialization"""
    global _s3_service_instance
    if _s3_service_instance is None:
        _s3_service_instance = S3Service()
    return _s3_service_instance

# For backward compatibility - this will be initialized when first accessed
class S3ServiceProxy:
    def __getattr__(self, name):
        return getattr(get_s3_service(), name)

s3_service = S3ServiceProxy()
