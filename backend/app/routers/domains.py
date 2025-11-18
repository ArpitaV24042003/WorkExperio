from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from ..dependencies import get_current_user
from ..models import User
from ..data.domains import DOMAINS, PROJECT_TEMPLATES, get_projects_for_domain

router = APIRouter()

@router.get("/domains", response_model=List[str])
def get_domains(current_user: User = Depends(get_current_user)):
    """Get all available project domains"""
    return DOMAINS

@router.get("/domains/{domain}/projects", response_model=List[str])
def get_projects_for_domain_endpoint(domain: str, current_user: User = Depends(get_current_user)):
    """Get all project templates for a specific domain"""
    if domain not in DOMAINS:
        return []
    return get_projects_for_domain(domain)

@router.get("/domains/{domain}/projects/{index}", response_model=Dict[str, Any])
def get_project_template(domain: str, index: int, current_user: User = Depends(get_current_user)):
    """Get a specific project template by domain and index"""
    if domain not in DOMAINS:
        return {"error": "Domain not found"}
    
    projects = get_projects_for_domain(domain)
    if 0 <= index < len(projects):
        return {
            "domain": domain,
            "index": index,
            "title": projects[index],
            "description": f"Build a {projects[index].lower()} project in the {domain} domain."
        }
    return {"error": "Project template not found"}

