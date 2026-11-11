# brutallOS

<p align="center">
  <strong>Tá tudo na tela. Vem que é livre!</strong><br>
  Linux + KDE Plasma 6 · Bru · Raio · Strikerzinho &amp; Friends
</p>

<p align="center">
  <a href="CONTRIBUTING.md"><strong>Quero contribuir</strong></a> ·
  <a href="https://github.com/leonardobluestriker/brutallos/issues/new/choose">Propor uma ideia</a> ·
  <a href="docs/interface-colors.md">Ver a interface</a> ·
  <a href="docs/product-direction.md">Conhecer a proposta</a>
</p>

O **brutallOS é uma distro brasileira em construção**, feita pra ser amigável e vívida. Pra quem quer usar Linux de forma criativa, gamer, hacker ou simplesmente casual: abrir e-mail, mexer em documentos e acessar a internet com segurança e privacidade.

A proposta é respeitar quem está usando o computador: sem telemetria, adware ou software empurrado goela abaixo por padrão. Né, Co-piloto… Segurança e privacidade fazem parte do que queremos construir, junto com atualizações e escolhas claras sobre o que entra no sistema.

**O protótipo foi, sim, vibe-codado. Mas eu quero humanidade.** Acredito num Linux fácil de instalar e usar, com a familiaridade que tanta gente encontra no Windows. Não quero que ninguém sofra com centenas de comandos no terminal, `sudo su`, `apt`, enfim, “tomando no cu” pra conseguir abrir um programa. É clicar e abrir, sem frescura.

Ok, com uma frescurinha ou outra no tema.

Se quiserem, eu faço um completamente dark, em tons de cinza e sem cores vibrantes. Abraço, Jean, meu ex-chefe que **ODIOU** um dashboard neobrutalista que eu fiz! Nunca me esquecerei.

Quero que **Strikerzinho e seus amigos sejam a cara do sistema**. Que cada pessoa encontre seu jeito de usar: ousado como o Strikerzinho; com potência total igual ao Thunder quando treina e joga; ou simplesmente leve, sutil e inteligente como a Luna, um amorzinho de personagem.

Janelas arredondadas, dock inspirada no macOS, atalhos e controles familiares ao Windows, temas com personalidade e ferramentas próprias. Esse é o caminho. E tem espaço pra você ajudar a dar forma a tudo isso.

![Desktop real do brutallOS com a interface Purple Luna](docs/screenshots/interface-colors/luna-interface-dark.png)

*Captura real do desktop completo no laboratório Debian 13 / Plasma 6.3.6. Projeto em desenvolvimento: os protótipos estão disponíveis neste repositório; a ISO instalável é uma etapa futura.*

## Bora colocar mais gente nessa história?

Quero gente comigo nessa: **código, ilustrações, design, testes, documentação e tudo mais**. Não precisa chegar sabendo de tudo nem trazendo uma entrega gigante. Uma correção pequena, um desenho, um teste bem explicado ou uma ideia de acessibilidade já contam.

Não quero depender 100% de IA. Ela pode ajudar, claro. Quero também o olhar de quem programa, desenha, joga, testa, encontra um problema e fala “isso aqui podia ser melhor”. Gente criando, revisando e colocando um pouco de si no brutallOS.

| Sua área | Onde você pode ajudar |
| --- | --- |
| Desenvolvimento | Python, Qt/QML, Plasma, KWin, Wayland, configurações e Striker Tools |
| Ilustração e personagens | Artes do Strikerzinho, Thunder e Luna, wallpapers e materiais do projeto |
| Design e experiência | Temas, ícones, tipografia, animações, usabilidade e acessibilidade |
| Testes | Hardware real, jogos, monitores, escala, teclado e relatos de problemas |
| Documentação e tradução | Guias para iniciantes, revisão de textos e novos idiomas |
| Áudio e outras ideias | Sons do sistema e propostas que ajudem a formar a identidade do brutallOS |

> **Em breve eu solto as style sheets do Strikerzinho, do Thunder e da Luna!** Vai ter referência pra quem quiser desenhar essa turma e ajudar a trazer os personagens pro sistema. Enquanto isso, já dá pra trocar ideias e conhecer as artes originais do repositório.

**[Veja como contribuir](CONTRIBUTING.md)** ou **[abra uma proposta de colaboração](https://github.com/leonardobluestriker/brutallos/issues/new/choose)** contando o que você quer fazer. Tá começando agora? Vem também. E, se conhecer alguém que curte Linux, programação ou arte, manda o projeto pra essa pessoa.

## O que já está funcionando

**Entrega atual:** destaque ajustável, cor automática por tema e fundos/molduras coloridos ou neutros, em modo claro/escuro. Purple Luna usa roxo. [Guia, validação e capturas completas](docs/interface-colors.md).

O [launcher próprio conectado à dock e os nove wallpapers originais](docs/launcher-and-wallpapers.md) continuam disponíveis com backup/desfazer. A decoração Bru mantém o sinaleiro nativo Aurorae à esquerda.

Experiência desktop sobre Linux, KDE Plasma 6, KWin e Aurorae. A distribuição própria é uma etapa posterior.

A referência técnica é [design-4.md](design-4.md), complementada pela [direção atual do produto](docs/product-direction.md). A sequência atual informada pelo projeto prevalece sobre a tarefa histórica de Fase 1 no final desse documento: **Welcome → painel superior → dock → launcher → configurações → Striker Tools**.

**Laboratório cloud executado:** Debian 13, Plasma/KWin 6.3.6 e Qt 6.8.2, com 40 testes automatizados aprovados e validação das cores nativas em X11/Wayland. Etapas anteriores validaram launcher/dock, aplicação/reversão dos nove wallpapers e duas saídas Wayland; escala 200% também foi exercitada antes. [Relatório atual](docs/interface-colors.md) e [histórico do laboratório](docs/cloud-lab-report.md). As capturas atuais usam a decoração Bru; as primeiras históricas usam Breeze.

## Onde queremos chegar

- Refinar painel, dock e launcher, incluindo a integração com Wayland.
- Completar os estilos visuais de Bru, Raio e Strikerzinho & Friends.
- Ampliar a Central de configurações e as Striker Tools com dados reais de hardware.
- Medir desempenho, uso de RAM, compatibilidade com jogos e autonomia.
- Integrar os aplicativos ArtCraft disponíveis para Linux.
- Preparar instalação, atualizações e uma futura distribuição própria, com backup e reversão.

Você pode ajudar a transformar qualquer uma dessas frentes em uma entrega concreta. O [guia de contribuição](CONTRIBUTING.md) indica os arquivos e os primeiros passos para cada área.

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
scripts/brutall-center --launcher
scripts/brutall-dock plan --offline
```

A dock usa o gerenciador de tarefas nativo, com agrupamento e seletor de janelas, além de backup/reversão seletiva. A central e os layouts foram exercitados no laboratório gráfico cloud; os limites estão no relatório. Perfis Gamer/Economia e benchmarks são etapas futuras.

O [registro e conexão do launcher próprio](docs/launcher-and-wallpapers.md) são opcionais e reversíveis. Sua janela lista os apps instalados, fecha com Escape e encerra após solicitar a abertura de um app. Em Wayland, ainda aparece também como tarefa enquanto aberta; esse detalhe da integração com o shell está pendente.

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

O Welcome salva preferências; a **Central** oferece os comandos explícitos de aplicação de wallpaper e aparência Bru. O Welcome não instala ArtCraft nem aplica painéis ou desktops virtuais. Não há autostart instalado. A seleção de espaço continua sendo uma preferência, não um desktop virtual já criado.

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

O código da decoração previamente validada pelo projeto não veio no anexo nem no repositório inicial. A [decoração Bru deste checkout](docs/bru-appearance.md) é uma implementação nova, com testes próprios no laboratório. Raio e Strikerzinho & Friends já têm seus wallpapers selecionáveis; seus estilos globais completos continuam pendentes.
