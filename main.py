import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import threading
import time
from datetime import datetime
import pystray
from PIL import Image, ImageDraw
import sys
import random

class DailyQuoteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Daily Quote")
        self.root.geometry("400x150")
        self.root.resizable(True, True)  # Cho phép thay đổi kích thước
        self.root.minsize(300, 120)  # Kích thước tối thiểu
        
        # Load dữ liệu (sẽ khởi tạo các biến với giá trị từ file hoặc giá trị mặc định)
        self.data_file = "D:\\Projects\\DailyQuote\\quotes_data.json"
        
        # Khởi tạo các biến cần thiết trước khi load (những biến không được lưu trong file)
        self.advance_thread = None
        self.stop_advance_event = threading.Event()  # Event để dừng thread đếm thời gian
        self.running = True
        
        # Load dữ liệu từ file (sẽ set các biến: quotes, display_time, current_index, 
        # show_controls, always_on_top, random_mode, show_notification_on_change, auto_advance_enabled)
        self.load_data()
        
        # Tạo giao diện
        self.create_widgets()
        
        # Bind event để cập nhật wraplength khi cửa sổ thay đổi kích thước
        self.root.bind('<Configure>', self.on_window_resize)
        
        # Bind các phím tắt (sau khi widgets đã được tạo)
        self.root.after(100, self.setup_keyboard_shortcuts)
        
        # Hiển thị quote đầu tiên
        self.show_current_quote()
        
        # Áp dụng trạng thái hiển thị thanh điều khiển
        if not self.show_controls:
            self.toggle_controls(False)
        
        # Áp dụng trạng thái always on top
        self.apply_always_on_top()
        
        # Bắt đầu auto-advance
        if self.auto_advance_enabled:
            self.start_auto_advance()
        
        # Xử lý đóng cửa sổ
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Set icon cho cửa sổ chính
        self.set_window_icon()
        
        # Tạo system tray icon
        self.create_tray_icon()
    
    def create_widgets(self):
        # Frame chính
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Label hiển thị quote
        self.quote_label = tk.Label(
            self.main_frame,
            text="",
            font=("Arial", 11),
            wraplength=380,
            justify=tk.CENTER,
            bg="#f0f0f0",
            fg="#333333",
            padx=10,
            pady=10,
            relief=tk.SUNKEN,
            bd=1
        )
        self.quote_label.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Frame cho các nút điều khiển
        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.pack(fill=tk.X)
        
        # Nút Previous
        ttk.Button(
            self.control_frame,
            text="◀ Trước",
            command=self.previous_quote,
            width=10
        ).pack(side=tk.LEFT, padx=2)
        
        # Nút Next
        ttk.Button(
            self.control_frame,
            text="Tiếp ▶",
            command=self.next_quote,
            width=10
        ).pack(side=tk.LEFT, padx=2)
        
        # Nút Settings
        ttk.Button(
            self.control_frame,
            text="⚙ Cài đặt",
            command=self.open_settings,
            width=10
        ).pack(side=tk.LEFT, padx=2)
        
        # Nút Minimize to tray
        ttk.Button(
            self.control_frame,
            text="▼ Thu nhỏ",
            command=self.minimize_to_tray,
            width=10
        ).pack(side=tk.LEFT, padx=2)
        
        # Frame chứa timer và quote counter trên cùng một dòng
        self.info_frame = ttk.Frame(self.main_frame)
        self.info_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Label hiển thị số quote hiện tại/tổng số (căn trái)
        self.quote_counter_label = tk.Label(
            self.info_frame,
            text="",
            font=("Arial", 8),
            fg="#666666"
        )
        self.quote_counter_label.pack(side=tk.LEFT)
        
        # Label hiển thị thời gian còn lại (căn phải)
        self.timer_label = tk.Label(
            self.info_frame,
            text="",
            font=("Arial", 8),
            fg="#666666"
        )
        self.timer_label.pack(side=tk.RIGHT)
    
    def on_window_resize(self, event):
        """Cập nhật wraplength khi cửa sổ thay đổi kích thước"""
        if event.widget == self.root:
            # Lấy chiều rộng cửa sổ và trừ đi padding
            window_width = self.root.winfo_width()
            # Cập nhật wraplength (trừ đi padding và margin)
            new_wraplength = max(200, window_width - 40)  # Tối thiểu 200px
            self.quote_label.config(wraplength=new_wraplength)
    
    def load_data(self):
        """Load dữ liệu từ file JSON"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.quotes = data.get('quotes', [])
                    self.display_time = data.get('display_time', 30)  # mặc định 30 giây
                    self.current_index = data.get('current_index', 0)
                    self.show_controls = data.get('show_controls', True)  # Mặc định hiển thị
                    self.always_on_top = data.get('always_on_top', True)  # Mặc định bật
                    self.random_mode = data.get('random_mode', False)  # Mặc định tuần tự
                    self.show_notification_on_change = data.get('show_notification_on_change', True)  # Mặc định bật
                    self.auto_advance_enabled = data.get('auto_advance_enabled', True)  # Mặc định bật
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể load dữ liệu: {e}")
                self.quotes = []
                self.display_time = 30
                self.current_index = 0
                self.show_controls = True
                self.always_on_top = True
                self.random_mode = False
                self.show_notification_on_change = True
                self.auto_advance_enabled = True
        else:
            # Dữ liệu mẫu
            self.quotes = [
                "Hôm nay là một ngày mới, hãy sống trọn vẹn!",
                "Thành công không đến từ những gì bạn làm thỉnh thoảng, mà từ những gì bạn làm thường xuyên.",
                "Đừng sợ thất bại, hãy sợ việc không dám thử.",
                "Mỗi ngày là một cơ hội mới để trở nên tốt hơn.",
                "Hãy làm những gì bạn yêu thích, và yêu thích những gì bạn làm."
            ]
            self.display_time = 30
            self.current_index = 0
            self.show_controls = True
            self.always_on_top = True
            self.random_mode = False
            self.show_notification_on_change = True
            self.auto_advance_enabled = True
            self.save_data()
    
    def save_data(self):
        """Lưu dữ liệu vào file JSON"""
        try:
            data = {
                'quotes': self.quotes,
                'display_time': self.display_time,
                'current_index': self.current_index,
                'show_controls': self.show_controls,
                'always_on_top': self.always_on_top,
                'random_mode': self.random_mode,
                'show_notification_on_change': self.show_notification_on_change,
                'auto_advance_enabled': self.auto_advance_enabled
            }
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu dữ liệu: {e}")
    
    def show_current_quote(self):
        """Hiển thị quote hiện tại"""
        if self.quotes:
            if 0 <= self.current_index < len(self.quotes):
                quote = self.quotes[self.current_index]
                self.quote_label.config(text=quote)
                # Cập nhật hiển thị số quote (current_index + 1 vì index bắt đầu từ 0)
                self.quote_counter_label.config(text=f"Quote {self.current_index + 1}/{len(self.quotes)}")
            else:
                self.current_index = 0
                self.quote_label.config(text=self.quotes[0])
                self.quote_counter_label.config(text=f"Quote 1/{len(self.quotes)}")
        else:
            self.quote_label.config(text="Chưa có câu nói nào. Hãy thêm câu nói trong phần Cài đặt.")
            self.quote_counter_label.config(text="Quote 0/0")
        # Cập nhật tooltip tray icon
        self.update_tray_tooltip()
    
    def next_quote(self):
        """Chuyển sang quote tiếp theo"""
        if self.quotes:
            if self.random_mode:
                # Chế độ ngẫu nhiên: chọn quote ngẫu nhiên, tránh trùng với quote hiện tại
                if len(self.quotes) > 1:
                    new_index = self.current_index
                    while new_index == self.current_index:
                        new_index = random.randint(0, len(self.quotes) - 1)
                    self.current_index = new_index
                else:
                    self.current_index = 0
            else:
                # Chế độ tuần tự: chuyển sang quote tiếp theo
                self.current_index = (self.current_index + 1) % len(self.quotes)
            self.show_current_quote()
            self.save_data()
            if self.auto_advance_enabled:
                self.restart_auto_advance()
            # Cập nhật tooltip tray icon
            self.update_tray_tooltip()
            # Hiển thị notification nếu cửa sổ ẩn và tính năng được bật
            if not self.root.winfo_viewable() and self.show_notification_on_change:
                self.show_quote_notification()
    
    def previous_quote(self):
        """Chuyển về quote trước đó"""
        if self.quotes:
            if self.random_mode:
                # Chế độ ngẫu nhiên: chọn quote ngẫu nhiên khác
                if len(self.quotes) > 1:
                    new_index = self.current_index
                    while new_index == self.current_index:
                        new_index = random.randint(0, len(self.quotes) - 1)
                    self.current_index = new_index
                else:
                    self.current_index = 0
            else:
                # Chế độ tuần tự: chuyển về quote trước đó
                self.current_index = (self.current_index - 1) % len(self.quotes)
            self.show_current_quote()
            self.save_data()
            if self.auto_advance_enabled:
                self.restart_auto_advance()
            # Cập nhật tooltip tray icon
            self.update_tray_tooltip()
            # Hiển thị notification nếu cửa sổ ẩn và tính năng được bật
            if not self.root.winfo_viewable() and self.show_notification_on_change:
                self.show_quote_notification()
    
    def start_auto_advance(self):
        """Bắt đầu tự động chuyển quote"""
        if not self.auto_advance_enabled or not self.quotes:
            return
        
        # Dừng thread cũ nếu đang chạy
        if self.advance_thread is not None and self.advance_thread.is_alive():
            self.stop_advance_event.set()
            # Đợi thread cũ kết thúc (tối đa 1 giây)
            self.advance_thread.join(timeout=1.0)
        
        # Reset event và tạo thread mới
        self.stop_advance_event.clear()
        self.remaining_time = self.display_time
        self.update_timer_display()
        
        def countdown():
            while self.running and not self.stop_advance_event.is_set() and self.remaining_time > 0:
                # Sử dụng wait với timeout thay vì sleep để có thể dừng ngay lập tức
                if self.stop_advance_event.wait(timeout=1.0):
                    # Event được set, dừng thread
                    break
                
                if self.running and not self.stop_advance_event.is_set():
                    self.remaining_time -= 1
                    self.root.after(0, self.update_timer_display)
            
            # Chỉ chuyển quote nếu thread không bị dừng bởi event
            if self.running and not self.stop_advance_event.is_set() and self.auto_advance_enabled:
                self.root.after(0, self.next_quote)
        
        self.advance_thread = threading.Thread(target=countdown, daemon=True)
        self.advance_thread.start()
    
    def restart_auto_advance(self):
        """Khởi động lại auto-advance"""
        self.remaining_time = self.display_time
        self.start_auto_advance()
    
    def update_timer_display(self):
        """Cập nhật hiển thị thời gian còn lại"""
        if self.auto_advance_enabled and hasattr(self, 'remaining_time'):
            minutes = self.remaining_time // 60
            seconds = self.remaining_time % 60
            self.timer_label.config(text=f"Chuyển tự động sau: {minutes:02d}:{seconds:02d}")
        else:
            self.timer_label.config(text="")
    
    def open_settings(self):
        """Mở cửa sổ cài đặt"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Cài đặt")
        settings_window.geometry("500x400")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Tab notebook
        notebook = ttk.Notebook(settings_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab Quản lý Quotes
        quotes_frame = ttk.Frame(notebook, padding="10")
        notebook.add(quotes_frame, text="Quản lý Quotes")
        
        # Listbox hiển thị quotes
        listbox_frame = ttk.Frame(quotes_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        quotes_listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set, font=("Arial", 10))
        quotes_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=quotes_listbox.yview)
        
        # Load quotes vào listbox
        for quote in self.quotes:
            quotes_listbox.insert(tk.END, quote)
        
        # Frame cho các nút
        buttons_frame = ttk.Frame(quotes_frame)
        buttons_frame.pack(fill=tk.X)
        
        def add_quote():
            quote = simpledialog.askstring("Thêm câu nói", "Nhập câu nói mới:")
            if quote:
                self.quotes.append(quote)
                quotes_listbox.insert(tk.END, quote)
                self.save_data()
        
        def edit_quote():
            selection = quotes_listbox.curselection()
            if selection:
                index = selection[0]
                old_quote = self.quotes[index]
                new_quote = simpledialog.askstring("Sửa câu nói", "Sửa câu nói:", initialvalue=old_quote)
                if new_quote:
                    self.quotes[index] = new_quote
                    quotes_listbox.delete(index)
                    quotes_listbox.insert(index, new_quote)
                    self.save_data()
        
        def delete_quote():
            selection = quotes_listbox.curselection()
            if selection:
                index = selection[0]
                if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa câu nói này?"):
                    quotes_listbox.delete(index)
                    self.quotes.pop(index)
                    self.save_data()
                    if self.current_index >= len(self.quotes) and self.quotes:
                        self.current_index = 0
                        self.show_current_quote()
        
        ttk.Button(buttons_frame, text="Thêm", command=add_quote).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="Sửa", command=edit_quote).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="Xóa", command=delete_quote).pack(side=tk.LEFT, padx=2)
        
        # Tab Cài đặt thời gian
        time_frame = ttk.Frame(notebook, padding="10")
        notebook.add(time_frame, text="Cài đặt thời gian")
        
        ttk.Label(time_frame, text="Thời gian hiển thị mỗi câu nói (giây):", font=("Arial", 10, "bold")).pack(pady=(10, 5))
        
        time_var = tk.IntVar(value=self.display_time)
        time_spinbox = ttk.Spinbox(time_frame, from_=5, to=3600, textvariable=time_var, width=10)
        time_spinbox.pack(pady=5)
        
        ttk.Label(time_frame, text="(Tối thiểu: 5 giây, Tối đa: 3600 giây = 1 giờ)", 
                 font=("Arial", 8), foreground="gray").pack()
        
        def save_time():
            new_time = time_var.get()
            if 5 <= new_time <= 3600:
                self.display_time = new_time
                self.save_data()
                if self.auto_advance_enabled:
                    self.restart_auto_advance()
                messagebox.showinfo("Thành công", "Đã lưu cài đặt thời gian!")
            else:
                messagebox.showerror("Lỗi", "Thời gian phải từ 5 đến 3600 giây!")
        
        ttk.Button(time_frame, text="Lưu", command=save_time).pack(pady=15)
        
        # Separator
        ttk.Separator(time_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
        
        # Checkbox bật/tắt auto-advance
        ttk.Label(time_frame, text="Tự động chuyển câu nói:", font=("Arial", 10, "bold")).pack(pady=(5, 5))
        auto_var = tk.BooleanVar(value=self.auto_advance_enabled)
        
        def toggle_auto_advance():
            """Xử lý bật/tắt auto-advance"""
            self.auto_advance_enabled = auto_var.get()
            self.save_data()  # Lưu setting
            if self.auto_advance_enabled:
                # Bật: khởi động lại auto-advance
                self.restart_auto_advance()
            else:
                # Tắt: dừng thread đếm thời gian
                if hasattr(self, 'stop_advance_event'):
                    self.stop_advance_event.set()
                self.update_timer_display()  # Ẩn timer display
        
        auto_checkbox = ttk.Checkbutton(
            time_frame,
            text="Bật tự động chuyển sang câu nói tiếp theo sau khoảng thời gian đã đặt",
            variable=auto_var,
            command=toggle_auto_advance
        )
        auto_checkbox.pack(pady=5, anchor=tk.W)
        
        # Separator
        ttk.Separator(time_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
        
        # Checkbox hiển thị notification khi chuyển quote
        ttk.Label(time_frame, text="Thông báo (Notification):", font=("Arial", 10, "bold")).pack(pady=(5, 5))
        notification_var = tk.BooleanVar(value=self.show_notification_on_change)
        
        def toggle_notification():
            """Xử lý bật/tắt notification"""
            self.show_notification_on_change = notification_var.get()
            self.save_data()
        
        notification_checkbox = ttk.Checkbutton(
            time_frame,
            text="Hiển thị thông báo khi chuyển câu nói (chỉ khi cửa sổ đang ẩn)",
            variable=notification_var,
            command=toggle_notification
        )
        notification_checkbox.pack(pady=5, anchor=tk.W)
        
        # Tab Cài đặt giao diện
        ui_frame = ttk.Frame(notebook, padding="10")
        notebook.add(ui_frame, text="Cài đặt giao diện")
        
        ttk.Label(ui_frame, text="Tùy chọn hiển thị:", font=("Arial", 10, "bold")).pack(pady=(10, 10))
        
        # Checkbox ẩn/hiện thanh điều khiển
        controls_var = tk.BooleanVar(value=self.show_controls)
        controls_checkbox = ttk.Checkbutton(
            ui_frame,
            text="Hiển thị thanh điều khiển (các nút Trước, Tiếp, Cài đặt, Thu nhỏ)",
            variable=controls_var,
            command=lambda: self.toggle_controls(controls_var.get())
        )
        controls_checkbox.pack(pady=10, anchor=tk.W)
        
        # Checkbox Always On Top
        always_on_top_var = tk.BooleanVar(value=self.always_on_top)
        always_on_top_checkbox = ttk.Checkbutton(
            ui_frame,
            text="Luôn ở trên cùng (Always On Top) - Cửa sổ luôn hiển thị phía trên các cửa sổ khác",
            variable=always_on_top_var,
            command=lambda: self.toggle_always_on_top(always_on_top_var.get())
        )
        always_on_top_checkbox.pack(pady=10, anchor=tk.W)
        
        # Tab Chế độ hiển thị
        mode_frame = ttk.Frame(notebook, padding="10")
        notebook.add(mode_frame, text="Chế độ hiển thị")
        
        ttk.Label(mode_frame, text="Chọn chế độ hiển thị câu nói:", font=("Arial", 10, "bold")).pack(pady=(10, 15))
        
        mode_var = tk.StringVar(value="sequential" if not self.random_mode else "random")
        
        def save_mode():
            """Tự động lưu khi thay đổi chế độ"""
            new_mode = mode_var.get() == "random"
            if new_mode != self.random_mode:
                self.random_mode = new_mode
                self.save_data()
        
        # Radio button cho chế độ tuần tự
        sequential_radio = ttk.Radiobutton(
            mode_frame,
            text="Tuần tự (Sequential)",
            variable=mode_var,
            value="sequential",
            command=save_mode
        )
        sequential_radio.pack(anchor=tk.W, padx=20, pady=5)
        
        ttk.Label(
            mode_frame,
            text="  → Hiển thị các câu nói theo thứ tự từ đầu đến cuối, sau đó lặp lại.",
            font=("Arial", 9),
            foreground="gray"
        ).pack(anchor=tk.W, padx=40, pady=(0, 10))
        
        # Radio button cho chế độ ngẫu nhiên
        random_radio = ttk.Radiobutton(
            mode_frame,
            text="Ngẫu nhiên (Random)",
            variable=mode_var,
            value="random",
            command=save_mode
        )
        random_radio.pack(anchor=tk.W, padx=20, pady=5)
        
        ttk.Label(
            mode_frame,
            text="  → Hiển thị các câu nói một cách ngẫu nhiên, không theo thứ tự.",
            font=("Arial", 9),
            foreground="gray"
        ).pack(anchor=tk.W, padx=40, pady=(0, 15))
        
        # Tab Phím tắt
        shortcuts_frame = ttk.Frame(notebook, padding="10")
        notebook.add(shortcuts_frame, text="Phím tắt")
        
        ttk.Label(shortcuts_frame, text="Danh sách phím tắt:", font=("Arial", 10, "bold")).pack(pady=(10, 15))
        
        shortcuts_text = """Space hoặc → (Mũi tên phải) : Chuyển sang câu nói tiếp theo
← (Mũi tên trái) : Chuyển về câu nói trước đó
H : Ẩn/hiện thanh điều khiển
S : Mở cửa sổ cài đặt
Escape : Thu nhỏ vào system tray"""
        
        shortcuts_label = ttk.Label(
            shortcuts_frame,
            text=shortcuts_text,
            font=("Arial", 10),
            justify=tk.LEFT
        )
        shortcuts_label.pack(anchor=tk.W, padx=10)
        
        ttk.Label(
            shortcuts_frame,
            text="\nLưu ý: Phím tắt chỉ hoạt động khi cửa sổ chính đang được focus.",
            font=("Arial", 8),
            foreground="gray",
            justify=tk.LEFT
        ).pack(anchor=tk.W, padx=10, pady=(15, 0))
    
    def toggle_controls(self, show=None):
        """Ẩn/hiện thanh điều khiển"""
        if show is None:
            self.show_controls = not self.show_controls
        else:
            self.show_controls = show
        
        if hasattr(self, 'control_frame'):
            if self.show_controls:
                # Pack lại control_frame sau quote_label
                self.control_frame.pack(fill=tk.X, after=self.quote_label)
            else:
                self.control_frame.pack_forget()
        
        self.save_data()
    
    def toggle_always_on_top(self, enable=None):
        """Bật/tắt Always On Top"""
        if enable is None:
            self.always_on_top = not self.always_on_top
        else:
            self.always_on_top = enable
        
        self.apply_always_on_top()
        self.save_data()
    
    def apply_always_on_top(self):
        """Áp dụng trạng thái Always On Top"""
        self.root.attributes('-topmost', self.always_on_top)
    
    def setup_keyboard_shortcuts(self):
        """Thiết lập các phím tắt"""
        def handle_key(event):
            """Xử lý phím tắt"""
            # Chỉ xử lý khi cửa sổ chính đang hiển thị
            if not self.root.winfo_viewable():
                return
            
            # Kiểm tra xem có dialog nào đang mở không
            for widget in self.root.winfo_children():
                if isinstance(widget, tk.Toplevel) and widget.winfo_viewable():
                    return
            
            # Lấy key từ event
            key = event.keysym if hasattr(event, 'keysym') else ''
            char = event.char if hasattr(event, 'char') and event.char else ''
            
            # Chuyển sang lowercase để so sánh
            key_lower = key.lower()
            char_lower = char.lower()
            
            # Xử lý các phím tắt
            if key_lower == 'space' or key_lower == 'right':
                self.next_quote()
                return "break"
            elif key_lower == 'left':
                self.previous_quote()
                return "break"
            elif key_lower == 'h' or char_lower == 'h':
                self.toggle_controls()
                return "break"
            elif key_lower == 's' or char_lower == 's':
                self.open_settings()
                return "break"
            elif key_lower == 'escape':
                self.minimize_to_tray()
                return "break"
        
        # Sử dụng bind_all để bind toàn cục trong ứng dụng
        self.root.bind_all('<KeyPress>', handle_key)
        self.root.bind_all('<Key>', handle_key)
        
        # Bind riêng cho root
        self.root.bind('<KeyPress>', handle_key)
        self.root.bind('<Key>', handle_key)
        
        # Focus vào root để nhận phím tắt
        self.root.focus_set()
        
        # Đảm bảo focus được giữ khi click vào cửa sổ hoặc các widget
        def set_focus(event):
            self.root.focus_set()
        
        self.root.bind('<Button-1>', set_focus)
        if hasattr(self, 'main_frame'):
            self.main_frame.bind('<Button-1>', set_focus)
        if hasattr(self, 'quote_label'):
            self.quote_label.bind('<Button-1>', set_focus)
    
    def minimize_to_tray(self):
        """Thu nhỏ vào system tray"""
        self.root.withdraw()
        self.update_tray_tooltip()
    
    def show_window(self):
        """Hiển thị lại cửa sổ từ system tray"""
        self.root.deiconify()
        self.root.lift()
        # Áp dụng trạng thái always on top
        self.apply_always_on_top()
        # Focus lại để phím tắt hoạt động
        self.root.focus_set()
    
    def toggle_window(self):
        """Toggle hiển thị/ẩn cửa sổ"""
        if self.root.winfo_viewable():
            self.minimize_to_tray()
        else:
            self.show_window()
    
    def get_current_quote_text(self):
        """Lấy text của quote hiện tại"""
        if self.quotes and 0 <= self.current_index < len(self.quotes):
            quote = self.quotes[self.current_index]
            # Giới hạn độ dài để hiển thị trong tooltip/notification
            if len(quote) > 100:
                return quote[:97] + "..."
            return quote
        return "Chưa có câu nói nào"
    
    def update_tray_tooltip(self):
        """Cập nhật tooltip của tray icon"""
        if hasattr(self, 'tray_icon'):
            quote_text = self.get_current_quote_text()
            self.tray_icon.title = f"Daily Quote\n\n{quote_text}"
    
    def show_quote_notification(self):
        """Hiển thị notification với quote hiện tại"""
        quote_text = self.get_current_quote_text()
        if hasattr(self, 'tray_icon'):
            self.tray_icon.notify(quote_text, "Daily Quote")
    
    def next_quote_from_tray(self):
        """Chuyển sang quote tiếp theo từ tray"""
        self.next_quote()
        self.update_tray_tooltip()
        if not self.root.winfo_viewable():
            self.show_quote_notification()
    
    def previous_quote_from_tray(self):
        """Chuyển về quote trước đó từ tray"""
        self.previous_quote()
        self.update_tray_tooltip()
        if not self.root.winfo_viewable():
            self.show_quote_notification()
    
    def open_settings_from_tray(self):
        """Mở cài đặt từ tray"""
        # Hiển thị cửa sổ nếu đang ẩn
        if not self.root.winfo_viewable():
            self.show_window()
        # Mở cài đặt
        self.open_settings()
    
    def create_icon_image(self, size=64):
        """Tạo icon hiện đại với style white-black"""
        # Tạo hình ảnh với nền trắng
        image = Image.new('RGBA', (size, size), color=(255, 255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        center = size // 2
        
        # Style hiện đại: Nền trắng với dấu ngoặc kép đen, bold và rõ ràng
        # Màu đen cho dấu ngoặc kép
        quote_color = (0, 0, 0, 255)  # Đen
        line_width = 5  # Độ dày của nét vẽ (bold hơn)
        
        # Vẽ dấu ngoặc kép với style minimal và hiện đại
        quote_y = center
        quote_height = 18
        quote_width = 8
        
        # Dấu ngoặc kép trái (") - style typography hiện đại
        quote_left_x = center - 10
        
        # Ngoặc trên trái - vẽ một phần ellipse cong đẹp
        draw.arc([quote_left_x - quote_width, quote_y - quote_height//2 - 1, 
                  quote_left_x + 2, quote_y - 1], 
                 start=180, end=270, fill=quote_color, width=line_width)
        # Ngoặc dưới trái
        draw.arc([quote_left_x - quote_width, quote_y + 1, 
                  quote_left_x + 2, quote_y + quote_height//2 + 1], 
                 start=90, end=180, fill=quote_color, width=line_width)
        
        # Dấu ngoặc kép phải (")
        quote_right_x = center + 2
        # Ngoặc trên phải
        draw.arc([quote_right_x - 2, quote_y - quote_height//2 - 1, 
                  quote_right_x + quote_width, quote_y - 1], 
                 start=270, end=360, fill=quote_color, width=line_width)
        # Ngoặc dưới phải
        draw.arc([quote_right_x - 2, quote_y + 1, 
                  quote_right_x + quote_width, quote_y + quote_height//2 + 1], 
                 start=0, end=90, fill=quote_color, width=line_width)
        
        return image
    
    def set_window_icon(self):
        """Set icon cho cửa sổ chính"""
        try:
            # Tạo icon
            icon_image = self.create_icon_image(64)
            # Convert PIL Image sang PhotoImage cho Tkinter
            from PIL import ImageTk
            photo = ImageTk.PhotoImage(icon_image)
            self.root.iconphoto(True, photo)
            # Giữ reference để tránh garbage collection
            self.window_icon = photo
        except Exception as e:
            # Nếu có lỗi, bỏ qua (không ảnh hưởng đến chức năng chính)
            pass
    
    def create_tray_icon(self):
        """Tạo icon trong system tray"""
        # Tạo icon đẹp với biểu tượng dấu ngoặc kép
        image = self.create_icon_image(64)
        
        # Tạo menu với nhiều tùy chọn
        menu = pystray.Menu(
            pystray.MenuItem("Hiển thị quote hiện tại", self.show_quote_notification),
            pystray.MenuItem("Câu tiếp theo", self.next_quote_from_tray),
            pystray.MenuItem("Câu trước", self.previous_quote_from_tray),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Cài đặt", self.open_settings_from_tray),
            pystray.MenuItem("Hiển thị cửa sổ", self.show_window),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Thoát", self.quit_app)
        )
        
        quote_text = self.get_current_quote_text()
        self.tray_icon = pystray.Icon(
            "DailyQuote", 
            image, 
            f"Daily Quote\n\n{quote_text}", 
            menu,
            default_action=self.toggle_window  # Click vào icon để toggle
        )
        
        # Chạy tray icon trong thread riêng
        tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
        tray_thread.start()
        
        # Cập nhật tooltip sau khi tạo tray icon
        self.root.after(100, self.update_tray_tooltip)
    
    def quit_app(self):
        """Thoát ứng dụng"""
        self.running = False
        # Dừng thread đếm thời gian nếu đang chạy
        if hasattr(self, 'stop_advance_event'):
            self.stop_advance_event.set()
        if self.advance_thread is not None and self.advance_thread.is_alive():
            self.advance_thread.join(timeout=1.0)
        if hasattr(self, 'tray_icon'):
            self.tray_icon.stop()
        self.root.quit()
        self.root.destroy()
    
    def on_closing(self):
        """Xử lý khi đóng cửa sổ"""
        self.minimize_to_tray()

def main():
    root = tk.Tk()
    app = DailyQuoteApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

