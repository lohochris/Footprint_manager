import re

from rest_framework import serializers

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MiB
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "text/plain",
}


def validate_file_size(file) -> None:
    """Validate that the uploaded file does not exceed ``MAX_FILE_SIZE``.

    Raises:
        serializers.ValidationError: If the file is too large.
    """
    if hasattr(file, "size") and file.size > MAX_FILE_SIZE:
        raise serializers.ValidationError(
            f"File size exceeds the maximum allowed limit of {MAX_FILE_SIZE // (1024 * 1024)} MiB."
        )


def validate_mime_type(file) -> None:
    """Validate that the file's MIME type is in the allowed list.

    Raises:
        serializers.ValidationError: If the MIME type is not permitted.
    """
    mime = getattr(file, "content_type", None)
    if mime not in ALLOWED_MIME_TYPES:
        raise serializers.ValidationError(f"MIME type '{mime}' is not allowed.")


def validate_sha256_checksum(value: str) -> None:
    """Validate that ``value`` matches a SHA‑256 hex digest.

    Raises:
        serializers.ValidationError: If the checksum is malformed.
    """
    if not re.fullmatch(r"[a-fA-F0-9]{64}", value or ""):
        raise serializers.ValidationError("Checksum must be a 64‑character hexadecimal SHA‑256 string.")


def validate_original_filename(filename: str) -> None:
    """Validate that the original filename is safe and non‑empty.

    Checks for length, disallowed path components and basic character safety.
    Raises:
        serializers.ValidationError: If the filename is invalid.
    """
    if not filename or not filename.strip():
        raise serializers.ValidationError("Original filename must be provided.")
    if len(filename) > 255:
        raise serializers.ValidationError("Original filename must not exceed 255 characters.")
    # Prevent directory traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise serializers.ValidationError("Original filename must not contain path separators.")
