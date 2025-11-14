from __future__ import annotations

from io import BytesIO
from typing import Dict, Any
import pdfplumber


def parse_pdf_resume(file_bytes: bytes, filename: str) -> Dict[str, Any]:
	"""
	Simple resume parsing placeholder.
	Extracts raw text and uses naive keyword spotting to build a structured payload.
	"""
	text_content = ""
	try:
		with pdfplumber.open(BytesIO(file_bytes)) as pdf:
			pages = [page.extract_text() or "" for page in pdf.pages]
			text_content = "\n".join(pages)
	except Exception:
		text_content = file_bytes.decode("utf-8", errors="ignore")

	lines = [line.strip() for line in text_content.splitlines() if line.strip()]
	keywords = {
		"education": [],
		"experience": [],
		"skills": [],
	}

	for line in lines:
		lc = line.lower()
		if any(token in lc for token in ["university", "college", "bachelor", "master", "degree"]):
			keywords["education"].append(line)
		elif any(token in lc for token in ["experience", "engineer", "intern", "developer", "manager"]):
			keywords["experience"].append(line)
		elif any(token in lc for token in ["skill", "skills", "technologies", "stack"]):
			keywords["skills"].append(line)

	return {
		"filename": filename,
		"raw_text": text_content,
		"extracted": keywords,
	}

