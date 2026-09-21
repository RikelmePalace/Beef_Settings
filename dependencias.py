"""Verifica e instala as dependências Python necessárias para executar o app.

Este módulo pode ser importado com segurança: a instalação só começa quando a função
``garantir_dependencias`` é chamada explicitamente pelo arquivo ``app.py``.
"""

import importlib
import subprocess
import sys
from importlib import metadata
from pathlib import Path
from typing import List


def _carregar_requisitos(caminho_requisitos: Path):
    """Lê o requirements.txt e devolve apenas os requisitos válidos neste ambiente.

    O sublinhado no começo do nome indica que esta é uma função interna do módulo.
    Ela transforma cada linha do arquivo em um objeto que sabe interpretar nomes,
    versões mínimas e marcadores de ambiente.
    """

    # Ambientes virtuais novos nem sempre possuem ``packaging`` como pacote separado.
    # Nesse caso, usamos a cópia que já acompanha o próprio pip.
    try:
        from packaging.requirements import InvalidRequirement, Requirement
    except ImportError:
        try:
            from pip._vendor.packaging.requirements import (
                InvalidRequirement,
                Requirement,
            )
        except ImportError as erro:
            raise RuntimeError(
                "Não foi possível carregar o leitor de requisitos do pip."
            ) from erro

    requisitos = []
    for numero_linha, linha in enumerate(
        caminho_requisitos.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        # Linhas vazias e comentários não representam bibliotecas instaláveis.
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue

        try:
            requisito = Requirement(linha)
        except InvalidRequirement as erro:
            raise RuntimeError(
                f"Requisito inválido na linha {numero_linha}: {linha}"
            ) from erro

        # Um marcador pode limitar o pacote a um sistema ou versão do Python.
        # Exemplo: ``colorama; sys_platform == "win32"``.
        if requisito.marker is None or requisito.marker.evaluate():
            requisitos.append(requisito)

    return requisitos


def _dependencias_pendentes(caminho_requisitos: Path) -> List[str]:
    """Lista pacotes ausentes ou instalados fora da versão solicitada.

    Os textos devolvidos são usados tanto para informar o usuário quanto para decidir
    se será necessário executar o pip.
    """

    pendentes = []
    for requisito in _carregar_requisitos(caminho_requisitos):
        try:
            # ``metadata`` consulta a distribuição instalada sem importar a biblioteca.
            versao_instalada = metadata.version(requisito.name)
        except metadata.PackageNotFoundError:
            pendentes.append(str(requisito))
            continue

        # Requisitos sem especificador aceitam qualquer versão já instalada.
        if requisito.specifier and not requisito.specifier.contains(
            versao_instalada
        ):
            pendentes.append(
                f"{requisito} (instalada: {versao_instalada})"
            )

    return pendentes


def garantir_dependencias() -> None:
    """Garante que o requirements.txt esteja atendido antes de iniciar o Flask.

    Se algo estiver ausente, executa o pip e confere novamente o ambiente. Qualquer
    falha encerra o programa com código diferente de zero para impedir que a aplicação
    inicie parcialmente configurada.
    """

    # O caminho parte deste arquivo, não da pasta atual do terminal. Assim, o usuário
    # pode executar o app.py estando em qualquer diretório.
    caminho_requisitos = Path(__file__).resolve().with_name("requirements.txt")

    if not caminho_requisitos.is_file():
        print(
            f"Erro: arquivo de dependências não encontrado: {caminho_requisitos}",
            file=sys.stderr,
        )
        raise SystemExit(1)

    print("Verificando dependências do projeto...")
    try:
        pendentes = _dependencias_pendentes(caminho_requisitos)
    except (OSError, RuntimeError, UnicodeError) as erro:
        print(f"Erro ao verificar dependências: {erro}", file=sys.stderr)
        raise SystemExit(1) from erro

    if not pendentes:
        print("Todas as dependências já estão instaladas.")
        return

    print("Dependências ausentes ou incompatíveis:")
    for dependencia in pendentes:
        print(f"  - {dependencia}")
    print("Instalando dependências. Aguarde...")
    sys.stdout.flush()

    # ``sys.executable`` aponta para o mesmo Python que abriu o app. Isso evita instalar
    # pacotes por engano em outro Python ou fora do ambiente virtual ativo.
    comando = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--disable-pip-version-check",
        "-r",
        str(caminho_requisitos),
    ]

    try:
        resultado = subprocess.run(comando, check=False)
    except OSError as erro:
        print(
            f"Erro ao iniciar o pip: {erro}\n"
            f"Execute manualmente: {sys.executable} -m pip install -r "
            f'"{caminho_requisitos}"',
            file=sys.stderr,
        )
        raise SystemExit(1) from erro

    if resultado.returncode != 0:
        print(
            "Não foi possível instalar as dependências. "
            "Verifique sua conexão, as permissões do ambiente e as mensagens acima.",
            file=sys.stderr,
        )
        raise SystemExit(resultado.returncode or 1)

    # O processo atual precisa enxergar imediatamente os pacotes recém-instalados.
    importlib.invalidate_caches()
    try:
        ainda_pendentes = _dependencias_pendentes(caminho_requisitos)
    except (OSError, RuntimeError, UnicodeError) as erro:
        print(
            f"Erro ao confirmar as dependências instaladas: {erro}",
            file=sys.stderr,
        )
        raise SystemExit(1) from erro

    if ainda_pendentes:
        print(
            "A instalação terminou, mas estes requisitos ainda não foram atendidos:",
            file=sys.stderr,
        )
        for dependencia in ainda_pendentes:
            print(f"  - {dependencia}", file=sys.stderr)
        raise SystemExit(1)

    print("Dependências instaladas com sucesso.")
