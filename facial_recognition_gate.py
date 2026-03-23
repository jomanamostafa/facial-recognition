#!/usr/bin/env python3
"""
Facial Recognition Gate Demo Application
A professional demo for facial recognition access control systems.
"""

import cv2
import numpy as np
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import json
from datetime import datetime
import base64
from pathlib import Path

class FacialRecognitionGate:
    """Main application class for the Facial Recognition Gate Demo."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🔐 SecureGate - Facial Recognition Access Control")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a2e')
        
        # Data storage
        self.registered_faces = {}
        self.data_file = "registered_faces.json"
        self.load_registered_faces()
        
        # Camera setup
        self.camera = None
        self.current_frame = None
        self.is_monitoring = False
        
        # Create UI
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=3, pady=(0, 20), sticky=(tk.W, tk.E))
        
        title_label = ttk.Label(
            header_frame, 
            text="🔐 SecureGate - Facial Recognition Access Control",
            font=('Helvetica', 24, 'bold'),
            foreground='#00d9ff'
        )
        title_label.pack(side=tk.LEFT)
        
        status_label = ttk.Label(
            header_frame,
            text="● System Ready",
            font=('Helvetica', 14),
            foreground='#00ff88'
        )
        status_label.pack(side=tk.RIGHT)
        self.status_label = status_label
        
        # Left panel - Controls
        control_frame = ttk.LabelFrame(main_frame, text="Control Panel", padding="15")
        control_frame.grid(row=1, column=0, padx=(0, 10), pady=10, sticky=(tk.N, tk.S, tk.W))
        
        # Register button
        register_btn = ttk.Button(
            control_frame,
            text="👤 Register New User",
            command=self.open_registration_dialog,
            width=25
        )
        register_btn.pack(pady=10, fill=tk.X)
        
        # Start/Stop monitoring
        self.monitor_btn = ttk.Button(
            control_frame,
            text="▶ Start Monitoring",
            command=self.toggle_monitoring,
            width=25
        )
        self.monitor_btn.pack(pady=10, fill=tk.X)
        
        # Load known faces
        load_btn = ttk.Button(
            control_frame,
            text="📁 Load Known Faces",
            command=self.load_known_faces,
            width=25
        )
        load_btn.pack(pady=10, fill=tk.X)
        
        # Clear all data
        clear_btn = ttk.Button(
            control_frame,
            text="🗑 Clear All Data",
            command=self.clear_all_data,
            width=25
        )
        clear_btn.pack(pady=10, fill=tk.X)
        
        # Registered users list
        users_frame = ttk.LabelFrame(control_frame, text="Registered Users", padding="10")
        users_frame.pack(pady=20, fill=tk.BOTH, expand=True)
        
        self.users_listbox = tk.Listbox(users_frame, height=10, bg='#16213e', fg='#ffffff')
        self.users_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Center - Camera feed
        camera_frame = ttk.LabelFrame(main_frame, text="Live Camera Feed", padding="10")
        camera_frame.grid(row=1, column=1, padx=10, pady=10, sticky=(tk.N, tk.S, tk.E, tk.W))
        
        self.camera_label = ttk.Label(camera_frame, text="Camera Feed", background='#0f0f23')
        self.camera_label.pack(fill=tk.BOTH, expand=True)
        
        # Right panel - Access Log
        log_frame = ttk.LabelFrame(main_frame, text="Access Log", padding="10")
        log_frame.grid(row=1, column=2, padx=(10, 0), pady=10, sticky=(tk.N, tk.S, tk.E))
        
        # Log text area
        self.log_text = tk.Text(log_frame, height=20, width=30, bg='#16213e', fg='#00ff88', wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar for log
        scrollbar = ttk.Scrollbar(self.log_text, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # Clear log button
        clear_log_btn = ttk.Button(log_frame, text="Clear Log", command=self.clear_log)
        clear_log_btn.pack(pady=10)
        
        # Update user list
        self.update_users_list()
        
    def load_registered_faces(self):
        """Load registered faces from JSON file."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.registered_faces = json.load(f)
            except Exception as e:
                self.registered_faces = {}
                
    def save_registered_faces(self):
        """Save registered faces to JSON file."""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.registered_faces, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {str(e)}")
            
    def update_users_list(self):
        """Update the registered users listbox."""
        self.users_listbox.delete(0, tk.END)
        for name in self.registered_faces.keys():
            self.users_listbox.insert(tk.END, f"👤 {name}")
            
    def log_access(self, message, success=True):
        """Log an access attempt."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "✅ GRANTED" if success else "❌ DENIED"
        log_entry = f"[{timestamp}] {status}: {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        if success:
            self.log_text.tag_add("success", "end-2c", "end-1c")
            self.log_text.tag_config("success", foreground='#00ff88')
        else:
            self.log_text.tag_add("denied", "end-2c", "end-1c")
            self.log_text.tag_config("denied", foreground='#ff4444')
            
        self.log_text.see(tk.END)
        
    def clear_log(self):
        """Clear the access log."""
        self.log_text.delete(1.0, tk.END)
        
    def clear_all_data(self):
        """Clear all registered faces data."""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all registered faces?"):
            self.registered_faces = {}
            self.save_registered_faces()
            self.update_users_list()
            self.log_access("All registered faces cleared", success=False)
            
    def load_known_faces(self):
        """Load known faces from image files."""
        filetypes = [("Image files", "*.jpg *.jpeg *.png *.bmp")]
        filenames = filedialog.askopenfilenames(title="Select face images", filetypes=filetypes)
        
        for filepath in filenames:
            filename = os.path.basename(filepath)
            name = os.path.splitext(filename)[0]
            
            # Read and encode image
            img = cv2.imread(filepath)
            if img is not None:
                # Convert to RGB
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                
                # Encode as base64 for storage
                _, buffer = cv2.imencode('.jpg', img_rgb)
                img_base64 = base64.b64encode(buffer).decode('utf-8')
                
                self.registered_faces[name] = {
                    'image': img_base64,
                    'registered_at': datetime.now().isoformat(),
                    'source_file': filepath
                }
                
                self.log_access(f"Loaded face: {name}")
                
        self.save_registered_faces()
        self.update_users_list()
        
    def open_registration_dialog(self):
        """Open dialog for registering a new user."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Register New User")
        dialog.geometry("600x500")
        dialog.configure(bg='#1a1a2e')
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Name entry
        ttk.Label(dialog, text="User Name:", font=('Helvetica', 12)).pack(pady=10)
        name_entry = ttk.Entry(dialog, width=40, font=('Helvetica', 12))
        name_entry.pack(pady=5)
        name_entry.focus()
        
        # Instructions
        instructions = ttk.Label(
            dialog,
            text="Instructions:\n1. Enter the user's name\n2. Click 'Start Camera'\n3. Position face in the frame\n4. Click 'Capture & Register'",
            font=('Helvetica', 10),
            justify=tk.CENTER
        )
        instructions.pack(pady=20)
        
        # Camera preview
        preview_frame = ttk.LabelFrame(dialog, text="Face Preview", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        preview_label = ttk.Label(preview_frame, text="Camera preview will appear here", background='#0f0f23')
        preview_label.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=20)
        
        reg = RegistrationDialog(self, dialog, name_entry, preview_label)
        
        start_btn = ttk.Button(btn_frame, text="📷 Start Camera", command=reg.start_camera)
        start_btn.pack(side=tk.LEFT, padx=10)
        
        capture_btn = ttk.Button(btn_frame, text="💾 Capture & Register", command=reg.capture_and_register)
        capture_btn.pack(side=tk.LEFT, padx=10)
        
        cancel_btn = ttk.Button(btn_frame, text="❌ Cancel", command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=10)
        
    def toggle_monitoring(self):
        """Toggle camera monitoring on/off."""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_btn.config(text="⏹ Stop Monitoring")
            self.status_label.config(text="● Monitoring Active", foreground='#ffaa00')
            self.log_access("Monitoring started")
            self.start_monitoring()
        else:
            self.is_monitoring = False
            self.monitor_btn.config(text="▶ Start Monitoring")
            self.status_label.config(text="● System Ready", foreground='#00ff88')
            self.log_access("Monitoring stopped")
            if self.camera:
                self.camera.release()
                self.camera = None
                
    def start_monitoring(self):
        """Start continuous monitoring for face recognition."""
        if not self.is_monitoring:
            return
            
        if self.camera is None:
            self.camera = cv2.VideoCapture(0)
            
        if not self.camera.isOpened():
            messagebox.showerror("Error", "Cannot access camera. Please check camera connection.")
            self.is_monitoring = False
            self.monitor_btn.config(text="▶ Start Monitoring")
            return
            
        self.monitor_cycle()
        
    def monitor_cycle(self):
        """Single cycle of monitoring - captures frame and checks for faces."""
        if not self.is_monitoring or self.camera is None:
            return
            
        ret, frame = self.camera.read()
        if not ret:
            self.root.after(100, self.monitor_cycle)
            return
            
        # Process frame
        processed_frame = self.process_frame_for_display(frame)
        
        # Convert to PhotoImage
        img_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_tk = ImageTk.PhotoImage(image=img_pil)
        
        # Update display
        self.camera_label.config(image=img_tk, text="")
        self.camera_label.image = img_tk
        
        # Check for face recognition
        self.check_for_recognition(frame)
        
        # Schedule next cycle
        self.root.after(100, self.monitor_cycle)
        
    def process_frame_for_display(self, frame):
        """Process frame for display with face detection overlay."""
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Load cascade classifier
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        face_cascade = cv2.CascadeClassifier(cascade_path)
        
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        # Draw rectangles around detected faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, "Face Detected", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
        return frame
        
    def check_for_recognition(self, frame):
        """Check if any detected face matches registered users."""
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Load cascade classifier
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        face_cascade = cv2.CascadeClassifier(cascade_path)
        
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        if len(faces) > 0 and len(self.registered_faces) > 0:
            # For demo purposes, we'll simulate recognition
            # In production, you would use face_recognition library
            (x, y, w, h) = faces[0]  # Use first detected face
            
            # Simple similarity check based on face size and position
            # This is a demo - real implementation would use proper face encoding
            best_match = None
            best_score = 0
            
            for name, data in self.registered_faces.items():
                # Simulate matching (in real app, compare face encodings)
                score = np.random.uniform(0.7, 0.99)  # Demo: random score
                if score > best_score and score > 0.85:
                    best_score = score
                    best_match = name
                    
            if best_match:
                self.log_access(f"Access granted to {best_match} (confidence: {best_score:.2%})")
                self.show_access_granted(best_match)
            else:
                self.log_access("Unknown face detected - Access denied", success=False)
                self.show_access_denied()
                
    def show_access_granted(self, name):
        """Show access granted notification."""
        # Flash green border
        self.camera_label.config(background='#00ff88')
        self.root.after(500, lambda: self.camera_label.config(background='#0f0f23'))
        self.root.after(1000, lambda: self.camera_label.config(background='#00ff88'))
        self.root.after(1500, lambda: self.camera_label.config(background='#0f0f23'))
        
    def show_access_denied(self):
        """Show access denied notification."""
        # Flash red border
        self.camera_label.config(background='#ff4444')
        self.root.after(500, lambda: self.camera_label.config(background='#0f0f23'))
        self.root.after(1000, lambda: self.camera_label.config(background='#ff4444'))
        self.root.after(1500, lambda: self.camera_label.config(background='#0f0f23'))


class RegistrationDialog:
    """Handles the registration dialog functionality."""
    
    def __init__(self, main_app, dialog, name_entry, preview_label):
        self.main_app = main_app
        self.dialog = dialog
        self.name_entry = name_entry
        self.preview_label = preview_label
        self.camera = None
        self.is_capturing = False
        
    def start_camera(self):
        """Start camera for registration preview."""
        self.camera = cv2.VideoCapture(0)
        
        if not self.camera.isOpened():
            messagebox.showerror("Error", "Cannot access camera")
            return
            
        self.is_capturing = True
        self.capture_preview()
        
    def capture_preview(self):
        """Capture frames for preview during registration."""
        if not self.is_capturing or self.camera is None:
            return
            
        ret, frame = self.camera.read()
        if not ret:
            self.dialog.after(100, self.capture_preview)
            return
            
        # Add face detection overlay
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        face_cascade = cv2.CascadeClassifier(cascade_path)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, "Position face here", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
        # Convert and display
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_tk = ImageTk.PhotoImage(image=img_pil)
        
        self.preview_label.config(image=img_tk, text="")
        self.preview_label.image = img_tk
        
        self.dialog.after(100, self.capture_preview)
        
    def capture_and_register(self):
        """Capture current frame and register the user."""
        name = self.name_entry.get().strip()
        
        if not name:
            messagebox.showwarning("Warning", "Please enter a user name")
            return
            
        if self.camera is None or not self.camera.isOpened():
            messagebox.showwarning("Warning", "Please start the camera first")
            return
            
        ret, frame = self.camera.read()
        if not ret:
            messagebox.showerror("Error", "Failed to capture image")
            return
            
        # Check if face is detected
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        face_cascade = cv2.CascadeClassifier(cascade_path)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        if len(faces) == 0:
            messagebox.showwarning("Warning", "No face detected. Please position your face in the frame.")
            return
            
        # Encode image
        _, buffer = cv2.imencode('.jpg', frame)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # Store registration
        self.main_app.registered_faces[name] = {
            'image': img_base64,
            'registered_at': datetime.now().isoformat(),
            'source_file': 'camera_capture'
        }
        
        self.main_app.save_registered_faces()
        self.main_app.update_users_list()
        self.main_app.log_access(f"New user registered: {name}")
        
        messagebox.showinfo("Success", f"User '{name}' registered successfully!")
        
        # Cleanup
        self.is_capturing = False
        if self.camera:
            self.camera.release()
            self.camera = None
            
        self.dialog.destroy()


def main():
    """Main entry point."""
    root = tk.Tk()
    
    # Set dark theme
    style = ttk.Style()
    style.theme_use('clam')
    
    # Configure colors
    style.configure('TFrame', background='#1a1a2e')
    style.configure('TLabelFrame', background='#1a1a2e', foreground='#ffffff')
    style.configure('TLabelFrame.Label', background='#1a1a2e', foreground='#00d9ff', font=('Helvetica', 11, 'bold'))
    style.configure('TButton', font=('Helvetica', 10))
    style.configure('TLabel', background='#1a1a2e', foreground='#ffffff')
    
    app = FacialRecognitionGate(root)
    root.mainloop()


if __name__ == "__main__":
    main()
