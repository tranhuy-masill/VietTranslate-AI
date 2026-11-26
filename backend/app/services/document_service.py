
from io import BytesIO

from docx import Document

from ai_engine.text_splitter import TextSplitter


class DocumentService:

    def __init__(self, translation_service):

        self.translation_service = translation_service

        self.splitter = TextSplitter(
            tokenizer=translation_service.engine.tokenizer,
            max_tokens=128
        )

    def translate_text(self, text, beam_size=4):

        if not text.strip():
            return text

        chunks = self.splitter.split(text)

        translated_chunks = []

        for chunk in chunks:

            result = self.translation_service.translate(
                text=chunk,
                beam_size=beam_size,
                max_new_tokens=256
            )

            translated_chunks.append(
                result["translated_text"]
            )

        return " ".join(translated_chunks)

    def translate_paragraph(self, paragraph, beam_size):

        # Skip complex paragraphs containing images,
        # hyperlinks, fields or mathematical equations.
        unsupported = paragraph._p.xpath(
            ".//w:drawing | .//w:pict | "
            ".//w:hyperlink | .//w:fldChar | "
            ".//w:instrText | .//m:oMath"
        )

        if unsupported:
            return

        original_text = paragraph.text

        if not original_text.strip():
            return

        translated_text = self.translate_text(
            original_text,
            beam_size
        )

        # Preserve paragraph style and first run formatting.
        if paragraph.runs:

            paragraph.runs[0].text = translated_text

            for run in paragraph.runs[1:]:
                run.text = ""

        else:

            paragraph.add_run(translated_text)

    def translate_table(self, table, beam_size, visited):

        for row in table.rows:

            for cell in row.cells:

                # Avoid translating merged cells twice.
                if cell._tc in visited:
                    continue

                visited.add(cell._tc)

                for paragraph in cell.paragraphs:

                    self.translate_paragraph(
                        paragraph,
                        beam_size
                    )

                for nested_table in cell.tables:

                    self.translate_table(
                        nested_table,
                        beam_size,
                        visited
                    )

    def translate_document(self, file_bytes, beam_size=4):

        document = Document(
            BytesIO(file_bytes)
        )

        visited = set()

        # Translate document paragraphs.
        for paragraph in document.paragraphs:

            self.translate_paragraph(
                paragraph,
                beam_size
            )

        # Translate tables.
        for table in document.tables:

            self.translate_table(
                table,
                beam_size,
                visited
            )

        # Export translated Word document.
        output = BytesIO()

        document.save(output)

        output.seek(0)

        return output
