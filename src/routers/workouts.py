from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas, security, database

router = APIRouter()

@router.get("/", response_model=List[schemas.WorkoutResponse])
def get_workouts(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    workouts = db.query(models.Workout).filter(models.Workout.owner_id == current_user.id).offset(skip).limit(limit).all()
    return workouts

@router.get("/{id}", response_model=schemas.WorkoutResponse)
def get_workout(
    id: int, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    workout = db.query(models.Workout).filter(models.Workout.id == id, models.Workout.owner_id == current_user.id).first()
    if not workout:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found")
    return workout

@router.post("/", response_model=schemas.WorkoutResponse, status_code=status.HTTP_201_CREATED)
def create_workout(
    workout: schemas.WorkoutCreate, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    new_workout = models.Workout(**workout.model_dump(), owner_id=current_user.id)
    db.add(new_workout)
    db.commit()
    db.refresh(new_workout)
    return new_workout

@router.patch("/{id}", response_model=schemas.WorkoutResponse)
def update_workout(
    id: int, 
    workout_update: schemas.WorkoutUpdate, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    db_workout = db.query(models.Workout).filter(models.Workout.id == id, models.Workout.owner_id == current_user.id).first()
    if not db_workout:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found")
    
    update_data = workout_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_workout, key, value)
        
    db.commit()
    db.refresh(db_workout)
    return db_workout

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout(
    id: int, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    db_workout = db.query(models.Workout).filter(models.Workout.id == id, models.Workout.owner_id == current_user.id).first()
    if not db_workout:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found")
    
    db.delete(db_workout)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)