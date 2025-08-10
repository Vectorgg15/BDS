import customtkinter as ctk
from tkinter import messagebox # Toplevel não é mais necessário aqui
from PIL import Image
import random
import os
import sys

# We'll use the 'screeninfo' library to detect multiple monitors.
# You need to install it: pip install screeninfo
try:
    from screeninfo import get_monitors
except ImportError:
    print("A biblioteca 'screeninfo' não está instalada. O modo mult Tela não funcionará.")
    print("Instale com: pip install screeninfo")
    get_monitors = None

# --- Configuration ---
COLOR_BACKGROUND = "#FEFDEE"
COLOR_HEADER_BG = "#B91C1C"
COLOR_HEADER_FG = "#FFFFFF"
COLOR_CURRENT_NUM_FG = "#1E293B"
COLOR_BOARD_NUM_CALLED_BG = "#FBBF24"
COLOR_BOARD_NUM_CALLED_FG = "#422006"
COLOR_BOARD_NUM_WAITING_BG = "#FFFFFF"
COLOR_BOARD_NUM_WAITING_FG = "#CBD5E1"

FONT_HEADER = ("Arial Rounded MT Bold", 40, "bold")
FONT_CURRENT_NUM = ("Arial Rounded MT Bold", 400, "bold")
FONT_BOARD_NUM = ("Arial Rounded MT Bold", 18, "bold")
LOGO_FILE = "Logo_Paróquia_ Alta_Definicao.png"

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class BigScreenWindow(ctk.CTkToplevel): # <-- CORREÇÃO 1: Herdar de CTkToplevel
    def __init__(self, master):
        super().__init__(master)
        self.title("Telão do Bingo")
        
        # <-- CORREÇÃO 2: Usar fg_color para definir o fundo em CustomTkinter
        self.configure(fg_color=COLOR_BACKGROUND) 

        # --- Multi-monitor setup ---
        self.setup_multiscreen()

        # --- Widgets ---
        # Label to display the large number being called
        self.current_number_label = ctk.CTkLabel(self, text="--", font=FONT_CURRENT_NUM,
                                                 text_color=COLOR_CURRENT_NUM_FG,
                                                 fg_color="transparent") # bg_color não é necessário se fg_color é transparent
        self.current_number_label.place(relx=0.75, rely=0.45, anchor="center")

        # Load and display the logo
        try:
            logo_path = resource_path(LOGO_FILE)
            pil_logo = Image.open(logo_path)
            self.logo_image = ctk.CTkImage(light_image=pil_logo, size=(120, 150))
            logo_label = ctk.CTkLabel(self, image=self.logo_image, text="",
                                      fg_color="transparent")
            logo_label.place(relx=0.75, rely=0.8, anchor="center")
        except Exception as e:
            print(f"Erro ao carregar a logo no telão: {e}")
            error_label = ctk.CTkLabel(self, text="Logo\nNão Encontrada", font=("Arial", 12))
            error_label.place(relx=0.75, rely=0.8, anchor="center")


        # Frame to hold the bingo board
        self.board_container = ctk.CTkFrame(self, fg_color="transparent")
        self.board_container.place(relx=0.3, rely=0.5, anchor="center")

        self.board_labels = {}
        headers = "BINGO"
        ranges = {
            'B': range(1, 16), 'I': range(16, 31), 'N': range(31, 46),
            'G': range(46, 61), 'O': range(61, 76)
        }

        # Create the board headers (B-I-N-G-O)
        for col_index, letter in enumerate(headers):
            ctk.CTkLabel(self.board_container, text=letter, font=FONT_HEADER, text_color=COLOR_HEADER_FG,
                         fg_color=COLOR_HEADER_BG, width=100, height=80, corner_radius=10).grid(
                row=0, column=col_index, padx=5, pady=(0, 10))

            # Create the number labels for each column
            for row_index, number in enumerate(ranges[letter]):
                label = ctk.CTkLabel(self.board_container, text=f"{number:02d}", font=FONT_BOARD_NUM, width=60, height=35,
                                     fg_color=COLOR_BOARD_NUM_WAITING_BG, text_color=COLOR_BOARD_NUM_WAITING_FG,
                                     corner_radius=8)
                label.grid(row=row_index + 1, column=col_index, padx=5, pady=2)
                self.board_labels[number] = label

    def setup_multiscreen(self):
        """Detects and configures the window for a second monitor if available."""
        if not get_monitors:
            self.geometry("1280x720") # Fallback geometry
            return

        monitors = get_monitors()
        if len(monitors) > 1:
            # Second monitor detected
            second_monitor = monitors[1]
            self.geometry(f"{second_monitor.width}x{second_monitor.height}+{second_monitor.x}+0")
            self.attributes("-fullscreen", True)
            # Bind Escape key to exit fullscreen
            self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))
        else:
            # Only one monitor
            self.geometry("1280x720") # Default size for single monitor
            self.resizable(True, True)

    def animate_number(self, new_number):
        """Animates the number change with a quick random sequence."""
        animation_numbers = list(range(1, 76))
        def update_animation(step=0):
            if step < 20: # Number of animation steps
                self.current_number_label.configure(text=f"{random.choice(animation_numbers):02d}")
                self.after(50, update_animation, step + 1) # Animation speed
            else:
                self.current_number_label.configure(text=f"{new_number:02d}")
        update_animation()

    def update_board(self, number):
        """Updates the color of a called number on the board."""
        if number in self.board_labels:
            label = self.board_labels[number]
            label.configure(fg_color=COLOR_BOARD_NUM_CALLED_BG, text_color=COLOR_BOARD_NUM_CALLED_FG)

    def clear_board(self):
        """Resets the board and current number for a new game."""
        self.current_number_label.configure(text="--")
        for label in self.board_labels.values():
            label.configure(fg_color=COLOR_BOARD_NUM_WAITING_BG, text_color=COLOR_BOARD_NUM_WAITING_FG)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Painel de Controle do Bingo")
        self.geometry("400x380")
        self.configure(fg_color=COLOR_BACKGROUND)
        ctk.set_default_color_theme("blue")
        self.called_numbers = set()

        # --- Main Widgets for Control Panel ---
        ctk.CTkLabel(self, text="Controle do Sorteio", font=("Arial", 22, "bold"),
                     text_color=COLOR_CURRENT_NUM_FG).pack(pady=15)

        manual_frame = ctk.CTkFrame(self, fg_color="transparent")
        manual_frame.pack(pady=5)

        ctk.CTkLabel(manual_frame, text="Número Sorteado:", font=("Arial", 14)).pack()
        self.manual_entry = ctk.CTkEntry(manual_frame, width=150, font=("Arial", 24, "bold"), justify="center")
        self.manual_entry.pack(pady=5)
        self.manual_entry.bind("<Return>", self.confirm_manual_number)

        self.confirm_button = ctk.CTkButton(manual_frame, text="Anunciar Número", command=self.confirm_manual_number,
                                            height=40, font=("Arial", 14, "bold"),
                                            fg_color=COLOR_HEADER_BG, hover_color="#991b1b") #Ajustei o Hover
        self.confirm_button.pack(pady=10)

        self.clear_button = ctk.CTkButton(self, text="Limpar Telão e Reiniciar Jogo", command=self.clear_all,
                                          font=("Arial", 14, "bold"),
                                          fg_color="#64748B", hover_color="#475569")
        self.clear_button.pack(pady=20)

        # --- Footer ---
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.pack(side="bottom", fill="x", pady=(5, 10))

        try:
            logo_path = resource_path(LOGO_FILE)
            logo_image = ctk.CTkImage(Image.open(logo_path), size=(40, 50))
            logo_label = ctk.CTkLabel(footer_frame, image=logo_image, text="")
            logo_label.pack()
        except Exception as e:
            print(f"Erro ao carregar a logo no painel de controle: {e}")

        signature_label = ctk.CTkLabel(footer_frame, text="por Victor Manuel", font=("Arial", 8),
                                       text_color="#666666")
        signature_label.pack()

        # --- Initialize the Big Screen ---
        self.big_screen = None # Inicia como None
        self.after(100, self.open_big_screen) # Abre a tela grande um pouco depois para garantir que a principal está pronta

        self.manual_entry.focus()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def open_big_screen(self):
        if self.big_screen is None or not self.big_screen.winfo_exists():
            self.big_screen = BigScreenWindow(self)
        else:
            self.big_screen.focus()

    def confirm_manual_number(self, event=None):
        """Validates and sends the manually entered number to the big screen."""
        if self.big_screen is None or not self.big_screen.winfo_exists():
            messagebox.showerror("Erro", "A janela do Telão não está aberta.")
            return

        try:
            num_str = self.manual_entry.get()
            if not num_str:
                return
            num = int(num_str)
            if not (1 <= num <= 75):
                messagebox.showwarning("Número Inválido", "Por favor, insira um número entre 1 e 75.")
                self.manual_entry.delete(0, 'end')
                return

            # Announce and update board
            self.big_screen.animate_number(num)
            self.big_screen.update_board(num)

            if num not in self.called_numbers:
                self.called_numbers.add(num)
                print(f"Anunciando número: {num}")
            else:
                print(f"Número {num} já foi sorteado (re-anunciando).")

            self.manual_entry.delete(0, 'end')
        except ValueError:
            messagebox.showerror("Entrada Inválida", "Por favor, insira um número válido.")
            self.manual_entry.delete(0, 'end')

    def clear_all(self):
        """Clears the board and resets the game state."""
        if self.big_screen is None or not self.big_screen.winfo_exists():
            messagebox.showerror("Erro", "A janela do Telão não está aberta.")
            return
            
        self.called_numbers.clear()
        self.big_screen.clear_board()
        print("Telão limpo. Novo jogo iniciado.")
        messagebox.showinfo("Jogo Reiniciado", "O telão foi limpo e um novo jogo foi iniciado.")

    def on_closing(self):
        """Ensure both windows close properly."""
        if messagebox.askokcancel("Sair", "Você tem certeza que quer fechar o programa?"):
            if self.big_screen is not None:
                self.big_screen.destroy()
            self.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()