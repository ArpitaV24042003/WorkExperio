import spacy
import pdfplumber
import re
import json

nlp = spacy.load(r"C:\Users\saisa\Desktop\College_Documents\proj1")

base_nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
    return text

def extract_email(text):
    return re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)

def extract_phone(text):
    return re.findall(r"\+?\d[\d\-\s]{8,15}\d", text)

def extract_links(text):
    return re.findall(r"(https?://\S+|www\.\S+)", text)

def extract_skills(text):
    skills_db = [
    "Python", "Java", "C", "C++", "C#", "Go", "R", "Scala", "Rust", "Swift",
    "Kotlin", "PHP", "JavaScript", "TypeScript", "HTML", "CSS", "SQL", "Bash",
    "Shell", "Perl", "MATLAB", "Ruby",

    # Frontend Frameworks & Libraries
    "React", "Angular", "Vue.js", "Svelte", "Bootstrap", "Tailwind CSS",
    "jQuery", "Next.js", "Nuxt.js",

    # Backend Frameworks
    "Node.js", "Express.js", "Django", "Flask", "FastAPI", "Spring", "Spring Boot",
    "ASP.NET", "Ruby on Rails", "Laravel",

    # Databases
    "MySQL", "PostgreSQL", "MongoDB", "SQLite", "MariaDB", "Oracle Database",
    "Cassandra", "Redis", "Elasticsearch", "Neo4j", "Firebase", "DynamoDB",

    # Cloud Platforms
    "AWS", "Amazon Web Services", "Azure", "Microsoft Azure", "GCP",
    "Google Cloud Platform", "IBM Cloud", "Heroku", "Netlify", "Vercel",

    # DevOps & Tools
    "Docker", "Kubernetes", "Jenkins", "Git", "GitHub", "GitLab", "Bitbucket",
    "CI/CD", "Terraform", "Ansible", "Puppet", "Chef", "Linux", "Unix",
    "Windows Server",

    # Machine Learning & AI
    "Machine Learning", "Deep Learning", "Natural Language Processing", "NLP",
    "Computer Vision", "TensorFlow", "Keras", "PyTorch", "Scikit-learn", "Pandas",
    "NumPy", "Matplotlib", "Seaborn", "XGBoost", "LightGBM", "OpenCV",
    "Spacy", "NLTK", "Hugging Face", "Transformers",

    # Data Tools
    "Excel", "Power BI", "Tableau", "Google Data Studio", "Data Analysis",
    "Data Visualization", "ETL", "SQL Server", "Snowflake", "BigQuery",
    "Hadoop", "Spark", "Databricks",

    # Cybersecurity
    "Penetration Testing", "Ethical Hacking", "Kali Linux", "Wireshark",
    "Metasploit", "Nmap", "Cybersecurity", "Network Security",

    # Project Management & Soft Skills
    "Agile", "Scrum", "Kanban", "JIRA", "Confluence", "Asana", "Trello",
    "Communication", "Leadership", "Time Management", "Problem Solving",
    "Collaboration", "Critical Thinking"
    ]
    
    found = []

    for skill in skills_db:
        if re.search(r"\b" + re.escape(skill) + r"\b", text, re.IGNORECASE):
            found.append(skill)

    for line in text.splitlines():
        if "SKILL" in line.upper():
            tokens = re.findall(r"[A-Za-z\+#\.]+", line)
            found.extend(tokens)

    return list(set(found))

def split_sections(text):
    sections = {}
    current_section = "General"
    for line in text.splitlines():
        line_clean = line.strip()
        upper = line_clean.upper()

        if re.match(r"^(EDUCATION|ACADEMIC|QUALIFICATION)", upper):
            current_section = "Education"
        elif re.match(r"^(EXPERIENCE|WORK|EMPLOYMENT|CAREER)", upper):
            current_section = "Experience"
        elif re.match(r"^(PROJECT|RESEARCH)", upper):
            current_section = "Projects"
        elif re.match(r"^(SKILLS|TECHNICAL)", upper):
            current_section = "Skills"
        elif re.match(r"^(CERTIFICATION|CERTIFICATES)", upper):
            current_section = "Certificates"

        sections.setdefault(current_section, []).append(line_clean)

    return sections


def parse_resume(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    doc = nlp(text)
    base_doc = base_nlp(text)

    parsed_data = {
        "Email": extract_email(text),
        "Phone": extract_phone(text),
        "Links": extract_links(text),
        "Skills": extract_skills(text),
        "Sections": split_sections(text),
        "Entities": {}
    }



    for ent in doc.ents:
        parsed_data["Entities"].setdefault(ent.label_, []).append(ent.text.strip())
    if "Name" not in parsed_data["Entities"]:
        for ent in base_doc.ents:
            if ent.label_ == "PERSON":
                parsed_data["Entities"].setdefault("Name", []).append(ent.text.strip())
                break

    return parsed_data
resume_path = r"D:\projects\Mini Project\Dimpu\1EP22CS043_KAMBHAM-SAISAHVIKA_RESUME.pdf"
parsed = parse_resume(resume_path)
print(json.dumps(parsed, indent=4))

output_file = r"D:\parsed_resume.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(parsed, f, indent=4, ensure_ascii=False)

print(f"Resume parsed and saved to {output_file}")
