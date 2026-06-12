import io
import pytest
from app.file_extract import extract_resume_text


def _make_min_pdf(text: str) -> bytes:
    objs = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        None,
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    stream = b"BT /F1 24 Tf 72 700 Td (" + text.encode("latin-1") + b") Tj ET"
    objs[3] = b"<< /Length %d >>\nstream\n%s\nendstream" % (len(stream), stream)
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, body in enumerate(objs, start=1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % i + body + b"\nendobj\n"
    xref_pos = len(out)
    out += b"xref\n0 %d\n" % (len(objs) + 1)
    out += b"0000000000 65535 f \n"
    for off in offsets:
        out += b"%010d 00000 n \n" % off
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF" % (len(objs) + 1, xref_pos)
    return bytes(out)


def _make_docx(text: str) -> bytes:
    import docx
    d = docx.Document()
    for line in text.split("\n"):
        d.add_paragraph(line)
    buf = io.BytesIO()
    d.save(buf)
    return buf.getvalue()


class TestResumeTextExtraction:
    def test_utf8_text(self):
        assert extract_resume_text("r.txt", b"Maya Chen\nGPA 3.7") == "Maya Chen\nGPA 3.7"

    def test_utf16_text(self):
        assert extract_resume_text("r.txt", "Maya Chen\nGPA 3.7".encode("utf-16")) == "Maya Chen\nGPA 3.7"

    def test_latin1_text_does_not_raise(self):
        # The original bug: non-UTF-8 bytes used to raise UnicodeDecodeError (500).
        out = extract_resume_text("r.txt", "Résumé Café".encode("latin-1"))
        assert "Caf" in out

    def test_docx(self):
        data = _make_docx("Maya Chen\nBachelor of Science in Pre-Med\nGPA: 3.7")
        out = extract_resume_text("resume.docx", data)
        assert "Pre-Med" in out
        assert "GPA: 3.7" in out

    def test_pdf(self):
        data = _make_min_pdf("Maya Chen Pre-Med GPA 3.7")
        out = extract_resume_text("resume.pdf", data)
        assert "Maya" in out

    def test_pdf_detected_by_magic_bytes_without_extension(self):
        data = _make_min_pdf("Hello Resume")
        out = extract_resume_text("noextension", data)
        assert "Hello" in out

    def test_corrupt_pdf_raises_valueerror(self):
        with pytest.raises(ValueError):
            extract_resume_text("broken.pdf", b"%PDF-1.4 totally not a real pdf")
