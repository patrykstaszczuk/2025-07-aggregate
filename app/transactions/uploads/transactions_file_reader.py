from typing import Iterator


class LocalTransactionsFileReader:
    def __init__(self, path: str) -> None:
        self._path = path

    def read_file(self) -> Iterator[str]:
        with open(self._path, mode="r", encoding="utf-8") as f:
            for line in f:
                yield line.strip()
