from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from pydantic import BaseModel
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Appointment
from app.security import assert_user_scope, get_current_user
from services.auth_service import get_user_by_public_id
from services.appointment_service import get_nearby_hospitals
from services.public_id_service import appointment_public_id

router = APIRouter(prefix="/appointments", tags=["Appointments"])


class BookRequest(BaseModel):
    user_id: Optional[str] = None
    preferred_date: Optional[str] = None
    doctor_name: Optional[str] = None
    hospital_name: Optional[str] = None
    preferred_time: Optional[str] = None


class AutoBookRequest(BaseModel):
    user_id: Optional[str] = None
    location: Optional[str] = "Current Location"
    lat: Optional[float] = None
    lon: Optional[float] = None


@router.get("/nearby-hospitals")
def nearby_hospitals(
    lat: Optional[float] = Query(None),
    lon: Optional[float] = Query(None),
):
    """Returns verified regional hospitals sorted by closest physical distance."""
    return get_nearby_hospitals(user_lat=lat, user_lon=lon)


@router.post("/book")
def book_appointment(
    body: BookRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if body.user_id:
        user = get_user_by_public_id(db, body.user_id)
        assert_user_scope(current_user, user.id)
    else:
        user = current_user

    doctor_name = body.doctor_name or "Dr. S. Lakshmi, MD"
    hospital_name = body.hospital_name or "Saveetha Medical College & Hospital"
    time_slot = body.preferred_time or "10:30 AM"
    pref_date = body.preferred_date or (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")

    appt_time = datetime.utcnow() + timedelta(days=1)
    appointment = Appointment(
        user_id=user.id,
        patient_name=user.full_name,
        doctor_name=doctor_name,
        hospital_name=hospital_name,
        appointment_time=appt_time,
        status="BOOKED",
        notes=f"Preferred date: {pref_date}, Time: {time_slot}",
    )
    db.add(appointment)
    db.flush()
    appointment.public_id = appointment_public_id(appointment.id)
    db.commit()

    return {
        "status": "booked",
        "doctor": appointment.doctor_name,
        "hospital": appointment.hospital_name,
        "time": time_slot,
        "date": pref_date,
    }


@router.post("/auto-book")
def auto_book_appointment(
    body: AutoBookRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if body.user_id:
        user = get_user_by_public_id(db, body.user_id)
        assert_user_scope(current_user, user.id)
    else:
        user = current_user

    hospitals = get_nearby_hospitals(body.lat, body.lon)
    chosen = hospitals[0] if hospitals else None
    doctor_name = chosen.get("doctor_name", "Dr. S. Lakshmi, MD") if chosen else "Dr. S. Lakshmi, MD"
    hospital_name = chosen.get("name", "Saveetha Medical College & Hospital") if chosen else "Saveetha Medical College & Hospital"

    appt_time = datetime.utcnow() + timedelta(hours=2)
    appointment = Appointment(
        user_id=user.id,
        patient_name=user.full_name,
        doctor_name=doctor_name,
        hospital_name=hospital_name,
        appointment_time=appt_time,
        status="SCHEDULED",
        notes=f"Auto-booked near {body.location or 'Current Location'}",
    )
    db.add(appointment)
    db.flush()
    appointment.public_id = appointment_public_id(appointment.id)
    db.commit()

    return {
        "status": "scheduled",
        "doctor": appointment.doctor_name,
        "hospital": appointment.hospital_name,
        "time": "Within 2 hours",
        "distance_km": chosen.get("distance_km") if chosen else 0.1,
        "mapsUrl": chosen.get("mapsUrl") if chosen else "",
    }

