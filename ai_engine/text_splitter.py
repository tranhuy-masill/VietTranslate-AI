import re


class TextSplitter:

    def __init__(self, tokenizer, max_tokens=128):

        self.tokenizer = tokenizer
        self.max_tokens = max_tokens

    def count_tokens(self, text):

        return len(
            self.tokenizer.encode(
                text,
                add_special_tokens=True,
                truncation=False
            )
        )

    def split_long_sentence(self, sentence):

        words = sentence.split()
        chunks = []
        current = ""

        for word in words:

            if self.count_tokens(word) > self.max_tokens:

                raise ValueError(
                    "A single word exceeds the model token limit."
                )

            candidate = f"{current} {word}".strip()

            if self.count_tokens(candidate) <= self.max_tokens:

                current = candidate

            else:

                if current:
                    chunks.append(current)

                current = word

        if current:
            chunks.append(current)

        return chunks

    def split(self, text):

        if not text or not text.strip():
            return []

        text = text.strip()

        sentences = re.split(
            r"(?<=[.!?])\s+|\n+",
            text
        )

        chunks = []

        for sentence in sentences:

            sentence = sentence.strip()

            if not sentence:
                continue

            if self.count_tokens(sentence) <= self.max_tokens:

                chunks.append(sentence)

            else:

                chunks.extend(
                    self.split_long_sentence(sentence)
                )

        return chunks