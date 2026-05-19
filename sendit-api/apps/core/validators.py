from django.core.exceptions import ValidationError


def validate_image_size(file, max_mb=5):
    """
    Validate that uploaded image does not exceed the maximum allowed size.

    Args:
        file: Uploaded file (InMemoryUploadedFile or TemporaryUploadedFile)
        max_mb (int): Maximum size in megabytes (default 5MB)

    Raises:
        ValidationError: If file size exceeds max_mb
    """
    if file.size > max_mb * 1024 * 1024:
        raise ValidationError(f"Maximum file size is {max_mb} MB")
