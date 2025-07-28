import json
import os
import io
from hashlib import sha256, md5
from datetime import datetime
from typing import Optional, cast

import pgpy
from pgpy.constants import CompressionAlgorithm, HashAlgorithm
from pgpy.pgp import PGPMessage

from refiner.config import settings


def mask_email(email: str) -> str:
    """
    Mask email addresses by hashing the local part (before @).

    Args:
        email: The email address to mask

    Returns:
        Masked email address with hashed local part
    """
    if not email or "@" not in email:
        return email

    local_part, domain = email.split("@", 1)
    hashed_local = md5(local_part.encode()).hexdigest()

    return f"{hashed_local}@{domain}"


def encrypt_file(
    encryption_key: str, file_path: str, output_path: Optional[str] = None
) -> str:
    """Symmetrically encrypts a file with an encryption key.

    Args:
        encryption_key: The passphrase to encrypt with
        file_path: Path to the file to encrypt
        output_path: Optional path to save encrypted file (defaults to file_path + .pgp)

    Returns:
        Path to encrypted file
    """
    if output_path is None:
        output_path = f"{file_path}.pgp"

    with open(file_path, "rb") as f:
        buffer = f.read()

    message = pgpy.PGPMessage.new(buffer, compression=CompressionAlgorithm.ZLIB)
    encrypted_message = message.encrypt(
        passphrase=encryption_key, hash=HashAlgorithm.SHA512
    )

    with open(output_path, "wb") as f:
        f.write(str(encrypted_message).encode())

    return output_path


# Not actually used in this project, it's here just for testing.
def decrypt_file(
    encryption_key: str, file_path: str, output_path: Optional[str] = None
) -> str:
    """Symmetrically decrypts a file with an encryption key.

    Args:
        encryption_key: The passphrase to decrypt with
        file_path: Path to the encrypted file
        output_path: Optional path to save decrypted file (defaults to file_path without .pgp)

    Returns:
        Path to decrypted file
    """
    if output_path is None:
        if file_path.endswith(".pgp"):
            output_path = f"{file_path[:-4]}.decrypted"  # Remove .pgp extension
        else:
            output_path = f"{file_path}.decrypted"

    with open(file_path, "rb") as f:
        encrypted_data = f.read()

    message = pgpy.PGPMessage.from_blob(encrypted_data)
    decrypted_message = cast(PGPMessage, message).decrypt(encryption_key)

    with open(output_path, "wb") as f:
        f.write(decrypted_message.message)  # type: ignore

    return output_path


def parse_timestamp(timestamp):
    """Parse a timestamp to a datetime object."""
    if isinstance(timestamp, int):
        return datetime.fromtimestamp(timestamp / 1000.0)
    return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))


def upload_json_to_storj(s3, data) -> str:
    """Upload json to storj, return path to it."""
    if not settings.STORJ_ACCESS_KEY or not settings.STORJ_SECRET_KEY:
        raise Exception(
            "Error: Credentials not found, please check your environment variables"
        )

    json_bytes = io.BytesIO(json.dumps(data).encode("utf-8"))
    key = sha256(json_bytes.getvalue()).hexdigest() + ".libsql.pgp"
    json_bytes.seek(0)
    s3.upload_fileobj(json_bytes, settings.STORJ_BUCKET_NAME, key)
    return f"https://gateway.storjshare.io/{settings.STORJ_BUCKET_NAME}/{key}"


def upload_file_to_storj(s3, file_path=None) -> str:
    """Upload file to storj, return path to it."""
    if file_path is None:
        # Default to the encrypted database file
        file_path = os.path.join(settings.OUTPUT_DIR, "db.libsql.pgp")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    if not settings.STORJ_ACCESS_KEY or not settings.STORJ_SECRET_KEY:
        raise Exception(
            "Error: Credentials not found, please check your environment variables"
        )
    with open(file_path, "rb") as f:
        file_bytes = f.read()
    file_name = sha256(file_bytes).hexdigest() + ".libsql.pgp"
    s3.upload_fileobj(io.BytesIO(file_bytes), settings.STORJ_BUCKET_NAME, file_name)
    return f"{settings.STORJ_BUCKET_NAME}/{file_name}"


# Test with: python -m refiner.utils
# if __name__ == "__main__":
#    s3 = boto3.client(
#        's3',
#        endpoint_url='https://gateway.storjshare.io',
#        aws_access_key_id=settings.STORJ_ACCESS_KEY,
#        aws_secret_access_key=settings.STORJ_SECRET_KEY,
#        config=Config(signature_version='s3v4'),
#        region_name='eu1'
#    )
#    path = upload_file_to_storj(s3)
#    print(f"File uploaded to")
#    print(f"Access at: {path}")

#    path = upload_json_to_storj(s3)
#    print(f"JSON uploaded to IPFS with hash: {path}")
#    print(f"Access at: {settings.IPFS_GATEWAY_URL}/{path}")

#    plaintext_db = os.path.join(settings.OUTPUT_DIR, "db.libsql")
#
#    # Encrypt and decrypt
#    encrypted_path = encrypt_file(settings.REFINEMENT_ENCRYPTION_KEY, plaintext_db)
#    print(f"File encrypted to: {encrypted_path}")
#
#    decrypted_path = decrypt_file(settings.REFINEMENT_ENCRYPTION_KEY, encrypted_path)
#    print(f"File decrypted to: {decrypted_path}")
