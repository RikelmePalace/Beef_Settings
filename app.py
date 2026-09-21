"""Aplicação web local com utilitários para imagens, PDFs e áudio do YouTube."""

import os
import re

from dependencias import garantir_dependencias

# A instalação precisa acontecer antes dos imports do Flask, Pillow, pypdf e yt-dlp.
# A condição evita efeitos colaterais quando este módulo é importado por testes ou WSGI.
if __name__ == "__main__":
    garantir_dependencias()


from flask import Flask, jsonify, render_template, request
from PIL import Image
from pypdf import PdfWriter
from yt_dlp import YoutubeDL

# O Flask localiza automaticamente ``templates/`` e ``static/`` ao lado deste arquivo.
app = Flask(__name__)


class YouTubeDownloader:
    """Valida links do YouTube e coordena a extração de áudio com o yt-dlp."""

    def __init__(self, output_path: str):
        """Define a pasta de saída e a cria caso ela ainda não exista."""

        self.output_path = output_path
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

    def validar_url(self, url: str) -> bool:
        """Retorna True quando a URL possui um domínio conhecido do YouTube."""

        regex_youtube = r"^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+$"
        return bool(re.match(regex_youtube, url))

    def obter_configuracoes_ytdlp(self) -> dict:
        """Monta as opções que controlam o download e a conversão para MP3."""

        return {
            # Escolhe a melhor faixa de áudio disponível e evita baixar uma playlist.
            "format": "bestaudio/best",
            "outtmpl": os.path.join(self.output_path, "%(title)s.%(ext)s"),
            "restrictfilenames": True,
            "noplaylist": True,
            # O yt-dlp chama o FFmpeg após o download para criar o MP3 e seus metadados.
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "320",
                },
                {"key": "FFmpegMetadata", "add_metadata": True},
            ],
            "quiet": True,
        }

    def baixar_mp3(self, url: str):
        """Baixa uma URL e retorna uma dupla ``(sucesso, mensagem)`` para a API."""

        if not self.validar_url(url):
            return False, "URL inválida do YouTube."

        ydl_opts = self.obter_configuracoes_ytdlp()
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                titulo = info.get("title", "Áudio")
                return True, f'Música "{titulo}" baixada em Downloads!'
        except Exception as e:
            # Rede, YouTube e FFmpeg podem gerar erros diferentes. A camada web recebe
            # todos no mesmo formato para conseguir exibir a mensagem ao usuário.
            return False, f"Erro ao baixar: {str(e)}"


# Rota principal: entrega a única página da interface.
@app.route("/")
def index():
    """Renderiza a interface localizada em ``templates/index.html``."""

    return render_template("index.html")


# Rota 1: recebe uma imagem enviada pelo formulário e a transforma em PDF.
@app.route("/api/converter-imagem", methods=["POST"])
def converter_imagem():
    """Converte a imagem recebida e salva o PDF na pasta Downloads do usuário."""

    # Arquivos enviados por formulário ficam em ``request.files``, não em ``form``.
    if "imagem" not in request.files:
        return jsonify(
            {"sucesso": False, "mensagem": "Nenhuma imagem enviada."}
        )

    arquivo = request.files["imagem"]
    if arquivo.filename == "":
        return jsonify(
            {"sucesso": False, "mensagem": "Nenhum arquivo selecionado."}
        )

    try:
        # ``stream`` permite ao Pillow ler o upload sem criar um arquivo temporário.
        img = Image.open(arquivo.stream)
        # PDF trabalha com RGB; esta conversão também remove transparência de PNGs.
        img_rgb = img.convert("RGB")

        # ``expanduser("~")`` encontra a pasta do usuário em Windows, Linux ou macOS.
        pasta_downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        nome_saida = (
            os.path.splitext(arquivo.filename)[0] + "_convertido.pdf"
        )
        caminho_final = os.path.join(pasta_downloads, nome_saida)

        img_rgb.save(caminho_final)
        return jsonify(
            {
                "sucesso": True,
                "mensagem": f"Salvo em Downloads como {nome_saida}",
            }
        )
    except Exception as e:
        # A interface sempre espera JSON, inclusive quando o Pillow rejeita o arquivo.
        return jsonify({"sucesso": False, "mensagem": str(e)})


# Rota 2: combina os PDFs na mesma ordem em que chegaram no formulário.
@app.route("/api/mesclar-pdfs", methods=["POST"])
def mesclar_pdfs():
    """Une dois ou mais PDFs e salva o arquivo resultante em Downloads."""

    # ``getlist`` é necessário porque todos os PDFs usam o mesmo nome de campo.
    arquivos = request.files.getlist("pdfs")
    nome_personalizado = request.form.get("nome_pdf", "").strip()

    if not arquivos or len(arquivos) < 2:
        return jsonify(
            {
                "sucesso": False,
                "mensagem": "Selecione pelo menos 2 arquivos PDF.",
            }
        )

    if not nome_personalizado:
        nome_saida = "PDF_Mesclado.pdf"
    else:
        # Garante a extensão mesmo quando o usuário informa apenas o nome.
        nome_saida = (
            nome_personalizado
            if nome_personalizado.lower().endswith(".pdf")
            else f"{nome_personalizado}.pdf"
        )

    try:
        merger = PdfWriter()
        # A ordem do laço define a ordem das páginas no arquivo final.
        for pdf in arquivos:
            merger.append(pdf.stream)

        pasta_downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        caminho_final = os.path.join(pasta_downloads, nome_saida)

        # O ``with`` fecha o arquivo automaticamente depois da gravação.
        with open(caminho_final, "wb") as arquivo_saida:
            merger.write(arquivo_saida)
        merger.close()

        return jsonify(
            {
                "sucesso": True,
                "mensagem": f'PDFs mesclados em Downloads como "{nome_saida}"!',
            }
        )
    except Exception as e:
        # Mantém o mesmo contrato JSON quando algum PDF está inválido ou inacessível.
        return jsonify({"sucesso": False, "mensagem": str(e)})


# Rota 3: recebe somente a URL; o serviço acima cuida do download e conversão.
@app.route("/api/baixar-mp3", methods=["POST"])
def baixar_mp3():
    """Valida o formulário e delega o download ao ``YouTubeDownloader``."""

    url = request.form.get("url", "").strip()
    if not url:
        return jsonify({"sucesso": False, "mensagem": "Informe a URL do vídeo."})

    pasta_downloads = os.path.join(os.path.expanduser("~"), "Downloads")
    downloader = YouTubeDownloader(output_path=pasta_downloads)

    sucesso, mensagem = downloader.baixar_mp3(url)
    return jsonify({"sucesso": sucesso, "mensagem": mensagem})


if __name__ == "__main__":
    # O modo debug recarrega o servidor ao salvar o código; use apenas localmente.
    app.run(debug=True, port=5000)
