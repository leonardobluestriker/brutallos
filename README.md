# brutallOS

Experiência desktop sobre Linux, KDE Plasma 6, KWin e Aurorae. A distribuição própria é uma etapa posterior.

A referência técnica é [design-4.md](design-4.md), complementada pela [direção atual do produto](docs/product-direction.md). A sequência atual informada pelo projeto prevalece sobre a tarefa histórica de Fase 1 no final desse documento: **Welcome → painel superior → dock → launcher → configurações → Striker Tools**.

**Laboratório cloud executado:** Debian 13, Plasma/KWin 6.3.6 e Qt 6.8.2, com sessões X11 e Wayland, duas saídas virtuais, escala 200% e 28 testes automatizados aprovados. [Relatório e screenshots do desktop inteiro](docs/cloud-lab-report.md). A decoração/temas Bru existentes ainda precisam ser fornecidos; as capturas usam Breeze provisoriamente.

## Painel superior

Layout nativo para Plasma 6.3+: marca brutallOS com Kickoff funcional, menu global quando disponível, bandeja de status e data/hora. A aparência segue o tema Plasma ativo. A ferramenta prepara backup antes de criar o painel e oferece reversão apenas do painel criado; preserva os painéis existentes.

Inspeção sem sessão Plasma e sem alterações:

```sh
scripts/brutall-top-panel plan --offline
```

Os comandos de aplicação e reversão, dependências e roteiro para a VM estão em [Painel superior](docs/top-panel.md). A aplicação, reversão e persistência foram verificadas no laboratório Plasma real em contêiner. A validação em sessão completa de login e hardware/VM continua necessária; veja o relatório acima.

## Dock, launcher e Striker Tools

A [Central brutallOS e a dock](docs/center-and-dock.md) ampliam o protótipo. A central nativa reúne busca e abertura de apps instalados, acesso aos módulos de configuração disponíveis, integração com o Welcome e monitoramento real inicial de CPU/RAM/disco/rede/temperaturas/GPU quando acessíveis.

```sh
scripts/brutall-center
scripts/brutall-dock plan --offline
```

A dock usa o gerenciador de tarefas nativo, com agrupamento e seletor de janelas, além de backup/reversão seletiva. A central e os layouts foram exercitados no laboratório gráfico cloud; os limites estão no relatório. Perfis Gamer/Economia e benchmarks são etapas futuras.

## brutall-welcome

Primeiro app nativo, escrito em Python/PySide6 + Qt Quick/QML. Inclui tour, seleção de identidade, preset inicial, revisão, persistência e reversão. Usa a decoração nativa da janela: na VM com o tema Aurorae ativo, os controles continuam sob responsabilidade do KWin.

As nove imagens fornecidas estão em `assets/wallpapers`, sem edição ou recompressão. Há um inventário SHA-256. Os temas são **Bru**, **Raio** e **Strikerzinho & Friends**. A suíte ArtCraft padrão é **Photocraft, Filmcraft, Wordcraft, Gridcraft e Deckcraft**; são escolhas de produto, não afirmações de que os apps estão implementados ou instalados.

### Executar sem instalar no sistema

Requer Python 3.9+ com suporte a venv e Qt 6 via PySide6. Em uma sessão gráfica Linux com as bibliotecas de plataforma Qt disponíveis:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r apps/brutall-welcome/requirements.txt
scripts/brutall-welcome --config-dir "$PWD/.test-state/manual"
```

Esses comandos preparam apenas dependências locais ao projeto. Não usam sudo nem gerenciam pacotes do sistema. Se houver uma instalação compatível de PySide6 já disponível, é possível definir `WELCOME_PYTHON=/caminho/para/python`.

Sem `--config-dir`, o destino é `${XDG_CONFIG_HOME:-$HOME/.config}/brutallos`. Nada é gravado até clicar em **Salvar preferências**. Para um teste inteiramente isolado, mantenha `--config-dir`.

### O que esta entrega faz

- Apresenta o projeto e o tour, escolhe tema/variante e um dos quatro presets.
- Mostra os PNGs originais completos, preservando a proporção.
- Oferece aparência clara/escura/do sistema, alto contraste e foco por teclado.
- Salva somente `welcome.json`, com versão de esquema e indicador de onboarding concluído.
- Faz backup antes de cada gravação, escreve atomicamente e permite desfazer a última gravação.

Ainda **não aplica** wallpaper, esquema de cores, decoração, painéis ou desktops virtuais; não instala ArtCraft nem executa comandos de configuração. Não há autostart instalado. O tour identifica componentes futuros como planejados. A seleção de espaço é uma preferência para a próxima etapa, não um desktop virtual já criado.

### Reversão

No app: **Desfazer última gravação**. Pela linha de comando, use o mesmo diretório usado ao salvar:

```sh
scripts/brutall-welcome --config-dir "$PWD/.test-state/manual" --restore
```

O backup guarda os bytes anteriores exatos. Na primeira gravação, desfazer remove `welcome.json`. Se outro processo tiver alterado o arquivo depois do backup, a reversão é recusada para preservar essa alteração. A reversão tem um nível; uma nova gravação substitui o backup anterior. O arquivo de lock e o diretório podem permanecer vazios de preferências.

### Verificação

```sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/pyside6-qmllint apps/brutall-welcome/qml/Main.qml
```

Consulte [a validação e os testes manuais](docs/validation.md), [as decisões de arquitetura](docs/architecture.md) e [o inventário das imagens](assets/wallpapers/README.md).

O código dos temas Bru e da decoração já validados não veio no anexo nem estava no repositório inicial. Esta entrega não os recria nem substitui. A validação prévia em Debian 13 / Plasma 6.3.6 / KWin 6.3.6 é informação fornecida pelo projeto; o Welcome ainda precisa passar pela matriz de integração nessa VM.
