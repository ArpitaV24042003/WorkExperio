# crud/domains.py
from sqlalchemy.orm import Session
from .. import models, schemas

def create_domain(db: Session, domain: schemas.DomainCreate):
    db_domain = models.Domain(
        name=domain.name,
        description=domain.description
    )
    db.add(db_domain)
    db.commit()
    db.refresh(db_domain)
    return db_domain

def get_all_domains(db: Session):
    return db.query(models.Domain).all()