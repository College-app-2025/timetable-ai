import boto3
import uuid
from PIL import Image
from io import BytesIO
from typing import Optional, Tuple
from botocore.exceptions import ClientError, NoCredentialsError
from fastapi import HTTPException, UploadFile
import os
from datetime import datetime
import sys

from src.utils.logger_config import get_logger

logger = get_logger("file_conversion")

class FileConversionService:
    """
    Service class for handling image uploads to AWS S3 and converting them to URLs.
    Provides image validation, processing, and cloud storage functionality.
    """

    def __init__(
        self,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        region_name: str = "us-east-1",
        bucket_name: Optional[str] = None
    ):
        
        self.aws_access_key_id = aws_access_key_id or os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = aws_secret_access_key or os.getenv("AWS_SECRET_ACCESS_KEY")
        self.region_name = region_name
        self.bucket_name = bucket_name or os.getenv("AWS_S3_BUCKET_NAME")

        # Initialize S3 client
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.region_name
            )
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to initialize cloud storage")

        # Validate required configuration
        if not self.bucket_name:
            raise ValueError("Bucket name is required. Set AWS_S3_BUCKET_NAME environment variable.")

    def validate_image(self, file: UploadFile) -> bool:
       try:
            # Check content type
            if not file.content_type.startswith('image/'):
                return False

            # Check file extension
            allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
            file_extension = os.path.splitext(file.filename.lower())[1]
            

            return file_extension in allowed_extensions
       
       except Exception as e:
            logger.error(f"Failed to upload image: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to validate image")

    def process_image(
        self, 
        image: Image.Image,
        max_width: int = 1920, 
        max_height: int = 1080,
        quality: int = 85,
        format: str = 'JPEG'
    ) -> BytesIO:
        
        # Convert RGBA/P mode to RGB for JPEG compatibility
        if image.mode in ('RGBA', 'P'):
            # Create white background for transparency
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background

        # Resize image if it exceeds maximum dimensions
        if image.width > max_width or image.height > max_height:
            image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            logger.info(f"Resized image to {image.width}x{image.height}")

        # Save processed image to buffer
        img_buffer = BytesIO()

        # Save with different settings based on format
        if format.upper() == 'JPEG':
            image.save(img_buffer, format=format, quality=quality, optimize=True)
        elif format.upper() == 'PNG':
            image.save(img_buffer, format=format, optimize=True)
        else:
            image.save(img_buffer, format=format)

        img_buffer.seek(0)
        return img_buffer

    def generate_file_key(self, original_filename: str, prefix: str = "images") -> str:
        
        # Get file extension
        file_extension = os.path.splitext(original_filename)[1].lower() if original_filename else '.jpg'

        # Generate unique identifier
        unique_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime('%Y%m%d')

        # Create structured key: prefix/year-month-day/uuid.extension
        file_key = f"{prefix}/{timestamp}/{unique_id}{file_extension}"

        return file_key

    def upload_to_s3(
        self, 
        file_buffer: BytesIO, 
        file_key: str, 
        content_type: str = "image/jpeg",
        metadata: Optional[dict] = None
    ) -> str:
       
        try:
            # Prepare extra arguments for upload
            extra_args = {
                'ContentType': content_type,
                'CacheControl': 'max-age=31536000',  # 1 year cache
            }

            # Add metadata if provided
            if metadata:
                extra_args['Metadata'] = metadata

            # Upload to S3
            self.s3_client.upload_fileobj(
                file_buffer,
                self.bucket_name,
                file_key,
                ExtraArgs=extra_args
            )

            # Generate public URL
            url = f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{file_key}"

            logger.info(f"Successfully uploaded file to S3: {file_key}")
            return url

        except NoCredentialsError:
            logger.error("AWS credentials not found")
            raise HTTPException(status_code=500, detail="Cloud storage credentials not configured")

        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"S3 upload failed with error {error_code}: {str(e)}")

            if error_code == 'NoSuchBucket':
                raise HTTPException(status_code=500, detail="Storage bucket not found")
            elif error_code == 'AccessDenied':
                raise HTTPException(status_code=500, detail="Access denied to storage bucket")
            else:
                raise HTTPException(status_code=500, detail="Failed to upload to cloud storage")

        except Exception as e:
            logger.error(f"Unexpected error during S3 upload: {str(e)}")
            raise HTTPException(status_code=500, detail="Unexpected error during upload")

    async def convert_image_to_url(
        self, 
        file: UploadFile,
        max_width: int = 1920,
        max_height: int = 1080,
        quality: int = 85,
        prefix: str = "images"
    ) -> dict:
       
        try:
            # Validate the uploaded file
            if not self.validate_image(file):
                raise HTTPException(
                    status_code=400, 
                    detail="Invalid image file. Supported formats: JPG, PNG, GIF, BMP, WEBP"
                )

            # Check file size (limit to 10MB)
            contents = await file.read()
            file_size_mb = len(contents) / (1024 * 1024)

            if file_size_mb > 10:
                raise HTTPException(status_code=400, detail="File size must be less than 10MB")

            # Reset file pointer and open image
            file.file.seek(0)

            try:
                image = Image.open(BytesIO(contents))
                original_size = image.size
            except Exception as e:
                logger.error(f"Failed to open image: {str(e)}")
                raise HTTPException(status_code=400, detail="Invalid or corrupted image file")

            # Process the image
            processed_buffer = self.process_image(
                image, 
                max_width=max_width, 
                max_height=max_height,
                quality=quality
            )

            # Generate unique file key
            file_key = self.generate_file_key(file.filename, prefix)

            # Prepare metadata
            metadata = {
                'original_filename': file.filename or 'unknown',
                'original_size': f"{original_size[0]}x{original_size[1]}",
                'processed_size': f"{image.width}x{image.height}",
                'upload_timestamp': datetime.now().isoformat()
            }

            # Upload to S3
            image_url = self.upload_to_s3(
                processed_buffer,
                file_key,
                content_type="image/jpeg",
                metadata=metadata
            )

            # Return success response
            return {
                "success": True,
                "image_url": image_url,
                "file_key": file_key,
                "metadata": {
                    "original_filename": file.filename,
                    "original_size": original_size,
                    "processed_size": (image.width, image.height),
                    "file_size_mb": round(file_size_mb, 2),
                    "upload_timestamp": datetime.now().isoformat()
                }
            }

        except HTTPException:
            # Re-raise HTTP exceptions
            raise

        except Exception as e:
            logger.error(f"Unexpected error in convert_image_to_url: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error during image processing")

    def delete_image_from_s3(self, file_key: str) -> bool:
        """
        Delete an image from S3 storage.

        Args:
            file_key: S3 object key to delete

        Returns:
            bool: True if deletion successful, False otherwise
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_key)
            logger.info(f"Successfully deleted file from S3: {file_key}")
            return True

        except ClientError as e:
            logger.error(f"Failed to delete file from S3: {str(e)}")
            return False

        except Exception as e:
            logger.error(f"Unexpected error during S3 deletion: {str(e)}")
            return False

    def get_image_info(self, file_key: str) -> Optional[dict]:
        """
        Get metadata information about an image stored in S3.

        Args:
            file_key: S3 object key

        Returns:
            dict: Image metadata if found, None otherwise
        """
        try:
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=file_key)

            return {
                "file_key": file_key,
                "size_bytes": response.get('ContentLength', 0),
                "content_type": response.get('ContentType', 'unknown'),
                "last_modified": response.get('LastModified'),
                "metadata": response.get('Metadata', {})
            }

        except ClientError as e:
            if e.response['Error']['Code'] == 'NotFound':
                logger.warning(f"File not found in S3: {file_key}")
                return None
            else:
                logger.error(f"Error getting file info from S3: {str(e)}")
                return None

        except Exception as e:
            logger.error(f"Unexpected error getting file info: {str(e)}")
            return None
        
type_conversion = FileConversionService()        