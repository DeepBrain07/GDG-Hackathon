from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from apps.core.models import Media
from apps.core.services.cloudinary_service import CloudinaryService
from rest_framework.exceptions import ValidationError
# from django.excep


class MediaService:
    """
    Service class for managing Media objects and handling all
    business logic related to file uploads, ordering, and tagging.

    Responsibilities:
    - Attach a new file to any model instance.
    - Replace an existing media file.
    - Delete media safely (both DB and Cloudinary).
    - Bulk upload multiple files to a model instance.
    - Enforce limits and rules like max files and unique tags.
    """

    MAX_FILES_PER_OBJECT = settings.MAX_FILES_PER_OBJECT
    MAX_IMAGE_SIZE_MB = settings.MAX_FILES_PER_OBJECT
    MAX_DOC_SIZE_MB = (settings.MAX_FILES_PER_OBJECT) * 2

    # Allowed MIME types
    ALLOWED_IMAGE_TYPES = ('image/jpeg', 'image/png')
    ALLOWED_DOC_TYPES = ('application/pdf',
                         'application/msword',  # .doc
                         'application/vnd.openxmlformats-officedocument.wordprocessingml.document')  # .docx

    @staticmethod
    def validate_file(file, allowed_types=None, max_mb=None):
        """
        Validate uploaded file type and size.
        Determines whether file is image or document automatically.
        """
        # Determine file category
        print(
            f"[MediaService] Uploading file: {file.name}, type: {file.content_type}, size: {file.size}")

        if hasattr(file, 'content_type'):
            content_type = file.content_type
        else:
            raise ValidationError("Cannot determine file type")

        if content_type in MediaService.ALLOWED_IMAGE_TYPES:
            max_size = max_mb or MediaService.MAX_IMAGE_SIZE_MB
        elif content_type in MediaService.ALLOWED_DOC_TYPES:
            max_size = max_mb or MediaService.MAX_DOC_SIZE_MB
        else:
            raise ValidationError(
                f"Unsupported file type: {content_type}. "
                f"Allowed: {MediaService.ALLOWED_IMAGE_TYPES + MediaService.ALLOWED_DOC_TYPES}"
            )

        # Size check
        if file.size > max_size * 1024 * 1024:
            raise ValidationError(f"File size cannot exceed {max_size} MB")

    @staticmethod
    def get_resource_type(file):
        """
        Determine Cloudinary resource type based on MIME type.
        """
        content_type = file.content_type

        if content_type in MediaService.ALLOWED_IMAGE_TYPES:
            return "image"
        elif content_type in MediaService.ALLOWED_DOC_TYPES:
            return "raw"   # 🔥 IMPORTANT for docs
        else:
            raise ValidationError(f"Unsupported file type: {content_type}")

    @staticmethod
    @transaction.atomic
    def attach_file(file, instance, tag="", order=None):
        """
        Attach a new media file to a given model instance.

        Args:
            file: File object to upload.
            instance: Django model instance to associate the media with.
            tag (str): Optional tag (e.g., "avatar", "document", "selfie", "gallery").
            order (int): Optional explicit order; defaults to next available.

        Returns:
            Media instance: Newly created Media object.

        Raises:
            ValueError: If maximum number of files for this object is exceeded.
        """
        # validate the file type and size
        print(f"[media attach]: attachined {instance}")
        MediaService.validate_file(file)

        content_type = ContentType.objects.get_for_model(instance)

        existing = Media.objects.filter(
            content_type=content_type,
            object_id=instance.pk
        ).order_by('order')

        if existing.count() >= MediaService.MAX_FILES_PER_OBJECT:
            raise ValueError("Maximum number of files reached")

        if tag in ["avatar", "document", "selfie"]:
            Media.objects.filter(
                content_type=content_type,
                object_id=instance.pk,
                tag=tag
            ).delete()  # one of these type can exist for an object

        resource_type = MediaService.get_resource_type(file)
        file_url, public_id = CloudinaryService.upload(
            file, resource_type=resource_type)

        if order is None:
            order = existing.count()

        if existing.count() == 0:
            tag = tag or "thumbnail"
    
        return Media.objects.create(
            file_url=file_url,
            public_id=public_id,
            content_type=content_type,
            object_id=instance.pk,
            tag=tag,
            order=order
        )

    @staticmethod
    @transaction.atomic
    def replace_file(file, media_instance):
        """
        Replace an existing media file with a new one.

        Args:
            file: New file object to upload.
            media_instance: Existing Media object to replace.

        Returns:
            Media instance: Updated Media object.

        Notes:
            - Deletes old file from Cloudinary.
            - Updates file_url and public_id in DB.
        """
        if media_instance.public_id:
            CloudinaryService.delete(media_instance.public_id)

        resource_type = MediaService.get_resource_type(file)
        file_url, public_id = CloudinaryService.upload(
            file, resource_type=resource_type)

        media_instance.file_url = file_url
        media_instance.public_id = public_id
        media_instance.save()

        return media_instance

    @staticmethod
    @transaction.atomic
    def delete_media(media_instance):
        """
        Safely delete a media instance from both Cloudinary and the database.

        Args:
            media_instance: Media object to delete.

        Notes:
            - Deletes Cloudinary file first to avoid orphaned storage.
        """
        if media_instance.public_id:
            CloudinaryService.delete(media_instance.public_id)

        media_instance.delete()

    @staticmethod
    @transaction.atomic
    def bulk_upload(files, instance, tag="gallery"):
        """
        Bulk upload multiple files to a model instance.

        Args:
            files (list): List of file objects to upload.
            instance: Model instance to attach media to.
            tag (str): Optional tag for all uploaded files.

        Returns:
            list: List of created Media objects.

        Raises:
            ValueError: If total files exceed MAX_FILES_PER_OBJECT.
        """
        content_type = ContentType.objects.get_for_model(instance)

        existing_count = Media.objects.filter(
            content_type=content_type,
            object_id=instance.pk
        ).count()

        if existing_count + len(files) > MediaService.MAX_FILES_PER_OBJECT:
            raise ValueError("Uploading these files exceeds allowed limit")

        created = []

        for index, file in enumerate(files):
            resource_type = MediaService.get_resource_type(file)

            file_url, public_id = CloudinaryService.upload(
                file, resource_type=resource_type)

            media = Media.objects.create(
                file_url=file_url,
                public_id=public_id,
                content_type=content_type,
                object_id=instance.pk,
                tag="thumbnail" if existing_count == 0 and index == 0 else tag,
                order=existing_count + index
            )
            created.append(media)

        return created


