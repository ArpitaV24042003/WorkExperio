# crud/roles.py
from sqlalchemy.orm import Session
from .. import models, schemas
from fastapi import HTTPException

def create_role(db: Session, role: schemas.RoleCreate):
    # Check if domain exists
    domain = db.query(models.Domain).filter(models.Domain.id == role.domain_id).first()
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
        
    # Check if skills exist and fetch them
    skills = db.query(models.Skill).filter(models.Skill.id.in_(role.required_skill_ids)).all()
    if len(skills) != len(role.required_skill_ids):
        # Find which skills are missing (for a better error message)
        found_skill_ids = {s.id for s in skills}
        missing_ids = set(role.required_skill_ids) - found_skill_ids
        raise HTTPException(
            status_code=404, 
            detail=f"One or more skills not found. Missing IDs: {missing_ids}"
        )

    # Create the role
    db_role = models.Role(name=role.name, domain_id=role.domain_id)
    
    # Add the skill relationships
    db_role.required_skills.extend(skills)
    
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

def get_all_roles(db: Session):
    return db.query(models.Role).all()