from db import doctor_collection, appointment_collection, user_collection
from pymongo.errors import DuplicateKeyError
from datetime import datetime
from bson import ObjectId

from utils.date_utils import normalize_date, normalize_time




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

def get_doctor_info(doctor_name):
    doctor = doctor_collection.find_one({"name": {"$regex": doctor_name, "$options": "i"}})

    if not doctor:
        return {"error": f"Doctor '{doctor_name}' not found"}

    return {
        "name": doctor["name"],
        "specialization": doctor["specialization"],
        "location": doctor["location"],
        "phone": doctor["phone"],
        # "next_available_slots": slot_list
    }




def list_doctors(category: str):

    doctors = list(doctor_collection.find({
        "categoryName": {"$regex": f"^{category}$", "$options": "i"}
    }))

    if not doctors:
        return {
            "message": f"Sorry, no doctors found under {category}."
        }

    doctor_names = [doc["name"] for doc in doctors]

    spoken_list = ", ".join(doctor_names)

    return {
        "message": f"Here are the available {category} doctors: {spoken_list}.",
        "doctors": doctor_names 
    }


















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


def book_appointment(patient_name, doctor_name, preferred_date, preferred_time):
    try:
        normalized_date = normalize_date(preferred_date)
        normalized_time = normalize_time(preferred_time)
    except ValueError as e:
        return {
            "error": "Invalid date or time",
            "message": str(e)
        }

    registered_user = user_collection.find_one({
        "name": {"$regex": patient_name, "$options": "i"}
    })
    

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

    if registered_user: 
        appointment = {
        "userId": registered_user["_id"],
        "doctorId": doctor_id,
        "doctorName": doctor["name"],
        # "patientName": patient_name,
        "patientName": registered_user['username'],
        "date": normalized_date,
        "time": normalized_time,
        "status": "confirmed",
        "paymentStatus": "Pending"
        # "createdAt": datetime.utcnow()
    }
    else:
        appointment = {
            "doctorId": doctor_id,
            "doctorName": doctor["name"],
            "patientName": patient_name,
            "date": normalized_date,
            "time": normalized_time,
            "status": "confirmed",
            "paymentStatus": "Pending"
            # "createdAt": datetime.utcnow()
        }

    result = appointment_collection.insert_one(appointment)

    return {
        "message": "Appointment confirmed",
        "date": normalized_date,
        "time": normalized_time
    }






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



def cancel_appointment(patient_name, doctor_name, appointment_date, appointment_time):
    try:
        normalized_date = normalize_date(appointment_date)
        normalized_time = normalize_time(appointment_time)
    except ValueError as e:
        return {"error": str(e)}

    doctor = doctor_collection.find_one({
        "name": {"$regex": doctor_name, "$options": "i"}
    })

    if not doctor:
        return {"error": "Doctor not found."}

    result = appointment_collection.find_one_and_update(
        {
            "doctorId": doctor["_id"],
            "patientName": patient_name,
            "date": normalized_date,
            "time": normalized_time,
            "status": "confirmed"
        },
        {
            "$set": {"status": "cancelled"}
        }
    )

    if not result:
        return {
            "error": "No matching appointment found."
        }

    return {
        "message": f"Your appointment on {normalized_date} at {normalized_time} has been successfully cancelled."
    }















# {
#                 "name": "reschedule_appointment",
#                 "description": "Reschedule an existing appointment to a new date and time. Call this function when the patient wants to change the date or time of a booked appointment. Make sure you have both the old appointment details and the new preferred date and time before calling.",
#                 "parameters": {
#                   "type": "object",
#                   "properties": {
#                     "patient_name": {
#                       "type": "string",
#                       "description": "Full name of the patient."
#                     },
#                     "doctor_name": {
#                       "type": "string",
#                       "description": "Doctor with whom the appointment exists."
#                     },
#                     "old_date": {
#                       "type": "string",
#                       "description": "Existing appointment date in natural language."
#                     },
#                     "old_time": {
#                       "type": "string",
#                       "description": "Existing appointment time in natural language."
#                     },
#                     "new_date": {
#                       "type": "string",
#                       "description": "New preferred appointment date in natural language."
#                     },
#                     "new_time": {
#                       "type": "string",
#                       "description": "New preferred appointment time in natural language."
#                     }
#                   },
#                   "required": [
#                     "patient_name",
#                     "doctor_name",
#                     "old_date",
#                     "old_time",
#                     "new_date",
#                     "new_time"
#                   ]
#                 }
#               }

# def reschedule_appointment(
#     patient_name,
#     doctor_name,
#     old_date,
#     old_time,
#     new_date,
#     new_time
# ):

#     try:
#         old_date_norm = normalize_date(old_date)
#         old_time_norm = normalize_time(old_time)
#         new_date_norm = normalize_date(new_date)
#         new_time_norm = normalize_time(new_time)
#     except ValueError as e:
#         return {"error": str(e)}

#     doctor = doctor_collection.find_one({
#         "name": {"$regex": doctor_name, "$options": "i"}
#     })

#     if not doctor:
#         return {"error": "Doctor not found."}

#     # Check if new slot is already booked
#     conflict = appointment_collection.find_one({
#         "doctorId": doctor["_id"],
#         "date": new_date_norm,
#         "time": new_time_norm,
#         "status": "confirmed"
#     })

#     if conflict:
#         return {
#             "error": "Requested new time slot is already booked. Please choose another time."
#         }

#     # Update existing appointment
#     updated = appointment_collection.find_one_and_update(
#         {
#             "doctorId": doctor["_id"],
#             "patientName": patient_name,
#             "date": old_date_norm,
#             "time": old_time_norm,
#             "status": "confirmed"
#         },
#         {
#             "$set": {
#                 "date": new_date_norm,
#                 "time": new_time_norm
#             }
#         }
#     )

#     if not updated:
#         return {"error": "Original appointment not found."}

#     return {
#         "message": f"Your appointment has been rescheduled to {new_date_norm} at {new_time_norm}."
#     }




# Function mapping dictionary
FUNCTION_MAP = {
    'list_doctors': list_doctors,
    'get_doctor_info': get_doctor_info,
    'book_appointment': book_appointment,
    'lookup_appointment': lookup_appointment,
    'cancel_appointment': cancel_appointment,
    # 'reschedule_appointment': reschedule_appointment,
}