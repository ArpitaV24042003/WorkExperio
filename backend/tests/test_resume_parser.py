from app.ai.resume_parser import parse_pdf_resume


def test_parse_pdf_resume_text_fallback():
	content = b"John Doe\nSkills: Python, FastAPI\nExperience: Developer"
	result = parse_pdf_resume(content, "resume.txt")

	assert result["filename"] == "resume.txt"
	assert "Python" in result["raw_text"]
	assert any("Skills" in entry for entry in result["extracted"]["skills"])

