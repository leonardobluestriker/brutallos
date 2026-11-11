# Laboratório descartável Debian 13 / Plasma 6

Este laboratório usa contêiner Docker e tela X11 virtual com Xvfb. Não é uma VM com boot, kernel próprio ou GPU dedicada. Os pacotes KDE são instalados apenas na imagem do contêiner. O usuário de teste não é root e o checkout é montado somente para leitura.

Em Codex Cloud, use o CA bundle fornecido pelo ambiente, mantendo o proxy e a validação TLS:

```sh
docker build --secret id=ca_bundle,src=/etc/ssl/certs/ca-certificates.crt \
  -t brutallos-lab:debian13 lab/plasma
mkdir -p "$PWD/.test-state/plasma-lab"
docker run -d --name brutallos-plasma-lab --shm-size=512m \
  --mount "type=bind,src=$PWD,dst=/project,readonly" \
  --mount "type=bind,src=$PWD/.test-state/plasma-lab,dst=/results" \
  brutallos-lab:debian13 bash /project/lab/plasma/start.sh
```

A sessão exporta apenas as variáveis necessárias ao D-Bus e à tela no arquivo interno `/tmp/brutall-session.env`. Para testar:

```sh
docker exec brutallos-plasma-lab bash -c \
  'source /tmp/brutall-session.env; python3 /project/lab/plasma/check.py'
```

**Execute `check.py` somente neste laboratório descartável.** Ele salva a configuração inicial e remove os painéis de fábrica do contêiner como preparação de teste. Essa preparação não faz parte dos comandos de aplicação do produto. Depois verifica criação, reaplicação, reversão seletiva e persistência ao reiniciar o shell.

`capture.py` usa o root window inteiro da tela X11. As imagens incluem wallpaper, painéis, dock e janelas; não são montagens nem recortes das janelas. `launch-app.py` abre os apps reais em posições reproduzíveis.

Para X11 em outra resolução, crie outro contêiner/diretório de resultados com `-e LAB_RESOLUTION=1366x768x24`.

Para reproduzir a sessão Wayland com duas saídas, acrescente `-e LAB_SESSION=wayland -e LAB_RESOLUTION=3840x1080x24`. Os defaults são duas saídas de 1920×1080. Dentro da sessão, execute `check-wayland.py` em vez de `check.py`. A janela de cada saída nasce na origem do framebuffer hospedeiro; inspecione `xwininfo -root -tree` e posicione a segunda ao lado da primeira com `xdotool windowmove ID 1920 0` antes de capturar o panorama. O Plasma enxerga geometrias contíguas reais no protocolo Wayland, independentemente da posição dessas janelas no hospedeiro.

Para a sessão pequena Wayland: `-e LAB_SESSION=wayland -e LAB_RESOLUTION=1366x768x24 -e LAB_WIDTH=1366 -e LAB_HEIGHT=768 -e LAB_OUTPUTS=1`.

Para HiDPI real no compositor: `-e LAB_SESSION=wayland -e LAB_RESOLUTION=3840x2160x24 -e LAB_WIDTH=1920 -e LAB_HEIGHT=1080 -e LAB_OUTPUTS=1 -e LAB_SCALE=2 -e LAB_OUTPUT_SCALE=2`. O backend aninhado multiplica o tamanho físico por `LAB_SCALE`; `LAB_OUTPUT_SCALE` configura também a escala lógica no KScreen antes de iniciar o Plasma. O resultado observado foi 3840×2160 físico, 1920×1080 lógico e DPR 2. Não use apenas `QT_SCALE_FACTOR` para declarar validada a escala do compositor.

`showcase.py` produz capturas adicionais dos apps e wallpapers, sem repetir os testes de aplicação/reversão. O [relatório](../../docs/cloud-lab-report.md) distingue o que foi efetivamente validado das pendências.

## Launcher e wallpapers

Depois de criar a dock e registrar/conectar o launcher conforme o [guia](../../docs/launcher-and-wallpapers.md), execute na sessão X11:

```sh
docker exec brutallos-plasma-lab bash -c \
  'source /tmp/brutall-session.env; python3 /project/lab/plasma/test-launcher-wallpaper.py'
docker exec brutallos-plasma-lab bash -c \
  'source /tmp/brutall-session.env; python3 /project/lab/plasma/test-wallpaper-ui.py'
```

O primeiro script altera e desfaz os nove wallpapers, exercita conexão/reversão e clica no launcher real da dock. Abre Dolphin ao testar Enter. O segundo seleciona as nove prévias na Central, aplica Purple Luna, captura o desktop inteiro e desfaz pela interface. Use somente no home descartável do laboratório.

No contêiner Wayland com duas saídas, execute na respectiva sessão:

```sh
python3 /project/lab/plasma/test-wallpaper-multiscreen.py
```

Ele verifica aplicação/reversão nas duas telas e isolamento ao alterar apenas a segunda. Resultados e capturas ficam em `/results`. O [relatório desta entrega](../../docs/launcher-and-wallpapers.md) registra a tarefa extra do launcher observada no dock em Wayland.

Para [cores da interface](../../docs/interface-colors.md), execute `test-accent-ui.py` na sessão X11 do laboratório: testa prévia, HEX, fundos neutros/coloridos, aplicação nativa, persistência no launcher, claro/escuro e reversão; captura três desktops completos. `test-identity-native.py` funciona nas sessões X11 e Wayland, compara a paleta de um novo cliente Qt e os bytes restaurados. Esses testes alteram apenas o home descartável do contêiner.

Encerrar o laboratório:

```sh
docker stop brutallos-plasma-lab
docker rm brutallos-plasma-lab
```

Isso remove a sessão e o home do usuário de teste. O checkout e os resultados no bind mount são preservados. Nenhum arquivo de configuração do desktop do host é montado ou alterado.
