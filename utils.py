import hashlib
from pathlib import Path


def safe_hash_file(path, algo: str = "sha256", chunk_size: int = 65536, max_bytes: int = 0):
    """Compute a file hash in a memory-safe streaming way.

    - path: file path
    - algo: hashing algorithm name (sha256, md5, etc.)
    - chunk_size: bytes to read per iteration
    - max_bytes: if >0, only read up to this many bytes (useful for very large files)

    Returns hexadecimal digest string or None on error.
    """
    try:
        p = Path(path)
        if not p.exists() or not p.is_file():
            return None
        h = hashlib.new(algo)
        read = 0
        with p.open("rb") as f:
            while True:
                if max_bytes and read >= max_bytes:
                    break
                to_read = chunk_size
                if max_bytes:
                    to_read = min(to_read, max_bytes - read)
                data = f.read(to_read)
                if not data:
                    break
                h.update(data)
                read += len(data)
        return h.hexdigest()
    except Exception:
        return None

import hashlib
from pathlib import Path
from typing import Optional

def safe_hash_file(path: str, algo: str = "sha256", max_bytes: int = 0) -> Optional[str]:
    """Return hex digest of file or None on error.

    - path: file path
    - algo: currently only 'sha256' supported
    - max_bytes: if >0, read up to this many bytes (useful for large files)
    """
    try:
        p = Path(path)
        if not p.exists() or not p.is_file():
            return None
        if algo.lower() != "sha256":
            return None
        h = hashlib.sha256()
        if max_bytes and max_bytes > 0:
            with p.open("rb") as f:
                h.update(f.read(max_bytes))
        else:
            # read in chunks to avoid memory spikes
            with p.open("rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None
