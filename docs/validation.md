# Validação do brutall-welcome

**Atualização:** o projeto agora tem 28 testes aprovados no Debian/Qt alvo e integração gráfica em cloud. Consulte [o relatório atual](cloud-lab-report.md). O restante deste documento registra o baseline e o roteiro da entrega inicial do Welcome.

## Ambiente desta entrega

- Host: Debian GNU/Linux 13.6 (trixie).
- Dependência local: PySide6 6.8.3 / Qt 6.8.3 em `.venv`.
- Renderização automatizada: plataforma Qt `offscreen`, backend Quick `software`.
- Plasma, KWin e sessão Wayland não estão disponíveis neste executor.
- Nenhum pacote global, tema, serviço ou configuração do desktop foi instalado/alterado.

O baseline de integração informado pelo projeto é Debian 13, Plasma 6.3.6 e KWin 6.3.6. Não confundir esse baseline com os testes efetivamente executados aqui.

## Testes automatizados

`test_preferences.py`: leitura sem criar arquivos, primeira gravação reversível, restauração exata de conteúdo anterior inválido, conflito de alteração externa, segunda gravação e rejeição de seleções inválidas.

`test_welcome.py`: carrega o QML real; navega com teclado e mouse QtTest; carrega as nove imagens; seleciona tema, variante e preset; salva; reabre com os valores gravados; desfaz pela UI; renderiza todas as etapas em claro/escuro. Capturas reproduzíveis em `docs/screenshots/`. O teste não instala nem aplica preferências do Plasma.

`test_assets.py`: confere os hashes de todos os PNGs e o inventário do catálogo.

Resultado nesta entrega: **8 testes aprovados**, `qmllint` sem avisos e teste Qt de onboarding repetido com `QT_SCALE_FACTOR=2` aprovado. Todas as cinco etapas foram renderizadas em claro/escuro a 1000×720, 1366×768 e 1920×1080. Isso verifica a renderização Qt; o roteiro abaixo continua necessário para avaliar o uso real no Plasma. O executor emite uma mensagem de cache de fontes sem diretório gravável; ela não impediu a renderização ou os testes.

## Roteiro manual na VM Plasma 6.3.6

1. Executar com `--config-dir "$PWD/.test-state/vm"`. Anotar versões de Qt, Plasma, KWin e tipo de sessão.
2. Percorrer o tour. Fechar antes de salvar: não deve existir `welcome.json`.
3. Abrir novamente, escolher cada um dos nove wallpapers e conferir nomes, cores e proporção com os originais. Conferir claro/escuro/do sistema e alto contraste.
4. Percorrer o fluxo com Tab, Shift+Tab, Space e Enter. Confirmar foco visível e acesso por rolagem. Avaliar com leitor de tela real; a presença de nomes acessíveis não substitui essa validação.
5. Repetir em 1366×768, 1920×1080 e escala 200%, inclusive em múltiplos monitores. Não deve haver controles essenciais inacessíveis.
6. Escolher um preset, revisar e salvar. Reabrir: as seleções devem persistir. Confirmar que wallpaper, dock, painéis e desktops virtuais continuam iguais aos anteriores.
7. Desfazer. A primeira gravação deve ser removida; havendo conteúdo anterior, os bytes devem ser restaurados. Alterar manualmente o JSON após salvar: desfazer deve recusar o conflito.
8. Com a decoração Bru Aurorae já ativa, testar fechar, minimizar, maximizar/restaurar, arrastar e redimensionar. Não deve haver controles de janela desenhados pelo Welcome. Comparar com um app Qt/KDE conhecido.

Testes nesta VM, Wayland real, leitor de tela e interação com a decoração Aurorae permanecem pendentes. Não há alegação de compatibilidade integral com Plasma/KWin baseada apenas em renderização offscreen.
