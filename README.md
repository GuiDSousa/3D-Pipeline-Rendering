# Trabalho I — Pipeline 3D (NumPy + Pygame)

Este repositório contém uma implementação didática de um pipeline 3D em software (sem OpenGL) usando NumPy para a matemática e Pygame para exibição.

Funcionalidades principais
- Criação e manipulação de objetos 3D (cubo, pirâmide, esfera e prisma hexagonal)
- Transformações geométricas 4x4 (translação, rotação, escala, cisalhamento)
- Câmera virtual com projeção perspectiva
- Rotações por quatérnios para animações suaves
- Renderização wireframe feita em software (pygame.draw.line)

Requisitos
- Python 3.8+ (recomendado 3.10/3.11)
- pip disponível (ou use o `python -m pip`)

Instalação (modo simples)
1. Abra um terminal na pasta do projeto (onde estão os arquivos `.py`).
2. Instale as dependências:

```powershell
python -m pip install --user -r requirements.txt
```

Instalação recomendada (venv isolado)
1. Criar e ativar um virtualenv:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # PowerShell
# ou .\.venv\Scripts\activate.bat para cmd.exe
```
2. Instalar dependências no venv:

```powershell
python -m pip install -r requirements.txt
```

Executando a demo

```powershell
python main.py
```

Observações para Windows/Conda
- Se você usa Conda e o `pip` não existir no PATH, pode ativar o ambiente Conda ou usar o executável Python local:

```powershell
"C:/caminho/para/python.exe" -m pip install -r requirements.txt
"C:/caminho/para/python.exe" main.py
```
- Para criar um ambiente Conda:

```powershell
conda create -n gfx python=3.11 numpy pygame
conda activate gfx
python main.py
```

Estrutura de arquivos
- `main.py` — demo e loop principal (Pygame)
- `transformacoes.py` — matrizes 4x4 (translacao, escala, rotacao, cisalhamento)
- `Quaternion.py` — classe Quaternion e utilitários
- `camera.py` — camera, view e projection matrices
- `objeto3d.py` — classe Objeto3D (modelo, transformações, orientação por quatérnio)
- `renderizador.py` — renderer wireframe em software
- `formas.py` — geradores de formas (cubo, pirâmide, esfera, prisma)
- `requirements.txt` — dependências: numpy, pygame

Controles
- Feche a janela ou pressione o botão de fechar para sair.

Problemas comuns
- Erro "pip não é reconhecido": execute `python -m pip ...` ou crie/ative um virtualenv.
- Erros de instalação do Pygame: verifique compatibilidade do Python (usar 3.10/3.11 geralmente evita builds locais).

Sugestões futuras (opcional)
- Adicionar controles de câmera (teclado + mouse).
- Implementar rasterização de faces com Z-buffer em software.
- Exportar imagens/framebuffers.

Licença
- Use livremente para fins acadêmicos. Cite o autor original deste trabalho quando reutilizar o código.

---

Se quiser, crio também um `run.bat` para iniciar por duplo-clique ou um `README_pt_BR.md` com mais imagens e exemplos de saída.