# Copyright 2026 Anthropic PBC
# SPDX-License-Identifier: Apache-2.0
"""Optional S3-backed cache for anvil RPC state, contract sources, and problem statements.

The cache is entirely optional. If `SCONE_S3_BUCKET` is unset, every method is a
no-op and the harness runs normally (just slower on cold starts, since anvil has
to fetch fork state and `cast source` has to hit Etherscan).
"""

import logging
import os
import sys
import tarfile
from pathlib import Path

log = logging.getLogger(__name__)


class Cache:
    def __init__(self) -> None:
        self.bucket = os.environ.get("SCONE_S3_BUCKET")
        self._session = None
        if self.bucket:
            try:
                import aioboto3
            except ImportError:
                log.warning(
                    "SCONE_S3_BUCKET is set but aioboto3 is not installed; "
                    "install scone_bench[cache] to enable S3 caching. Disabling cache."
                )
                self.bucket = None
                return
            self._session = aioboto3.Session(
                region_name=os.environ.get("SCONE_S3_REGION", "us-east-1"),
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
            )

    @property
    def enabled(self) -> bool:
        return self.bucket is not None

    async def get_file(self, key: str, local_path: Path) -> bool:
        """Download `key` to `local_path`. Returns True on cache hit."""
        if not self.enabled:
            return False
        assert self._session is not None
        try:
            local_path.parent.mkdir(parents=True, exist_ok=True)
            async with self._session.client("s3") as s3:
                await s3.download_file(self.bucket, key, str(local_path))
            print(f"[cache] HIT {key}", file=sys.stderr, flush=True)
            return True
        except Exception as e:
            log.info(f"cache miss {key}: {e}")
            print(f"[cache] MISS {key}", file=sys.stderr, flush=True)
            return False

    async def put_file(self, key: str, local_path: Path) -> None:
        if not self.enabled or not local_path.exists():
            return
        assert self._session is not None
        try:
            async with self._session.client("s3") as s3:
                await s3.upload_file(str(local_path), self.bucket, key)
            log.info(f"cached {key}")
        except Exception as e:
            log.warning(f"cache write failed for {key}: {e}")

    async def get_text(self, key: str) -> str | None:
        if not self.enabled:
            return None
        assert self._session is not None
        try:
            async with self._session.client("s3") as s3:
                resp = await s3.get_object(Bucket=self.bucket, Key=key)
                body = await resp["Body"].read()
            print(f"[cache] HIT {key}", file=sys.stderr, flush=True)
            return body.decode("utf-8")
        except Exception:
            print(f"[cache] MISS {key}", file=sys.stderr, flush=True)
            return None

    async def put_text(self, key: str, text: str) -> None:
        if not self.enabled:
            return
        assert self._session is not None
        try:
            async with self._session.client("s3") as s3:
                await s3.put_object(Bucket=self.bucket, Key=key, Body=text.encode("utf-8"))
        except Exception as e:
            log.warning(f"cache write failed for {key}: {e}")

    async def get_tree(self, key: str, dest_dir: str) -> bool:
        """Download and extract a tarball to `dest_dir`. Returns True on cache hit."""
        if not self.enabled:
            return False
        tmp = Path(f"/tmp/scone_cache_{abs(hash(key))}.tar.gz")
        if not await self.get_file(key, tmp):
            return False
        os.makedirs(dest_dir, exist_ok=True)
        with tarfile.open(tmp, "r:gz") as tar:
            tar.extractall(dest_dir, filter="data")
        tmp.unlink(missing_ok=True)
        return True

    async def put_tree(self, key: str, src_dir: str) -> None:
        if not self.enabled or not os.path.isdir(src_dir):  # noqa: ASYNC240
            return
        tmp = Path(f"/tmp/scone_cache_{abs(hash(key))}.tar.gz")
        with tarfile.open(tmp, "w:gz") as tar:
            tar.add(src_dir, arcname=".")
        await self.put_file(key, tmp)
        tmp.unlink(missing_ok=True)
