"""Shared image upload for exam content; unrelated to study features."""
import os
import uuid
import httpx
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from app.models.user import User
from app.security import require_teacher

router = APIRouter(prefix='/media', tags=['media'])

SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY', '')
# Preserve existing image URLs/bucket; this storage also contains exam images.
BUCKET = os.getenv('SUPABASE_MEDIA_BUCKET', 'flashcard-images')

def _supabase_headers():
    return {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
    }

def _public_url(file_path: str) -> str:
    return f'{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{file_path}'

async def _upload_to_supabase(file: UploadFile) -> str:
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        raise HTTPException(status_code=500, detail='supabase storage not configured')
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else 'jpg'
    file_path = f'{uuid.uuid4()}.{ext}'
    content = await file.read()
    upload_url = f'{SUPABASE_URL}/storage/v1/object/{BUCKET}/{file_path}'
    headers = {**_supabase_headers(), 'Content-Type': file.content_type or 'image/jpeg'}
    async with httpx.AsyncClient() as client:
        res = await client.post(upload_url, content=content, headers=headers)
        if res.status_code not in (200, 201):
            raise HTTPException(status_code=500, detail=f'image upload failed: {res.text}')
    return _public_url(file_path)


@router.post('/upload-image')
async def upload_image(
    file: UploadFile = File(...),
    teacher: User = Depends(require_teacher),
):
    allowed = {'image/jpeg', 'image/png', 'image/webp', 'image/gif'}
    if file.content_type not in allowed:
        raise HTTPException(status_code=400, detail='only jpeg, png, webp, gif allowed')
    url = await _upload_to_supabase(file)
    return {'url': url}


