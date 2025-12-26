import cloudinary
import cloudinary.uploader

def upload_logo(file_stream):
    result = cloudinary.uploader.upload(
        file_stream,
        folder="barbersaas/logos",
        resource_type="image"
    )
    return result["secure_url"]
