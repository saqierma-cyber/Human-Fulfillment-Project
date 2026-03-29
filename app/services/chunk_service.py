class ChunkService:
    def __init__(self, chunk_size: int, chunk_overlap: int) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_pages(self, pages: list[dict]) -> list[dict]:
        chunks: list[dict] = []
        step = max(self.chunk_size - self.chunk_overlap, 1)

        for page in pages:
            text = page["text"].strip()
            if not text:
                continue

            start = 0
            while start < len(text):
                end = start + self.chunk_size
                chunk_text = text[start:end].strip()
                if chunk_text:
                    chunks.append(
                        {
                            "page_label": page["page_label"],
                            "content": chunk_text,
                        }
                    )
                start += step

        return chunks

