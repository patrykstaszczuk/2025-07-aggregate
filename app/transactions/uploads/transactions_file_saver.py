import os
from abc import ABC, abstractmethod
from uuid import UUID

from fastapi import UploadFile


class TransactionsCsvFileSaver(ABC):
    @abstractmethod
    def save(self) -> None: ...


class S3TransactionsCsvFileSaver(ABC):
    def save(self) -> None:
        raise NotImplementedError


class LocalTransactionsCsvFileSaver(ABC):
    def __init__(self, media_dir: str) -> None:
        self._media_dir = media_dir

    async def save(self, import_id: UUID, file: UploadFile) -> None:
        save_path = os.path.join(self._media_dir, f"transactions/{import_id}.csv")
        os.makedirs(f"{self._media_dir}/transactions", exist_ok=True)

        with open(save_path, "wb") as out_file:
            content = await file.read()
            out_file.write(content)
