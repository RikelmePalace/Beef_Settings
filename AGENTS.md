# AGENTS.md

## Visao geral

Beef Settings e uma aplicacao web local, em Flask, que centraliza tres utilitarios:

- conversao de uma imagem para PDF;
- mesclagem de dois ou mais PDFs;
- download do audio de um video do YouTube em MP3.

A interface e servida pelo proprio Flask e todo arquivo gerado e gravado diretamente
na pasta `Downloads` do usuario que executa o processo. Nao ha banco de dados, login,
fila de tarefas ou armazenamento no servidor alem dos arquivos finais.

## Estrutura do projeto

- `app.py`: aplicacao Flask, rotas HTTP e integracoes com Pillow, pypdf e yt-dlp.
- `dependencias.py`: bootstrap que valida e instala os requisitos na execucao direta.
- `templates/index.html`: pagina unica, formularios e JavaScript que chama a API.
- `static/style.css`: layout responsivo simples e tema escuro.
- `requirements.txt`: dependencias Python.
- `README.md`: instrucoes de instalacao e uso para o usuario final.

## Fluxo da aplicacao

1. `GET /` renderiza `templates/index.html`.
2. O JavaScript monta um `FormData` e faz uma requisicao `POST` para a rota adequada.
3. A rota processa o arquivo ou URL de forma sincrona.
4. O resultado e salvo em `~/Downloads`.
5. A API responde JSON no formato `{"sucesso": bool, "mensagem": str}` e a pagina
   mostra a mensagem na caixa de status.

### Contratos HTTP atuais

- `POST /api/converter-imagem`: recebe um arquivo no campo `imagem`.
- `POST /api/mesclar-pdfs`: recebe dois ou mais arquivos no campo `pdfs` e aceita
  `nome_pdf` como nome de saida opcional.
- `POST /api/baixar-mp3`: recebe a URL no campo `url`.

Ao alterar uma rota, mantenha os nomes dos campos e o formato da resposta alinhados
com o JavaScript de `templates/index.html`.

## Ambiente de desenvolvimento

Requer Python 3.8 ou superior. Para o recurso de MP3, `ffmpeg` e `ffprobe` tambem
precisam estar acessiveis ao yt-dlp; no uso atual em Windows, o README orienta colocar
os executaveis na raiz do projeto.

Configuracao recomendada no PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python app.py
```

Ao executar `python app.py`, o bootstrap verifica os pacotes e as versoes declaradas
em `requirements.txt`. Se necessario, ele executa o pip com o mesmo interpretador
antes de importar o Flask. A aplicacao fica disponivel em `http://127.0.0.1:5000`.

O bootstrap nao e executado quando `app.py` e apenas importado. Para testes, Gunicorn
ou outro servidor WSGI, instale as dependencias manualmente:

```powershell
python -m pip install -r requirements.txt
```

## Validacao de mudancas

O repositorio ainda nao possui uma suite automatizada. Antes de concluir uma mudanca:

```powershell
python -m compileall app.py
```

Depois, execute a aplicacao e valide manualmente apenas os fluxos afetados:

- uma imagem JPG ou PNG gera um PDF legivel em `Downloads`;
- dois PDFs sao unidos na ordem selecionada;
- uma URL valida do YouTube gera um MP3 quando o FFmpeg esta disponivel;
- entradas ausentes ou invalidas exibem erro compreensivel na interface;
- a troca entre as tres abas continua funcionando.
- a execucao direta instala requisitos ausentes antes de importar o Flask;
- uma falha do pip encerra o processo sem iniciar o servidor.

Se forem adicionados testes, prefira `pytest` e o test client do Flask. Isole a pasta
de saida nos testes para nunca gravar artefatos reais em `~/Downloads`.

## Convencoes para contribuicao

- Preserve os textos voltados ao usuario em portugues do Brasil.
- Mantenha as mudancas pequenas e coerentes com a estrutura atual; evite adicionar
  frameworks ou camadas sem uma necessidade concreta.
- Use nomes claros em portugues quando estiver estendendo codigo que ja segue esse
  padrao, e mantenha nomes exigidos por bibliotecas em seu formato original.
- Documente funcoes novas com docstrings e comente fluxos menos intuitivos explicando
  o motivo; evite comentarios que apenas repetem o que a linha de codigo ja diz.
- Nao versione `ffmpeg.exe`, `ffprobe.exe`, ambientes virtuais, downloads ou arquivos
  gerados durante testes.
- Nao altere silenciosamente o destino dos arquivos: hoje o comportamento publico e
  salvar em `~/Downloads`.
- Feche recursos de arquivo e objetos do pypdf mesmo quando o processamento falhar.
- Nao exponha detalhes internos ou credenciais em mensagens retornadas pela API.

## Pontos de atencao do codigo atual

Considere estes itens ao tocar nas areas relacionadas:

- `app.run(debug=True)` e adequado somente para desenvolvimento local.
- Os nomes enviados pelo cliente ainda precisam de sanitizacao robusta antes de serem
  usados como caminhos; nomes personalizados nao devem escapar de `~/Downloads`.
- Uploads nao possuem limite de tamanho nem validacao completa de tipo/conteudo.
- O processamento e sincrono; downloads e arquivos grandes bloqueiam a requisicao.
- Arquivos com o mesmo nome podem ser sobrescritos.
- Excecoes sao devolvidas diretamente ao usuario e as falhas usam, em geral, HTTP 200.
- A funcao de MP3 depende de acesso a internet, disponibilidade do YouTube, yt-dlp
  atualizado e FFmpeg instalado.
- `gunicorn` esta listado para servidores compativeis com Unix; no Windows, use o
  servidor de desenvolvimento apenas localmente ou escolha um servidor WSGI adequado.

Ao corrigir um desses pontos, atualize tambem o README e os testes correspondentes.

## Criterios de conclusao

Uma alteracao esta pronta quando:

- o codigo compila e a aplicacao inicia sem erro;
- os fluxos afetados foram testados;
- nenhum arquivo gerado ou binario foi incluido no Git;
- interface e backend continuam usando o mesmo contrato;
- README e este arquivo refletem qualquer mudanca de instalacao ou arquitetura.
