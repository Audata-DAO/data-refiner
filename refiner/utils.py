import logging
import requests
import json
import os
from hashlib import md5
from datetime import datetime
from typing import Optional, cast

import pgpy
from pgpy.constants import CompressionAlgorithm, HashAlgorithm
from pgpy.pgp import PGPMessage

from refiner.config import settings


PINATA_FILE_API_ENDPOINT = "https://api.pinata.cloud/pinning/pinFileToIPFS"
PINATA_JSON_API_ENDPOINT = "https://api.pinata.cloud/pinning/pinJSONToIPFS"


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


def upload_json_to_ipfs(data):
    """
    Uploads JSON data to IPFS using Pinata API.
    :param data: JSON data to upload (dictionary or list)
    :return: IPFS hash
    """
    if not settings.PINATA_API_KEY or not settings.PINATA_API_SECRET:
        raise Exception(
            "Error: Pinata IPFS API credentials not found, please check your environment variables"
        )

    headers = {
        "Content-Type": "application/json",
        "pinata_api_key": settings.PINATA_API_KEY,
        "pinata_secret_api_key": settings.PINATA_API_SECRET,
    }

    try:
        response = requests.post(
            PINATA_JSON_API_ENDPOINT, data=json.dumps(data), headers=headers
        )
        response.raise_for_status()

        result = response.json()
        logging.info(
            f"Successfully uploaded JSON to IPFS with hash: {result['IpfsHash']}"
        )
        return result["IpfsHash"]

    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred while uploading JSON to IPFS: {e}")
        raise e


def upload_file_to_ipfs(file_path=None):
    """
    Uploads a file to IPFS using Pinata API (https://pinata.cloud/)
    :param file_path: Path to the file to upload (defaults to encrypted database)
    :return: IPFS hash
    """
    if file_path is None:
        # Default to the encrypted database file
        file_path = None # os.path.join(settings.OUTPUT_DIR, "db.libsql.pgp")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    if not settings.PINATA_API_KEY or not settings.PINATA_API_SECRET:
        raise Exception(
            "Error: Pinata IPFS API credentials not found, please check your environment variables"
        )

    headers = {
        "pinata_api_key": settings.PINATA_API_KEY,
        "pinata_secret_api_key": settings.PINATA_API_SECRET,
    }

    try:
        with open(file_path, "rb") as file:
            files = {"file": file}
            response = requests.post(
                PINATA_FILE_API_ENDPOINT, files=files, headers=headers
            )

        response.raise_for_status()
        result = response.json()
        logging.info(
            f"Successfully uploaded file to IPFS with hash: {result['IpfsHash']}"
        )
        return result["IpfsHash"]

    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred while uploading file to IPFS: {e}")
        raise e


# Test with: python -m refiner.utils.ipfs
if __name__ == "__main__":
    ipfs_hash = upload_file_to_ipfs()
    print(f"File uploaded to IPFS with hash: {ipfs_hash}")
    print(f"Access at: {settings.PINATA_GATEWAY}/{ipfs_hash}")

    ipfs_hash = upload_json_to_ipfs({"data": "data"})
    print(f"JSON uploaded to IPFS with hash: {ipfs_hash}")
    print(f"Access at: {settings.PINATA_GATEWAY}/{ipfs_hash}")
