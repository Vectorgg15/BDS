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
        # PyInstaller cria uma pasta temporária e armazena o caminho em _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Se não estiver rodando como .exe, use o caminho normal do script
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- CONFIGURAÇÕES DE DESIGN ---
COLOR_BACKGROUND = "#FEFDEE"
COLOR_HEADER_BG = "#B91C1C"
COLOR_HEADER_FG = "#FFFFFF"
COLOR_CURRENT_NUM_FG = "#1E293B"
COLOR_BOARD_NUM_CALLED_BG = "#FBBF24" # Amarelo-dourado para números chamados
COLOR_BOARD_NUM_CALLED_FG = "#422006" # Marrom escuro para números chamados
COLOR_BOARD_NUM_WAITING_BG = "#FFFFFF" # Fundo branco para números em espera
COLOR_BOARD_NUM_WAITING_FG = "#CBD5E1" # Cinza bem claro para números em espera

FONT_HEADER = ("Arial Rounded MT Bold", 40, "bold")
FONT_CURRENT_NUM = ("Arial Rounded MT Bold", 250, "bold")
FONT_BOARD_NUM = ("Arial Rounded MT Bold", 18, "bold")


class BigScreenWindow(Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Telão do Bingo")
        self.attributes('-fullscreen', True)
        self.configure(bg=COLOR_BACKGROUND)

        # --- Display do número ATUAL (posicionado à direita) ---
        self.current_number_label = ctk.CTkLabel(self, text="--", font=FONT_CURRENT_NUM, text_color=COLOR_CURRENT_NUM_FG, fg_color="transparent", bg_color=COLOR_BACKGROUND)
        self.current_number_label.place(relx=0.75, rely=0.45, anchor="center")

        # --- Logo da Paróquia (posicionada à direita, abaixo do número) ---
        try:
            logo_path = resource_path("Logo_Paróquia_ Alta_Definicao.png")
            pil_logo = Image.open(logo_path)
            self.logo_image = ctk.CTkImage(light_image=pil_logo, size=(120, 150))
            logo_label = ctk.CTkLabel(self, image=self.logo_image, text="", fg_color="transparent", bg_color=COLOR_BACKGROUND)
            logo_label.place(relx=0.75, rely=0.8, anchor="center")
        except Exception as e:
            print(f"Erro ao carregar a logo no telão: {e}")

        # --- Frame principal para o quadro BINGO (posicionado à esquerda) ---
        self.board_container = ctk.CTkFrame(self, fg_color="transparent", bg_color=COLOR_BACKGROUND)
        self.board_container.place(relx=0.3, rely=0.5, anchor="center")

        self.board_labels = {}
        
        headers = "BINGO"
        ranges = {
            'B': range(1, 16),
            'I': range(16, 31),
            'N': range(31, 46),
            'G': range(46, 61),
            'O': range(61, 76)
        }

        for col_index, letter in enumerate(headers):
            # Cabeçalho da coluna (B, I, N, G, O)
            ctk.CTkLabel(self.board_container, text=letter, font=FONT_HEADER, text_color=COLOR_HEADER_FG,
                         fg_color=COLOR_HEADER_BG, width=100, height=80, corner_radius=10).grid(row=0, column=col_index, padx=5, pady=(0,10))
            
            # Cria e posiciona os 15 números para cada coluna
            for row_index, number in enumerate(ranges[letter]):
                label = ctk.CTkLabel(self.board_container, text=f"{number:02d}", font=FONT_BOARD_NUM, width=60, height=35,
                                     fg_color=COLOR_BOARD_NUM_WAITING_BG, text_color=COLOR_BOARD_NUM_WAITING_FG,
                                     corner_radius=8)
                label.grid(row=row_index + 1, column=col_index, padx=5, pady=2)
                self.board_labels[number] = label

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
        """Apenas muda a cor do número sorteado no quadro."""
        if number in self.board_labels:
            label = self.board_labels[number]
            label.configure(fg_color=COLOR_BOARD_NUM_CALLED_BG, text_color=COLOR_BOARD_NUM_CALLED_FG)
            
    def clear_board(self):
        """Reseta as cores de todos os números no quadro para o estado inicial."""
        self.current_number_label.configure(text="--")
        for number, label in self.board_labels.items():
            label.configure(fg_color=COLOR_BOARD_NUM_WAITING_BG, text_color=COLOR_BOARD_NUM_WAITING_FG)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Painel de Controle do Bingo")
        self.geometry("400x350")
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
        
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.pack(side="bottom", fill="x", pady=(5, 10))
        try:
            logo_path = resource_path("Logo_Paróquia_ Alta_Definicao.png")
            logo_image = ctk.CTkImage(Image.open(logo_path), size=(40, 50))
            logo_label = ctk.CTkLabel(footer_frame, image=logo_image, text="")
            logo_label.pack()
        except Exception as e:
            print(f"Erro ao carregar a logo no painel de controle: {e}")
        signature_label = ctk.CTkLabel(footer_frame, text="por Victor Manuel", font=("Arial", 8), text_color="#666666")
        signature_label.pack()

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
            
            # Atualiza a cor no quadro, mesmo que já tenha sido chamado
            self.big_screen.update_board(num)
            
            if num not in self.called_numbers:
                self.called_numbers.add(num)
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
