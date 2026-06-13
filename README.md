# AI-Powered Smart Classroom Monitoring and Attendance System Using Face Recognition

## 📌 Overview
This project introduces an **AI-powered smart classroom monitoring and attendance system** that leverages **face recognition** and **computer vision** to automate attendance tracking and enhance classroom management. Traditional attendance methods are time-consuming, error-prone, and susceptible to proxy attendance. Our solution ensures **accuracy, transparency, and efficiency** while also monitoring student engagement and behavior in real time.

---

## 🚀 Features
- **Automated Attendance**  
  - Real-time face detection and recognition using deep learning (CNNs, MTCNN).  
  - Eliminates proxy attendance and manual errors.  

- **Smart Classroom Monitoring**  
  - Detects inattentiveness (sleeping, mobile phone usage).  
  - Tracks engagement via gaze, posture, and emotion recognition.  

- **Faculty & Student Notifications**  
  - Alerts faculty 10 minutes before class.  
  - Notifies HOD/Principal in case of faculty absence.  
  - Sends absence notifications to parents.  

- **Centralized Database**  
  - Secure storage of attendance and behavioral data.  
  - Easy retrieval and reporting with analytics dashboards.  

- **Scalability & Integration**  
  - Supports multiple classrooms and institutions.  
  - Integrates with Learning Management Systems (LMS).  

---

## 🏗️ System Architecture
The system follows a modular design:

1. **Image Capture Module** – Cameras capture real-time video.  
2. **Face Detection Module** – Identifies faces using Haar cascades / MTCNN.  
3. **Feature Extraction Module** – Generates embeddings via CNNs.  
4. **Face Recognition Module** – Matches faces against the database using similarity metrics.  
5. **Attendance Management Module** – Records attendance automatically.  
6. **Monitoring & Analytics Module** – Tracks student engagement and behavior.  
7. **Database Module** – Stores attendance and monitoring data securely.  
8. **User Interface Module** – Provides dashboards for faculty and administrators.  

---

## 📊 UML Diagrams
- **Use Case Diagram** – Shows interactions between Admin, Faculty, and Students.  
- **Class Diagram** – Defines system classes (Student, Attendance, Camera, FaceRecognition, Database, Admin).  
- **Sequence Diagram** – Step-by-step workflow of attendance marking.  
- **Activity Diagram** – Logical flow from image capture to attendance recording.  
- **Component Diagram** – Organization of system components (Camera, Processing Unit, AI Engine, Database, UI).  

---

## 🔒 Security & Privacy
- Biometric data is encrypted and stored securely.  
- Access control ensures only authorized personnel can view/modify records.  
- Complies with data protection regulations and ethical guidelines.  

---

## ⚙️ Requirements
### Hardware
- High-resolution cameras  
- Edge devices for preprocessing  
- Cloud servers for storage and analytics  

### Software
- Python (OpenCV, TensorFlow/Keras, PyTorch)  
- Database (MySQL/PostgreSQL)  
- Web-based dashboard (Flask/Django)  

---

## 📈 Benefits
- Saves classroom time by automating attendance.  
- Improves accuracy and prevents fraudulent practices.  
- Provides real-time insights into student engagement.  
- Reduces administrative workload with automated reporting.  
- Enhances teaching outcomes through data-driven feedback.  

---

## 🔮 Future Enhancements
- Integration of multimodal biometrics (fingerprint, iris).  
- Emotion recognition for deeper engagement analysis.  
- Predictive analytics for attendance and performance trends.  
- Improved recognition under challenging conditions (lighting, masks).  

---

## 🏫 Institution
Developed at **Avanthi Institute of Engineering and Technology (AIETTA)**, Department of Master of Computer Applications.  
NAAC “A+” Accredited, Affiliated to J.N.T.U-GV., Vizianagaram.  

---

## 📧 Contact
For inquiries: [principal@aietta.ac.in](mailto:principal@aietta.ac.in)  
Website: [www.aietta.ac.in](http://www.aietta.ac.in)

