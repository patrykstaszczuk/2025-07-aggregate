import os
from abc import ABC, abstractmethod
from uuid import UUID

from fastapi import UploadFile

from .exceptions import CSVHeaderInvalidException


class TransactionsCsvFileSaver(ABC):
    _FILE_HEADER = [
        "transaction_id",
        "timestamp",
        "amount",
        "currency",
        "customer_id",
        "product_id",
        "quantity",
    ]

    def __init__(self, media_dir: str, delimiter: str) -> None:
        self._media_dir = media_dir
        self._delimiter = delimiter

    def _validate_header(self, header: list[str]) -> bool:
        return header == self._FILE_HEADER

    @abstractmethod
    def save(self, import_id: UUID, file: UploadFile) -> None: ...


class S3TransactionsCsvFileSaver(TransactionsCsvFileSaver):
    def save(self, import_id: UUID, file: UploadFile) -> None:
        raise NotImplementedError


class LocalTransactionsCsvFileSaver(TransactionsCsvFileSaver):
    def save(self, import_id: UUID, file: UploadFile) -> None:
        header_bytes = file.file.readline()
        is_valid = self._validate_header(header=header_bytes.decode("utf-8").strip().split(self._delimiter))
        if not is_valid:
            raise CSVHeaderInvalidException(f"Invalid header. Expected={self._FILE_HEADER}")

        save_path = os.path.join(self._media_dir, f"transactions/{import_id}.csv")
        os.makedirs(f"{self._media_dir}/transactions", exist_ok=True)

        with open(save_path, "wb") as out_file:
            content = file.file.read()
            out_file.write(content)
