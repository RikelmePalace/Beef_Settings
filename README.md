# 🛠️ Beef Settings - Central de Utilitários

![HTML](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=ffdd54)

Uma aplicação web simples, rápida e prática desenvolvida em **Python (Flask)** para resolver tarefas do dia a dia:
* 🖼️ **Converter Imagens em PDF**
* 📄 **Mesclar Múltiplos Arquivos PDF**
* 🎵 **Baixar Áudio (MP3) do YouTube**

---

## 🚀 Como Usar no Seu Computador

Siga as instruções passo a passo abaixo para instalar e rodar a aplicação na sua máquina:

### 📌 Pré-requisitos
Antes de começar, certifique-se de ter em seu computador:
1. **[Python](https://www.python.org/downloads/)** (versão 3.8 ou superior).
2. **[Git](https://git-scm.com/downloads)** (opcional, para clonar o repositório).

---

### 📦 Passo 1: Baixar o Projeto
Baixe os arquivos deste repositório para o seu computador (ou clone via terminal):
```bash
git clone [https://github.com/seu-usuario/seu-repositorio.git](https://github.com/seu-usuario/seu-repositorio.git)
cd seu-repositorio
```

---

### 🎬 Passo 2: Baixar os Arquivos do FFmpeg (Necessário para MP3)
Para a função de baixar músicas em MP3 funcionar corretamente, você precisa ter os executáveis do **FFmpeg**:

1. Baixe o pacote comprimido do FFmpeg para Windows (pode usar [este link direto do gyan.dev](https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip)).
2. Abra o arquivo `.zip` baixado e entre na pasta `bin`.
3. Copie os arquivos **`ffmpeg.exe`** e **`ffprobe.exe`**.
4. Cole esses dois arquivos **diretamente na pasta raiz do projeto** (junto com o arquivo `app.py`).

---

### ▶️ Passo 3: Iniciar a Aplicação
Abra o **Terminal** (ou **Prompt de Comando / PowerShell**) e rode o comando:

```bash
python app.py
```

Antes de iniciar o servidor, o programa verifica o `requirements.txt`. Se alguma
biblioteca estiver ausente ou com uma versão incompatível, ela será instalada
automaticamente no mesmo Python usado para executar o comando.

Se preferir instalar manualmente, ou se for iniciar a aplicação com Gunicorn, execute:

```bash
python -m pip install -r requirements.txt
```

Se a instalação automática falhar, confira as mensagens do terminal, sua conexão com
a internet e as permissões do ambiente Python.

---

### 🌐 Passo 4: Acessar no Navegador
Abra o seu navegador de internet (Chrome, Edge, Firefox, etc.) e acesse:

👉 **[http://localhost:5000](http://localhost:5000)** (ou `http://127.0.0.1:5000`)

---

## 📂 Onde os Arquivos São Salvos?

Para sua comodidade, todos os arquivos gerados (PDFs convertidos, PDFs mesclados e MP3s) são salvos automaticamente na pasta padrão do seu sistema:
* 📁 **Downloads** (`/Usuários/seu_nome/Downloads`)

---

## 🛠️ Tecnologias Utilizadas

* **[Python 3](https://www.python.org/)** — Linguagem base
* **[Flask](https://flask.palletsprojects.com/)** — Framework web
* **[Pillow (PIL)](https://pillow.readthedocs.io/)** — Conversão de imagens
* **[pypdf](https://pypdf.readthedocs.io/)** — Mesclagem de PDFs
* **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** — Download de áudios do YouTube
* **[FFmpeg](https://ffmpeg.org/)** — Processamento e conversão de áudio

---

## 📝 Licença

Este projeto é livre para uso pessoal e modificações!
