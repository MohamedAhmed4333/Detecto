import hashlib
import os
import re


def calculate_hash(file_path, hash_type="md5"):
    try:
        hash_func = getattr(hashlib, hash_type)()
    except AttributeError:
        raise ValueError(f"Unsupported hash type: {hash_type}")

    with open(file_path, "rb") as f:
        while chunk := f.read(4096):
            hash_func.update(chunk)

    return hash_func.hexdigest()


def calculate_all_hashes(file_path):
    hashers = {
        "md5": hashlib.md5(),
        "sha1": hashlib.sha1(),
        "sha256": hashlib.sha256()
    }

    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            for h in hashers.values():
                h.update(chunk)

    return {name: h.hexdigest() for name, h in hashers.items()}


def get_file_info(file_path):

    return {
        "file_name": os.path.basename(file_path),
        "file_size": os.path.getsize(file_path)
    }

def analyze_hashes(file_path):
    return {
        "file_info": get_file_info(file_path),
        "hashes": calculate_all_hashes(file_path)
    }



def is_valid_hash(hash_value, hash_type="sha256"):
    patterns = {
        "md5": r"^[a-fA-F0-9]{32}$",
        "sha1": r"^[a-fA-F0-9]{40}$",
        "sha256": r"^[a-fA-F0-9]{64}$"
    }
    return bool(re.match(patterns[hash_type], hash_value))


known_hashes = set()

def is_duplicate(file_hash):
    if file_hash in known_hashes:
        return True
    known_hashes.add(file_hash)
    return False


def get_file_type(file_path):
    with open(file_path, "rb") as f:
        header = f.read(2)

    if header == b'MZ':
        return "Windows Executable (PE)"
    return "Unknown"


def get_sha256(file_path):
    return calculate_hash(file_path, "sha256")