import base64
import io
import threading
import os
from socket import socket, AF_INET, SOCK_STREAM
from customtkinter import *
from tkinter import filedialog
from PIL import Image

set_appearance_mode("dark")

class MainWindow(CTk):
    def __init__(self):
        super().__init__()

        self.geometry('1200x700')
        self.title("LogiTalk Chat")

        self.colors = {
            "bg": "#000000",
            "menu": "#0a0a0a",
            "menu_dark": "#050505",
            "accent": "#7c3aed",
            "accent_dark": "#5b21b6",
            "accent_light": "#a78bfa",
            "message_bg": "#111111",
            "entry_bg": "#0a0a0a",
            "text": "#e5e5e5",
            "text_dark": "#6b7280",
            "border": "#1f1f1f",
        }

        self.configure(fg_color=self.colors["bg"])

        self.menu_frame = CTkFrame(
            self,
            width=240,
            height=700,
            fg_color=self.colors["menu"],
            corner_radius=0
        )
        self.menu_frame.pack_propagate(False)
        self.menu_frame.place(x=0, y=0)

        self.title_label = CTkLabel(
            self.menu_frame,
            text="LogiTalk",
            text_color=self.colors["accent"],
            font=("Consolas", 22, "bold")
        )
        self.title_label.pack(pady=(35, 5))

        self.subtitle_label = CTkLabel(
            self.menu_frame,
            text="chat client",
            text_color=self.colors["text_dark"],
            font=("Consolas", 10)
        )
        self.subtitle_label.pack(pady=(0, 30))

        CTkFrame(
            self.menu_frame,
            height=1,
            fg_color=self.colors["accent"]
        ).pack(pady=(0, 20), padx=20, fill="x")

        self.name_section_label = CTkLabel(
            self.menu_frame,
            text="USER",
            text_color=self.colors["text_dark"],
            font=("Consolas", 10, "bold")
        )
        self.name_section_label.pack(pady=(10, 8))

        self.name_entry = CTkEntry(
            self.menu_frame,
            placeholder_text="nickname...",
            height=38,
            fg_color=self.colors["menu_dark"],
            border_color=self.colors["border"],
            text_color=self.colors["text"],
            corner_radius=4
        )
        self.name_entry.pack(pady=(0, 10), padx=20, fill="x")
        self.name_entry.insert(0, "user")
        self.username = "user"

        self.save_button = CTkButton(
            self.menu_frame,
            text="[ save ]",
            command=self.save_name,
            height=36,
            fg_color="transparent",
            hover_color=self.colors["accent_dark"],
            border_color=self.colors["accent"],
            border_width=1,
            corner_radius=4,
            font=("Consolas", 11)
        )
        self.save_button.pack(pady=(0, 20), padx=20, fill="x")

        CTkFrame(
            self.menu_frame,
            height=1,
            fg_color=self.colors["border"]
        ).pack(pady=(10, 10), padx=20, fill="x")

        self.status_label = CTkLabel(
            self.menu_frame,
            text="> connecting...",
            text_color="#f59e0b",
            font=("Consolas", 10)
        )
        self.status_label.pack(side="bottom", pady=20)

        self.version_label = CTkLabel(
            self.menu_frame,
            text="v2.0",
            text_color=self.colors["text_dark"],
            font=("Consolas", 9)
        )
        self.version_label.pack(side="bottom", pady=(0, 10))

        self.chat_field = CTkScrollableFrame(
            self,
            width=930,
            height=600,
            fg_color=self.colors["bg"],
            corner_radius=0
        )
        self.chat_field.place(x=250, y=15)

        self.bottom_frame = CTkFrame(
            self,
            width=930,
            height=60,
            fg_color=self.colors["menu"],
            corner_radius=0
        )
        self.bottom_frame.place(x=250, y=630)
        self.bottom_frame.pack_propagate(False)

        self.message_entry = CTkEntry(
            self.bottom_frame,
            placeholder_text='>_',
            height=38,
            fg_color=self.colors["menu_dark"],
            border_color=self.colors["border"],
            text_color=self.colors["text"],
            corner_radius=4,
            font=("Consolas", 12)
        )
        self.message_entry.pack(side="left", padx=(10, 5), pady=11, fill="x", expand=True)

        self.open_img_button = CTkButton(
            self.bottom_frame,
            text='[img]',
            width=55,
            height=38,
            command=self.open_image,
            fg_color="transparent",
            hover_color=self.colors["accent_dark"],
            border_color=self.colors["border"],
            border_width=1,
            corner_radius=4,
            font=("Consolas", 10)
        )
        self.open_img_button.pack(side="left", padx=5, pady=11)

        self.send_button = CTkButton(
            self.bottom_frame,
            text='[send]',
            width=65,
            height=38,
            command=self.send_message,
            fg_color=self.colors["accent"],
            hover_color=self.colors["accent_dark"],
            corner_radius=4,
            font=("Consolas", 10, "bold")
        )
        self.send_button.pack(side="left", padx=(5, 10), pady=11)

        self.message_entry.bind("<Return>", lambda e: self.send_message())

        self.add_system_message("LogiTalk initialized")
        self.add_system_message("set username to start chatting")

        self.after(100, self.connect_to_server)

    def connect_to_server(self):
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(('localhost', 8080))
            hello = f"TEXT@{self.username}@[SYSTEM] {self.username} joined\n"
            self.sock.send(hello.encode('utf-8'))
            threading.Thread(target=self.recv_message, daemon=True).start()
            self.status_label.configure(text="> online", text_color="#10b981")
            self.add_system_message(f"connected as {self.username}")
        except Exception as e:
            self.status_label.configure(text="> offline", text_color="#ef4444")
            self.add_system_message(f"connection failed: {e}")

    def add_system_message(self, message):
        message_frame = CTkFrame(self.chat_field, fg_color=self.colors["menu_dark"], corner_radius=4)
        message_frame.pack(pady=4, anchor='center', padx=20, fill="x")

        CTkLabel(
            message_frame,
            text=f"# {message}",
            wraplength=850,
            text_color=self.colors["accent_light"],
            justify='center',
            font=("Consolas", 10)
        ).pack(padx=15, pady=6)

    def save_name(self):
        new_name = self.name_entry.get().strip()
        if new_name and new_name != self.username:
            old_name = self.username
            self.username = new_name
            self.add_message(f"{old_name} -> {self.username}", is_system=True)
            try:
                name_change_msg = f"TEXT@{self.username}@[SYSTEM] {old_name} is now {self.username}\n"
                self.sock.send(name_change_msg.encode('utf-8'))
            except:
                pass

    def add_message(self, message, img=None, is_system=False):
        message_frame = CTkFrame(
            self.chat_field,
            fg_color=self.colors["message_bg"] if not is_system else self.colors["menu_dark"],
            corner_radius=4
        )
        message_frame.pack(pady=5, anchor='w' if not is_system else 'center', padx=15, fill="x")

        wrapleng_size = 850

        if not img:
            text_color = self.colors["text"] if not is_system else self.colors["text_dark"]
            prefix = "" if not is_system else "# "
            CTkLabel(
                message_frame,
                text=f"{prefix}{message}",
                wraplength=wrapleng_size,
                text_color=text_color,
                justify='left',
                font=("Consolas", 11)
            ).pack(padx=12, pady=8)
        else:
            CTkLabel(
                message_frame,
                text=message,
                wraplength=wrapleng_size,
                text_color=self.colors["text"],
                image=img,
                compound='top',
                justify='left',
                font=("Consolas", 11)
            ).pack(padx=12, pady=8)

        self.chat_field._parent_canvas.yview_moveto(1)

    def send_message(self):
        message = self.message_entry.get().strip()
        if message:
            self.add_message(f"{self.username}> {message}")
            data = f"TEXT@{self.username}@{message}\n"
            try:
                self.sock.sendall(data.encode())
            except:
                self.add_system_message("send failed (no connection)")
        self.message_entry.delete(0, END)

    def recv_message(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode('utf-8', errors='ignore')

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle_line(line.strip())

            except:
                break
        self.sock.close()
        self.status_label.configure(text="> offline", text_color="#ef4444")

    def handle_line(self, line):
        if not line:
            return
        parts = line.split("@", 3)
        msg_type = parts[0]

        if msg_type == "TEXT":
            if len(parts) >= 3:
                author = parts[1]
                message = parts[2]
                if "[SYSTEM]" in message:
                    self.add_message(f"{message}", is_system=True)
                else:
                    self.add_message(f"{author}> {message}")
        elif msg_type == "IMAGE":
            if len(parts) >= 4:
                author = parts[1]
                filename = parts[2]
                b64_img = parts[3]
                try:
                    img_data = base64.b64decode(b64_img)
                    pil_img = Image.open(io.BytesIO(img_data))
                    ctk_img = CTkImage(pil_img, size=(300, 300))
                    self.add_message(f"{author} sent: {filename}", img=ctk_img)
                except Exception as e:
                    self.add_system_message(f"image error: {e}")
        else:
            self.add_message(line)

    def open_image(self):
        file_name = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if not file_name:
            return
        try:
            with open(file_name, "rb") as f:
                raw = f.read()
            b64_data = base64.b64encode(raw).decode()
            short_name = os.path.basename(file_name)
            data = f"IMAGE@{self.username}@{short_name}@{b64_data}\n"
            self.sock.sendall(data.encode())
            self.add_message(f"[you] sent: {short_name}",
                             CTkImage(Image.open(file_name), size=(300, 300)))
        except Exception as e:
            self.add_system_message(f"send failed: {e}")


if __name__ == "__main__":
    win = MainWindow()
    win.mainloop()