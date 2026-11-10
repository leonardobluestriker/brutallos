# Integração em cloud: Debian 13 / Plasma 6.3.6

**Etapa posterior:** a decoração Bru agora foi implementada e testada. Veja [aparência Bru](bru-appearance.md) e as novas capturas em `screenshots/bru-theme/`. Este relatório e suas imagens registram a etapa anterior, que usava Breeze.

Laboratório executado em 10 de novembro de 2026. Contêineres descartáveis, usuário sem privilégios, checkout somente para leitura, homes isolados, sem alterar pacotes ou configurações do desktop do host. Não é uma VM de boot nem um teste de hardware físico.

## Ambiente observado

- Debian GNU/Linux 13 (trixie), Plasma 6.3.6, KWin 6.3.6.
- Qt/PySide6 do Debian: Qt 6.8.2, PySide6 6.8.2.1.
- Sessão X11: Xvfb em 1920×1080 com KWin X11 e renderização por software.
- Sessão Wayland: KWin aninhado sobre Xvfb, duas saídas reais para o compositor, cada uma em 1920×1080. Geometrias observadas: `(0,0,1920,1080)` e `(1920,0,1920,1080)`.
- Sessão pequena: saída Wayland de 1366×768.
- Sessão HiDPI: saída física 3840×2160, área lógica 1920×1080 e `devicePixelRatio=2.0`, confirmado por um cliente Qt Wayland.

## Resultados

| Verificação | Resultado e alcance |
| --- | --- |
| Suíte automatizada no Debian/Qt alvo | **28 testes aprovados**, incluindo a correção de descoberta dos módulos de configuração |
| Aplicação do painel superior e dock | Passou na sessão Plasma real |
| Conflito com painel de fábrica | A dock recusou sobreposição, preservando o painel existente |
| Reaplicação | Retornou `unchanged`, sem duplicação |
| Backup | Criado antes das solicitações de mudança; baseline do laboratório arquivado |
| Reversão seletiva | Remoção da dock preservou o painel superior; reversão repetida retornou `absent` |
| Persistência | Após saída e reinício do plasmashell X11, os dois painéis retornaram com os mesmos IDs |
| Duas telas Wayland | Painel e dock criados por tela; reverter a dock da segunda preservou a primeira |
| Launcher | Apps reais descobertos; abrir Dolphin pelo backend do launcher produziu uma janela `Home — Dolphin` |
| Configurações | Módulos disponíveis descobertos; ação Teclado abriu `Keyboard — System Settings` |
| Teclado dos apps | Busca e navegação/foco por teclado verificadas nos testes Qt; não equivale a validar todos os atalhos globais da sessão |
| 1366×768 | Launcher renderizado na saída real do compositor, com acesso à rolagem |
| Escala 200% | Central renderizada em Wayland com DPR 2, screenshot físico completo de 3840×2160 |
| Imagens | Originais Bru, Raio e Blue Striker aplicados pelo Plasma sem edição dos PNGs |

O teste inicial de Alt+F4 via XTest não fechou a janela na sessão X11 montada manualmente. A consulta ao serviço de atalhos mostrou as teclas atuais vazias apesar de haver defaults registrados. Portanto os atalhos globais **não são declarados validados**. O laboratório não executa todo o fluxo de login/autostart de uma instalação normal; é necessário repetir essa parte numa sessão KDE completa.

## Correção encontrada pela integração

O app de configurações procurava apenas `kcmshell6`. Nesta instalação Debian, `systemsettings --list` funciona, mas `kcmshell6` não está instalado. A central agora usa `systemsettings` como alternativa e continua aceitando somente módulos conhecidos e realmente descobertos. Um teste de regressão verifica a descoberta e a abertura com argumentos separados, sem comandos shell.

O módulo Tela (`kcm_kscreen`) e Bluetooth não estão instalados nesta imagem mínima e continuam desabilitados. Som, rede, energia, data/hora e teclado foram descobertos. A abertura do módulo não demonstra que todos os serviços de hardware funcionem no contêiner.

## Ajustes do laboratório

- Inicialização do catálogo KDE com `XDG_MENU_PREFIX=plasma-` e `kbuildsycoca6`.
- Saída do shell via D-Bus Qt, pois o utilitário `kquitapp6` não está instalado nesta imagem mínima.
- Inicialização explícita do serviço de atalhos, normalmente iniciado pela sessão KDE completa.
- Cópia sem capabilities do executável KWin Wayland dentro do home descartável, para execução sem a capability de prioridade de agendamento indisponível no contêiner.
- No teste HiDPI, a escala é configurada pelo KScreen antes de iniciar o Plasma. O primeiro ensaio de mudança de escala com a cena por software já aberta deixou buffers antigos no wallpaper. As capturas finais usam uma sessão nova, com DPR correto desde a inicialização.
- Reiniciar o compositor encerra a sessão manual supervisionada. O teste de persistência concluído reiniciou o shell; não é uma validação de suspend/resume, boot ou login.

## Visual e limitações

As capturas são do desktop real inteiro, sem montagem, geração de imagens ou recorte da janela. A captura X11 inclui o root window. Nas sessões Wayland, captura o framebuffer X11 que hospeda as saídas aninhadas do compositor; o panorama mostra ambas lado a lado.

**As molduras são Breeze, não a Aurorae Bru validada pelo projeto.** O código dessa decoração e os temas Bru não vieram no anexo. O laboratório usa BreezeDark/breeze-dark como acabamento provisório, com os wallpapers originais. As imagens não demonstram os três conjuntos de temas completos nem um sinaleiro já integrado.

Rede, áudio, Bluetooth, sensores e GPU não possuem o hardware/serviços normais de uma máquina de uso diário. Indicadores indisponíveis não são inventados. Os números do Striker refletem o ambiente cloud/kernel exposto, com vários laboratórios em execução; não são uma medição de RAM mínima do brutallOS ou benchmark do computador do usuário.

Permanecem pendentes: importar os temas/decoração existentes, validar menus globais e agrupamento de múltiplas janelas em mais aplicativos, hotplug de monitores, atalhos globais, sessão completa de login, boot, suspensão, drivers, jogos e bateria em hardware/VM apropriados.

## Capturas completas

| Captura | Dimensão |
| --- | --- |
| [Desktop Bru](screenshots/full-desktop/01-desktop-bru.png) | 1920×1080 |
| [Launcher](screenshots/full-desktop/02-launcher.png) | 1920×1080 |
| [Striker Tools](screenshots/full-desktop/03-striker.png) | 1920×1080 |
| [Welcome + Blue Striker](screenshots/full-desktop/04-welcome-friends.png) | 1920×1080 |
| [Duas telas Wayland: Bru e Raio](screenshots/full-desktop/05-wayland-two-monitors.png) | 3840×1080 |
| [HiDPI 200%](screenshots/full-desktop/06-hidpi-200-percent.png) | 3840×2160 |
| [Launcher em tela menor](screenshots/full-desktop/07-small-1366x768.png) | 1366×768 |
| [Desktop Raio](screenshots/full-desktop/08-desktop-raio.png) | 1920×1080 |

Construção e reprodução: [lab/plasma](../lab/plasma/README.md). Configurações pessoais de teste, backups completos e endereços D-Bus ficam em `.test-state`, fora do Git.
