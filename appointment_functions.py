from db import doctor_collection, appointment_collection
from pymongo.errors import DuplicateKeyError
from datetime import datetime
from bson import ObjectId

from utils.date_utils import normalize_date, normalize_time

# Simple in-memory storage
# APPOINTMENTS_DB = {"appointments": {}, "next_id": 1000}

# DOCTORS_DB = {
#     "john_smith": {
#         "name": "Dr. John Smith",
#         "specialization": "General Practitioner",
#         "availability": ["Monday 9AM-5PM", "Tuesday 9AM-5PM", "Wednesday 9AM-1PM", "Thursday 9AM-5PM", "Friday 9AM-5PM"],
#         "location": "Building A, Room 101",
#         "phone": "555-0101"
#     },
#     "sarah_wilson": {
#         "name": "Dr. Sarah Wilson",
#         "specialization": "Cardiology",
#         "availability": ["Monday 10AM-4PM", "Wednesday 10AM-4PM", "Friday 10AM-4PM"],
#         "location": "Building B, Room 205",
#         "phone": "555-0102"
#     },
#     "michael_brown": {
#         "name": "Dr. Michael Brown",
#         "specialization": "Orthopedics",
#         "availability": ["Tuesday 8AM-12PM", "Wednesday 2PM-6PM", "Thursday 8AM-12PM", "Friday 1PM-5PM"],
#         "location": "Building C, Room 310",
#         "phone": "555-0103"
#     },
#     "emily_davis": {
#         "name": "Dr. Emily Davis",
#         "specialization": "Dermatology",
#         "availability": ["Monday 1PM-5PM", "Tuesday 9AM-1PM", "Thursday 2PM-6PM"],
#         "location": "Building A, Room 202",
#         "phone": "555-0104"
#     },
#     "david_martinez": {
#         "name": "Dr. David Martinez",
#         "specialization": "Pediatrics",
#         "availability": ["Monday 9AM-12PM", "Tuesday 1PM-5PM", "Wednesday 9AM-12PM", "Thursday 1PM-5PM", "Friday 9AM-12PM"],
#         "location": "Building B, Room 150",
#         "phone": "555-0105"
#     }
# }

# APPOINTMENT_SLOTS = {
#     "john_smith": ["Monday 10:00 AM", "Monday 2:00 PM", "Tuesday 11:00 AM", "Tuesday 3:00 PM", "Wednesday 10:00 AM", "Thursday 9:00 AM", "Thursday 2:00 PM", "Friday 1:00 PM"],
#     "sarah_wilson": ["Monday 10:30 AM", "Monday 3:00 PM", "Wednesday 11:00 AM", "Wednesday 3:30 PM", "Friday 10:00 AM", "Friday 2:00 PM"],
#     "michael_brown": ["Tuesday 8:30 AM", "Tuesday 11:00 AM", "Wednesday 2:30 PM", "Wednesday 4:00 PM", "Thursday 9:00 AM", "Friday 1:30 PM"],
#     "emily_davis": ["Monday 1:30 PM", "Monday 4:00 PM", "Tuesday 9:30 AM", "Tuesday 12:00 PM", "Thursday 2:30 PM"],
#     "david_martinez": ["Monday 9:30 AM", "Monday 11:00 AM", "Tuesday 1:30 PM", "Tuesday 3:00 PM", "Wednesday 9:30 AM", "Wednesday 11:00 AM", "Thursday 1:30 PM", "Friday 9:30 AM"]
# }











# Operations on the Mock DB

# def get_doctor_info(doctor_name):
#     """Get information about a specific doctor."""
#     doctor_key = doctor_name.lower().replace(" ", "_")
#     doctor = DOCTORS_DB.get(doctor_key)
#     if doctor:
#         available_slots = APPOINTMENT_SLOTS.get(doctor_key, [])
#         return {
#             "name": doctor["name"],
#             "specialization": doctor["specialization"],
#             "location": doctor["location"],
#             "phone": doctor["phone"],
#             "availability": doctor["availability"],
#             "next_available_slots": available_slots[:3]  # Show next 3 slots
#         }
#     return {"error": f"Doctor '{doctor_name}' not found. Available doctors: Dr. John Smith, Dr. Sarah Wilson, Dr. Michael Brown, Dr. Emily Davis, Dr. David Martinez"}

# from db import doctor_collection, slot_collection

# def get_doctor_info(doctor_name):
#     doctor = doctor_collection.find_one({"name": {"$regex": doctor_name, "$options": "i"}})

#     if not doctor:
#         return {"error": f"Doctor '{doctor_name}' not found"}

#     slots = slot_collection.find({"doctor_id": doctor["_id"], "available": True}).limit(3)

#     slot_list = [slot["time"] for slot in slots]

#     return {
#         "name": doctor["name"],
#         "specialization": doctor["specialization"],
#         "location": doctor["location"],
#         "phone": doctor["phone"],
#         "next_available_slots": slot_list
#     }


































# def book_appointment(patient_name, doctor_name, preferred_time):
#     """Book an appointment with a doctor."""
#     doctor_key = doctor_name.lower().replace(" ", "_")
#     doctor = DOCTORS_DB.get(doctor_key)
#     if not doctor:
#         return {"error": f"Doctor '{doctor_name}' not found"}

#     available_slots = APPOINTMENT_SLOTS.get(doctor_key, [])
#     if preferred_time not in available_slots:
#         return {
#             "error": f"Time slot '{preferred_time}' is not available",
#             "available_slots": available_slots[:5]
#         }

#     appointment_id = APPOINTMENTS_DB["next_id"]
#     APPOINTMENTS_DB["next_id"] += 1

#     appointment = {
#         "id": appointment_id,
#         "patient": patient_name,
#         "doctor": doctor["name"],
#         "doctor_specialization": doctor["specialization"],
#         "time": preferred_time,
#         "location": doctor["location"],
#         "status": "confirmed"
#     }
#     APPOINTMENTS_DB["appointments"][appointment_id] = appointment

#     # Remove the booked slot from availability
#     APPOINTMENT_SLOTS[doctor_key].remove(preferred_time)

#     return {
#         "appointment_id": appointment_id,
#         "message": f"Appointment confirmed! You have an appointment with{doctor['name']} ({doctor['specialization']}) on {preferred_time}",
#         "doctor": doctor["name"],
#         "time": preferred_time,
#         "location": doctor["location"],
#         "phone": doctor["phone"]
#     }

# from datetime import datetime

# def book_appointment(patient_name, doctor_name, preferred_day, preferred_time):
#     doctor = doctor_collection.find_one(
#         {"name": {"$regex": doctor_name, "$options": "i"}}
#     )

#     if not doctor:
#         return {"error": f"Doctor '{doctor_name}' not found"}

#     slot = slot_collection.find_one({
#         "doctor_id": doctor["_id"],
#         "time": preferred_time,
#         "available": True
#     })

#     if not slot:
#         return {"error": f"Time slot '{preferred_time}' not available"}

#     # Create appointment
#     appointment = {
#         "patient": patient_name,
#         "doctor_id": doctor["_id"],
#         "doctor_name": doctor["name"],
#         "time": preferred_time,
#         "location": doctor["location"],
#         "status": "confirmed",
#         "created_at": datetime.utcnow()
#     }

#     result = appointment_collection.insert_one(appointment)

#     # Mark slot unavailable
#     slot_collection.update_one(
#         {"_id": slot["_id"]},
#         {"$set": {"available": False}}
#     )

#     return {
#         "appointment_id": str(result.inserted_id),
#         "doctor": doctor["name"],
#         "time": preferred_time,
#         "location": doctor["location"],
#         "message": "Appointment confirmed"
#     }


# def book_appointment(patient_name, patient_phone, doctor_name, preferred_date, preferred_time):

#     doctor = doctor_collection.find_one({
#         "name": {"$regex": doctor_name, "$options": "i"}
#     })

#     if not doctor:
#         return {"error": "Doctor not found"}

#     try:
#         appointment = {
#             "doctorId": doctor["_id"],
#             "doctorName": doctor["name"],
#             "patientName": patient_name,
#             # "patientPhone": patient_phone,
#             "date": preferred_date,
#             "startTime": preferred_time,
#             "status": "confirmed",
#             "createdAt": datetime.utcnow()
#         }

#         appointment_collection.insert_one(appointment)

#         return {
#             "message": f"Appointment confirmed with {doctor['name']} at {preferred_time}"
#         }

#     except DuplicateKeyError:
#         return {
#             "error": "Slot already booked",
#             "message": "That time is already taken. Please choose another time."
#         }



# def book_appointment(patient_name, doctor_name, preferred_date, preferred_time):

#     # 1️⃣ Find doctor
#     doctor = doctor_collection.find_one({
#         "name": {"$regex": doctor_name, "$options": "i"}
#     })

#     if not doctor:
#         return {"error": f"Doctor {doctor_name} not found"}

#     doctor_id = doctor["_id"]

#     # 2️⃣ Check if slot already booked
#     existing_appointment = appointment_collection.find_one({
#         "doctorId": doctor_id,
#         "date": preferred_date,
#         "time": preferred_time,
#         # "status": "confirmed"
#     })

#     if existing_appointment:
#         return {
#             "error": "Slot already booked",
#             "message": "That time is not available. Please select another time."
#         }

#     # 3️⃣ Create appointment
#     appointment = {
#         "doctorId": doctor_id,
#         "doctorName": doctor["name"],
#         "patientName": patient_name,
#         # "patientPhone": patient_phone,
#         "date": preferred_date,
#         "time": preferred_time,
#         # "status": "confirmed",
#         # "bookedVia": "voice_ai",
#         # "createdAt": datetime.utcnow()
#     }

#     result = appointment_collection.insert_one(appointment)

#     return {
#         "appointment_id": str(result.inserted_id),
#         "doctor": doctor["name"],
#         "date": preferred_date,
#         "time": preferred_time,
#         "message": "Appointment confirmed successfully"
#     }

from utils.date_utils import normalize_date, normalize_time

def book_appointment(patient_name, doctor_name, preferred_date, preferred_time):

    try:
        normalized_date = normalize_date(preferred_date)
        normalized_time = normalize_time(preferred_time)
    except ValueError as e:
        return {
            "error": "Invalid date or time",
            "message": str(e)
        }

    doctor = doctor_collection.find_one({
        "name": {"$regex": doctor_name, "$options": "i"}
    })

    if not doctor:
        return {"error": "Doctor not found"}

    doctor_id = doctor["_id"]

    existing = appointment_collection.find_one({
        "doctorId": doctor_id,
        "date": normalized_date,
        "time": normalized_time
    })

    if existing:
        return {
            "error": "Slot already booked",
            "message": "That time is not available. Please choose another time."
        }

    appointment = {
        "doctorId": doctor_id,
        "doctorName": doctor["name"],
        "patientName": patient_name,
        "date": normalized_date,
        "time": normalized_time,
        # "status": "confirmed",
        # "createdAt": datetime.utcnow()
    }

    result = appointment_collection.insert_one(appointment)

    return {
        "message": "Appointment confirmed",
        "date": normalized_date,
        "time": normalized_time
    }















# def lookup_appointment(appointment_id):
#     """Look up an existing appointment."""
#     appointment = APPOINTMENTS_DB["appointments"].get(int(appointment_id))
#     if appointment:
#         return {
#             "appointment_id": appointment_id,
#             "patient": appointment["patient"],
#             "doctor": appointment["doctor"],
#             "doctor_specialization": appointment["doctor_specialization"],
#             "time": appointment["time"],
#             "location": appointment["location"],
#             "status": appointment["status"]
#         }
#     return {"error": f"Appointment {appointment_id} not found"}

def lookup_appointment(patient_name):

    appointment = appointment_collection.find_one(
        {"patientName": {"$regex": f"^{patient_name}$", "$options": "i"}}
    )

    if not appointment:
        return {"error": "Appointment not found"}

    return {
        "patient": appointment["patientName"],
        "doctor": appointment["doctorName"],
        "date": appointment["date"],
        "time": appointment["time"]
    }

# def list_doctors():
#     doctors = doctor_collection.find()

#     doctor_list = []
#     for doc in doctors:
#         doctor_list.append({
#             "name": doc["name"],
#             "specialization": doc["specialization"],
#             "location": doc["location"]
#         })

#     return {"doctors": doctor_list}


# Function mapping dictionary
FUNCTION_MAP = {
    # 'get_doctor_info': get_doctor_info,
    'book_appointment': book_appointment,
    'lookup_appointment': lookup_appointment,
    # 'list_doctors': list_doctors
}