from pathlib import Path
from typing import Iterable, Tuple
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch
from pypdf import PdfReader, PdfWriter
import textwrap
import tempfile

# ---- EDIT THESE if you like ----
PAGE_SIZE = letter
MARGIN_L = 0.75 * inch
MARGIN_R = 0.75 * inch
MARGIN_T = 0.75 * inch
MARGIN_B = 0.75 * inch
FONT_NAME = "Courier"
FONT_SIZE = 9.5
TITLE = "Appendix: Simulation Code"
TITLE_FONT_SIZE = 12
# --------------------------------

# Register Courier (usually built-in, but this keeps it explicit)
try:
    pdfmetrics.registerFont(TTFont("Courier", "Courier.ttf"))
except Exception:
    # If not available as TTF, ReportLab's built-in "Courier" still works.
    pass

def wrap_code_lines(code: str, max_width_pts: float) -> Iterable[str]:
    """Yield lines wrapped to the page width in a monospace font."""
    # Approximates characters per line in monospace:
    # width per char (Courier) at given size:
    char_width = pdfmetrics.stringWidth("M", FONT_NAME, FONT_SIZE)
    max_chars = max(10, int(max_width_pts // char_width))
    for raw_line in code.splitlines():
        # Keep indentation; wrap without breaking words when possible
        # preserve whitespace by expanding tabs
        expanded = raw_line.expandtabs(4)
        # textwrap with long words allowed (code can be long)
        wrapped = textwrap.wrap(
            expanded, width=max_chars, replace_whitespace=False,
            drop_whitespace=False, break_long_words=True, break_on_hyphens=False
        ) or [""]
        for w in wrapped:
            yield w

def render_code_to_pdf_pages(code: str, out_pdf_path: Path) -> None:
    """Render code into one or more PDF pages."""
    page_w, page_h = PAGE_SIZE
    usable_w = page_w - (MARGIN_L + MARGIN_R)
    usable_h = page_h - (MARGIN_T + MARGIN_B)

    # Line spacing
    leading = FONT_SIZE * 1.25

    c = canvas.Canvas(str(out_pdf_path), pagesize=PAGE_SIZE)

    def new_page(header=True):
        c.setFont(FONT_NAME, FONT_SIZE)
        y = page_h - MARGIN_T
        if header and TITLE:
            c.setFont(FONT_NAME, TITLE_FONT_SIZE)
            c.drawString(MARGIN_L, y, TITLE)
            y -= (TITLE_FONT_SIZE * 1.6)
            c.setFont(FONT_NAME, FONT_SIZE)
        return y

    y = new_page(header=True)

    for line in wrap_code_lines(code, usable_w):
        if y < MARGIN_B + leading:  # start a new page
            c.showPage()
            y = new_page(header=False)
        c.drawString(MARGIN_L, y, line)
        y -= leading

    c.showPage()
    c.save()

def append_pdf(base_pdf: Path, appendix_pdf: Path, out_pdf: Path) -> None:
    reader_base = PdfReader(str(base_pdf))
    reader_appendix = PdfReader(str(appendix_pdf))
    writer = PdfWriter()

    for page in reader_base.pages:
        writer.add_page(page)
    for page in reader_appendix.pages:
        writer.add_page(page)

    with out_pdf.open("wb") as f:
        writer.write(f)

if __name__ == "__main__":
    # --- Inputs: edit these paths or adapt to argparse ---
    input_pdf = Path("pendulum.pdf")          # existing PDF
    output_pdf = Path("output_with_code.pdf")   # where to write result

    # Your code as a triple-quoted string (paste it exactly):
    CODE_SNIPPET = r'''import numpy as np

g=9.81 # m/s^2
pendulum_length = 1 # meters
theta_0 = 40 # degrees
t_final = 16.5 # seconds
dt=0.005 # seconds
n_steps=int(t_final/dt)

def pendulum_rk4(dt, n_steps, initial_theta_degrees, l):
    """ RK4 integrator to solve the Simple Pendulum ODE system:
        d^2 theta / d theta ^2 = -(g/l)sin(theta)
        returns the x,y position, time, theta and d theta/ dt arrays with n_steps steps
    """
    theta_old = initial_theta_degrees*(np.pi/180)

    theta_dot_old = 0

    pos_x = np.zeros(n_steps+1)
    pos_y = np.zeros(n_steps+1)
    times = np.zeros(n_steps+1)
    thetas = np.zeros(n_steps+1)
    theta_dots = np.zeros(n_steps+1)

    ## initial conditions
    pos_x[0] = np.sin(theta_old)*l
    pos_y[0] = -np.cos(theta_old)*l
    times[0] = 0
    thetas[0] = theta_old
    

    t_new = 0
    for i in range(n_steps):
        t_new += dt

        
        k1_theta = theta_dot_old
        k1_theta_dot = -(g/l)*np.sin(theta_old) ## use ODE equation for k_theta_dot

        k2_theta = theta_dot_old + k1_theta_dot*dt/2 
        k2_theta_dot = -(g/l)*np.sin(theta_old + k1_theta*dt/2)

        k3_theta = theta_dot_old + k2_theta_dot*dt/2
        k3_theta_dot = -(g/l)*np.sin(theta_old + k2_theta*dt/2)


        k4_theta = theta_dot_old + k3_theta_dot*dt
        k4_theta_dot =  -(g/l)*np.sin(theta_old + k3_theta*dt)

        ## use k1,k2,k3,k4 to update theta and dtheta/ dt
        theta_new = theta_old + dt * (k1_theta + 2*k2_theta + 2*k3_theta + k4_theta)/6 
        theta_dot_new = theta_dot_old + dt * (k1_theta_dot + 2*k2_theta_dot + 2*k3_theta_dot + k4_theta_dot)/6 


        ### update arrays
        pos_x[i+1] = np.sin(theta_new)*l
        pos_y[i+1] = -np.cos(theta_new)*l
        times[i+1] = times[i]+dt
        thetas[i+1] = theta_new
        theta_dots[i+1] = theta_dot_new
        ###

        theta_old = theta_new
        theta_dot_old = theta_dot_new
        
    return pos_x, pos_y, times, thetas, theta_dots


g=9.81 # m/s^2
pendulum_length = 1 # meters
theta_0 = 40 # degrees
t_final = 16.5 # seconds
dt=0.005 # seconds
n_steps=int(t_final/dt)


pos_x, pos_y, times, thetas, theta_dots = pendulum_rk4(dt, n_steps, theta_0, pendulum_length)

print(f"After {round(times[-1], 2)} seconds, the pedulum bob has height {round(5 + pos_y[-1], 2)} meters")
'''

    # --- Work ---
    if not input_pdf.exists():
        raise SystemExit(f"Input PDF not found: {input_pdf}")

    with tempfile.TemporaryDirectory() as td:
        tmp_code_pdf = Path(td) / "code_pages.pdf"
        render_code_to_pdf_pages(CODE_SNIPPET, tmp_code_pdf)
        append_pdf(input_pdf, tmp_code_pdf, output_pdf)

    print(f"Done. Wrote: {output_pdf.resolve()}")
