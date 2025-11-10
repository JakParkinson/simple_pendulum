
python - <<'PY'
from pypdf import PdfReader, PdfWriter
inputs = ["pendulum_written.pdf", "pendulum.pdf"]  # <-- put your actual original PDF name in place of YOUR_INPUT.pdf
out = "pendulum_with_code.pdf"

w = PdfWriter()
for src in inputs:
    r = PdfReader(src)
    for p in r.pages:
        w.add_page(p)

with open(out, "wb") as f:
    w.write(f)
print("Done ->", out)
PY
