RoomGuard:

RoomGuard is a lightweight Python-based security monitoring application that uses a webcam to detect motion, record video clips, capture screenshots, and send real-time alerts via Discord.

It is designed as a personal room monitoring tool that runs on a standard desktop setup and provides simple, automated surveillance without requiring dedicated security hardware.

Install:

1. On a discord server you have permissions for (I would suggest creating a private server) create a new webhook Server Settings > Integrations > Webhooks > New Webhook. Give it a name and select a channel. In my case I have created an #alerts channel
2. Select "Copy Webhook URL" in the same menu and paste in self.webhook_url = "URL HERE" under the #--Config banner
3. Run RoomGuard.py
4. Press start monitoring
5. Two folders will be created in the same directory as RoomGuard.py Screenshots and Recordings
6. Photos and videos will be stored in there respective folders. Photos will also be posted to discord via the webhook

Features:
Live webcam preview with GUI interface (Tkinter),
Motion detection using OpenCV frame differencing,
Automatic video recording on detected movement,
Screenshot capture when motion occurs,
Auto-stop recording after inactivity,
Discord webhook alerts with image attachments,
Event logging system (GUI + file logs),
Fast camera initialization using DirectShow backend (Windows),
Use Cases:
Room or home entry monitoring,
Detecting unexpected access to a private space,
Simple DIY security setup using a USB webcam,
Learning project for computer vision and GUI development in Python,
Tech Stack:
Python,
OpenCV,
Tkinter,
Pillow,
Requests,
Notes:

This project is intended for personal and educational use. It is not a replacement for professional security systems.
