"""
API routes for multiple schedule generation and selection.
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import json

from ..core.multi_schedule_optimizer import MultiScheduleOptimizer
from ..data.models import OptimizationConfig
from .schemas import MultiScheduleRequest, ScheduleSelectionRequest

router = APIRouter()

# Initialize multi-schedule optimizer
multi_optimizer = MultiScheduleOptimizer()

@router.post('/generate-multiple-schedules')
async def generate_multiple_schedules(request: MultiScheduleRequest):
    """Generate multiple timetable options for admin selection."""
    try:
        # Convert request to data format
        data = {
            "students": request.students,
            "courses": request.courses,
            "faculty": request.faculty,
            "rooms": request.rooms,
            "time_slots": request.time_slots,
            "student_preferences": request.student_preferences
        }
        
        # Generate multiple schedules
        result = await multi_optimizer.generate_multiple_schedules(
            institute_id=request.institute_id,
            semester=request.semester,
            data=data,
            num_options=request.num_options
        )
        
        if result["success"]:
            return JSONResponse({
                "success": True,
                "message": f"Generated {result['total_options']} schedule options",
                "institute_id": result["institute_id"],
                "semester": result["semester"],
                "total_options": result["total_options"],
                "schedules": result["schedules"]
            })
        else:
            return JSONResponse({
                "success": False,
                "error": result["error"]
            }, status_code=400)
            
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@router.post('/select-schedule')
async def select_schedule(request: ScheduleSelectionRequest):
    """Save the admin-selected schedule to the database."""
    try:
        result = await multi_optimizer.save_selected_schedule(
            selected_schedule=request.selected_schedule,
            institute_id=request.institute_id
        )
        
        if result["success"]:
            return JSONResponse({
                "success": True,
                "message": "Schedule selected and saved successfully",
                "schedule_id": result["schedule_id"]
            })
        else:
            return JSONResponse({
                "success": False,
                "error": result["error"]
            }, status_code=400)
            
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@router.get('/schedule-options/{institute_id}')
async def get_schedule_options(institute_id: str):
    """Get available schedule options for an institute."""
    try:
        # This would typically fetch from a cache or database
        # For now, return a placeholder response
        return JSONResponse({
            "success": True,
            "institute_id": institute_id,
            "available_options": 0,
            "message": "No schedule options available. Generate schedules first."
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

