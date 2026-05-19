import cloudinary
from rest_framework.exceptions import ValidationError


class CloudinaryService:
    """
    Service class for handling Cloudinary image uploads and deletions.

    Responsibilities:
    - Upload a file to Cloudinary.
    - Delete a file from Cloudinary.
    - Centralizes all Cloudinary logic for consistency.
    """



    @staticmethod
    def upload(file, resource_type,folder="sendit/"):
        """
        Uploads a file to Cloudinary.

        Args:
            file: File object (from Django request.FILES) to upload.
            folder (str): Cloudinary folder path where the file will be stored.

        Returns:
            tuple: (file_url (str), public_id (str))
                - file_url: URL to access the uploaded file.
                - public_id: Cloudinary public_id for deletion or transformations.

        Raises:
            ValidationError: If upload fails for any reason.
        """
        try:
            result = cloudinary.uploader.upload(
                file,
                folder=folder,
                overwrite=True,
                resource_type=resource_type
            )
            return result["secure_url"], result["public_id"]

        except Exception as e:
            raise ValidationError(
                {"image": f"Cloudinary upload failed: {str(e)}"})

    @staticmethod
    def delete(public_id):
        """
        Deletes a file from Cloudinary.

        Args:
            public_id (str): Cloudinary public_id of the file to delete.

        Notes:
            - Exceptions are caught and logged, but deletion failures do not
              interrupt the main flow.
        """
        try:
            cloudinary.uploader.destroy(public_id)
        except Exception as e:
            print(f"Cloudinary deletion failed: {e}")
