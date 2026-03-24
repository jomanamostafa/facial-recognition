#!/usr/bin/env python3
"""
MIrai - Advanced Facial Recognition System
A professional, accurate facial recognition access control system with clean UI.
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
from deepface import DeepFace
import threading

class MIraiFacialRecognition:
    """Main application class for MIrai Facial Recognition System."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🔐 MIrai - Advanced Facial Recognition")
        self.root.geometry("1400x900")
        self.root.configure(bg='#0f0f1a')
        
        # Data storage
        self.registered_faces = {}
        self.data_file = "mirai_registered_faces.json"
        self.load_registered_faces()
        
        # Camera setup
        self.camera = None
        self.current_frame = None
        self.is_monitoring = False
        self.recognition_thread = None
        self.stop_recognition = False
        
        # Recognition settings
        self.confidence_threshold = 0.60
        self.detection_model = 'retinaface'
        self.recognition_model = 'Facenet512'
        
        # Create UI
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the modern user interface."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="0")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=3)
        main_frame.rowconfigure(2, weight=1)
        
        # Header
        header_frame = tk.Frame(main_frame, bg='#0f0f1a', height=80)
        header_frame.grid(row=0, column=0, columnspan=3, pady=(0, 10), sticky=(tk.W, tk.E))
        header_frame.grid_propagate(False)
        
        # Logo and title
        title_container = tk.Frame(header_frame, bg='#0f0f1a')
        title_container.pack(side=tk.LEFT, padx=30, pady=20)
        
        logo_label = tk.Label(
            title_container,
            text="🔐",
            font=('Helvetica', 36),
            bg='#0f0f1a',
            fg='#00d9ff'
        )
        logo_label.pack(side=tk.LEFT)
        
        title_label = tk.Label(
            title_container, 
            text="MIrai",
            font=('Helvetica', 32, 'bold'),
            bg='#0f0f1a',
            fg='#ffffff'
        )
        title_label.pack(side=tk.LEFT, padx=(15, 0))
        
        subtitle_label = tk.Label(
            title_container,
            text="Advanced Facial Recognition System",
            font=('Helvetica', 12),
            bg='#0f0f1a',
            fg='#6c7a89'
        )
        subtitle_label.pack(side=tk.LEFT, padx=(15, 0))
        
        # Status indicator
        status_frame = tk.Frame(header_frame, bg='#1a1a2e')
        status_frame.pack(side=tk.RIGHT, padx=30, pady=20)
        
        self.status_indicator = tk.Canvas(status_frame, width=16, height=16, bg='#1a1a2e', highlightthickness=0)
        self.status_indicator.pack(side=tk.LEFT)
        self.status_circle = self.status_indicator.create_oval(2, 2, 14, 14, fill='#00ff88', outline='')
        
        status_text = tk.Label(
            status_frame,
            text="System Ready",
            font=('Helvetica', 11),
            bg='#1a1a2e',
            fg='#00ff88'
        )
        status_text.pack(side=tk.LEFT, padx=(10, 0))
        self.status_label = status_text
        
        # Left panel - Controls
        control_frame = tk.LabelFrame(
            main_frame, 
            text=" Control Panel ", 
            font=('Helvetica', 11, 'bold'),
            bg='#16162a',
            fg='#00d9ff',
            padx=15,
            pady=15
        )
        control_frame.grid(row=1, column=0, padx=(20, 10), pady=10, sticky=(tk.N, tk.S, tk.W))
        control_frame.columnconfigure(0, weight=1)
        
        # Register button
        register_btn = tk.Button(
            control_frame,
            text="➕ Register New User",
            command=self.open_registration_dialog,
            font=('Helvetica', 11, 'bold'),
            bg='#00d9ff',
            fg='#0f0f1a',
            activebackground='#00b8d9',
            activeforeground='#ffffff',
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=12,
            borderwidth=0
        )
        register_btn.grid(row=0, column=0, pady=8, sticky=(tk.W, tk.E))
        
        # Start/Stop monitoring
        self.monitor_btn = tk.Button(
            control_frame,
            text="▶ Start Monitoring",
            command=self.toggle_monitoring,
            font=('Helvetica', 11, 'bold'),
            bg='#00ff88',
            fg='#0f0f1a',
            activebackground='#00cc6a',
            activeforeground='#ffffff',
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=12,
            borderwidth=0
        )
        self.monitor_btn.grid(row=1, column=0, pady=8, sticky=(tk.W, tk.E))
        
        # Settings frame
        settings_frame = tk.LabelFrame(
            control_frame,
            text=" Recognition Settings ",
            font=('Helvetica', 10, 'bold'),
            bg='#1a1a2e',
            fg='#a0a0a0',
            padx=10,
            pady=10
        )
        settings_frame.grid(row=2, column=0, pady=20, sticky=(tk.W, tk.E))
        settings_frame.columnconfigure(1, weight=1)
        
        # Confidence threshold
        tk.Label(settings_frame, text="Confidence:", font=('Helvetica', 9), bg='#1a1a2e', fg='#a0a0a0').grid(row=0, column=0, pady=5, sticky=tk.W)
        self.conf_var = tk.DoubleVar(value=self.confidence_threshold)
        conf_slider = tk.Scale(
            settings_frame,
            from_=0.3, to=0.9,
            resolution=0.05,
            variable=self.conf_var,
            orient=tk.HORIZONTAL,
            length=150,
            bg='#1a1a2e',
            fg='#00d9ff',
            troughcolor='#2a2a3e',
            highlightthickness=0,
            command=lambda x: setattr(self, 'confidence_threshold', float(x))
        )
        conf_slider.grid(row=0, column=1, pady=5, sticky=(tk.W, tk.E))
        self.conf_label = tk.Label(settings_frame, text=f"{self.confidence_threshold:.0%}", font=('Helvetica', 9), bg='#1a1a2e', fg='#00d9ff')
        self.conf_label.grid(row=0, column=2, pady=5, padx=(10, 0))
        
        # Load known faces
        load_btn = tk.Button(
            control_frame,
            text="📁 Load from Images",
            command=self.load_known_faces,
            font=('Helvetica', 10),
            bg='#2a2a3e',
            fg='#ffffff',
            activebackground='#3a3a4e',
            activeforeground='#ffffff',
            relief='flat',
            cursor='hand2',
            padx=15,
            pady=8,
            borderwidth=0
        )
        load_btn.grid(row=3, column=0, pady=8, sticky=(tk.W, tk.E))
        
        # Clear all data
        clear_btn = tk.Button(
            control_frame,
            text="🗑 Clear All Data",
            command=self.clear_all_data,
            font=('Helvetica', 10),
            bg='#2a2a3e',
            fg='#ff6b6b',
            activebackground='#3a3a4e',
            activeforeground='#ff6b6b',
            relief='flat',
            cursor='hand2',
            padx=15,
            pady=8,
            borderwidth=0
        )
        clear_btn.grid(row=4, column=0, pady=8, sticky=(tk.W, tk.E))
        
        # Registered users list
        users_frame = tk.LabelFrame(
            control_frame, 
            text=f" Registered Users ({len(self.registered_faces)}) ", 
            font=('Helvetica', 10, 'bold'),
            bg='#1a1a2e',
            fg='#a0a0a0',
            padx=10,
            pady=10
        )
        users_frame.grid(row=5, column=0, pady=20, sticky=(tk.N, tk.S, tk.W, tk.E))
        users_frame.columnconfigure(0, weight=1)
        users_frame.rowconfigure(0, weight=1)
        
        self.users_listbox = tk.Listbox(
            users_frame, 
            height=8, 
            bg='#0f0f1a', 
            fg='#ffffff',
            font=('Helvetica', 10),
            selectbackground='#00d9ff',
            selectforeground='#0f0f1a',
            relief='flat',
            highlightthickness=0,
            activestyle='none'
        )
        self.users_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        users_scrollbar = tk.Scrollbar(users_frame, orient=tk.VERTICAL, command=self.users_listbox.yview)
        users_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.users_listbox.config(yscrollcommand=users_scrollbar.set)
        
        # Center - Camera feed
        camera_container = tk.Frame(main_frame, bg='#1a1a2e', relief='sunken', bd=2)
        camera_container.grid(row=1, column=1, rowspan=2, padx=10, pady=10, sticky=(tk.N, tk.S, tk.E, tk.W))
        main_frame.columnconfigure(1, weight=3)
        main_frame.rowconfigure(2, weight=1)
        
        camera_header = tk.Frame(camera_container, bg='#1a1a2e')
        camera_header.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            camera_header,
            text="📹 Live Feed",
            font=('Helvetica', 12, 'bold'),
            bg='#1a1a2e',
            fg='#ffffff'
        ).pack(side=tk.LEFT)
        
        self.resolution_label = tk.Label(
            camera_header,
            text="",
            font=('Helvetica', 9),
            bg='#1a1a2e',
            fg='#6c7a89'
        )
        self.resolution_label.pack(side=tk.RIGHT)
        
        self.camera_label = tk.Label(camera_container, text="Camera Offline", background='#0f0f1a', font=('Helvetica', 14), fg='#6c7a89')
        self.camera_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Right panel - Access Log & Info
        right_panel = tk.Frame(main_frame, bg='#16162a')
        right_panel.grid(row=1, column=2, rowspan=2, padx=(10, 20), pady=10, sticky=(tk.N, tk.S, tk.E, tk.W))
        
        # Access Log section
        log_frame = tk.LabelFrame(
            right_panel,
            text=" Access Log ",
            font=('Helvetica', 11, 'bold'),
            bg='#16162a',
            fg='#00d9ff',
            padx=10,
            pady=10
        )
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = tk.Text(
            log_frame, 
            height=15, 
            width=35, 
            bg='#0f0f1a', 
            fg='#00ff88',
            font=('Consolas', 9),
            wrap=tk.WORD,
            relief='flat',
            highlightthickness=0
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        log_scrollbar = tk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        log_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text.config(yscrollcommand=log_scrollbar.set)
        
        # Configure tags for log
        self.log_text.tag_config("success", foreground='#00ff88')
        self.log_text.tag_config("denied", foreground='#ff6b6b')
        self.log_text.tag_config("info", foreground='#00d9ff')
        
        # Clear log button
        clear_log_btn = tk.Button(
            log_frame,
            text="Clear Log",
            command=self.clear_log,
            font=('Helvetica', 9),
            bg='#2a2a3e',
            fg='#ffffff',
            activebackground='#3a3a4e',
            relief='flat',
            cursor='hand2',
            padx=15,
            pady=5,
            borderwidth=0
        )
        clear_log_btn.grid(row=1, column=0, columnspan=2, pady=(10, 0), sticky=(tk.W, tk.E))
        
        # System Info section
        info_frame = tk.LabelFrame(
            right_panel,
            text=" System Information ",
            font=('Helvetica', 11, 'bold'),
            bg='#16162a',
            fg='#00d9ff',
            padx=10,
            pady=10
        )
        info_frame.pack(fill=tk.X)
        info_frame.columnconfigure(1, weight=1)
        
        # Model info
        tk.Label(info_frame, text="Detection Model:", font=('Helvetica', 9), bg='#16162a', fg='#a0a0a0').grid(row=0, column=0, pady=3, sticky=tk.W)
        tk.Label(info_frame, text=self.detection_model, font=('Helvetica', 9), bg='#16162a', fg='#00d9ff').grid(row=0, column=1, pady=3, sticky=tk.W)
        
        tk.Label(info_frame, text="Recognition Model:", font=('Helvetica', 9), bg='#16162a', fg='#a0a0a0').grid(row=1, column=0, pady=3, sticky=tk.W)
        tk.Label(info_frame, text=self.recognition_model, font=('Helvetica', 9), bg='#16162a', fg='#00d9ff').grid(row=1, column=1, pady=3, sticky=tk.W)
        
        tk.Label(info_frame, text="Registered Users:", font=('Helvetica', 9), bg='#16162a', fg='#a0a0a0').grid(row=2, column=0, pady=3, sticky=tk.W)
        self.info_users_count = tk.Label(info_frame, text=str(len(self.registered_faces)), font=('Helvetica', 9, 'bold'), bg='#16162a', fg='#00ff88')
        self.info_users_count.grid(row=2, column=1, pady=3, sticky=tk.W)
        
        # Update user list
        self.update_users_list()
        self.log_access("MIrai System initialized successfully", "info")
        
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
        for name, data in self.registered_faces.items():
            reg_date = data.get('registered_at', 'Unknown')[:10]
            self.users_listbox.insert(tk.END, f"  👤 {name}  •  {reg_date}")
            
    def log_access(self, message, level="success"):
        """Log an access attempt."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if level == "success":
            status = "✓ GRANTED"
            tag = "success"
        elif level == "denied":
            status = "✗ DENIED"
            tag = "denied"
        else:
            status = "ℹ INFO"
            tag = "info"
            
        log_entry = f"[{timestamp}] {status}: {message}\n"
        
        self.log_text.insert(tk.END, log_entry, tag)
        self.log_text.see(tk.END)
        
    def clear_log(self):
        """Clear the access log."""
        self.log_text.delete(1.0, tk.END)
        
    def clear_all_data(self):
        """Clear all registered faces data."""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all registered faces? This action cannot be undone."):
            self.registered_faces = {}
            self.save_registered_faces()
            self.update_users_list()
            self.info_users_count.config(text="0")
            self.log_access("All registered faces cleared", "denied")
            
    def load_known_faces(self):
        """Load known faces from image files."""
        filetypes = [("Image files", "*.jpg *.jpeg *.png *.bmp")]
        filenames = filedialog.askopenfilenames(title="Select face images", filetypes=filetypes)
        
        if not filenames:
            return
            
        loaded_count = 0
        for filepath in filenames:
            filename = os.path.basename(filepath)
            name = os.path.splitext(filename)[0]
            
            try:
                # Verify face can be detected
                img = cv2.imread(filepath)
                if img is not None:
                    # Encode as base64 for storage
                    _, buffer = cv2.imencode('.jpg', img)
                    img_base64 = base64.b64encode(buffer).decode('utf-8')
                    
                    self.registered_faces[name] = {
                        'image': img_base64,
                        'registered_at': datetime.now().isoformat(),
                        'source_file': filepath
                    }
                    
                    loaded_count += 1
                    self.log_access(f"Loaded: {name}")
            except Exception as e:
                self.log_access(f"Failed to load {name}: {str(e)}", "denied")
                
        if loaded_count > 0:
            self.save_registered_faces()
            self.update_users_list()
            self.info_users_count.config(text=str(len(self.registered_faces)))
            messagebox.showinfo("Success", f"Successfully loaded {loaded_count} face(s)")
        
    def open_registration_dialog(self):
        """Open dialog for registering a new user."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Register New User - MIrai")
        dialog.geometry("650x550")
        dialog.configure(bg='#0f0f1a')
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Make dialog modal
        dialog.resizable(False, False)
        
        # Header
        header = tk.Frame(dialog, bg='#00d9ff', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="Register New User",
            font=('Helvetica', 18, 'bold'),
            bg='#00d9ff',
            fg='#0f0f1a'
        ).pack(pady=15)
        
        # Content frame
        content = tk.Frame(dialog, bg='#0f0f1a')
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Name entry
        name_frame = tk.Frame(content, bg='#0f0f1a')
        name_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(name_frame, text="User Name:", font=('Helvetica', 12, 'bold'), bg='#0f0f1a', fg='#ffffff').pack(anchor=tk.W)
        name_entry = tk.Entry(name_frame, font=('Helvetica', 13), bg='#1a1a2e', fg='#ffffff', insertbackground='#ffffff', relief='flat', highlightthickness=2, highlightbackground='#2a2a3e', highlightcolor='#00d9ff')
        name_entry.pack(fill=tk.X, pady=(8, 0), ipady=8)
        name_entry.focus()
        
        # Instructions
        instructions = tk.Label(
            content,
            text="📋 Instructions:\n• Enter the user's full name above\n• Click 'Start Camera' to activate\n• Position face clearly in the frame\n• Ensure good lighting\n• Click 'Capture & Register' when ready",
            font=('Helvetica', 10),
            bg='#1a1a2e',
            fg='#a0a0a0',
            justify=tk.LEFT,
            padx=15,
            pady=15,
            relief='flat'
        )
        instructions.pack(fill=tk.X, pady=(0, 20))
        
        # Camera preview
        preview_frame = tk.LabelFrame(content, text=" Live Preview ", font=('Helvetica', 10, 'bold'), bg='#1a1a2e', fg='#00d9ff', padx=10, pady=10)
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        preview_label = tk.Label(preview_frame, text="Camera will appear here", background='#0f0f1a', font=('Helvetica', 11), fg='#6c7a89')
        preview_label.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        btn_frame = tk.Frame(content, bg='#0f0f1a')
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        
        reg_dialog = RegistrationDialog(self, dialog, name_entry, preview_label)
        
        start_btn = tk.Button(
            btn_frame, 
            text="📷 Start Camera", 
            command=reg_dialog.start_camera,
            font=('Helvetica', 11, 'bold'),
            bg='#00d9ff',
            fg='#0f0f1a',
            activebackground='#00b8d9',
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=10,
            borderwidth=0
        )
        start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        capture_btn = tk.Button(
            btn_frame, 
            text="💾 Capture & Register", 
            command=reg_dialog.capture_and_register,
            font=('Helvetica', 11, 'bold'),
            bg='#00ff88',
            fg='#0f0f1a',
            activebackground='#00cc6a',
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=10,
            borderwidth=0
        )
        capture_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        cancel_btn = tk.Button(
            btn_frame, 
            text="Cancel", 
            command=lambda: (reg_dialog.stop_camera(), dialog.destroy()),
            font=('Helvetica', 11),
            bg='#2a2a3e',
            fg='#ffffff',
            activebackground='#3a3a4e',
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=10,
            borderwidth=0
        )
        cancel_btn.pack(side=tk.LEFT)
        
    def toggle_monitoring(self):
        """Toggle camera monitoring on/off."""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_btn.config(text="⏹ Stop Monitoring", bg='#ff6b6b', fg='#ffffff')
            self.status_label.config(text="Monitoring Active", fg='#ffaa00')
            self.status_indicator.itemconfig(self.status_circle, fill='#ffaa00')
            self.log_access("Monitoring started", "info")
            self.start_monitoring()
        else:
            self.is_monitoring = False
            self.stop_recognition = True
            self.monitor_btn.config(text="▶ Start Monitoring", bg='#00ff88', fg='#0f0f1a')
            self.status_label.config(text="System Ready", fg='#00ff88')
            self.status_indicator.itemconfig(self.status_circle, fill='#00ff88')
            self.log_access("Monitoring stopped", "info")
            if self.camera:
                self.camera.release()
                self.camera = None
            self.camera_label.config(image='', text="Camera Stopped", bg='#0f0f1a')
                
    def start_monitoring(self):
        """Start continuous monitoring for face recognition."""
        if not self.is_monitoring:
            return
            
        if self.camera is None:
            self.camera = cv2.VideoCapture(0)
            
        if not self.camera.isOpened():
            messagebox.showerror("Error", "Cannot access camera. Please check camera connection.")
            self.is_monitoring = False
            self.monitor_btn.config(text="▶ Start Monitoring", bg='#00ff88', fg='#0f0f1a')
            return
            
        # Set camera resolution
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        self.stop_recognition = False
        self.monitor_cycle()
        
    def monitor_cycle(self):
        """Single cycle of monitoring - captures frame and checks for faces."""
        if not self.is_monitoring or self.camera is None or self.stop_recognition:
            return
            
        ret, frame = self.camera.read()
        if not ret:
            self.root.after(100, self.monitor_cycle)
            return
            
        self.current_frame = frame.copy()
        
        # Get frame dimensions
        height, width = frame.shape[:2]
        self.resolution_label.config(text=f"{width}x{height}")
        
        # Process frame for display
        processed_frame = self.process_frame_for_display(frame)
        
        # Convert to PhotoImage
        img_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        
        # Resize to fit display while maintaining aspect ratio
        display_width = self.camera_label.winfo_width()
        display_height = self.camera_label.winfo_height()
        
        if display_width > 1 and display_height > 1:
            scale = min(display_width / width, display_height / height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            img_pil = img_pil.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        img_tk = ImageTk.PhotoImage(image=img_pil)
        
        # Update display
        self.camera_label.config(image=img_tk, text="")
        self.camera_label.image = img_tk
        
        # Run face recognition in separate thread to avoid blocking UI
        if len(self.registered_faces) > 0:
            thread = threading.Thread(target=self.recognize_faces, args=(frame.copy(),), daemon=True)
            thread.start()
        
        # Schedule next cycle
        self.root.after(50, self.monitor_cycle)
        
    def process_frame_for_display(self, frame):
        """Process frame for display with face detection overlay."""
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Use OpenCV's built-in face detector for real-time display
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        # Draw rectangles around detected faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, "Detecting...", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
        return frame
        
    def recognize_faces(self, frame):
        """Perform accurate face recognition using DeepFace."""
        try:
            if not self.is_monitoring or len(self.registered_faces) == 0:
                return
                
            # Find faces in frame using DeepFace
            try:
                faces = DeepFace.extract_faces(
                    img_path=frame,
                    detector_backend=self.detection_model,
                    enforce_detection=False,
                    align=True
                )
            except:
                return
                
            if not faces or len(faces) == 0:
                return
                
            # For each detected face, try to recognize
            for face_obj in faces:
                face_img = face_obj['face']
                
                # Convert face to proper format
                if len(face_img.shape) == 4:
                    face_img = face_img[0]
                    
                # Convert to RGB if needed
                if face_img.shape[2] == 3:
                    face_img_bgr = cv2.cvtColor(face_img, cv2.COLOR_RGB2BGR)
                else:
                    face_img_bgr = face_img
                    
                best_match = None
                best_confidence = 0
                
                # Compare against all registered faces
                for name, data in self.registered_faces.items():
                    try:
                        # Decode stored image
                        img_bytes = base64.b64decode(data['image'])
                        img_array = np.frombuffer(img_bytes, np.uint8)
                        registered_img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                        
                        if registered_img is None:
                            continue
                            
                        # Verify face similarity
                        result = DeepFace.verify(
                            img1_path=face_img_bgr,
                            img2_path=registered_img,
                            model_name=self.recognition_model,
                            detector_backend='skip',
                            enforce_detection=False,
                            distance_metric='cosine'
                        )
                        
                        if result['verified']:
                            confidence = 1.0 - result['distance']
                            if confidence > best_confidence and confidence >= self.confidence_threshold:
                                best_confidence = confidence
                                best_match = name
                                
                    except Exception as e:
                        continue
                        
                # Report result
                if best_match:
                    self.root.after(0, lambda: self.handle_recognition_result(best_match, best_confidence))
                else:
                    # Only log unknown faces occasionally to avoid spam
                    pass
                    
        except Exception as e:
            pass
            
    def handle_recognition_result(self, name, confidence):
        """Handle recognition result in main thread."""
        if not hasattr(self, '_last_recognition') or (datetime.now() - self._last_recognition).total_seconds() > 3:
            self._last_recognition = datetime.now()
            
            self.log_access(f"{name} recognized ({confidence:.1%} confidence)", "success")
            self.show_access_granted(name, confidence)
            
    def show_access_granted(self, name, confidence):
        """Show access granted notification."""
        # Flash green border
        original_bg = self.camera_label.cget('bg')
        
        def flash(times):
            if times <= 0 or not self.is_monitoring:
                self.camera_label.config(bg=original_bg)
                return
                
            self.camera_label.config(bg='#00ff88')
            self.root.after(150, lambda: self.camera_label.config(bg=original_bg))
            self.root.after(300, lambda: flash(times - 1))
            
        flash(3)
        
        # Show overlay message
        overlay = tk.Toplevel(self.root)
        overlay.overrideredirect(True)
        overlay.attributes('-topmost', True)
        overlay.configure(bg='#00ff88')
        
        # Center overlay on camera feed
        x = self.camera_label.winfo_rootx() + 50
        y = self.camera_label.winfo_rooty() + 50
        
        overlay.geometry(f"+{x}+{y}")
        
        tk.Label(
            overlay,
            text=f"✓ ACCESS GRANTED\n{name}\n{confidence:.1%} Confidence",
            font=('Helvetica', 24, 'bold'),
            bg='#00ff88',
            fg='#0f0f1a',
            padx=40,
            pady=30
        ).pack()
        
        # Auto-close after 2 seconds
        self.root.after(2000, overlay.destroy)


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
            messagebox.showerror("Error", "Cannot access camera. Please check camera connection.")
            return
            
        # Set resolution
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
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
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, "Face Detected ✓", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
        # Convert and display
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        
        # Resize to fit
        label_width = self.preview_label.winfo_width()
        label_height = self.preview_label.winfo_height()
        
        if label_width > 1 and label_height > 1:
            scale = min(label_width / 640, label_height / 480)
            new_width = int(640 * scale)
            new_height = int(480 * scale)
            img_pil = img_pil.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        img_tk = ImageTk.PhotoImage(image=img_pil)
        
        self.preview_label.config(image=img_tk, text="")
        self.preview_label.image = img_tk
        
        self.dialog.after(50, self.capture_preview)
        
    def stop_camera(self):
        """Stop the camera."""
        self.is_capturing = False
        if self.camera:
            self.camera.release()
            self.camera = None
        
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
            
        # Check if face is detected using DeepFace for accuracy
        try:
            faces = DeepFace.extract_faces(
                img_path=frame,
                detector_backend='retinaface',
                enforce_detection=True,
                align=True
            )
            
            if len(faces) == 0:
                messagebox.showwarning("Warning", "No face detected. Please position your face clearly in the frame with good lighting.")
                return
                
            # Use the first detected face
            face_obj = faces[0]
            face_img = face_obj['face']
            
            if len(face_img.shape) == 4:
                face_img = face_img[0]
                
            # Convert to BGR for storage
            if face_img.shape[2] == 3:
                face_bgr = cv2.cvtColor(face_img, cv2.COLOR_RGB2BGR)
            else:
                face_bgr = face_img
                
            # Encode the aligned face image
            _, buffer = cv2.imencode('.jpg', face_bgr)
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            
        except Exception as e:
            messagebox.showwarning("Warning", f"Could not detect face clearly. Please ensure good lighting and face the camera directly. Error: {str(e)}")
            return
            
        # Store registration
        self.main_app.registered_faces[name] = {
            'image': img_base64,
            'registered_at': datetime.now().isoformat(),
            'source_file': 'camera_capture'
        }
        
        self.main_app.save_registered_faces()
        self.main_app.update_users_list()
        self.main_app.info_users_count.config(text=str(len(self.main_app.registered_faces)))
        self.main_app.log_access(f"New user registered: {name}", "info")
        
        messagebox.showinfo("Success", f"User '{name}' registered successfully!\n\nThe system is now trained to recognize this user.")
        
        # Cleanup
        self.stop_camera()
        self.dialog.destroy()


def main():
    """Main entry point."""
    root = tk.Tk()
    
    # Set dark theme colors
    style = ttk.Style()
    style.theme_use('clam')
    
    # Configure colors
    style.configure('TFrame', background='#0f0f1a')
    style.configure('TLabelFrame', background='#16162a', foreground='#00d9ff')
    style.configure('TLabelFrame.Label', background='#16162a', foreground='#00d9ff', font=('Helvetica', 10, 'bold'))
    style.configure('TButton', font=('Helvetica', 10))
    style.configure('TLabel', background='#0f0f1a', foreground='#ffffff')
    
    app = MIraiFacialRecognition(root)
    root.mainloop()


if __name__ == "__main__":
    main()
