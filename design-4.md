# brutallOS — Design & Engineering Specification

> **Status:** projeto conceitual, implementação incremental  
> **Versão do documento:** 0.1  
> **Nome do produto:** brutallOS  
> **Proposta:** ambiente desktop Linux para criadores, desenvolvedores e uso diário, com flat design neobrutalista e ergonomia consistente.

## 1. Visão de produto

O brutallOS é inicialmente uma **experiência desktop construída sobre uma distribuição Linux existente**, e não um kernel, sistema de drivers ou distribuição independente escrita do zero. Seu objetivo é combinar a usabilidade de uma dock, barra superior, launcher e múltiplos espaços de trabalho com uma linguagem visual própria: geometria modular, cores vivas, sombras sólidas, contornos disciplinados e densidade de informação controlada.

**Princípios:**
1. **Funcionalidade antes de decoração.** Tudo o que parece um botão deve executar uma ação real.
2. **Uma ação, um controle.** Não colocar um X adicional ao lado dos controles de janela.
3. **Neobrutalismo com respiro.** Áreas amplas, poucas cores simultâneas por tela, sombras sólidas em elementos de foco, não em tudo.
4. **Compatibilidade primeiro.** Aplicativos Linux existentes continuam funcionando, mesmo quando não adotam perfeitamente a identidade visual.
5. **Acessível e configurável.** Alto contraste opcional, navegação por teclado, escala HiDPI e animação reduzida.
6. **Mudanças reversíveis.** Nunca editar arquivos do sistema sem backup e mecanismo de reversão.

### Não objetivos da primeira versão

- Criar um kernel Linux, gerenciador de pacotes, driver gráfico ou stack de áudio próprios.
- Fazer fork completo de KDE Plasma ou KWin logo no início.
- Reescrever Firefox, LibreOffice, Blender, GIMP ou Kdenlive.
- Substituir o sistema operacional do computador principal durante os primeiros testes.
- Garantir que programas GTK, Qt, Electron e aplicativos com decoração própria exibam imediatamente controles idênticos.

## 2. Base técnica recomendada

| Camada | Recomendação inicial | Responsabilidade |
|---|---|---|
| Distribuição base | Fedora KDE ou outra distro KDE estável e suportada | Pacotes, atualizações, drivers, instalação |
| Kernel | Linux fornecido pela distribuição | Hardware, processos, memória |
| Sessão gráfica | Wayland, com compatibilidade XWayland | Exibição e entrada |
| Compositor/gerenciador de janelas | KWin | Janelas, maximização, desktops virtuais, efeitos |
| Shell de desktop | KDE Plasma 6 | Painéis, widgets, área de trabalho, notificações |
| Interface dos novos apps | Qt 6 + QML / Qt Quick | Componentes de UI e aplicações próprias |
| Tema de janela | Aurorae (protótipo); KDecoration C++ se necessário | Barra de título e controles de janela |
| Tema gráfico | Plasma Style + esquema de cores + ícones | Identidade consistente |
| Pesquisa e execução | KRunner (reutilizado/estendido) | Busca de apps, arquivos e comandos |
| Integrações do sistema | APIs KDE, freedesktop.org e D-Bus | Serviços, notificações, media player, estado do sistema |
| Distribuição de apps extras | Repositórios nativos e Flatpak | Instalação de softwares |

**Nota:** conferir APIs, versões e requisitos na distribuição selecionada. Evitar exemplos de Plasma 5 em projetos Plasma 6. Recursos que dependem de patches ou APIs privadas devem ser classificados como experimentais.

## 3. O que criar, modificar ou simplesmente manter

| Elemento | Decisão | Implementação sugerida | Prioridade |
|---|---|---|---|
| Wallpaper oficial | Criar | SVGs autorais e variantes por espaço | P0 |
| Identidade, ícones e tipografia | Criar | SVGs, fontes licenciadas e tokens | P0 |
| Paleta, cores, widgets e painel | Modificar | Tema Plasma 6 e configurações | P0 |
| Controles vermelho/amarelo/verde | Modificar | Tema Aurorae/KWin, sem segundo X | P0 |
| Dock inferior | Adaptar primeiro | Painel Plasma com ícones e task manager | P0 |
| Barra superior | Adaptar primeiro | Painel Plasma com widgets e relógio | P0 |
| Espaços de trabalho | Reutilizar/ajustar | Desktops virtuais e regras KWin | P0 |
| Launcher de apps | Adaptar; depois criar UI própria | Primeiro Kickoff/KRunner; depois plasmoid QML | P1 |
| Central de controle rápido | Criar como extensão | Plasmoid QML usando serviços existentes | P1 |
| App de personalização brutallOS | Criar | Qt/QML que altera configurações permitidas | P1 |
| File manager | Reutilizar | Dolphin + tema/ícones; fork só se houver necessidade | P0 |
| Editor de texto/notas | Reutilizar; app autoral opcional | Kate/KWrite; novo app simples depois | P2 |
| Terminal | Reutilizar | Konsole + perfil de cores e fonte | P0 |
| Multimídia | Reutilizar | Apps Linux existentes + integração MPRIS | P0 |
| Monitor de sistema | Reutilizar | Plasma System Monitor, podendo usar sensores via APIs | P0 |
| Notificações | Reutilizar e tematizar | Sistema de notificações Plasma | P0 |
| Login e lock screen | Tematizar mais tarde | SDDM e lock screen compatíveis | P2 |
| Instalador e ISO própria | Não fazer no MVP | Pipeline de imagem imutável/reprodutível posteriormente | P3 |

Legenda: **P0** = indispensável ao protótipo; **P1** = MVP; **P2** = refinamento; **P3** = distribuição.

## 4. Design system

### 4.1 Paleta inicial (tokens ajustáveis)

```yaml
colors:
  ink: '#101322'
  surface: '#FFFFFF'
  surfaceMuted: '#F4F5F9'
  cobalt: '#1557FF'
  acidLime: '#DFFF00'
  pink: '#FF4FA0'
  cyan: '#3DD9F5'
  yellow: '#FFD74A'
  red: '#FF5B58'
  green: '#42D884'
  border: '#151525'
```

Evitar usar todas as cores de destaque na mesma janela. O wallpaper pode ser expressivo; os painéis de trabalho devem ser mais contidos.

### 4.2 Tipografia

- Interface: fonte sans-serif legível, preferencialmente **Inter** ou equivalente com licença de redistribuição compatível.
- Logo e títulos de marca: lettering modular/interlock **como recurso gráfico**, não em parágrafos nem campos de texto.
- Tamanhos e pesos definidos em tokens e compatíveis com escalonamento do sistema.
- Nunca sacrificar legibilidade de menus pela fidelidade à imagem conceitual.

### 4.3 Geometria e sombras

```yaml
shape:
  radiusSmall: 8
  radiusMedium: 12
  radiusLarge: 18
  borderThin: 1
  borderBold: 2
  focusBorder: 3
spacing: [4, 8, 12, 16, 24, 32]
shadow:
  raised: '4px 4px 0px #101322'
  floating: '6px 6px 0px #101322'
```

As sombras acima são **tokens visuais**, não código CSS a aplicar diretamente em QML. Implementar os equivalentes conforme o toolkit.

### 4.4 Estados obrigatórios

Cada componente interativo deve definir: normal, hover, foco do teclado, pressionado, selecionado, desabilitado e modo de alto contraste. Ícones devem ter área clicável suficiente, tooltip quando necessário e alternativa textual.

## 5. Regras de janelas: sem controles contraditórios

**O sinaleiro é o único grupo de ações de janela** nas decorações gerenciadas pelo brutallOS:

| Posição | Cor | Clique principal |
|---|---|---|
| Esquerda | Vermelho | Fechar janela |
| Centro | Amarelo | Minimizar janela |
| Direita | Verde | Alternar maximizar/restaurar |

- O verde **não deve prometer fullscreen exclusivo** se a implementação executa apenas maximização. Tela cheia é uma ação diferente e deve seguir o suporte do aplicativo/ambiente (por exemplo, atalho dedicado).
- Estados de hover e foco mostram símbolos discretos, sem adicionar um X independente à direita.
- Se a janela não suporta minimizar ou maximizar, representar o controle como desabilitado quando possível.
- Priorizar botões à esquerda, título equilibrado e área de arraste claramente definida.
- Janelas com **client-side decorations** (CSD), incluindo vários apps GTK/Electron, podem desenhar os próprios títulos. Não forçar ou prometer uniformidade universal no MVP.
- Não substituir eventos internos de fechar/minimizar/maximizar por scripts frágeis de mouse. Deixar o **KWin** executar as ações nativas.
- Construir primeiro um tema **Aurorae** para a decoração das janelas compatíveis. Migrar para KDecoration em C++ apenas se Aurorae não atender requisitos de desempenho, layout ou interação.

**Critério de aceite:** abrir vários apps Qt/KDE, testar fechar, minimizar, maximizar, restaurar, arrastar, redimensionar, alternar desktops e usar teclado; confirmar que não existem comandos duplicados na decoração controlada pelo KWin.

## 6. Shell: barra superior, dock, launcher e centro de controle

### 6.1 Barra superior

À esquerda: marca `brutallOS` e menu contextual **somente quando suportado**. À direita: rede, som, energia, data/hora e acesso a controles rápidos. Evitar menus globais falsos: aplicativos que não exportam menus não devem exibir opções fictícias.

**MVP:** painel Plasma configurado e tematizado. **Posteriormente:** widgets QML específicos para marca, indicador de workspace e área de status.

### 6.2 Dock

Dock inferior centralizada, com lançadores fixos, tarefas em execução, indicadores de foco e acesso ao launcher. Reaproveitar o task manager do Plasma para preservar execução, agrupamento, múltiplas janelas e alternância; estilizar seus componentes sem criar um segundo gerenciador de tarefas.

**Regras:** não duplicar apps quando já existem instâncias agrupadas; clique deve ativar ou iniciar conforme configuração; interação de múltiplas janelas deve oferecer um seletor.

### 6.3 Launcher

**Fase 1:** personalizar Kickoff/KRunner. **Fase 2:** plasmoid `brutall-launcher` em QML, com lista de apps, categorias, favoritos, recentes e busca.

**Fonte de dados:** entradas `.desktop` e mecanismos de lançamento/consulta disponibilizados pelo desktop; não manter um catálogo inventado ou uma lista fixa de programas. Execução segura: nada de concatenar texto do usuário em comandos shell indiscriminadamente.

### 6.4 Centro de controle

Criar `brutall-control-center` como plasmoid ou app, com atalhos para rede, áudio, Bluetooth, brilho, tema e modo não perturbe, usando serviços e permissões existentes. Valores reais devem refletir o estado do dispositivo; controles indisponíveis precisam aparecer desabilitados. Nunca armazenar credenciais Wi-Fi no próprio app.

## 7. Quatro espaços de trabalho

### 7.1 Espaço Criativo

**Apps sugeridos:** GIMP, Inkscape, Krita, Blender, Kdenlive, Audacity e gerenciador de arquivos.  
**Preset:** dock com softwares criativos, wallpaper cobalt/lime/pink, atalhos a projetos.  
**Personalização:** paleta e regras de posicionamento de janelas; não alterar automaticamente perfis de cor ou comportamento de apps profissionais.

### 7.2 Espaço Power User / Desenvolvedor

**Apps sugeridos:** Konsole, Kate ou VS Code, Git GUI, monitor de sistema, Docker/Podman conforme instalação e virtualização quando suportada.  
**Preset:** janelas em mosaico, terminal acessível, monitoramento opcional e busca rápida.  
**Segurança:** execução de comandos administrativos apenas por mecanismos normais do Linux (por exemplo, Polkit/sudo), nunca embutir permissões elevadas no shell.

### 7.3 Espaço Produtividade

**Apps sugeridos:** LibreOffice, calendário, notas, gerenciador de arquivos, e-mail e navegador.  
**Preset:** cores menos agressivas, dock focada, notificações contidas, atalhos de organização.  
**Integração:** calendários e contas são opcionais; usar padrões existentes quando possível.

### 7.4 Espaço Mídia / Uso Caseiro

**Apps sugeridos:** Firefox, VLC/Celluloid, Elisa/Haruna, visualizador de imagens e loja de aplicativos.  
**Preset:** controles de reprodução MPRIS, biblioteca de mídia e acesso a dispositivos.  
**Restrições:** não criar player de codecs próprio, nem prometer DRM de plataformas de streaming.

### Implementação dos espaços

- Inicialmente, cada espaço corresponde a um **desktop virtual e um preset de lançadores/janelas**, não a uma sessão gráfica diferente.
- Guardar preferências em arquivos de configuração de usuário; documentar conflito entre perfis e o estado global da dock.
- Definir se os espaços são apenas layouts de janelas ou se mudam tema/painéis; no MVP **não mudar todo o tema ao trocar de desktop** para evitar instabilidade e surpresa.
- Scripts do KWin podem ajudar no posicionamento de janelas quando APIs públicas suportarem o caso.

## 8. Aplicativos autorais: o que vale programar primeiro

1. **brutall-welcome** — primeira execução, tour, seleção de presets; app Qt/QML simples. Primeira criação recomendada.
2. **brutall-settings** — preferências próprias (paletas, wallpapers, dock, controles); front-end que reutiliza configurações e módulos existentes. Não refazer NetworkManager, Bluetooth ou gerenciamento de energia.
3. **brutall-launcher** — interface diferenciada para descobrir e iniciar apps; dependente do shell Plasma.
4. **brutall-control-center** — painel rápido centralizado com estado real do sistema.
5. **brutall-notes** (opcional) — notas simples, se houver uma experiência que justifique competir com apps maduros.
6. **brutall-media-hub** (opcional) — agregador local de mídia, usando serviços MPRIS e players existentes; não substituir decodificadores.

Todos os novos apps devem respeitar tema claro/escuro, teclado, tradução, escalonamento e interoperabilidade com ambientes Linux convencionais quando possível.

## 9. Estrutura de repositório sugerida

```text
brutallos/
├── README.md
├── design.md
├── LICENSES/
├── docs/
│   ├── architecture.md
│   ├── compatibility.md
│   ├── accessibility.md
│   └── release-checklist.md
├── assets/
│   ├── branding/
│   ├── wallpapers/
│   ├── icons/
│   └── fonts/                 # somente fontes redistribuíveis
├── tokens/
│   ├── colors.yaml
│   ├── typography.yaml
│   └── components.yaml
├── plasma/
│   ├── global-theme/
│   ├── plasma-style/
│   ├── colors/
│   ├── icons/
│   ├── aurorae/
│   ├── widgets/
│   │   ├── brutall-launcher/
│   │   ├── brutall-control-center/
│   │   └── brutall-workspaces/
│   └── layouts/
├── kwin/
│   ├── scripts/
│   └── rules/
├── apps/
│   ├── brutall-welcome/
│   └── brutall-settings/
├── presets/
│   ├── creative/
│   ├── developer/
│   ├── productivity/
│   └── media/
├── packaging/
│   ├── fedora/
│   └── flatpak/
├── scripts/
│   ├── check-dependencies.sh
│   ├── install-user.sh
│   ├── backup-settings.sh
│   └── restore-settings.sh
└── tests/
    ├── visual/
    ├── functional/
    └── integration/
```

**Observação:** essa estrutura é uma proposta de organização, **não** contém, por si só, instaladores prontos ou manifests validados.

## 10. Sequência de desenvolvimento

### Fase 0 — laboratório e baseline

- Criar VM com Fedora KDE ou outra distribuição Plasma adequada; registrar versões exatas de KDE Plasma, Qt, KWin e Wayland.
- Criar repositório Git e salvaguarda de configurações.
- Fazer capturas de tela do desktop padrão como referência.
- Documentar como reverter tema, decoração, painel e scripts.

**Entregável:** desktop original restaurável e documentação de ambiente.

### Fase 1 — aparência funcional (P0)

- Implementar paleta, wallpaper, ícones iniciais e estilo Plasma.
- Configurar barra superior e dock com componentes existentes.
- Desenvolver decoração Aurorae com exatamente os três botões à esquerda.
- Aplicar perfil de terminal e testar programas comuns.

**Entregável:** desktop real que parece brutallOS, com apps Linux funcionando.

### Fase 2 — experiência própria (P1)

- Criar `brutall-welcome`.
- Criar launcher QML, com apps verdadeiros.
- Criar control center integrado a estados reais.
- Criar presets dos quatro desktops virtuais.
- Criar painel de personalização.

**Entregável:** primeiro MVP utilizável diariamente em VM ou equipamento secundário.

### Fase 3 — robustez (P2)

- Testar múltiplos monitores, HiDPI, temas claro/escuro, entrada por teclado, idiomas, suspensão, login e recuperação.
- Testar apps com CSD e comportamento Wayland/XWayland.
- Fazer testes de regressão após atualizações da distribuição.
- Criar pacote instalável e mecanismo completo de rollback.

**Entregável:** release candidata do ambiente de desktop.

### Fase 4 — distribuição própria (P3)

- Somente após estabilizar os componentes, montar uma imagem instalável baseada em uma distribuição existente.
- Definir manutenção de pacotes, repositórios, assinatura de atualizações, política de segurança, suporte e licenças.
- Automatizar a construção reprodutível e testar instalações/atualizações em VMs.
- Documentar claramente que `brutallOS` é uma distribuição baseada em Linux e KDE, com atribuições correspondentes.

**Entregável:** imagem instalável versionada e mantida; não criar ISO antes de ter estratégia de atualização.

## 11. Critérios de aceite do MVP

- [ ] Inicia sessão Wayland KDE sem erro crítico.
- [ ] Barra superior, dock e wallpaper funcionam.
- [ ] Menu e launcher mostram aplicativos realmente instalados.
- [ ] Sinaleiro vermelho/amarelo/verde executa fechar/minimizar/maximizar-restaurar sem X redundante nas janelas suportadas.
- [ ] O tema mantém contraste legível e foco de teclado visível.
- [ ] Painéis e janelas funcionam em 1920×1080, 1366×768 e HiDPI.
- [ ] Os quatro espaços de trabalho podem ser acessados sem reiniciar sessão.
- [ ] Firefox, Dolphin, LibreOffice e um app GTK abrem e executam tarefas básicas.
- [ ] Central de controle não apresenta interruptores falsos.
- [ ] Instalação e desinstalação restauram preferências do usuário com segurança.
- [ ] Não exige privilégios de administrador durante a sessão normal.
- [ ] O ambiente continua utilizável se um widget autoral falhar.

## 12. Riscos e decisões pendentes

| Risco | Mitigação |
|---|---|
| Controles inconsistentes em apps com CSD | Documentar escopo; adaptar individualmente apenas quando viável |
| Atualizações do Plasma quebrarem temas antigos | Usar APIs documentadas, fixar matriz de testes e automatizar regressões |
| Dock ou launcher recriado prejudicar multitarefa | Preservar mecanismos nativos de tarefas e lançamento |
| Poluição visual | Limitar cores por janela e usar sombras só onde ajudam foco/hierarquia |
| Tema alterar configurações pessoais | Instalação opt-in, backup, uninstall e rollback |
| Branding conflitar com marcas de apps | Manter nomes/logos de terceiros conforme permissões e licenças |
| Redistribuição de fontes ou ícones | Inventário de licenças e atribuições |
| ISO própria gerar dívida de manutenção | Adiar até ter empacotamento e atualizações confiáveis |

## 13. Orientações para o Codex

**Agente: leia este `design.md` como fonte principal dos requisitos.**

1. Comece auditando a máquina/VM: distribuição, desktop, sessão, versões KDE/Qt/KWin e ferramentas instaladas.
2. Antes de editar qualquer configuração, apresente um plano com arquivos afetados, dependências e procedimento reversível.
3. Trabalhe no diretório de projeto; não altere `/usr`, `/etc`, serviços, partições, login ou pacotes globais sem aprovação explícita.
4. Implemente **uma feature vertical por vez**: código + instalação em ambiente de teste + validação + rollback.
5. Prefira configuração por usuário em `~/.local/share` e `~/.config` conforme os padrões adequados.
6. Evite APIs privadas e scripts de automação por coordenadas de tela.
7. Use recursos nativos do KWin para ações de janela, Plasma para tarefas/painéis e Qt/QML para componentes novos.
8. Não crie controles decorativos sem funcionalidade; ações sem integração devem ser omitidas ou desabilitadas.
9. Escreva README e testes manuais reproduzíveis para cada componente.
10. Não afirme compatibilidade total nem conclua uma etapa sem demonstrar o que foi testado.

### Primeira tarefa concreta para o Codex

> Analise este `design.md` e o ambiente Linux atual. Sem modificar nenhuma configuração do usuário, proponha a implementação da **Fase 1** para Plasma 6: tema de cores, wallpaper, painel superior, dock inferior e decoração Aurorae com sinaleiro à esquerda. Liste dependências, estrutura real de arquivos exigida pelas versões instaladas, passos de teste e script de reversão. Depois implemente somente o tema de cores e a decoração de janelas num diretório isolado, aguardando minha aprovação antes de instalar ou ativar.

## 14. Referências técnicas

- KDE Plasma developer documentation: https://develop.kde.org/docs/plasma/
- Plasma Style: https://develop.kde.org/docs/plasma/theme/
- Aurorae: https://develop.kde.org/docs/plasma/aurorae/
- Plasma desktop scripting: https://develop.kde.org/docs/plasma/scripting/
- Widgets QML: https://develop.kde.org/docs/plasma/widget/setup/
- KWin scripting: https://develop.kde.org/docs/plasma/kwin/
- KCM development: https://develop.kde.org/docs/features/configuration/kcm/

---

**Decisão central:** primeiro tornar o Linux existente visualmente e funcionalmente reconhecível como brutallOS; depois desenvolver apps exclusivos; por último considerar distribuí-lo como uma distro própria.
