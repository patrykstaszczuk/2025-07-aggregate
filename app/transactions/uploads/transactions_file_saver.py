import os
from abc import ABC, abstractmethod
from uuid import UUID

from fastapi import UploadFile

from app.transactions.config import CSV_FILE_HEADERS_TO_ROW_MAP

from .exceptions import CSVHeaderInvalidException


class TransactionsCsvFileSaver(ABC):

    def __init__(self, media_dir: str, delimiter: str) -> None:
        self._media_dir = media_dir
        self._delimiter = delimiter

    def _validate_header(self, header: list[str]) -> bool:
        return header == list(CSV_FILE_HEADERS_TO_ROW_MAP.keys())

    @abstractmethod
    def save(self, import_id: UUID, file: UploadFile) -> str: ...


class S3TransactionsCsvFileSaver(TransactionsCsvFileSaver):
    def save(self, import_id: UUID, file: UploadFile) -> str:
        raise NotImplementedError


class LocalTransactionsCsvFileSaver(TransactionsCsvFileSaver):
    def save(self, import_id: UUID, file: UploadFile) -> str:
        header_bytes = file.file.readline()
        is_valid = self._validate_header(header=header_bytes.decode("utf-8").strip().split(self._delimiter))
        if not is_valid:
            raise CSVHeaderInvalidException(f"Invalid header. Expected={list(CSV_FILE_HEADERS_TO_ROW_MAP.keys())}")

        save_path = os.path.join(self._media_dir, f"transactions/{import_id}.csv")
        os.makedirs(f"{self._media_dir}/transactions", exist_ok=True)

        with open(save_path, "wb") as out_file:
            content = file.file.read()
            out_file.write(content)
        return save_path
