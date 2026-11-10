# Dock e Central brutallOS

**Atualização:** foram executados testes gráficos X11/Wayland em cloud, com capturas do desktop inteiro. Consulte [o relatório de integração](cloud-lab-report.md) para os resultados atuais. A central aceita `systemsettings` como alternativa a `kcmshell6`, conforme disponibilidade no Debian.

## Executar a central

Com o ambiente virtual preparado conforme o README:

```sh
scripts/brutall-center
```

O app nativo Qt 6/QML reúne quatro páginas com navegação por teclado, aparência clara/escura por sessão, superfícies arredondadas e decoração gerenciada pelo KWin. Não instala atalhos, não grava preferências do desktop e não exige administrador.

### Aplicativos

O launcher autônomo lê arquivos `.desktop` de `XDG_DATA_HOME` e `XDG_DATA_DIRS`, respeita precedência, Hidden, NoDisplay, OnlyShowIn, NotShowIn e TryExec. Busca nome, descrição e categorias. Enter na busca solicita abrir o primeiro resultado; Escape limpa o texto. Botões usam Tab e Space. Não há execução de texto de busca como comando shell: a abertura passa por `gio launch` com o caminho da entrada já descoberta.

É a primeira interface própria do launcher, com lista e busca; ainda não é um plasmoid substituto do Kickoff. Não tem favoritos/recentes persistentes nem atualização automática do catálogo enquanto estiver aberto. Reabrir refaz a descoberta. Se GIO não estiver disponível, as ações de abrir aplicativos ficam desabilitadas. Os nomes ArtCraft aparecem no launcher somente quando os aplicativos estão instalados. Ícones de apps e integração do launcher autoral na dock ficam para refinamento.

### Configurações

O console tem atalhos reais para tela, som, rede, energia, data/hora, teclado e Bluetooth. Consulta `kcmshell6 --list`, ou `systemsettings --list` quando o primeiro não está disponível, e só habilita módulos disponíveis. A edição ocorre nas interfaces nativas do KDE, com suas permissões e confirmações; a central não reescreve configurações do sistema. Mudanças feitas manualmente nesses módulos não são cobertas pelo backup dos painéis. Identidade abre o Welcome existente e mantém o mecanismo de backup/reversão das preferências dele.

### Striker Tools: monitoramento inicial

- CPU: porcentagem calculada pela diferença entre amostras de `/proc/stat`.
- RAM: MemTotal menos MemAvailable de `/proc/meminfo`, em GiB.
- Disco: capacidade e ocupação do filesystem `/`; não é benchmark nem medição de saúde do SSD.
- Rede: diferença de contadores por interface em `/proc/net/dev`, excluindo loopback. Soma interfaces, inclusive virtuais; pode contar tráfego encaminhado mais de uma vez. Não é teste de velocidade da internet.
- Temperaturas: canais acessíveis em `/sys/class/hwmon`, com nomes dos drivers/sensores.
- GPU: `gpu_busy_percent` via sysfs quando o driver expõe esse contador. Drivers NVIDIA/Intel que não oferecem esse arquivo aparecem como indisponíveis; nenhum dado é inventado.

A coleta ocorre a cada 2 segundos apenas na página Striker, parando ao mudar de página ou minimizar. Não há daemon de monitoramento. Em contêineres, `/proc` pode refletir o host. Não são apresentados números de economia de RAM ou ganho de desempenho sem medições.

Perfis Gamer/Economia, undervolt e benchmarks ainda não estão implementados. Não há botões simulando essas ações. A entrega não congela processos nem modifica clocks, drivers, prioridade, energia ou discos.

## Dock nativa

```sh
scripts/brutall-dock plan --offline
```

Na VM Plasma 6.3+:

```sh
scripts/brutall-dock plan --screen 0
scripts/brutall-dock apply --screen 0 --height 56
scripts/brutall-dock status --screen 0
scripts/brutall-dock rollback --backup /caminho/exato/informado/ao/aplicar
```

A dock é um painel Plasma inferior flutuante, centralizado e com largura ajustada ao conteúdo. Usa Kickoff e **Icon-only Task Manager**. Agrupa por programa, une tarefas e lançadores e usa o seletor de janelas agrupadas. Mostra tarefas da tela atual e de todos os desktops virtuais. Favoritos iniciais incluem Dolphin, Firefox e Konsole quando descobertos, além dos cinco ArtCraft quando instalados com seus nomes correspondentes. O usuário pode fixar/remover favoritos pelos controles nativos do Plasma.

O layout compartilhado fica em `plasma/layouts/top-panel.js`; o wrapper usa `--layout dock` no controlador existente. A propriedade e o backup da dock são separados dos do painel superior. Diretório de backups: `${XDG_STATE_HOME:-$HOME/.local/state}/brutallos/dock/backups`. As garantias de backup antes da aplicação, falha de comunicação e reversão seletiva são as mesmas de [top-panel.md](top-panel.md).

Um painel inferior preexistente bloqueia a aplicação. Ele não é apagado nem convertido automaticamente. Antes de testar a dock, guarde seu layout e mova o painel antigo para outra borda pelo modo de edição do Plasma. Essa movimentação manual não é desfeita pela reversão da dock. Não restaure um appletsrc antigo com o Plasma em execução.

## Verificação

Resultado desta rodada: **27 testes aprovados na suíte completa**, incluindo Welcome, ativos originais, painel superior, dock, descoberta de aplicativos e central. `qmllint` da central terminou sem avisos. Nenhuma configuração de Plasma foi aplicada no executor.

Foram testados descoberta com override Hidden, métricas por diferença com arquivos de teste, ausência de sensores, busca e navegação por teclado no QML real, renderização clara/escura, pausa do timer e rejeição de IDs arbitrários de aplicativo/módulo. A dock foi testada no QJSEngine com objetos Plasma simulados: geometria, agrupamento, conflitos, reaplicação e reversão preservando o painel superior. A suíte anterior cobre o backup e os erros de transporte.

Capturas do app real em `docs/screenshots/center-launcher.png` e `center-striker.png`. Nenhuma captura da dock é apresentada como validação numa sessão real. É necessário testar na VM Plasma: aplicar/reverter, múltiplas janelas agrupadas, arrastar favoritos, múltiplos monitores, escala 200%, atalhos e abertura real dos módulos KDE e aplicativos. GIO e sensores também devem ser verificados no equipamento alvo.

O schema do gerenciador de tarefas foi consultado na tag [Plasma 6.3.6](https://github.com/KDE/plasma-desktop/blob/v6.3.6/applets/taskmanager/package/contents/config/main.xml).
