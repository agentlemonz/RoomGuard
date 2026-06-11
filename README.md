RoomGuard

RoomGuard is a lightweight Python-based security monitoring application that uses a webcam to detect motion, record video clips, capture screenshots, and send real-time alerts via Discord.

It is designed as a personal room monitoring tool that runs on a standard desktop setup and provides simple, automated surveillance without requiring dedicated security hardware.

Features
Live webcam preview with GUI interface (Tkinter)
Motion detection using OpenCV frame differencing
Automatic video recording on detected movement
Screenshot capture when motion occurs
Auto-stop recording after inactivity
Discord webhook alerts with image attachments
Event logging system (GUI + file logs)
Fast camera initialization using DirectShow backend (Windows)
Use Cases
Room or home entry monitoring
Detecting unexpected access to a private space
Simple DIY security setup using a USB webcam
Learning project for computer vision and GUI development in Python
Tech Stack
Python
OpenCV
Tkinter
Pillow
Requests
Notes

This project is intended for personal and educational use. It is not a replacement for professional security systems.
