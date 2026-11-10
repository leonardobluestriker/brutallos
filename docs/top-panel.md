# Painel superior brutallOS

**Atualização:** aplicação, reversão e persistência já foram testadas no laboratório cloud Plasma 6.3.6. O relato abaixo descreve também a validação inicial; veja [o resultado da integração](cloud-lab-report.md) para o estado atual e as limitações.

Primeira implementação do shell: um painel Plasma nativo, criado pelas APIs públicas de desktop scripting. O script foi conferido contra o código do Plasma **6.3.6**. Não há plasmoid autoral, daemon adicional, polling de sensores ou dependência de PySide6 na ferramenta de aplicação.

## Composição

| Posição | Componente | Comportamento |
| --- | --- | --- |
| Esquerda | Kickoff com rótulo `brutallOS` | Abre o launcher nativo com aplicativos instalados |
| Ao lado da marca | Menu global Plasma | Mostra o menu exportado pelo aplicativo em foco; sem opções fictícias |
| Centro | Espaçador Plasma | Mantém status e relógio à direita |
| Direita | Bandeja do sistema Plasma | Rede, áudio, energia e demais indicadores disponíveis, com seus controles nativos |
| Extremidade direita | Relógio digital Plasma | Data local, hora e calendário reais |

Altura padrão: **36 pixels lógicos**, ajustável de 28 a 64. Painel de largura total, fixo no topo, opaco e sem flutuação. Usa fontes, cores, ícones e menus do **tema Plasma ativo**. Não força a cor preta da referência nem altera o tema global para consegui-la; o acabamento será refinado no Plasma Style Bru. As artes originais e a decoração Aurorae não são alteradas.

O ícone do Kickoff é o nativo do KDE acompanhado do texto brutallOS. A substituição por um ícone de marca licenciado poderá ser feita depois. A marca já é funcional; o launcher autoral continua sendo uma etapa própria. Não há atalhos para programas ArtCraft ausentes.

O menu global é omitido quando o widget não está instalado. Com o widget presente, o suporte do aplicativo determina o conteúdo exibido. Rede, volume e bateria vêm dos serviços KDE correspondentes; hardware ou serviços ausentes não são simulados. A bandeja mantém as regras nativas de visibilidade, incluindo a bateria.

## Arquivos e dependências

- `plasma/layouts/top-panel.js`: layout, inspeção, criação idempotente e remoção por identificador de propriedade.
- `scripts/brutall-top-panel`: ferramenta Python 3 padrão, com comandos `plan`, `status`, `apply` e `rollback`.
- Sessão do usuário com Plasma 6.3+ na série 6, `plasmashell`, barramento D-Bus de sessão e qdbus Qt 6 (`qdbus6`, `qdbus-qt6` ou `/usr/lib/qt6/bin/qdbus`). Em Debian, o pacote do utilitário é `qdbus-qt6`; a ferramenta não o instala.
- Widgets obrigatórios: Kickoff, espaçador, bandeja e relógio. Widgets de status e menu global são detectados antes da criação.
- O teste automatizado do JavaScript usa o QJSEngine do PySide6 já presente no ambiente de desenvolvimento.

## Plano sem alterar a sessão

No diretório raiz do projeto:

```sh
scripts/brutall-top-panel plan --offline
```

Isso mostra apenas a estrutura pretendida, sem acessar D-Bus nem criar diretórios. Na VM Plasma, a inspeção real também é somente leitura:

```sh
scripts/brutall-top-panel plan --screen 0
scripts/brutall-top-panel status --screen 0
```

`--screen` é o índice de tela do Plasma; `0` não é uma promessa de monitor primário. O plano informa a quantidade de telas, os painéis atuais, conflitos, widgets ausentes e se a criação está disponível. Não são desbloqueados widgets automaticamente.

## Aplicação e backup

Execute na VM de teste, como seu usuário normal, dentro da sessão Plasma:

```sh
scripts/brutall-top-panel apply --screen 0 --height 36
```

A criação é aditiva: **o painel inferior atual permanece** até a etapa da dock. Um painel superior de outra origem na mesma tela bloqueia a criação para evitar sobreposição. Nenhum painel é removido ou reposicionado para abrir espaço. Aplicar novamente retorna `unchanged` quando já existe um painel brutallOS nessa tela; alterações manuais nele são preservadas.

Antes de criar o painel, a ferramenta:

1. Inspeciona a sessão e verifica os componentes obrigatórios.
2. Obtém lock para serializar suas próprias operações.
3. Cria um diretório exclusivo em `${XDG_STATE_HOME:-$HOME/.local/state}/brutallos/top-panel/backups/`.
4. Copia os bytes em disco de `${XDG_CONFIG_HOME:-$HOME/.config}/plasma-org.kde.plasma.desktop-appletsrc` e `plasmashellrc`, registrando arquivos ausentes e hashes SHA-256. Esses arquivos contêm layout/applet settings e geometria do shell, respectivamente.
5. Salva o código do layout e um manifesto `prepared`, com identificador único, plano e versão do Plasma.
6. Solicita a criação via `org.kde.PlasmaShell.evaluateScript`, sem shell ou privilégios administrativos.

O caminho do backup aparece no terminal antes da solicitação de mudança. Falhar ao salvar o backup impede a aplicação. Se a comunicação cair, o manifesto fica `uncertain`: a alteração remota pode ter ocorrido. Use `status` e a reversão com esse backup.

As cópias são dos arquivos em disco durante uma sessão ativa, não um snapshot de todo o estado em memória do Plasma. A reversão normal abaixo usa a propriedade do painel, sem restaurar arquivos globais de layout. Isso evita perder alterações que o usuário fizer depois.

## Reversão

Use o caminho exato informado pela aplicação:

```sh
scripts/brutall-top-panel rollback --backup /caminho/exato/do/backup
```

Remove apenas o painel que tem a marca brutallOS **e** o identificador exclusivo daquele backup. Funciona mesmo que o painel tenha sido movido ou a tela original tenha sido desconectada. Repetir a reversão retorna `absent`. Painéis preexistentes e outros painéis brutallOS não são removidos. Personalizações posteriores no painel criado serão removidas junto com ele.

Se um widget falhar durante a criação, o próprio layout solicita a remoção do painel parcialmente criado. O backup continua disponível. A bandeja e os widgets são destruídos pelos mecanismos normais do Plasma.

As cópias brutas servem para recuperação excepcional: restaure-as **somente com a sessão Plasma encerrada**, depois de guardar também o estado atual, e volte a entrar. Nunca copie um `appletsrc` antigo sobre uma sessão em execução; o shell pode sobrescrevê-lo. Essa recuperação global não é feita automaticamente pela ferramenta.

## Validação executada e pendências

Neste executor Debian 13, Plasma/KWin e qdbus Qt 6 não estão instalados. O painel **não foi aplicado nem renderizado em uma sessão Plasma real**. Não há captura conceitual apresentada como prova de funcionamento.

Resultado: **13 testes do painel aprovados**. Eles usam o motor JavaScript Qt com objetos Plasma simulados e verificam: inspeção sem mutação, criação, ordem dos widgets, reaplicação sem duplicação, omissão de menu ausente, conflitos, widgets ausentes, sessão bloqueada, erro durante criação e reversão por proprietário após mover/desconectar a tela. Testes Python verificam o backup anterior à aplicação, preservação de bytes, falha de backup, recuperação após timeout, mensagem de erro D-Bus e plano offline sem efeitos colaterais. A suíte completa anterior também passou com os 8 testes do Welcome/ativos. Esses testes não substituem a integração com widgets KDE reais.

```sh
.venv/bin/python -m unittest discover -s tests -p test_top_panel.py -v
```

Na VM Debian 13 / Plasma 6.3.6 / KWin 6.3.6:

1. Registrar as versões e guardar uma captura do desktop original.
2. Rodar `plan`; conferir índice da tela, conflitos e widgets disponíveis.
3. Aplicar; guardar o caminho do backup e conferir a barra no topo. O painel inferior deve permanecer.
4. Abrir a marca: conferir que o Kickoff lista apps reais. Testar mouse e teclado.
5. Alternar Dolphin/Kate e um aplicativo sem menu global. Não devem aparecer menus inventados.
6. Verificar rede, áudio e energia conforme o hardware; abrir os popups e conferir o calendário/hora local.
7. Testar Bru claro/escuro já disponível na VM, 1366×768, 1920×1080, escala 200% e múltiplos monitores. Conferir legibilidade e se maximizar respeita a área reservada do painel.
8. Aplicar outra vez: não deve criar cópia nem resetar personalizações.
9. Reverter pelo backup: o painel novo deve desaparecer, preservando painel inferior e demais configurações. Repetir: deve retornar `absent`.
10. Sair e entrar novamente para verificar persistência tanto da criação quanto da reversão.

## Referências verificadas (tag v6.3.6)

- [API de painel](https://github.com/KDE/plasma-workspace/blob/v6.3.6/shell/scripting/panel.cpp): posição, tela, altura, largura, opacidade e flutuação.
- [API de containment](https://github.com/KDE/plasma-workspace/blob/v6.3.6/shell/scripting/containment.cpp): widgets e remoção.
- [Propriedades do motor](https://github.com/KDE/plasma-workspace/blob/v6.3.6/shell/scripting/scriptengine.cpp): `knownWidgetTypes`, `locked`, `screenCount`.
- [D-Bus evaluateScript](https://github.com/KDE/plasma-workspace/blob/v6.3.6/shell/shellcorona.cpp): retorno e erros.
- [Configuração do Kickoff](https://github.com/KDE/plasma-desktop/blob/v6.3.6/applets/kickoff/package/contents/config/main.xml): rótulo `menuLabel`.
- [Configuração do relógio](https://github.com/KDE/plasma-workspace/blob/v6.3.6/applets/digital-clock/package/contents/config/main.xml).
- [Configuração da bandeja](https://github.com/KDE/plasma-workspace/blob/v6.3.6/applets/systemtray/package/contents/config/main.xml).
