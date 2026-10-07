# 🏋️ AI Real-time GYM Coach

An AI-powered real-time gym coaching application that uses **computer vision and pose detection** to monitor exercise movements, track workout progress, and provide intelligent coaching feedback.

## 📌 Project Overview

**AI Real-time GYM Coach** is a computer-vision-based fitness assistant designed to help users perform exercises with better form.

The application uses a webcam to detect body pose landmarks in real time and analyzes exercise movements. It provides workout monitoring, repetition and set tracking, posture analysis, and AI-based coaching feedback.

## ✨ Features

* 👤 User login and personalized workout sessions
* 🏋️ Workout plan creation
* 🎯 Exercise selection
* 🔢 Sets and repetitions tracking
* 📷 Real-time webcam/video input
* 🦴 Real-time human pose detection
* 🧍 Body joints and skeleton visualization
* 📊 Workout metrics and progress tracking
* 📝 Workout history
* 🤖 AI-based coaching feedback
* 🔊 Voice coaching and feedback
* ⚠️ Exercise form and posture monitoring

## 🏃 Supported Exercises

The project currently includes exercise analysis for:

* Squats
* Push-ups
* Biceps Curls
* Shoulder Press
* Lunges

## 🛠️ Technologies Used

| Category             | Technologies                         |
| -------------------- | ------------------------------------ |
| Programming Language | Python                               |
| Web Framework        | Streamlit                            |
| Computer Vision      | OpenCV, MediaPipe                    |
| Data Processing      | NumPy, Pandas                        |
| Real-time Video      | Streamlit-WebRTC                     |
| AI                   | Groq API                             |
| Voice Feedback       | gTTS                                 |
| Core Concepts        | AI, Computer Vision, Pose Estimation |

## 📂 Project Structure

```text
AI Real-time GYM Coach
│
├── Main App
│   ├── core/
│   ├── detector/
│   ├── ml/
│   ├── model/
│   ├── pages/
│   ├── services/
│   ├── static/
│   ├── tutorial-info/
│   ├── main.py
│   ├── packages.txt
│   ├── requirements.txt
│   └── .gitignore
│
└── README.md
```

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/PreshitaSomkuwar/ai-real-time-gym-coach.git
```

### 2. Open the Project

```bash
cd ai-real-time-gym-coach
cd "Main App"
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

### 4. Activate the Virtual Environment

**Windows:**

```bash
venv\Scripts\activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

## 🔐 Environment Configuration

The application may require API credentials for AI-powered coaching features.

**Do not upload API keys or secret credentials to GitHub.**

For local development, configure credentials using your local Streamlit secrets configuration or environment variables.

## ▶️ Run the Application

From the `Main App` directory:

```bash
streamlit run main.py
```

The application will open in your web browser.

## 🔄 How It Works

```text
Webcam / Video Input
        ↓
Real-time Pose Detection
        ↓
Body Landmark Extraction
        ↓
Exercise Movement Analysis
        ↓
Repetition / Set Tracking
        ↓
Posture & Form Analysis
        ↓
AI Coaching Feedback
        ↓
Voice Feedback
```

## 🎯 Project Objective

The main objective of this project is to develop an AI-assisted gym coaching system that can provide real-time exercise monitoring and feedback using computer vision and artificial intelligence.

The system aims to make fitness guidance more accessible by combining pose estimation, workout tracking, and AI-based coaching in a single application.

## 📸 Project Screenshots

Screenshots of the application will be added here to demonstrate the user interface, exercise monitoring, pose detection, and workout tracking features.

## 🚧 Project Status

This project is being developed as a **College Major Project**.

Current development includes the core user interface, workout planning, webcam-based pose detection, exercise analysis, workout tracking, and AI coaching components. Additional improvements and testing are ongoing.

## 👩‍💻 Author

**Preshita Somkuwar**

College Major Project — **AI Real-time GYM Coach**

---

⭐ If you find this project interesting, feel free to explore the repository.
