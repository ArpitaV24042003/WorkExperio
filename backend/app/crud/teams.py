# # crud/teams.py
# from sqlalchemy.orm import Session
# from app import models
# from app.schemas import TeamCreate

# def create_team(db: Session, team: TeamCreate):
#     db_team = models.Team(name=team.name)
#     db.add(db_team)
#     db.commit()
#     db.refresh(db_team)
#     return db_team

# def get_all_teams(db: Session):
#     return db.query(models.Team).all()

# def get_team_by_id(db: Session, team_id: int):
#     return db.query(models.Team).filter(models.Team.id == team_id).first()


# crud/teams.py
from sqlalchemy.orm import Session
from app import models
from app.schemas import TeamCreate

def create_team(db: Session, team: TeamCreate):
    """
    Creates a new Team and its associated ChatRoom.
    """
    # Create the team
    db_team = models.Team(name=team.name)
    db.add(db_team)
    
    # We must flush to get the new db_team.id before creating the room
    db.flush() 
    
    # Create the associated chat room
    db_chat_room = models.ChatRoom(
        name=f"{db_team.name} Room",
        team_id=db_team.id
    )
    db.add(db_chat_room)
    
    db.commit()
    db.refresh(db_team)
    return db_team

def get_all_teams(db: Session):
    return db.query(models.Team).all()

def get_team_by_id(db: Session, team_id: int):
    return db.query(models.Team).filter(models.Team.id == team_id).first()