import customtkinter as ctk
from tkinter import Toplevel
from PIL import Image
import random
import os
import sys
import speech_recognition as sr
import threading
import json
import re

# --- FUNÇÃO PARA ENCONTRAR ARQUIVOS EMPACOTADOS ---
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- CONFIGURAÇÕES DE DESIGN ---
COLOR_BACKGROUND = "#FEFDEE"
COLOR_HEADER_BG = "#B91C1C"
COLOR_HEADER_FG = "#FFFFFF"
# ... (outras cores e fontes) ...
COLOR_CURRENT_NUM_FG = "#1E293B"
COLOR_BOARD_BG = "transparent"
COLOR_BOARD_NUM_CALLED_BG = "#FBBF24"
COLOR_BOARD_NUM_CALLED_FG = "#422006"
COLOR_BOARD_NUM_WAITING_BG = "#FFFFFF"
COLOR_BOARD_NUM_WAITING_FG = "#64748B"

FONT_HEADER = ("Arial Rounded MT Bold", 60, "bold")
FONT_CURRENT_NUM = ("Arial Rounded MT Bold", 280, "bold")
FONT_BOARD_NUM = ("Arial Rounded MT Bold", 22, "bold")


# --- DICIONÁRIO OTIMIZADO PARA RECONHECIMENTO DE VOZ ---
def build_recognition_dictionary():
    word_map = {}
    units = ["", "um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove"]
    teens = ["dez", "onze", "doze", "treze", "catorze", "quinze", "dezesseis", "dezessete", "dezoito", "dezenove"]
    tens = ["", "dez", "vinte", "trinta", "quarenta", "cinquenta", "sessenta", "setenta"]
    
    # Mapeia números de 1 a 75
    for i in range(1, 76):
        if i < 10: word = units[i]
        elif i < 20: word = teens[i-10]
        else:
            ten, unit = divmod(i, 10)
            if unit == 0: word = tens[ten]
            else: word = f"{tens[ten]} e {units[unit]}"
        word_map[word] = i
        # Adiciona variações comuns (ex: "vinte cinco" em vez de "vinte e cinco")
        word_map[word.replace(" e ", " ")] = i

    # Adiciona letras do bingo
    letters = {'b': 'bê', 'i': 'i', 'n': 'ene', 'g': 'gê', 'o': 'o'}
    for key, name in letters.items():
        word_map[name] = key

    return word_map

RECOGNITION_MAP = build_recognition_dictionary()


class BigScreenWindow(Toplevel):
    # (Esta classe não muda, é a mesma da versão anterior)
    def __init__(self, master):
        super().__init__(master)
        self.title("Telão do Bingo")
        self.attributes('-fullscreen', True)
        self.configure(bg=COLOR_BACKGROUND)
        try:
            logo_path = resource_path("parish_logo.png")
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
        self.geometry("450x450") # Um pouco mais alto para o status da voz
        
        self.configure(fg_color=COLOR_BACKGROUND)
        self.called_numbers = set()
        
        # Atributos para reconhecimento de voz
        self.recognizer = None
        self.microphone = None
        self.is_listening = False
        self.stop_listening_callback = None

        ctk.CTkLabel(self, text="Controle do Sorteio", font=("Arial", 22, "bold"), text_color=COLOR_CURRENT_NUM_FG).pack(pady=10)
        
        # Botão de controle do microfone
        self.listen_button = ctk.CTkButton(self, text="▶️ Iniciar Reconhecimento de Voz", command=self.toggle_listening, height=40)
        self.listen_button.pack(pady=10)
        
        # Status do que foi ouvido
        status_frame = ctk.CTkFrame(self, fg_color="transparent")
        status_frame.pack(pady=5)
        ctk.CTkLabel(status_frame, text="Ouvido:").pack(side="left")
        self.last_heard_text_label = ctk.CTkLabel(status_frame, text="...", font=("Arial", 12, "italic"), text_color="#64748B")
        self.last_heard_text_label.pack(side="left", padx=5)

        # Número interpretado
        interpret_frame = ctk.CTkFrame(self, fg_color="transparent")
        interpret_frame.pack(pady=5)
        ctk.CTkLabel(interpret_frame, text="Número Interpretado:").pack(side="left")
        self.interpreted_number_label = ctk.CTkLabel(interpret_frame, text="--", font=("Arial", 16, "bold"))
        self.interpreted_number_label.pack(side="left", padx=5)

        # Correção manual
        manual_frame = ctk.CTkFrame(self, fg_color="transparent")
        manual_frame.pack(pady=10)
        ctk.CTkLabel(manual_frame, text="Correção Manual:").grid(row=0, column=0, padx=5)
        self.manual_entry = ctk.CTkEntry(manual_frame, width=80, font=("Arial", 16, "bold"), justify="center")
        self.manual_entry.grid(row=0, column=1, padx=5)
        self.manual_entry.bind("<Return>", self.confirm_manual_number)
        ctk.CTkButton(manual_frame, text="Anunciar", command=self.confirm_manual_number, fg_color=COLOR_HEADER_BG, hover_color="#8c1c1c").grid(row=0, column=2, padx=5)

        self.clear_button = ctk.CTkButton(self, text="Limpar Telão e Reiniciar Jogo", command=self.clear_all, fg_color="#64748B", hover_color="#475569")
        self.clear_button.pack(pady=10)

        # Rodapé
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.pack(side="bottom", fill="x", pady=(5, 10))
        try:
            logo_path = resource_path("parish_logo.png")
            logo_image = ctk.CTkImage(Image.open(logo_path), size=(40, 50))
            logo_label = ctk.CTkLabel(footer_frame, image=logo_image, text="")
            logo_label.pack()
        except Exception as e:
            print(f"Erro ao carregar a logo no painel: {e}")
        signature_label = ctk.CTkLabel(footer_frame, text="por Victor Manuel", font=("Arial", 8), text_color="#666666")
        signature_label.pack()

        self.big_screen = BigScreenWindow(self)
        self.manual_entry.focus()
        
        self.initialize_audio()

    def initialize_audio(self):
        """Prepara os objetos de áudio."""
        try:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
        except Exception as e:
            print(f"Erro ao inicializar áudio: {e}")
            self.listen_button.configure(state="disabled", text="Erro de Microfone")

    def find_number_in_text(self, text):
        text = text.lower().strip()
        # Procura por números por extenso
        for word, number in RECOGNITION_MAP.items():
            if re.search(r'\b' + re.escape(word) + r'\b', text):
                return number
        # Procura por dígitos numéricos
        nums = re.findall(r'\d+', text)
        if nums:
            try:
                num = int("".join(nums))
                if 1 <= num <= 75: return num
            except ValueError: pass
        return None

    def process_new_number(self, number):
        if number and 1 <= number <= 75:
            self.big_screen.animate_number(number)
            if number not in self.called_numbers:
                self.called_numbers.add(number)
                self.big_screen.update_board(number)
                print(f"Anunciando número: {number}")
            else:
                print(f"Número {number} já foi sorteado (re-anunciando).")
        else:
            print(f"Número inválido processado: {number}")

    def confirm_manual_number(self, event=None):
        try:
            num = int(self.manual_entry.get())
            self.interpreted_number_label.configure(text=str(num))
            self.process_new_number(num)
            self.manual_entry.delete(0, 'end')
        except (ValueError, TypeError):
            print("Entrada manual inválida.")
            self.manual_entry.delete(0, 'end')

    def clear_all(self):
        self.called_numbers.clear()
        self.big_screen.clear_board()
        self.interpreted_number_label.configure(text="--")
        self.last_heard_text_label.configure(text="...")
        print("Telão limpo. Novo jogo iniciado.")

    def toggle_listening(self):
        if not self.recognizer or not self.microphone:
            print("Dispositivos de áudio não inicializados.")
            return

        if self.is_listening:
            self.is_listening = False
            self.listen_button.configure(text="▶️ Iniciar Reconhecimento de Voz")
            if self.stop_listening_callback:
                self.stop_listening_callback(wait_for_stop=False)
            print("Reconhecimento parado.")
        else:
            self.is_listening = True
            self.listen_button.configure(text="⏸️ Parar Reconhecimento")
            # Inicia uma thread separada para a calibração, para não travar a UI
            threading.Thread(target=self.start_background_listening).start()

    def start_background_listening(self):
        print("Calibrando para ruído ambiente...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Calibração concluída. Ouvindo em segundo plano...")
        
        # Inicia o reconhecimento em background
        # Usar model="model" instrui o SpeechRecognition a usar o Vosk com a pasta local
        self.stop_listening_callback = self.recognizer.listen_in_background(
            self.microphone, self.audio_callback, phrase_time_limit=4
        )

    def audio_callback(self, recognizer, audio):
        if not self.is_listening: return
        try:
            # A biblioteca agora usa o Vosk por trás dos panos
            result_json = recognizer.recognize_vosk(audio, language='pt')
            result_dict = json.loads(result_json)
            heard_text = result_dict.get("text", "")
            
            if heard_text:
                print(f"Vosk ouviu: '{heard_text}'")
                self.after(0, self.last_heard_text_label.configure, {"text": f'"{heard_text}"'})
                
                number = self.find_number_in_text(heard_text)
                if number:
                    self.after(0, self.interpreted_number_label.configure, {"text": str(number)})
                    self.after(0, self.process_new_number, number)
                else:
                    self.after(0, self.interpreted_number_label.configure, {"text": "--"})

        except sr.UnknownValueError:
            print("Vosk não conseguiu entender o áudio.")
        except sr.RequestError as e:
            print(f"Erro no serviço Vosk; {e}")

if __name__ == "__main__":
    app = App()
    app.mainloop()