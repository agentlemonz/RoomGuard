import cv2
import tkinter as tk
from tkinter import scrolledtext
from PIL import Image, ImageTk
import threading
import time
import os
from datetime import datetime
import requests


class RoomGuard:

    def __init__(self, root):

        self.root = root
        self.root.title("RoomGuard")
        self.root.geometry("900x700")

        # ---------------- CONFIG ----------------
        self.webhook_url = "https://discord.com/api/webhooks/1514590599108493312/UzaPY4cjOpIiApeXLS139D-mNeBMjbJSURdwdX-Hkb-W4qw5OuHHeKubc8cHekHYXPfu"

        # ---------------- FOLDERS ----------------
        os.makedirs("recordings", exist_ok=True)
        os.makedirs("screenshots", exist_ok=True)
        os.makedirs("logs", exist_ok=True)

        # ---------------- CAMERA (FIXED FAST START) ----------------
        self.camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        # ---------------- STATE ----------------
        self.monitoring = False
        self.previous_frame = None
        self.recording = False
        self.video_writer = None
        self.last_motion_time = 0

        # ---------------- UI STATUS ----------------
        self.status_var = tk.StringVar()
        self.status_var.set("Status: Idle")

        tk.Label(
            root,
            textvariable=self.status_var,
            font=("Arial", 12)
        ).pack(pady=5)

        # ---------------- VIDEO FEED ----------------
        self.video_label = tk.Label(root)
        self.video_label.pack()

        # ---------------- BUTTONS ----------------
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        tk.Button(
            btn_frame,
            text="Start Monitoring",
            command=self.start_monitoring
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="Stop Monitoring",
            command=self.stop_monitoring
        ).pack(side=tk.LEFT, padx=5)

        # ---------------- LOGS ----------------
        self.log_box = scrolledtext.ScrolledText(root, height=10)
        self.log_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Start GUI loop
        self.update_video()

    # ---------------- LOGGING ----------------
    def log(self, msg):

        ts = time.strftime("%H:%M:%S")

        self.log_box.insert(tk.END, f"[{ts}] {msg}\n")
        self.log_box.see(tk.END)

        with open("logs/events.txt", "a") as f:
            f.write(f"{datetime.now()} - {msg}\n")

    # ---------------- DISCORD ----------------
    def send_discord_alert(self, image_path):

        if not self.webhook_url or "PASTE" in self.webhook_url:
            return

        try:
            with open(image_path, "rb") as f:

                files = {
                    "file": (image_path, f)
                }

                data = {
                    "content": "🚨 Motion detected in RoomGuard"
                }

                r = requests.post(
                    self.webhook_url,
                    data=data,
                    files=files
                )

                if r.status_code == 204:
                    self.log("Discord alert sent")
                else:
                    self.log(f"Discord error: {r.status_code}")

        except Exception as e:
            self.log(f"Discord failed: {e}")

    # ---------------- SCREENSHOT ----------------
    def save_screenshot(self, frame):

        filename = datetime.now().strftime(
            "screenshots/%Y-%m-%d_%H-%M-%S.jpg"
        )

        cv2.imwrite(filename, frame)

        self.log(f"Screenshot saved: {filename}")

        return filename

    # ---------------- RECORDING ----------------
    def start_recording(self, frame):

        filename = datetime.now().strftime(
            "recordings/%Y-%m-%d_%H-%M-%S.mp4"
        )

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")

        self.video_writer = cv2.VideoWriter(
            filename,
            fourcc,
            20.0,
            (frame.shape[1], frame.shape[0])
        )

        self.recording = True

        self.log(f"Recording started: {filename}")

    def stop_recording(self):

        if self.video_writer:
            self.video_writer.release()

        self.video_writer = None
        self.recording = False

        self.log("Recording stopped")

    # ---------------- CONTROL ----------------
    def start_monitoring(self):

        if self.monitoring:
            return

        self.monitoring = True
        self.status_var.set("Status: Monitoring")

        threading.Thread(
            target=self.motion_loop,
            daemon=True
        ).start()

        self.log("Monitoring started")

    def stop_monitoring(self):

        self.monitoring = False
        self.status_var.set("Status: Idle")

        if self.recording:
            self.stop_recording()

        self.log("Monitoring stopped")

    # ---------------- MOTION LOOP ----------------
    def motion_loop(self):

        while self.monitoring:

            ret, frame = self.camera.read()
            if not ret:
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)

            if self.previous_frame is None:
                self.previous_frame = gray
                continue

            diff = cv2.absdiff(self.previous_frame, gray)
            thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=3)

            contours, _ = cv2.findContours(
                thresh,
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE
            )

            motion = False

            for c in contours:
                if cv2.contourArea(c) < 3000:
                    continue
                motion = True
                break

            if motion:

                self.last_motion_time = time.time()

                self.log("Motion detected")

                ret2, frame2 = self.camera.read()

                if ret2:

                    img_path = self.save_screenshot(frame2)

                    self.send_discord_alert(img_path)

                    if not self.recording:
                        self.start_recording(frame2)

            # Write video
            if self.recording and ret:
                self.video_writer.write(frame)

            # Auto stop recording
            if self.recording:
                if time.time() - self.last_motion_time > 10:
                    self.stop_recording()

            self.previous_frame = gray
            time.sleep(0.1)

    # ---------------- VIDEO FEED ----------------
    def update_video(self):

        ret, frame = self.camera.read()

        if ret:

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            img = Image.fromarray(rgb)
            img = img.resize((800, 450))

            imgtk = ImageTk.PhotoImage(image=img)

            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        self.root.after(30, self.update_video)

    # ---------------- CLEANUP ----------------
    def cleanup(self):

        self.monitoring = False

        if self.video_writer:
            self.video_writer.release()

        if self.camera.isOpened():
            self.camera.release()

        self.root.destroy()


# ---------------- RUN ----------------
root = tk.Tk()
app = RoomGuard(root)

root.protocol("WM_DELETE_WINDOW", app.cleanup)
root.mainloop()
