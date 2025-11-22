from __future__ import annotations

from typing import List, Dict, Any, Optional
import os
import zipfile
import tempfile
from pathlib import Path
import json

from openai import OpenAI


def analyze_code_comprehensive(
	files_data: List[Dict[str, str]],  # List of {"filename": "...", "content": "..."}
	analysis_type: str = "comprehensive",  # "individual", "team", "comprehensive"
) -> Dict[str, Any]:
	"""
	Comprehensive code analysis using AI.
	
	Analyzes code quality, accuracy, performance, and provides detailed feedback.
	"""
	api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY_WORKEXPERIO")
	
	if not api_key:
		return _analyze_code_fallback(files_data)
	
	try:
		client = OpenAI(api_key=api_key)
		
		# Prepare file contents for analysis
		files_summary = []
		for file_data in files_data[:20]:  # Limit to 20 files for token efficiency
			filename = file_data.get("filename", "unknown")
			content = file_data.get("content", "")
			lines = len(content.splitlines())
			files_summary.append(f"{filename} ({lines} lines)")
		
		files_text = "\n".join([
			f"=== {fd.get('filename', 'unknown')} ===\n{fd.get('content', '')[:2000]}"
			for fd in files_data[:10]  # Include full content for first 10 files
		])
		
		system_prompt = """You are an expert code reviewer and quality analyst. Analyze the provided code files and provide a comprehensive evaluation.

Focus on:
1. **Code Quality**: Readability, maintainability, adherence to best practices, code smells
2. **Accuracy**: Functional correctness, potential bugs, error handling
3. **Performance**: Bottlenecks, inefficient algorithms, resource utilization

Return a JSON object with this structure:
{
  "overall_score": 85.0,
  "code_quality": {
    "score": 80.0,
    "issues": ["List of quality issues"],
    "strengths": ["List of strengths"]
  },
  "accuracy": {
    "score": 90.0,
    "potential_bugs": ["List of potential bugs"],
    "error_handling": "good|fair|poor"
  },
  "performance": {
    "score": 85.0,
    "bottlenecks": ["List of performance issues"],
    "recommendations": ["List of recommendations"]
  },
  "individual_files": [
    {
      "filename": "file.py",
      "score": 85.0,
      "issues": ["List of issues"],
      "recommendations": ["List of recommendations"]
    }
  ],
  "summary": "Overall summary of the codebase"
}"""
		
		user_prompt = f"""Analyze the following code files:

Files to analyze ({len(files_data)} total):
{', '.join(files_summary)}

Code content:
{files_text}

Provide a comprehensive analysis focusing on code quality, accuracy, and performance."""
		
		response = client.chat.completions.create(
			model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
			messages=[
				{"role": "system", "content": system_prompt},
				{"role": "user", "content": user_prompt}
			],
			temperature=0.2,
		)
		
		content = response.choices[0].message.content or "{}"
		
		# Try to parse JSON response
		try:
			# Extract JSON from markdown code blocks if present
			import re
			json_match = re.search(r'\{.*\}', content, re.DOTALL)
			if json_match:
				analysis = json.loads(json_match.group())
			else:
				analysis = json.loads(content)
		except json.JSONDecodeError:
			# Fallback to basic analysis
			return _analyze_code_fallback(files_data)
		
		# Ensure required fields
		if "overall_score" not in analysis:
			analysis["overall_score"] = 75.0
		
		return analysis
		
	except Exception as e:
		import logging
		logger = logging.getLogger(__name__)
		logger.error(f"Error in comprehensive code analysis: {e}")
		return _analyze_code_fallback(files_data)


def _analyze_code_fallback(files_data: List[Dict[str, str]]) -> Dict[str, Any]:
	"""Fallback analysis when AI is not available."""
	total_lines = sum(len(fd.get("content", "").splitlines()) for fd in files_data)
	avg_lines = total_lines / len(files_data) if files_data else 0
	
	# Simple heuristic scoring
	score = 100.0
	if avg_lines > 500:
		score -= 20
	if avg_lines > 1000:
		score -= 20
	
	return {
		"overall_score": max(0, min(100, score)),
		"code_quality": {
			"score": score,
			"issues": ["Unable to perform detailed analysis without AI"],
			"strengths": []
		},
		"accuracy": {
			"score": 75.0,
			"potential_bugs": [],
			"error_handling": "unknown"
		},
		"performance": {
			"score": 75.0,
			"bottlenecks": [],
			"recommendations": []
		},
		"individual_files": [
			{
				"filename": fd.get("filename", "unknown"),
				"score": 75.0,
				"issues": [],
				"recommendations": []
			}
			for fd in files_data
		],
		"summary": f"Analyzed {len(files_data)} files with {total_lines} total lines. Enable AI for detailed analysis."
	}


def extract_files_from_zip(zip_content: bytes) -> List[Dict[str, str]]:
	"""Extract and read files from a zip archive."""
	files_data = []
	
	with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
		tmp_file.write(zip_content)
		tmp_path = tmp_file.name
	
	try:
		with zipfile.ZipFile(tmp_path, 'r') as zip_ref:
			for file_info in zip_ref.namelist():
				# Skip directories and hidden files
				if file_info.endswith('/') or file_info.startswith('.'):
					continue
				
				try:
					content = zip_ref.read(file_info).decode('utf-8', errors='ignore')
					files_data.append({
						"filename": file_info,
						"content": content
					})
				except Exception:
					# Skip binary files
					continue
	finally:
		# Clean up temp file
		try:
			os.unlink(tmp_path)
		except Exception:
			pass
	
	return files_data

