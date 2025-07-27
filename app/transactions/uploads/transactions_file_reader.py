import csv
from abc import ABC, abstractmethod
from typing import Iterator


class FileReader(ABC):
    def __init__(self, path: str, delimiter: str) -> None:
        self._path = path
        self._delimiter = delimiter

    @abstractmethod
    def read_file(self) -> Iterator[list[str]]:
        pass


class PandasLocalTransactionsCSVFileReader(FileReader):
    def read_file(self) -> Iterator[list[str]]:
        raise NotImplementedError()


class StandardLocalTransactionsCSVFileReader(FileReader):
    def read_file(self) -> Iterator[list[str]]:
        with open(self._path, mode="r", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter=self._delimiter)
            for row in reader:
                yield row
