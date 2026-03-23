# 🔐 SecureGate - Facial Recognition Access Control Demo

A professional desktop application demonstrating facial recognition technology for access control gates and security systems.

## Features

- **User Registration**: Register new users via webcam capture or by loading existing photos
- **Real-time Face Detection**: Live camera feed with face detection overlay
- **Access Control Simulation**: Visual feedback for granted/denied access
- **Access Logging**: Complete audit trail of all access attempts
- **Persistent Storage**: Registered faces stored in JSON format
- **Professional UI**: Modern dark theme interface suitable for business demonstrations

## Requirements

- Python 3.8+
- OpenCV (opencv-python-headless)
- NumPy
- Pillow (PIL)
- tkinter (usually included with Python)

## Installation

1. Install required dependencies:
```bash
pip install opencv-python-headless numpy pillow
```

2. Run the application:
```bash
python facial_recognition_gate.py
```

## Usage

### Registering New Users

**Option 1: Via Webcam**
1. Click "👤 Register New User"
2. Enter the user's name
3. Click "📷 Start Camera"
4. Position your face in the frame
5. Click "💾 Capture & Register"

**Option 2: From Image Files**
1. Click "📁 Load Known Faces"
2. Select one or more face images (JPG, PNG, BMP)
3. The filename (without extension) will be used as the user's name

### Monitoring Mode

1. Click "▶ Start Monitoring" to activate the camera
2. The system will continuously monitor for faces
3. When a face is detected:
   - **Green flash**: Access granted (recognized user)
   - **Red flash**: Access denied (unknown person)
4. All access attempts are logged in the right panel

### Managing Data

- **View Registered Users**: See all registered users in the left panel
- **Clear Log**: Remove all entries from the access log
- **Clear All Data**: Delete all registered face data

## Business Use Case

This demo showcases a complete facial recognition access control system suitable for:

- Office building entry gates
- Secure facility access points
- Employee time tracking systems
- Visitor management systems
- High-security areas

## Technical Notes

- Uses OpenCV's Haar Cascade classifier for face detection
- For production use, consider integrating with `face_recognition` library for actual face matching
- Camera feed requires a working webcam connected to the system
- All data is stored locally in `registered_faces.json`

## Customization

The application can be customized for specific business needs:

- Modify confidence thresholds for access decisions
- Integrate with physical gate controllers via GPIO or API
- Add database backend for multi-location deployments
- Implement user roles and access levels
- Add photo capture for audit purposes

## License

MIT License - Feel free to modify and distribute for your business needs.

---

**Demo Purpose**: This application is designed as a proof-of-concept for demonstrating facial recognition gate technology to potential clients and stakeholders.
