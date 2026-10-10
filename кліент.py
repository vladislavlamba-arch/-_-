import threading
from socket import *
from customtkinter import *

class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        self.geometry('600x400')
        self.title('CTk Chat')
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.label = None
        self.entry = None
        self.menu_frame = CTkFrame(self, width=30)
        self.menu_frame.pack_propagate(False)
        self.menu_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.is_show_menu = False
        self.speed_animate_menu = -5
        self.btn = CTkButton(self.menu_frame, text='▶️', command=self.toggle_show_menu, width=30)
        self.btn.place(x=0, y=0)
        self.chat_field = CTkTextbox(self, font=('Arial', 14, 'bold'), state='disable')
        self.chat_field.grid(row=0, column=1, sticky="nsew", padx=(5, 5), pady=(5, 5))
        self.input_frame = CTkFrame(self, fg_color="transparent")
        self.input_frame.grid(row=1, column=1, sticky="ew", padx=(5, 5), pady=(0, 5))
        self.message_entry = CTkEntry(self.input_frame, placeholder_text='Введіть повідомлення:', height=40)
        self.message_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.send_button = CTkButton(self.input_frame, text='>', width=50, height=40, command=self.send_message)
        self.send_button.pack(side="right")
        self.username = 'Artem'
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(('5.tcp.eu.ngrok.io', 12296))
            hello = f"TEXT@{self.username}@[SYSTEM] {self.username} приєднався(лась) до чату!\n"
            self.sock.send(hello.encode('utf-8'))
            threading.Thread(target=self.recv_message, daemon=True).start()
        except Exception as e:
            self.add_message(f"Не вдалося підключитися до сервера: {e}")

    def toggle_show_menu(self):
        if self.is_show_menu:
            self.is_show_menu = False
            self.speed_animate_menu = -5
            self.btn.configure(text='▶️')
            self.show_menu()
        else:
            self.is_show_menu = True
            self.speed_animate_menu = 5
            self.btn.configure(text='◀️')
            self.show_menu()
            
            if not self.label and not self.entry:
                self.label = CTkLabel(self.menu_frame, text='Імʼя')
                self.label.pack(pady=(40, 10))
                self.entry = CTkEntry(self.menu_frame)
                self.entry.pack()

    def show_menu(self):
        cur_w = self.menu_frame.winfo_width()
        new_w = cur_w + self.speed_animate_menu
        
        if self.is_show_menu and cur_w < 200:
            self.menu_frame.configure(width=new_w)
            self.after(10, self.show_menu)
        elif not self.is_show_menu and cur_w > 30:
            self.menu_frame.configure(width=new_w)
            self.after(10, self.show_menu)
            if cur_w <= 40:
                if self.label:
                    self.label.destroy()
                    self.label = None
                if self.entry:
                    self.entry.destroy()
                    self.entry = None

    def add_message(self, text):
        self.chat_field.configure(state='normal')
        self.chat_field.insert(END, text + '\n')
        self.chat_field.configure(state='disable')
        self.chat_field.see(END)

    def send_message(self):
        message = self.message_entry.get()
        if message:
            self.add_message(f"Я: {message}")
            data = f"TEXT@{self.username}@{message}\n"
            try:
                self.sock.sendall(data.encode())
            except:
                pass
        self.message_entry.delete(0, END)

    def recv_message(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode()

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle_line(line.strip())
            except:
                break
        self.sock.close()

    def handle_line(self, line):
        if not line:
            return
        parts = line.split("@", 3)
        msg_type = parts[0]
        if msg_type == "TEXT":
            if len(parts) >= 3:
                author = parts[1]
                message = parts[2]
                if author != self.username:
                    self.add_message(f"{author}: {message}")
        elif msg_type == "IMAGE":
            if len(parts) >= 4:
                author = parts[1]
                filename = parts[2]
                self.add_message(f"{author} надіслав(ла) зображення: {filename}")
        else:
            self.add_message(line)

win = MainWindow()
win.mainloop()