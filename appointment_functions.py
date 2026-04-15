from db import doctor_collection, appointment_collection, user_collection
from pymongo.errors import DuplicateKeyError
from datetime import datetime
from bson import ObjectId
import re
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
    doctor = doctor_collection.find_one({"name": {"$regex": doctor_name.strip(), "$options": "i"}
})

    if not doctor:
        return {"error": f"Doctor '{doctor_name}' not found"}

    return {
        "name": doctor["name"],
        "specialization": doctor["specialization"],
        "location": doctor["location"],
        "phone": doctor["phone"],
        # "next_available_slots": slot_list
    }




def list_doctors(category: str = None):

    if not category:
        available_categories = [c for c in doctor_collection.distinct("categoryName") if c]
        if available_categories:
            return {
                "message": f"Please tell me a category. Available categories are: {', '.join(available_categories)}."
            }
        return {
            "message": "Please tell me which doctor category you are looking for."
        }

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
#         "name": {"$regex": doctor_name.strip(), "$options": "i"}
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
        "username": {"$regex": patient_name, "$options": "i"}
    })
    print("checking if patient is registered: ", registered_user)

    doctor = doctor_collection.find_one({
        "name": {"$regex": doctor_name.strip(), "$options": "i"} 
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
        "patientId": registered_user["_id"],
        "patientName": registered_user['username'],
        "doctorId": doctor_id,
        "doctorName": doctor["name"],
        # "patientName": patient_name,
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






# def lookup_appointment(patient_name):

#     appointment = appointment_collection.find_one(
#         {"patientName": {"$regex": f"^{patient_name}$", "$options": "i"}}
#     )

#     if not appointment:
#         return {"error": "Appointment not found"}

#     return {
#         "patient": appointment["patientName"],
#         "doctor": appointment["doctorName"],
#         "date": appointment["date"],
#         "time": appointment["time"]
#     }
def lookup_appointment(patient_name=None, appointment_id=None):
    query = {}

    if appointment_id:
        query["_id"] = ObjectId(appointment_id)
    elif patient_name:
        query["patientName"] = {"$regex": f"^{patient_name}$", "$options": "i"}
    else:
        return {"error": "Provide patient name or appointment ID"}

    appointment = appointment_collection.find_one(query)

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
        "name": {"$regex": doctor_name.strip(), "$options": "i"}
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









def reschedule_appointment(
    patient_name,
    doctor_name,
    old_date,
    old_time,
    new_date,
    new_time
):
    try:
        old_date_norm = normalize_date(old_date)
        old_time_norm = normalize_time(old_time)
        new_date_norm = normalize_date(new_date)
        new_time_norm = normalize_time(new_time)
    except ValueError as e:
        return {"error": str(e)}

    patient_name = patient_name.strip()
    doctor_name = doctor_name.strip()

    if old_date_norm == new_date_norm and old_time_norm == new_time_norm:
        return {"error": "New date/time is same as old date/time"}

    # Resolve doctor first (preferred, unambiguous)
    doctor = doctor_collection.find_one({
        "name": {"$regex": f"^{re.escape(doctor_name)}$", "$options": "i"}
    })

    # Find the exact original confirmed appointment
    original_query = {
        "patientName": {"$regex": f"^{re.escape(patient_name)}$", "$options": "i"},
        "date": old_date_norm,
        "time": old_time_norm,
        "status": "confirmed"
    }

    if doctor:
        original_query["doctorId"] = doctor["_id"]
    else:
        # Fallback by doctorName if doctor master record is missing
        original_query["doctorName"] = {
            "$regex": f"^(Dr\\.?\\s*)?{re.escape(doctor_name)}$",
            "$options": "i"
        }

    original_appointment = appointment_collection.find_one(original_query)

    if not original_appointment:
        return {"error": "Original appointment not found"}

    doctor_id = original_appointment.get("doctorId")
    doctor_display_name = original_appointment.get("doctorName", doctor_name)

    # Check conflict in requested new confirmed slot (excluding current appointment)
    conflict_query = {
        "date": new_date_norm,
        "time": new_time_norm,
        "status": "confirmed",
        "_id": {"$ne": original_appointment["_id"]}
    }

    if doctor_id:
        conflict_query["doctorId"] = doctor_id
    else:
        conflict_query["doctorName"] = {
            "$regex": f"^{re.escape(doctor_display_name)}$",
            "$options": "i"
        }

    if appointment_collection.find_one(conflict_query):
        return {"error": "New slot already booked"}

    updated = appointment_collection.find_one_and_update(
        {"_id": original_appointment["_id"]},
        {
            "$set": {
                "date": new_date_norm,
                "time": new_time_norm,
                "updatedAt": datetime.utcnow()
            }
        }
    )

    if not updated:
        return {"error": "Failed to reschedule appointment"}

    return {
        "message": f"Appointment with {doctor_display_name} rescheduled to {new_date_norm} at {new_time_norm}",
        "old_date": old_date_norm,
        "old_time": old_time_norm,
        "new_date": new_date_norm,
        "new_time": new_time_norm
    }





# Function mapping dictionary
FUNCTION_MAP = {
    'list_doctors': list_doctors,
    'get_doctor_info': get_doctor_info,
    'book_appointment': book_appointment,
    'lookup_appointment': lookup_appointment,
    'cancel_appointment': cancel_appointment,
    'reschedule_appointment': reschedule_appointment,
}