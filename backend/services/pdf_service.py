from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os

async def generate_pdf(session_id: str, markdown_text: str) -> str:
    output_path = f"./reports/report_{session_id}.pdf"
    os.makedirs("./reports", exist_ok=True)
    
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    Story = []
    
    for line in markdown_text.split('\n'):
        if line.strip():
            p = Paragraph(line, styles["Normal"])
            Story.append(p)
            Story.append(Spacer(1, 0.2 * 28.34))
            
    doc.build(Story)
    return output_path
