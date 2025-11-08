import copy
import time
from multiprocessing import Process, Manager, Lock
import os

# ----------------- DOMAIN CONFIG -----------------
DOMAIN_CONFIG = {
    "Frontend Development": {
        "roles": {
            "UI/UX Designer": {"skills": ["Figma", "Sketch", "Adobe XD", "Wireframing", "Prototyping", "User Research", "Journey Mapping", "Design Systems", "Usability Testing"], "default_count": 1},
            "Frontend Developer": {"skills": ["HTML", "CSS", "JavaScript", "TypeScript", "React", "Angular", "Vue", "Next.js", "Redux", "Webpack", "Vite", "Responsive Design", "SASS"], "default_count": 2},
            "Frontend Architect": {"skills": ["Micro-frontends", "Design Patterns", "Component Architecture", "State Management", "Performance Optimization", "Server-Side Rendering (SSR)", "Web Security (CSP, CORS)"], "default_count": 1},
            "Accessibility & Performance Engineer": {"skills": ["WCAG Compliance", "ARIA", "Screen Reader Testing", "Lighthouse Audits", "Core Web Vitals", "Performance Tuning", "Cross-browser Testing", "Lazy Loading"], "default_count": 1},
            "Frontend QA Engineer": {"skills": ["Jest", "Cypress", "Playwright", "Selenium", "Storybook", "Visual Regression Testing", "Unit Testing", "Integration Testing", "E2E Testing"], "default_count": 1}
        },
        "default_team_size": 6
    },
    "Backend Development": {
        "roles": {
            "Backend Developer": {"skills": ["Java", "Spring Boot", "Node.js", "Express", "Python", "Django", "Go", "Rust", "REST APIs", "GraphQL", "Authentication", "PostgreSQL", "MySQL", "MongoDB", "Redis"], "default_count": 2},
            "Database Engineer": {"skills": ["SQL", "NoSQL", "Query Optimization", "Schema Design", "Data Warehousing", "Indexing", "Replication", "Sharding", "Database Migration"], "default_count": 1},
            "API Integration Specialist": {"skills": ["REST APIs", "GraphQL", "Microservices", "gRPC", "Swagger", "OpenAPI", "OAuth", "Postman", "API Gateways"], "default_count": 1},
            "Backend Architect": {"skills": ["Scalability", "System Design", "Microservices Architecture", "Domain-Driven Design (DDD)", "Event-Driven Architecture", "Caching Strategies", "Message Queues (RabbitMQ, Kafka)"], "default_count": 1},
            "Backend QA Engineer": {"skills": ["Postman", "JUnit", "PyTest", "JMeter", "K6", "API Testing", "Load Testing", "Contract Testing", "Security Testing"], "default_count": 1}
        },
        "default_team_size": 6
    },
    "Full Stack Development": {
        "roles": {
            "Full Stack Developer": {"skills": ["React", "Angular", "Node.js", "Java", "Python", "TypeScript", "REST APIs", "GraphQL", "SQL", "NoSQL", "Docker", "CI/CD"], "default_count": 2},
            "Frontend Specialist": {"skills": ["HTML", "CSS", "JavaScript", "TypeScript", "React", "Next.js", "Angular", "State Management"], "default_count": 1},
            "Backend Specialist": {"skills": ["Node.js", "Java", "Python", "Databases", "PostgreSQL", "MongoDB", "Authentication", "Message Queues", "ORM"], "default_count": 1},
            "DevOps Engineer": {"skills": ["CI/CD", "Jenkins", "GitHub Actions", "Docker", "Kubernetes", "Terraform", "AWS", "GCP", "Azure"], "default_count": 1},
            "QA Automation Engineer": {"skills": ["Selenium", "Cypress", "Playwright", "CI/CD Integration", "Test Planning", "Unit/Integration Testing", "Performance Testing"], "default_count": 1},
            "Tech Lead": {"skills": ["Architecture Decisions", "System Design", "Code Review", "Mentorship", "Agile Planning", "Project Management", "Stakeholder Communication"], "default_count": 1}
        },
        "default_team_size": 7
    },
    "Cybersecurity": {
        "roles": {
            "Security Analyst": {"skills": ["SIEM (Splunk, ELK)", "Intrusion Detection Systems (IDS)", "Threat Intelligence", "Log Analysis", "Vulnerability Assessment", "Firewall Management"], "default_count": 2},
            "Penetration Tester": {"skills": ["Ethical Hacking", "Metasploit", "Burp Suite", "Nmap", "Kali Linux", "Web Application Security", "Network Penetration Testing", "Social Engineering"], "default_count": 1},
            "Security Engineer": {"skills": ["Network Security", "Cloud Security (AWS, Azure)", "IAM", "Encryption", "Security Architecture", "Hardening Systems", "Scripting (Python, Bash)"], "default_count": 1},
            "Incident Responder": {"skills": ["Digital Forensics", "Malware Analysis", "Incident Handling", "Threat Containment", "Recovery Planning", "Forensic Tools (EnCase, FTK)"], "default_count": 1},
            "Compliance Analyst": {"skills": ["GDPR", "HIPAA", "ISO 27001", "SOC 2", "Risk Assessment", "Security Audits", "Policy Development"], "default_count": 1}
        },
        "default_team_size": 6
    },
    "AI / Machine Learning Development": {
        "roles": {
            "ML Engineer": {"skills": ["Python", "Scikit-learn", "TensorFlow", "PyTorch", "Keras", "XGBoost", "Feature Engineering", "MLflow", "Model Optimization"], "default_count": 2},
            "Data Engineer": {"skills": ["SQL", "ETL", "Data Pipelines", "Spark", "Airflow", "Kafka", "Hadoop", "Data Warehousing (BigQuery, Redshift)", "Data Governance"], "default_count": 1},
            "Data Scientist": {"skills": ["Statistics", "Pandas", "NumPy", "Scipy", "Jupyter", "Visualization (Matplotlib, Seaborn)", "Model Evaluation", "A/B Testing", "Statistical Modeling"], "default_count": 1},
            "MLOps Engineer": {"skills": ["Model Deployment", "Docker", "Kubernetes", "Kubeflow", "Seldon Core", "CI/CD for ML", "Monitoring (Prometheus, Grafana)", "Infrastructure as Code (Terraform)"], "default_count": 1},
            "AI Researcher": {"skills": ["NLP", "Computer Vision", "Reinforcement Learning", "Deep Learning", "Research Papers", "Published Research", "Algorithm Design"], "default_count": 1},
            "AI QA Engineer": {"skills": ["Model Testing", "Bias Detection", "Fairness Evaluation", "Explainability (XAI)", "Adversarial Testing", "Stress Testing", "Data Validation"], "default_count": 1}
        },
        "default_team_size": 7
    }
}


initial_candidates = [
    {"id": 1, "name": "Alice", "skills": [
        "React", "CSS", "UI/UX"], "preferred_domain": "Frontend Development"},
    {"id": 2, "name": "Bob", "skills": [
        "HTML", "JavaScript", "Angular"], "preferred_domain": "Frontend Development"},
    {"id": 3, "name": "Charlie", "skills": [
        "WCAG Compliance", "ARIA"], "preferred_domain": "Frontend Development"},
    {"id": 4, "name": "David", "skills": [
        "Cypress", "Playwright"], "preferred_domain": "Frontend Development"},
    {"id": 5, "name": "Eve", "skills": [
        "Lighthouse Audits", "Performance Tuning"], "preferred_domain": "Frontend Development"},
    {"id": 6, "name": "Fiona", "skills": [
        "Figma", "Design Systems"], "preferred_domain": "Frontend Development"},
    {"id": 7, "name": "George", "skills": [
        "Micro-frontends", "SSR"], "preferred_domain": "Frontend Development"},
    {"id": 8, "name": "Hannah", "skills": [
        "GraphQL", "State Management"], "preferred_domain": "Frontend Development"},
    {"id": 9, "name": "Ian", "skills": [
        "React", "Integration Testing"], "preferred_domain": "Frontend Development"},
    {"id": 10, "name": "Jack", "skills": [
        "Vue", "CSS", "Vite"], "preferred_domain": "Frontend Development"},
    {"id": 11, "name": "Karen", "skills": [
        "Node.js", "Express", "MongoDB"], "preferred_domain": "Backend Development"},
    {"id": 12, "name": "Leo", "skills": [
        "Python", "Django", "PostgreSQL"], "preferred_domain": "Backend Development"},
    {"id": 13, "name": "Mona", "skills": [
        "Java", "Spring Boot", "Kafka"], "preferred_domain": "Backend Development"},
    {"id": 14, "name": "Nathan", "skills": [
        "SQL", "Query Optimization", "Indexing"], "preferred_domain": "Backend Development"},
    {"id": 15, "name": "Olivia", "skills": [
        "MongoDB", "Sharding", "Replication"], "preferred_domain": "Backend Development"},
    {"id": 16, "name": "Paul", "skills": [
        "REST APIs", "API Gateways", "Swagger"], "preferred_domain": "Backend Development"},
    {"id": 17, "name": "Quincy", "skills": [
        "GraphQL", "Microservices"], "preferred_domain": "Backend Development"},
    {"id": 18, "name": "Rachel", "skills": [
        "System Design", "Scalability"], "preferred_domain": "Backend Development"},
    {"id": 19, "name": "Steve", "skills": [
        "Go", "gRPC", "Python"], "preferred_domain": "Backend Development"},
    {"id": 20, "name": "Tina", "skills": [
        "JMeter", "Load Testing", "PyTest"], "preferred_domain": "Backend Development"},
    {"id": 21, "name": "Uma", "skills": [
        "HTML", "CSS", "Node.js", "Docker"], "preferred_domain": "Full Stack Development"},
    {"id": 22, "name": "Victor", "skills": [
        "React", "SQL", "TypeScript"], "preferred_domain": "Full Stack Development"},
    {"id": 23, "name": "Wendy", "skills": [
        "Angular", "Python", "Django"], "preferred_domain": "Full Stack Development"},
    {"id": 24, "name": "Xander", "skills": [
        "Vue", "PostgreSQL", "CI/CD"], "preferred_domain": "Full Stack Development"},
    {"id": 25, "name": "Yara", "skills": [
        "UI/UX", "Figma", "React"], "preferred_domain": "Full Stack Development"},
    {"id": 26, "name": "Zane", "skills": [
        "GraphQL", "Authentication", "Node.js"], "preferred_domain": "Full Stack Development"},
    {"id": 27, "name": "Abby", "skills": [
        "MongoDB", "SQL", "Java"], "preferred_domain": "Full Stack Development"},
    {"id": 28, "name": "Ben", "skills": [
        "React", "Node.js", "Express", "AWS"], "preferred_domain": "Full Stack Development"},
    {"id": 29, "name": "Clara", "skills": [
        "Architecture Decisions", "Mentorship"], "preferred_domain": "Full Stack Development"},
    {"id": 30, "name": "Derek", "skills": [
        "Python", "FastAPI", "Kubernetes"], "preferred_domain": "Full Stack Development"},
    {"id": 31, "name": "Ethan", "skills": [
        "SIEM", "Splunk", "Log Analysis"], "preferred_domain": "Cybersecurity"},
    {"id": 32, "name": "Faye", "skills": [
        "Metasploit", "Burp Suite", "Ethical Hacking"], "preferred_domain": "Cybersecurity"},
    {"id": 33, "name": "Gina", "skills": [
        "Cloud Security", "AWS", "IAM"], "preferred_domain": "Cybersecurity"},
    {"id": 34, "name": "Harry", "skills": [
        "Digital Forensics", "Malware Analysis"], "preferred_domain": "Cybersecurity"},
    {"id": 35, "name": "Isla", "skills": [
        "GDPR", "ISO 27001", "Security Audits"], "preferred_domain": "Cybersecurity"},
    {"id": 36, "name": "Jake", "skills": [
        "Intrusion Detection Systems", "Firewall Management"], "preferred_domain": "Cybersecurity"},
    {"id": 37, "name": "Kylie", "skills": [
        "Nmap", "Kali Linux", "Web Application Security"], "preferred_domain": "Cybersecurity"},
    {"id": 38, "name": "Liam", "skills": [
        "Python", "Scripting", "Hardening Systems"], "preferred_domain": "Cybersecurity"},
    {"id": 39, "name": "Maya", "skills": [
        "Incident Handling", "Threat Containment"], "preferred_domain": "Cybersecurity"},
    {"id": 40, "name": "Nora", "skills": [
        "Risk Assessment", "Policy Development"], "preferred_domain": "Cybersecurity"},
    {"id": 41, "name": "Owen", "skills": [
        "Python", "TensorFlow", "Keras"], "preferred_domain": "AI / Machine Learning Development"},
    {"id": 42, "name": "Piper", "skills": [
        "Pandas", "Statistics", "A/B Testing"], "preferred_domain": "AI / Machine Learning Development"},
    {"id": 43, "name": "Quinn", "skills": [
        "PyTorch", "Machine Learning", "NLP"], "preferred_domain": "AI / Machine Learning Development"},
    {"id": 44, "name": "Riley", "skills": [
        "ETL", "SQL", "Spark", "Airflow"], "preferred_domain": "AI / Machine Learning Development"},
    {"id": 45, "name": "Sophia", "skills": ["Experimentation", "Model Evaluation",
                                            "Statistical Modeling"], "preferred_domain": "AI / Machine Learning Development"},
    {"id": 46, "name": "Tyler", "skills": [
        "FastAPI", "Docker", "Model Deployment"], "preferred_domain": "AI / Machine Learning Development"},
    {"id": 47, "name": "Uma", "skills": [
        "MLflow", "Kubernetes", "Kubeflow"], "preferred_domain": "AI / Machine Learning Development"},
    {"id": 48, "name": "Victor", "skills": [
        "Model Deployment", "CI/CD for ML"], "preferred_domain": "AI / Machine Learning Development"},
    {"id": 49, "name": "Willa", "skills": [
        "Python", "scikit-learn", "XGBoost"], "preferred_domain": "AI / Machine Learning Development"},
    {"id": 50, "name": "Xena", "skills": [
        "Data Analysis", "Python", "Bias Detection"], "preferred_domain": "AI / Machine Learning Development"}
]


def get_rule_based_score(candidate_skills, role_skills):
    """Calculates a score based purely on the number of matching skills."""
    return len(set(candidate_skills).intersection(set(role_skills)))


def attempt_to_form_team(domain, candidates):
    """
    Tries to form a complete team for a given domain from a list of candidates.
    This version uses a robust greedy algorithm based on the best rule-based score at each step.
    Args:
        domain (str): The development domain for the team.
        candidates (list): A list of available candidates.
    Returns:
        tuple: A tuple containing the formed team (dict) and a list of assigned candidates (list).
               Returns (None, None) if a team cannot be formed.
    """
    domain_roles = DOMAIN_CONFIG[domain]["roles"]
    team = {role: [] for role, data in domain_roles.items()}

    unfilled_slots = []
    for role, data in domain_roles.items():
        unfilled_slots.extend([role] * data["default_count"])

    unassigned_candidates = list(candidates)
    assigned_candidates = []

    while unfilled_slots and unassigned_candidates:
        best_match = {
            "candidate": None,
            "role_slot": None,
            "score": -1
        }

        for candidate in unassigned_candidates:
            for slot in set(unfilled_slots):
                role_skills = domain_roles[slot]["skills"]
                candidate_skills = candidate["skills"]
                score = get_rule_based_score(candidate_skills, role_skills)

                if score > best_match["score"]:
                    best_match["score"] = score
                    best_match["candidate"] = candidate
                    best_match["role_slot"] = slot

        if best_match["candidate"]:
            assigned_candidate = best_match["candidate"]
            filled_slot = best_match["role_slot"]

            team[filled_slot].append(assigned_candidate["name"])
            assigned_candidates.append(assigned_candidate)

            unassigned_candidates.remove(assigned_candidate)
            unfilled_slots.remove(filled_slot)
        else:
            break

    if not unfilled_slots:
        return team, assigned_candidates

    return None, None



def team_formation_process(domain, shared_candidates, shared_teams, lock):
    """
    A process that continuously tries to form teams for a specific domain.
    Args:
        domain (str): The domain this process is responsible for.
        shared_candidates (Manager.list): A shared list of candidates.
        shared_teams (Manager.list): A shared list of formed teams.
        lock (Manager.Lock): A lock to synchronize access to shared resources.
    """
    while True:
        lock.acquire()
        try:
            domain_specific_candidates = [
                c for c in shared_candidates if c.get("preferred_domain") == domain
            ]

            team, assigned_candidates = attempt_to_form_team(
                domain, domain_specific_candidates)

            if team:
                shared_teams.append((domain, team))

                print(
                    f"\n>>>>>>>>>> Team Formed in {domain} (Process: {os.getpid()}) <<<<<<<<<<")
                assigned_candidate_details = {
                    c['name']: c for c in assigned_candidates}
                for role, members in team.items():
                    if not members:
                        continue  
                    print(f"  Role: {role}")
                    for member_name in members:
                        skills = assigned_candidate_details.get(
                            member_name, {}).get('skills', [])
                        skills_str = ', '.join(skills) if skills else "N/A"
                        print(
                            f"    - Member: {member_name.ljust(10)} | Skills: {skills_str}")
                print("----------------------------------------------------")

                assigned_ids = {c['id'] for c in assigned_candidates}
                new_candidates_list = [
                    c for c in shared_candidates if c['id'] not in assigned_ids]

                print("\n--- Current Waiting List ---")
                if not new_candidates_list:
                    print("  No candidates remaining.")
                else:
                    print(
                        f"  ({len(new_candidates_list)} candidates remaining)")
                    for c in new_candidates_list:
                        skills_str = ', '.join(c.get('skills', []))
                        print(
                            f"  - Name: {c['name'].ljust(10)} | Skills: {skills_str} | Domain: {c['preferred_domain']}")
                print("----------------------------------------------------\n")

                shared_candidates[:] = new_candidates_list

        finally:
            lock.release()

        time.sleep(1)


def main():
    """
    Main function to set up and run the multiprocessing environment.
    """
    manager = Manager()
    shared_candidates = manager.list(copy.deepcopy(initial_candidates))
    shared_teams = manager.list()
    lock = Lock()
    processes = []
    for domain in DOMAIN_CONFIG.keys():
        p = Process(target=team_formation_process, args=(
            domain, shared_candidates, shared_teams, lock))
        p.daemon = True 
        p.start()
        processes.append(p)

    try:
        print("Initial team formation in progress...")
        time.sleep(3) 

        while True:
            with lock:
                candidate_count = len(shared_candidates)

            if candidate_count == 0:
                print("\nNo candidates left in the waiting list.")
                time.sleep(2) 
                if len(shared_candidates) == 0:
                    print("All possible teams have been formed. Exiting main loop.")
                    break

            print(
                f"\n(Main thread) Currently waiting candidates: {candidate_count}.")
            choice = input(
                "Do you want to add a new candidate? (yes/no/exit): ").strip().lower()

            if choice == 'exit':
                print("Exiting user input loop.")
                break

            if choice == 'yes':
                with lock:
                    name = input("  Enter candidate name: ").strip()
                    if not name:
                        print("  Name cannot be empty. Aborting candidate addition.")
                        continue

                    skills_input = input(
                        "  Enter skills (comma-separated): ").strip()
                    skills = [s.strip()
                              for s in skills_input.split(",") if s.strip()]

                    print("  Available domains:")
                    domain_list = list(DOMAIN_CONFIG.keys())
                    for i, d in enumerate(domain_list):
                        print(f"    {i+1}. {d}")

                    domain_choice_idx = -1
                    while True:
                        try:
                            domain_choice = int(
                                input(f"  Choose a preferred domain (1-{len(domain_list)}): "))
                            if 1 <= domain_choice <= len(domain_list):
                                domain_choice_idx = domain_choice - 1
                                break
                            else:
                                print(
                                    "  Invalid choice. Please select a number from the list.")
                        except ValueError:
                            print("  Invalid input. Please enter a number.")

                    preferred_domain = domain_list[domain_choice_idx]

                    all_ids = [c['id'] for c in initial_candidates] + \
                        [c['id'] for c in shared_candidates]
                    new_id = max(all_ids + [0]) + 1

                    new_candidate = {
                        "id": new_id,
                        "name": name,
                        "skills": skills,
                        "preferred_domain": preferred_domain
                    }
                    shared_candidates.append(new_candidate)
                    print(f"--> Added new candidate: {name} (ID: {new_id})")

            print("\n...allowing time for team formation processes...")
            time.sleep(3)

    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")
    finally:
        print("\n\n--- Final Summary of All Formed Teams ---")
        if not shared_teams:
            print("No teams were formed.")
        else:
            for idx, (domain, team) in enumerate(shared_teams, 1):
                print(f"\nTeam {idx} ({domain}):")
                for role, members in team.items():
                    print(f"  {role}: {', '.join(members)}")

        print("\n--- Remaining Candidates ---")

        final_candidates = list(shared_candidates)
        if not final_candidates:
            print("No candidates remaining.")
        else:
            for c in final_candidates:
                print(f"  - {c['name']} (ID: {c['id']})")


if __name__ == "__main__":
    main()
