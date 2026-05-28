import random
from datetime import datetime


class HospitalAgent:
    def __init__(self):
        self.departments = {
            "cardiology": ["Dr. Smith", "Dr. Patel"],
            "dermatology": ["Dr. Brown", "Dr. Mehta"],
            "general medicine": ["Dr. Wilson", "Dr. Sharma"],
            "orthopedics": ["Dr. Taylor", "Dr. Khan"],
            "pediatrics": ["Dr. Clark", "Dr. Rao"],
        }
        self.patients = {}
        self.appointments = []

    def handle_request(self, message: str) -> str:
        msg = message.lower()

        if msg.startswith("register patient"):
            return self.register_patient(message)

        if "book" in msg or "appointment" in msg:
            return self.book_appointment(message)

        if "appointments" in msg or "history" in msg:
            return self.get_appointments()

        if any(word in msg for word in ["emergency", "accident", "chest pain", "bleeding"]):
            return "Emergency detected. Please call emergency services immediately or visit the nearest ER."

        if any(word in msg for word in ["fever", "cough", "pain", "rash", "headache"]):
            return self.symptom_checker(msg)

        if "doctor" in msg or "department" in msg:
            return self.list_departments()

        if "medicine" in msg or "prescription" in msg:
            return "Medicine safety warning: Do not take medication without consulting a licensed doctor."

        if "billing" in msg or "bill" in msg or "invoice" in msg:
            return "Billing support is available from 9 AM to 6 PM. Please provide your patient ID or invoice number."

        if "visiting" in msg or "hours" in msg:
            return "Hospital visiting hours are 10 AM to 12 PM and 5 PM to 7 PM."

        if msg in ["hi", "hello", "hey"]:
            return "Hello! I can help with patient registration, appointments, symptoms, doctors, billing, and emergency guidance."

        return "I can help with registration, appointments, symptoms, departments, billing, and hospital information."

    def register_patient(self, message: str) -> str:
        name = message.replace("register patient", "").strip()

        if not name:
            return "Please provide patient name. Example: Register patient Nilesh"

        patient_id = f"PAT-{random.randint(1000, 9999)}"
        self.patients[patient_id] = {
            "name": name,
            "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        return f"Patient registered successfully. Name: {name}, Patient ID: {patient_id}"

    def book_appointment(self, message: str) -> str:
        msg = message.lower()
        department = None

        for dept in self.departments:
            if dept in msg:
                department = dept
                break

        if not department:
            return "Please mention department. Example: Book appointment for cardiology"

        doctor = random.choice(self.departments[department])
        appointment_id = f"APT-{random.randint(1000, 9999)}"

        appointment = {
            "appointment_id": appointment_id,
            "department": department,
            "doctor": doctor,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.appointments.append(appointment)

        return f"Appointment booked. ID: {appointment_id}, Department: {department.title()}, Doctor: {doctor}"

    def get_appointments(self) -> str:
        if not self.appointments:
            return "No appointments found."

        result = "Appointment history:\n"
        for appt in self.appointments:
            result += f"{appt['appointment_id']} - {appt['department'].title()} with {appt['doctor']} at {appt['created_at']}\n"

        return result

    def list_departments(self) -> str:
        result = "Available departments:\n"
        for dept, doctors in self.departments.items():
            result += f"- {dept.title()}: {', '.join(doctors)}\n"
        return result

    def symptom_checker(self, msg: str) -> str:
        if "chest pain" in msg:
            return "Chest pain can be serious. Please seek emergency care immediately."
        if "fever" in msg:
            return "For fever, consult General Medicine if it lasts more than 2 days."
        if "rash" in msg:
            return "For skin rash, Dermatology is recommended."
        if "joint" in msg or "bone" in msg:
            return "For joint or bone pain, Orthopedics is recommended."
        if "cough" in msg:
            return "For cough, consult General Medicine if it continues or becomes severe."

        return "Please describe your symptoms clearly."