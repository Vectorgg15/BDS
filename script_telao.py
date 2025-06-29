import customtkinter as ctk
from tkinter import Toplevel
from PIL import Image
import random
import os
import sys

# --- FUNÇÃO PARA ENCONTRAR ARQUIVOS EMPACOTADOS ---
def resource_path(relative_path):
    """ Retorna o caminho absoluto para o recurso, funcionando tanto no modo dev quanto no PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- CONFIGURAÇÕES DE DESIGN ---
COLOR_BACKGROUND = "#FEFDEE"
COLOR_HEADER_BG = "#B91C1C"
COLOR_HEADER_FG = "#FFFFFF"
COLOR_CURRENT_NUM_FG = "#1E293B"
COLOR_BOARD_BG = "transparent"
COLOR_BOARD_NUM_CALLED_BG = "#FBBF24"
COLOR_BOARD_NUM_CALLED_FG = "#422006"
COLOR_BOARD_NUM_WAITING_BG = "#FFFFFF"
COLOR_BOARD_NUM_WAITING_FG = "#64748B"

FONT_HEADER = ("Arial Rounded MT Bold", 60, "bold")
FONT_CURRENT_NUM = ("Arial Rounded MT Bold", 280, "bold")
FONT_BOARD_NUM = ("Arial Rounded MT Bold", 22, "bold")


class BigScreenWindow(Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Telão do Bingo")
        self.attributes('-fullscreen', True)
        self.configure(bg=COLOR_BACKGROUND)

        # Logo da Paróquia no Telão
        try:
            logo_path = resource_path("Logo_Paróquia_ Alta_Definicao.png")
            pil_logo = Image.open(logo_path)
            self.logo_image = ctk.CTkImage(light_image=pil_logo, size=(120, 150))
            logo_label = ctk.CTkLabel(self, image=self.logo_image, text="", fg_color="transparent", bg_color=COLOR_BACKGROUND)
            logo_label.place(relx=0.02, rely=0.03, anchor="nw")
        except Exception as e:
            print(f"Erro ao carregar a logo no telão: {e}")

        header_frame = ctk.CTkFrame(self, fg_color="transparent", bg_color=COLOR_BACKGROUND)
        header_frame.pack(pady=(40, 20))
        headers = "BINGO"
        for letter in headers:
            ctk.CTkLabel(header_frame, text=letter, font=FONT_HEADER, text_color=COLOR_HEADER_FG,
                         fg_color=COLOR_HEADER_BG, width=120, height=100, corner_radius=0).pack(side="left", padx=2)

        self.current_number_label = ctk.CTkLabel(self, text="--", font=FONT_CURRENT_NUM, text_color=COLOR_CURRENT_NUM_FG, fg_color="transparent", bg_color=COLOR_BACKGROUND)
        self.current_number_label.pack(fill="both", expand=True)

        self.board_frame = ctk.CTkFrame(self, fg_color=COLOR_BOARD_BG, bg_color=COLOR_BACKGROUND)
        self.board_frame.pack(pady=(0, 30), side="bottom", fill="x", padx=50)
        self.board_labels = {}
        for i in range(1, 76):
            label = ctk.CTkLabel(self.board_frame, text=f"{i:02d}", font=FONT_BOARD_NUM, width=55, height=55,
                                 fg_color=COLOR_BOARD_NUM_WAITING_BG, text_color=COLOR_BOARD_NUM_WAITING_FG,
                                 corner_radius=28)
            self.board_labels[i] = label

    def animate_number(self, new_number):
        animation_numbers = list(range(1, 76))
        
        def update_animation(step=0):
            if step < 20:
                self.current_number_label.configure(text=f"{random.choice(animation_numbers):02d}")
                self.after(50, update_animation, step + 1)
            else:
                self.current_number_label.configure(text=f"{new_number:02d}")
        update_animation()

    def update_board(self, number):
        if number in self.board_labels:
            label = self.board_labels[number]
            label.configure(fg_color=COLOR_BOARD_NUM_CALLED_BG, text_color=COLOR_BOARD_NUM_CALLED_FG)
            row = (number - 1) // 15
            col = (number - 1) % 15
            label.grid(row=row, column=col, padx=4, pady=4)

    def clear_board(self):
        self.current_number_label.configure(text="--")
        for label in self.board_labels.values():
            label.grid_forget()


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Painel de Controle do Bingo")
        self.geometry("400x350") # Ajustei a altura
        
        self.configure(fg_color=COLOR_BACKGROUND)
        ctk.set_default_color_theme("blue")

        self.called_numbers = set()

        ctk.CTkLabel(self, text="Controle do Sorteio", font=("Arial", 22, "bold"), text_color=COLOR_CURRENT_NUM_FG).pack(pady=15)
        
        manual_frame = ctk.CTkFrame(self, fg_color="transparent")
        manual_frame.pack(pady=5)

        ctk.CTkLabel(manual_frame, text="Número Sorteado:", font=("Arial", 14)).pack()
        self.manual_entry = ctk.CTkEntry(manual_frame, width=150, font=("Arial", 24, "bold"), justify="center")
        self.manual_entry.pack(pady=5)
        self.manual_entry.bind("<Return>", self.confirm_manual_number)

        self.confirm_button = ctk.CTkButton(manual_frame, text="Anunciar Número", command=self.confirm_manual_number, height=40,
                                            fg_color=COLOR_HEADER_BG, hover_color="#8c1c1c")
        self.confirm_button.pack(pady=10)

        self.clear_button = ctk.CTkButton(self, text="Limpar Telão e Reiniciar Jogo", command=self.clear_all, 
                                          fg_color="#64748B", hover_color="#475569")
        self.clear_button.pack(pady=10)

        # --- FRAME DO RODAPÉ DO PAINEL DE CONTROLE (NOVO) ---
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.pack(side="bottom", fill="x", pady=(5, 10))

        # Logo da Paróquia
        try:
            logo_path = resource_path("Logo_Paróquia_ Alta_Definicao.png")
            logo_image = ctk.CTkImage(Image.open(logo_path), size=(40, 50))
            logo_label = ctk.CTkLabel(footer_frame, image=logo_image, text="")
            logo_label.pack()
        except Exception as e:
            print(f"Erro ao carregar a logo no painel de controle: {e}")

        # Assinatura
        signature_label = ctk.CTkLabel(footer_frame, text="por Victor Manuel", font=("Arial", 8), text_color="#666666")
        signature_label.pack()

        # --- Inicializa a janela do Telão e foca o entry ---
        self.big_screen = BigScreenWindow(self)
        self.manual_entry.focus()

    def confirm_manual_number(self, event=None):
        try:
            num_str = self.manual_entry.get()
            if not num_str: return
            
            num = int(num_str)
            
            if not (1 <= num <= 75):
                print("Número fora do intervalo (1-75).")
                self.manual_entry.delete(0, 'end')
                return
            
            self.big_screen.animate_number(num)
            
            if num not in self.called_numbers:
                self.called_numbers.add(num)
                self.big_screen.update_board(num)
                print(f"Anunciando número: {num}")
            else:
                print(f"Número {num} já foi sorteado (re-anunciando).")

            self.manual_entry.delete(0, 'end')

        except ValueError:
            print("Entrada manual inválida.")
            self.manual_entry.delete(0, 'end')

    def clear_all(self):
        self.called_numbers.clear()
        self.big_screen.clear_board()
        print("Telão limpo. Novo jogo iniciado.")


if __name__ == "__main__":
    app = App()
    app.mainloop()