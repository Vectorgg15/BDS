# 📺 Bingo Display System (BDS)

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white)
![Status](https://img.shields.io/badge/Status-Concluído-brightgreen?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-informational?style=for-the-badge)

Um sistema de desktop prático e moderno para exibir os números sorteados de um bingo em tempo real, construído com Python e CustomTkinter, ideal para telões, TVs ou projetores.

### Sobre o Projeto

O Bingo Display System (BDS) foi desenvolvido para modernizar e organizar a exibição de bingos em eventos. O objetivo foi criar uma ferramenta com duas telas: uma para o público (o telão) e outra para o operador (o painel de controle), garantindo uma experiência fluida e profissional.

Para alcançar esse resultado, o projeto foi estruturado com:
- **Programação Orientada a Objetos (OOP):** O código é organizado em classes (`App`, `BigScreenWindow`), tornando-o limpo, reutilizável e fácil de manter.
- **Design de UI/UX:** Foco em uma interface de alto contraste e com fontes grandes, garantindo a visibilidade mesmo a longas distâncias.

---

### ✨ Principais Funcionalidades

- **Exibição em Telão Dedicada:** Uma janela otimizada para ser usada em tela cheia (`F11`), mostrando o número sorteado em destaque e a grade de números.
- **Painel de Controle Intuitivo:** Uma janela separada para o operador inserir os números sorteados e gerenciar o jogo.
- **Animação de Sorteio:** Efeito visual que simula um sorteio antes de revelar o número final, criando mais expectativa.
- **Grade de Números Inteligente:** O painel principal mostra todos os números de 1 a 75 e marca visualmente aqueles que já foram chamados.
- **Layout Clássico B-I-N-G-O:** Os números são organizados automaticamente nas colunas corretas, facilitando a conferência.
- **Gerenciamento de Jogo:** Funcionalidades para anunciar um número, re-anunciar (caso seja digitado novamente) e um botão para limpar o telão e reiniciar a partida.

---

### 🖼️ Capturas de Tela

<p align="center">
  <img src="assets/Screenshot_BDS.png" alt="Tela principal do sistema" width="700" />
</p>

---

### 🛠️ Tecnologias Utilizadas

- **Python 3.8+**
- **Tkinter:** A base para a criação de janelas nativas.
- **CustomTkinter:** Para criar os componentes modernos e elegantes da interface.
- **Pillow (PIL):** Para manipulação e exibição de imagens (logo da paróquia).

---

### 🚀 Como Executar o Projeto

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/Vectorgg15/BDS.git](https://github.com/Vectorgg15/BDS.git)
    cd BDS
    ```

2.  **Crie e ative um ambiente virtual (Recomendado):**
    ```bash
    python -m venv venv
    # No Windows
    venv\Scripts\activate
    # No macOS/Linux
    # source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute o aplicativo:**
    ```bash
    python script_telao.py
    ```

---

### 📄 Licença

Este projeto está sob a Licença MIT. Veja o arquivo [LICENSE](https://github.com/Vectorgg15/BDS/blob/main/LICENSE) para mais detalhes.

**Desenvolvido por Victor Manuel com 💙**
