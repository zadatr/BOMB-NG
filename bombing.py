import os
import sys
from tkinter import *
import tkinter.messagebox as msg
import pygame
import time
import threading
import cv2
from PIL import Image, ImageTk
import random

# ---- Ses %100 ayarlama (sadece Windows) ----
try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from comtypes import CLSCTX_ALL
    from ctypes import cast, POINTER

    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volume.SetMasterVolumeLevelScalar(1.0, None)
except Exception:
    print("Ses seviyesi ayarlanamadı (muhtemelen Windows dışı sistem).")

# ---- Tkinter pencere ayarları ----
root = Tk()
root.title("AÇMA")
root.geometry("1920x1080")
root.configure(bg="black")

# Pencere kapatma engelleme
def kapatma_engelle():
    pass
root.protocol("WM_DELETE_WINDOW", kapatma_engelle)
root.bind("<Alt-F4>", lambda e: "break")

text1 = Label(root, text="Devam etmek istediğine emin misin?",
              font=("Arial", 20, "bold"), fg="white", bg="black")
text1.pack(side='top', pady=40)


# ---- Çoklu uyarı popup fonksiyonu ----
def show_many_warnings(root,
                       count=100,
                       popup_width=300,
                       popup_height=90,
                       duration_ms=1200,
                       interval_ms=30,
                       title="UYARI",
                       text="KAPATAMAZSIN"):
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()

    def create_popup(i):
        win = Toplevel(root)
        win.overrideredirect(True)
        win.attributes("-topmost", True)

        x = random.randint(0, max(0, sw - popup_width))
        y = random.randint(0, max(0, sh - popup_height))
        win.geometry(f"{popup_width}x{popup_height}+{x}+{y}")

        frame = Frame(win, bg="#220000", bd=3, relief="raised")
        frame.pack(fill="both", expand=True)
        Label(frame, text=title, fg="white", bg="#220000",
              font=("Helvetica", 12, "bold")).pack(side="top", fill="x", pady=(6, 0))
        Label(frame, text=text, fg="yellow", bg="#220000",
              font=("Helvetica", 12, "bold")).pack(side="top", fill="both", expand=True, pady=(0, 6))

        # otomatik kapat
        win.after(duration_ms, lambda w=win: (w.destroy() if w.winfo_exists() else None))

    for i in range(count):
        root.after(i * interval_ms, lambda i=i: create_popup(i))


# ---- Video oynatma fonksiyonu ----
def video_oynat(duration_seconds=60):
    video_path = "Flash WarningFollow me now video every day..mp4"
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Video açılamadı:", video_path)
        return

    etiket = Label(root, bg="black")
    etiket.pack(fill="both", expand=True)

    baslangic = time.time()
    fps = cap.get(cv2.CAP_PROP_FPS) or 30

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (root.winfo_width(), root.winfo_height()))
        img = ImageTk.PhotoImage(Image.fromarray(frame))

        etiket.imgtk = img
        etiket.configure(image=img)

        try:
            root.update_idletasks()
            root.update()
        except Exception:
            break

        if time.time() - baslangic > duration_seconds:
            break

        time.sleep(max(0, 1.0 / (fps if fps > 0 else 30)))

    cap.release()
    try:
        etiket.destroy()
    except Exception:
        pass


# ---- Siren + Video + Uyarılar ----
def siren_cal():
    # Uyarılar (video ile eşzamanlı)
    root.after(0, lambda: show_many_warnings(root,
                                             count=300,
                                             popup_width=300,
                                             popup_height=90,
                                             duration_ms=1200,
                                             interval_ms=30,
                                             title="KAPATAMAZSIN",
                                             text="UYARI!"))

    # Siren sesi
    try:
        pygame.mixer.init()
        pygame.mixer.music.load("Ahlayan Karı Siren Sesi.mp3")
        pygame.mixer.music.set_volume(1.0)
        pygame.mixer.music.play(-1)
    except Exception as e:
        print("Ses oynatılırken hata:", e)

    # Video oynat
    video_oynat(duration_seconds=60)

    # Müzik durdur
    try:
        pygame.mixer.music.stop()
    except Exception:
        pass


# ---- Buton işlemi ----
def on_button():
    for i in range(3):
        msg.showwarning('Uyarı', 'Sirenler 5 saniye içinde çalışacak!')
        msg.showinfo('DİKKAT!', 'EMİN MİSİN?')

    threading.Thread(target=siren_cal, daemon=True).start()


# ---- Buton ----
btn = Button(root, text='Devam Et!', fg='white', bg='red',
             font=("Arial", 16, "bold"), command=on_button)
btn.pack(pady=10)

root.mainloop()
