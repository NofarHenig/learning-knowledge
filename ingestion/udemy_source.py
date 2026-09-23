import json
import re
from pathlib import Path

import requests

from .source import Document


class UdemySource:
    def __init__(
        self,
        lectures_file: str,
        captions_file: str,
        limit: int | None = None
    ):
        self.lectures_file = Path(lectures_file)
        self.captions_file = Path(captions_file)
        self.limit = limit

    def load(self) -> list[Document]:
        lectures = self._load_json(self.lectures_file)
        captions = self._load_json(self.captions_file)

        captions_by_lecture_id = {}

        for caption in captions:
            lecture_id = caption["lecture_id"]
            vtt_url = caption["english_vtt_url"]

            captions_by_lecture_id[lecture_id] = vtt_url

        documents = []

        lectures_with_captions = [
            lecture
            for lecture in lectures
            if captions_by_lecture_id.get(lecture["id"])
        ]

        if self.limit is not None:
            lectures_with_captions = lectures_with_captions[:self.limit]

        total = len(lectures_with_captions)

        for index, lecture in enumerate(
            lectures_with_captions,
            start=1
        ):
            lecture_id = lecture["id"]
            title = lecture["title"]
            vtt_url = captions_by_lecture_id[lecture_id]

            print(
                f"Downloading lecture "
                f"{index}/{total}: {title}"
            )

            try:
                response = requests.get(
                    vtt_url,
                    timeout=30
                )
                response.raise_for_status()
            except requests.RequestException as error:
                raise RuntimeError(
                    f"Failed to download lecture "
                    f"{lecture_id} - {title}"
                ) from error

            text = self._vtt_to_text(response.text)

            documents.append(
                Document(
                    text=text,
                    metadata={
                        "source": "udemy",
                        "lecture_id": lecture_id,
                        "title": title,
                        "asset_id": lecture["asset_id"]
                    }
                )
            )

        return documents

    def _load_json(self, file_path: Path):
        with file_path.open(
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)

    def _vtt_to_text(self, vtt_text: str) -> str:
        clean_lines = []

        for line in vtt_text.splitlines():
            line = line.strip()

            if not line:
                continue

            if line == "WEBVTT":
                continue

            if "-->" in line:
                continue

            if re.match(r"^\d+$", line):
                continue

            clean_lines.append(line)

        return "\n".join(clean_lines)