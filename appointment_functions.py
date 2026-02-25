# Simple in-memory storage
APPOINTMENTS_DB = {"appointments": {}, "next_id": 1000}

DOCTORS_DB = {
    "john_smith": {
        "name": "Dr. John Smith",
        "specialty": "General Practitioner",
        "availability": ["Monday 9AM-5PM", "Tuesday 9AM-5PM", "Wednesday 9AM-1PM", "Thursday 9AM-5PM", "Friday 9AM-5PM"],
        "location": "Building A, Room 101",
        "phone": "555-0101"
    },
    "sarah_wilson": {
        "name": "Dr. Sarah Wilson",
        "specialty": "Cardiology",
        "availability": ["Monday 10AM-4PM", "Wednesday 10AM-4PM", "Friday 10AM-4PM"],
        "location": "Building B, Room 205",
        "phone": "555-0102"
    },
    "michael_brown": {
        "name": "Dr. Michael Brown",
        "specialty": "Orthopedics",
        "availability": ["Tuesday 8AM-12PM", "Wednesday 2PM-6PM", "Thursday 8AM-12PM", "Friday 1PM-5PM"],
        "location": "Building C, Room 310",
        "phone": "555-0103"
    },
    "emily_davis": {
        "name": "Dr. Emily Davis",
        "specialty": "Dermatology",
        "availability": ["Monday 1PM-5PM", "Tuesday 9AM-1PM", "Thursday 2PM-6PM"],
        "location": "Building A, Room 202",
        "phone": "555-0104"
    },
    "david_martinez": {
        "name": "Dr. David Martinez",
        "specialty": "Pediatrics",
        "availability": ["Monday 9AM-12PM", "Tuesday 1PM-5PM", "Wednesday 9AM-12PM", "Thursday 1PM-5PM", "Friday 9AM-12PM"],
        "location": "Building B, Room 150",
        "phone": "555-0105"
    }
}

APPOINTMENT_SLOTS = {
    "john_smith": ["Monday 10:00 AM", "Monday 2:00 PM", "Tuesday 11:00 AM", "Tuesday 3:00 PM", "Wednesday 10:00 AM", "Thursday 9:00 AM", "Thursday 2:00 PM", "Friday 1:00 PM"],
    "sarah_wilson": ["Monday 10:30 AM", "Monday 3:00 PM", "Wednesday 11:00 AM", "Wednesday 3:30 PM", "Friday 10:00 AM", "Friday 2:00 PM"],
    "michael_brown": ["Tuesday 8:30 AM", "Tuesday 11:00 AM", "Wednesday 2:30 PM", "Wednesday 4:00 PM", "Thursday 9:00 AM", "Friday 1:30 PM"],
    "emily_davis": ["Monday 1:30 PM", "Monday 4:00 PM", "Tuesday 9:30 AM", "Tuesday 12:00 PM", "Thursday 2:30 PM"],
    "david_martinez": ["Monday 9:30 AM", "Monday 11:00 AM", "Tuesday 1:30 PM", "Tuesday 3:00 PM", "Wednesday 9:30 AM", "Wednesday 11:00 AM", "Thursday 1:30 PM", "Friday 9:30 AM"]
}


def get_doctor_info(doctor_name):
    """Get information about a specific doctor."""
    doctor_key = doctor_name.lower().replace(" ", "_")
    doctor = DOCTORS_DB.get(doctor_key)
    if doctor:
        available_slots = APPOINTMENT_SLOTS.get(doctor_key, [])
        return {
            "name": doctor["name"],
            "specialty": doctor["specialty"],
            "location": doctor["location"],
            "phone": doctor["phone"],
            "availability": doctor["availability"],
            "next_available_slots": available_slots[:3]  
        }
    return {"error": f"Doctor '{doctor_name}' not found. Available doctors: Dr. John Smith, Dr. Sarah Wilson, Dr. Michael Brown, Dr. Emily Davis, Dr. David Martinez"}


def book_appointment(patient_name, doctor_name, preferred_time):
    """Book an appointment with a doctor."""
    doctor_key = doctor_name.lower().replace(" ", "_")
    doctor = DOCTORS_DB.get(doctor_key)
    if not doctor:
        return {"error": f"Doctor '{doctor_name}' not found"}

    available_slots = APPOINTMENT_SLOTS.get(doctor_key, [])
    if preferred_time not in available_slots:
        return {
            "error": f"Time slot '{preferred_time}' is not available",
            "available_slots": available_slots[:5]
        }

    appointment_id = APPOINTMENTS_DB["next_id"]
    APPOINTMENTS_DB["next_id"] += 1

    appointment = {
        "id": appointment_id,
        "patient": patient_name,
        "doctor": doctor["name"],
        "doctor_specialty": doctor["specialty"],
        "time": preferred_time,
        "location": doctor["location"],
        "status": "confirmed"
    }
    APPOINTMENTS_DB["appointments"][appointment_id] = appointment

    APPOINTMENT_SLOTS[doctor_key].remove(preferred_time)

    return {
        "appointment_id": appointment_id,
        "message": f"Appointment confirmed! You have an appointment with {doctor['name']} ({doctor['specialty']}) on {preferred_time}",
        "doctor": doctor["name"],
        "time": preferred_time,
        "location": doctor["location"],
        "phone": doctor["phone"]
    }


def lookup_appointment(appointment_id):
    """Look up an existing appointment."""
    appointment = APPOINTMENTS_DB["appointments"].get(int(appointment_id))
    if appointment:
        return {
            "appointment_id": appointment_id,
            "patient": appointment["patient"],
            "doctor": appointment["doctor"],
            "doctor_specialty": appointment["doctor_specialty"],
            "time": appointment["time"],
            "location": appointment["location"],
            "status": appointment["status"]
        }
    return {"error": f"Appointment {appointment_id} not found"}


def list_doctors():
    """List all available doctors with their specialties."""
    doctors = []
    for key, doctor in DOCTORS_DB.items():
        doctors.append({
            "name": doctor["name"],
            "specialty": doctor["specialty"],
            "location": doctor["location"]
        })
    return {"doctors": doctors}


# Function mapping dictionary
FUNCTION_MAP = {
    'get_doctor_info': get_doctor_info,
    'book_appointment': book_appointment,
    'lookup_appointment': lookup_appointment,
    'list_doctors': list_doctors
}