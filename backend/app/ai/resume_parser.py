from __future__ import annotations

from io import BytesIO
from typing import Dict, Any, List
import pdfplumber
import re


def format_text(text: str) -> str:
	"""
	Format text to add proper spacing between words.
	Handles cases where words are concatenated without spaces.
	"""
	if not text:
		return ""
	
	# Add space before capital letters (camelCase -> camel Case)
	text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
	
	# Add space around common separators if missing
	text = re.sub(r'([a-zA-Z])([,;:])', r'\1 \2', text)
	text = re.sub(r'([,;:])([a-zA-Z])', r'\1 \2', text)
	
	# Normalize multiple spaces to single space
	text = re.sub(r'\s+', ' ', text)
	
	return text.strip()


def split_skills(skill_text: str) -> List[str]:
	"""
	Split skill text into individual skills, handling various separators.
	"""
	if not skill_text:
		return []
	
	# Common separators: comma, semicolon, pipe, slash, newline
	separators = [',', ';', '|', '/', '\n', '•', '-']
	
	for sep in separators:
		if sep in skill_text:
			skills = [format_text(s.strip()) for s in skill_text.split(sep)]
			return [s for s in skills if s]
	
	# If no separator found, try to split by capital letters
	skills = re.split(r'(?=[A-Z][a-z])', skill_text)
	skills = [format_text(s.strip()) for s in skills if s.strip()]
	return skills


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

	skills_section = False
	current_skills_text = ""
	
	for line in lines:
		lc = line.lower()
		
		# Detect skills section
		if any(token in lc for token in ["skill", "skills", "technologies", "stack", "technical skills"]):
			skills_section = True
			# Extract skills from this line (remove section header)
			skill_line = re.sub(r'^(skills?|technologies?|stack|technical\s+skills?)[:]\s*', '', line, flags=re.IGNORECASE)
			if skill_line.strip():
				current_skills_text += " " + skill_line
			continue
		
		# If we're in skills section, collect skills
		if skills_section:
			if line and not any(token in lc for token in ["education", "experience", "project", "certification"]):
				current_skills_text += " " + line
			else:
				# End of skills section, process collected text
				if current_skills_text:
					skills = split_skills(current_skills_text)
					keywords["skills"].extend(skills)
				skills_section = False
				current_skills_text = ""
		
		# Education detection
		if any(token in lc for token in ["university", "college", "bachelor", "master", "degree", "education"]):
			formatted = format_text(line)
			if formatted and formatted not in keywords["education"]:
				keywords["education"].append(formatted)
		
		# Experience detection
		elif any(token in lc for token in ["experience", "engineer", "intern", "developer", "manager", "worked", "position"]):
			formatted = format_text(line)
			if formatted and formatted not in keywords["experience"]:
				keywords["experience"].append(formatted)
	
	# Process any remaining skills
	if current_skills_text:
		skills = split_skills(current_skills_text)
		keywords["skills"].extend(skills)
	
	# Format all extracted data
	keywords["education"] = [format_text(e) for e in keywords["education"]]
	keywords["experience"] = [format_text(e) for e in keywords["experience"]]
	keywords["skills"] = [format_text(s) for s in keywords["skills"] if format_text(s)]

	return {
		"filename": filename,
		"raw_text": text_content,
		"extracted": keywords,
	}

