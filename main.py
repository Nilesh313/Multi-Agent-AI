from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from agent import HospitalAgent
from database import SessionLocal, Patient, create_tables
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from auth import authenticate_user, create_access_token, get_current_user

app = FastAPI(title="Hospital Agentic AI Chatbot")
create_tables()

agent = HospitalAgent()


class ChatRequest(BaseModel):
    message: str

class PatientCreate(BaseModel):
    name: str
    age: int
    gender: str
    phone: str

@app.get("/", response_class=HTMLResponse)
def home():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Hospital Agentic AI</title>
    <style>
        * { box-sizing: border-box; }
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #eef3f8;
        }
        .layout {
            display: flex;
            min-height: 100vh;
        }
        .sidebar {
            width: 230px;
            background: #123456;
            color: white;
            padding: 25px;
        }
        .sidebar h2 {
            margin-bottom: 30px;
        }
        .sidebar p {
            padding: 12px;
            background: rgba(255,255,255,0.1);
            border-radius: 8px;
        }
        .main {
            flex: 1;
            padding: 25px;
        }
        .header {
            background: white;
            padding: 20px;
            border-radius: 14px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        .card {
            background: white;
            padding: 20px;
            border-radius: 14px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }
        input, button {
            width: 100%;
            padding: 11px;
            margin: 7px 0;
            border-radius: 8px;
            border: 1px solid #ccc;
        }
        button {
            background: #0066cc;
            color: white;
            border: none;
            cursor: pointer;
            font-weight: bold;
        }
        button:hover {
            background: #004f9e;
        }
        #messages {
            height: 320px;
            overflow-y: auto;
            background: #f7f9fc;
            border: 1px solid #ddd;
            padding: 12px;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        .user {
            background: #dbeafe;
            padding: 10px;
            margin: 8px;
            border-radius: 10px;
            text-align: right;
        }
        .bot {
            background: #dcfce7;
            padding: 10px;
            margin: 8px;
            border-radius: 10px;
        }
        pre {
            background: #f7f9fc;
            padding: 12px;
            border-radius: 10px;
            max-height: 260px;
            overflow-y: auto;
        }
        .status {
            font-weight: bold;
            color: green;
        }
    </style>
</head>
<body>

<div class="layout">
    <div class="sidebar">
        <h2>🏥 Hospital AI</h2>
        <p>Dashboard</p>
        <p>Chatbot</p>
        <p>Patients</p>
        <p>Appointments</p>
    </div>

    <div class="main">
        <div class="header">
            <h1>Hospital Agentic AI Assistant</h1>
            <p>Login, chat with the assistant, and manage patient records.</p>
            <p id="loginStatus" class="status">Not logged in</p>
        </div>

        <div class="grid">
            <div class="card">
                <h2>Login</h2>
                <input id="username" value="admin" placeholder="Username">
                <input id="password" value="admin123" type="password" placeholder="Password">
                <button onclick="login()">Login</button>
            </div>

            <div class="card">
                <h2>Add Patient</h2>
                <input id="patientName" placeholder="Patient name">
                <input id="patientAge" placeholder="Age">
                <input id="patientGender" placeholder="Gender">
                <input id="patientPhone" placeholder="Phone">
                <button onclick="addPatient()">Add Patient</button>
                <button onclick="getPatients()">Show Patients</button>
            </div>

            <div class="card">
                <h2>Chatbot</h2>
                <div id="messages"></div>
                <input id="userInput" placeholder="Ask something...">
                <button onclick="sendMessage()">Send Message</button>
            </div>

            <div class="card">
                <h2>Patient Records</h2>
                <pre id="patientOutput">No patient data loaded.</pre>
            </div>
        </div>
    </div>
</div>

<script>
let token = "";

async function login() {
    const formData = new URLSearchParams();
    formData.append("username", document.getElementById("username").value);
    formData.append("password", document.getElementById("password").value);

    const response = await fetch("/login", {
        method: "POST",
        headers: {"Content-Type": "application/x-www-form-urlencoded"},
        body: formData
    });

    const data = await response.json();

    if (data.access_token) {
        token = data.access_token;
        document.getElementById("loginStatus").innerText = "Logged in successfully";
    } else {
        document.getElementById("loginStatus").innerText = "Login failed";
    }
}

async function sendMessage() {
    const input = document.getElementById("userInput");
    const text = input.value.trim();
    const messages = document.getElementById("messages");

    if (!text) return;

    messages.innerHTML += `<div class="user"><b>You:</b> ${text}</div>`;
    input.value = "";

    const response = await fetch("/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({message: text})
    });

    const data = await response.json();
    messages.innerHTML += `<div class="bot"><b>Bot:</b> ${data.agent_response}</div>`;
    messages.scrollTop = messages.scrollHeight;
}

async function addPatient() {
    if (!token) {
        alert("Please login first");
        return;
    }

    const patient = {
        name: document.getElementById("patientName").value,
        age: parseInt(document.getElementById("patientAge").value),
        gender: document.getElementById("patientGender").value,
        phone: document.getElementById("patientPhone").value
    };

    const response = await fetch("/patients", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify(patient)
    });

    const data = await response.json();
    document.getElementById("patientOutput").innerText = JSON.stringify(data, null, 2);
}

async function getPatients() {
    if (!token) {
        alert("Please login first");
        return;
    }

    const response = await fetch("/patients", {
        method: "GET",
        headers: {
            "Authorization": "Bearer " + token
        }
    });

    const data = await response.json();
    document.getElementById("patientOutput").innerText = JSON.stringify(data, null, 2);
}
</script>

</body>
</html>
"""
@app.post("/chat")
def chat(request: ChatRequest):
    response = agent.handle_request(request.message)
    return {
        "user_message": request.message,
        "agent_response": response
    }


@app.get("/departments")
def departments():
    return agent.departments


@app.get("/appointments")
def appointments():
    return agent.appointments

@app.get("/patients")
def patients():
    return agent.patients


@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/patients")
def create_patient(patient: PatientCreate):
    db = SessionLocal()

    new_patient = Patient(
        name=patient.name,
        age=patient.age,
        gender=patient.gender,
        phone=patient.phone
    )

    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    db.close()

    return {
        "message": "Patient created successfully",
        "patient_id": new_patient.id,
        "name": new_patient.name
    }


# @app.get("/patients")
# def get_patients():
#     db = SessionLocal()
#     patients = db.query(Patient).all()
#     db.close()
#     return patients
@app.post("/patients")
def create_patient(patient: PatientCreate, current_user=Depends(get_current_user)):
    db = SessionLocal()

    new_patient = Patient(
        name=patient.name,
        age=patient.age,
        gender=patient.gender,
        phone=patient.phone
    )

    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    db.close()

    return {
        "message": "Patient created successfully",
        "patient_id": new_patient.id,
        "created_by": current_user["username"]
    }


@app.get("/patients")
def get_patients(current_user=Depends(get_current_user)):
    db = SessionLocal()
    patients = db.query(Patient).all()
    db.close()
    return patients

@app.post("/seed-patients")
def seed_patients():
    db = SessionLocal()

    dummy_patients = [
        Patient(name="Nilesh Patel", age=25, gender="Male", phone="9876543210"),
        Patient(name="Priya Sharma", age=31, gender="Female", phone="9123456780"),
        Patient(name="Aarav Mehta", age=40, gender="Male", phone="9988776655"),
        Patient(name="Sneha Rao", age=29, gender="Female", phone="9012345678"),
        Patient(name="Rahul Verma", age=35, gender="Male", phone="9090909090")
    ]

    db.add_all(dummy_patients)
    db.commit()
    db.close()

    return {"message": "Dummy patients inserted successfully"}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)

    if not user:
        return {"error": "Invalid username or password"}

    token = create_access_token(data={"sub": user["username"]})

    return {
        "access_token": token,
        "token_type": "bearer"
    }