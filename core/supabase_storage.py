"""
Supabase Storage & Image Optimization Module for Bahi Hata.

Handles:
1. Converting uploaded images to WebP format for 60-80% smaller payload and ultra-fast mobile loading.
2. Direct upload to Supabase Storage Public Bucket ('bahi-hata-images').
3. Returning public CDN URLs with edge caching.
"""

import os
import io
import uuid
import logging
from datetime import datetime
from PIL import Image, ImageOps
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

def optimize_image(file_obj, max_dimension=1200, quality=82) -> tuple[bytes, str]:
    """
    Optimizes and converts any input image (JPEG, PNG, WEBP, HEIC, etc.) to modern WebP.
    Resizes if larger than max_dimension while preserving aspect ratio.
    Strips unnecessary metadata to reduce byte size and improve latency.
    """
    try:
        image = Image.open(file_obj)
        # Fix orientation from EXIF if present
        image = ImageOps.exif_transpose(image)

        # Convert palette/RGBA modes appropriately for WebP
        if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
            image = image.convert('RGBA')
        else:
            image = image.convert('RGB')

        # Resize if dimensions exceed max_dimension
        w, h = image.size
        if w > max_dimension or h > max_dimension:
            image.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)

        output_buffer = io.BytesIO()
        image.save(output_buffer, format='WEBP', quality=quality, optimize=True)
        optimized_bytes = output_buffer.getvalue()
        return optimized_bytes, 'image/webp'
    except Exception as e:
        logger.error(f"Image optimization error: {e}")
        # If pillow processing fails, read raw bytes
        if hasattr(file_obj, 'seek'):
            file_obj.seek(0)
        raw_bytes = file_obj.read()
        content_type = getattr(file_obj, 'content_type', 'image/jpeg')
        return raw_bytes, content_type


def upload_to_supabase(file_obj, folder='books', filename_prefix='item') -> dict:
    """
    Uploads an image file to Supabase Public Storage bucket.
    
    Returns:
        dict: {
            'success': True/False,
            'url': 'https://<project_ref>.supabase.co/storage/v1/object/public/bahi-hata-images/books/...webp',
            'error': None or error message
        }
    """
    supabase_url = getattr(settings, 'SUPABASE_URL', '').rstrip('/')
    supabase_key = getattr(settings, 'SUPABASE_SERVICE_ROLE_KEY', '') or getattr(settings, 'SUPABASE_ANON_KEY', '')
    bucket_name = getattr(settings, 'SUPABASE_STORAGE_BUCKET', 'bahi-hata-images')

    # 1. Optimize image to WebP
    optimized_bytes, mime_type = optimize_image(file_obj)
    ext = 'webp' if mime_type == 'image/webp' else 'jpg'

    # 2. Build unique object path: e.g. books/2026/09/prefix_uuid.webp
    now = datetime.now()
    unique_id = uuid.uuid4().hex[:10]
    safe_prefix = "".join(c for c in filename_prefix if c.isalnum() or c in ('-', '_')).strip()[:30] or 'image'
    object_path = f"{folder}/{now.year}/{now.month:02d}/{safe_prefix}_{unique_id}.{ext}"

    # If Supabase is not configured (e.g. offline local development without credentials), fallback
    if not supabase_url or not supabase_key:
        logger.warning("Supabase credentials missing. Falling back to local media storage.")
        media_dir = os.path.join(settings.MEDIA_ROOT, folder)
        os.makedirs(media_dir, exist_ok=True)
        local_filename = f"{safe_prefix}_{unique_id}.{ext}"
        local_path = os.path.join(media_dir, local_filename)
        with open(local_path, 'wb') as f:
            f.write(optimized_bytes)
        local_url = f"{settings.MEDIA_URL}{folder}/{local_filename}"
        return {
            'success': True,
            'url': local_url,
            'size_bytes': len(optimized_bytes),
            'storage': 'local_fallback'
        }

    # 3. Upload via Supabase Storage REST API
    upload_endpoint = f"{supabase_url}/storage/v1/object/{bucket_name}/{object_path}"
    headers = {
        'Authorization': f'Bearer {supabase_key}',
        'apikey': supabase_key,
        'Content-Type': mime_type,
        'x-upsert': 'true'
    }

    try:
        response = requests.post(upload_endpoint, data=optimized_bytes, headers=headers, timeout=15)
        
        # If bucket does not exist (404 / 400), try to create bucket if using service role key
        if response.status_code in (404, 400) and 'Bucket not found' in response.text:
            create_bucket_endpoint = f"{supabase_url}/storage/v1/bucket"
            requests.post(create_bucket_endpoint, json={
                'id': bucket_name,
                'name': bucket_name,
                'public': True,
                'file_size_limit': 10485760, # 10MB
                'allowed_mime_types': ['image/*']
            }, headers=headers, timeout=10)
            # Retry upload
            response = requests.post(upload_endpoint, data=optimized_bytes, headers=headers, timeout=15)

        if response.status_code in (200, 201):
            public_url = f"{supabase_url}/storage/v1/object/public/{bucket_name}/{object_path}"
            return {
                'success': True,
                'url': public_url,
                'size_bytes': len(optimized_bytes),
                'storage': 'supabase'
            }
        else:
            logger.error(f"Supabase storage upload error [{response.status_code}]: {response.text}")
            return {
                'success': False,
                'error': f"Upload failed ({response.status_code}): {response.text}"
            }
    except Exception as e:
        logger.error(f"Supabase connection exception during upload: {e}")
        return {
            'success': False,
            'error': str(e)
        }
