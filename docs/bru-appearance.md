# Bru: aparência e sinaleiro

**Etapas seguintes disponíveis:** [launcher e wallpapers](launcher-and-wallpapers.md) e [cores ajustáveis da interface](interface-colors.md). A paleta atual pode acompanhar cada tema ou uma cor personalizada. As capturas abaixo registram a etapa inicial da aparência Bru.

Implementação nova, criada nesta etapa. Os arquivos da decoração anteriormente validada pelo projeto não estavam no anexo; esta implementação não é apresentada como uma cópia daquela versão.

## Aparência

- Decoração **Aurorae/QML para KWin 6**, título centralizado, contorno de 2 pixels e quatro cantos de raio 18.
- Somente três controles à esquerda: vermelho fecha, amarelo minimiza e verde maximiza/restaura. Nenhum X adicional à direita.
- Ações, estados indisponíveis e mouse são fornecidos pelo `DecorationButton` nativo do KDE. Símbolos aparecem no hover/pressionado; janelas inativas e controles indisponíveis ficam atenuados.
- Paletas próprias `BruLight` e `BruDark`, com superfícies claras/escuras, cobalt e seleção lime.
- Central compacta, cartões de métricas em duas colunas, controles arredondados e página Identidade com as três prévias originais.
- Launcher com ícones reais do tema instalado, busca e filtro por categorias `.desktop`.
- Dock com tarefas à esquerda e launcher de quatro quadrados à direita, mantendo o task manager e o Kickoff nativos.
- Altura padrão do novo painel superior revisada para 32 pixels lógicos. Painéis existentes não são resetados pela reaplicação.

Arquivos: `plasma/aurorae/org.brutallos.bru`, `plasma/colors` e `assets/icons/brutall-launcher.svg`. Os nove PNGs originais permanecem intactos. Aplicar Bru não troca o wallpaper nem as escolhas do Welcome.

## Aplicação e reversão

Na central: **Identidade → Aplicar Bru claro/escuro**. O processo é assíncrono e faz backup antes das mudanças. Depois aparece **Desfazer**, válido para a última aplicação nesta execução da central. O botão “Prévia clara/escura” do cabeçalho muda somente a prévia da central.

Pelo terminal, inclusive para reverter depois de fechar a central:

```sh
scripts/brutall-appearance plan --mode light
scripts/brutall-appearance apply --mode light
scripts/brutall-appearance apply --mode dark
scripts/brutall-appearance rollback --backup /caminho/do/backup.json
```

`plan` apenas lista destinos. A aplicação exige sessão KWin 6, motor Aurorae, `kwriteconfig6`, `plasma-apply-colorscheme` e qdbus Qt 6. Não há sudo nem instalação de pacotes globais.

Os backups ficam em `${XDG_STATE_HOME:-$HOME/.local/state}/brutallos/appearance/UUID.json`, com permissão 0600, bytes e permissões anteriores. Destinos alterados:

- `${XDG_DATA_HOME:-$HOME/.local/share}/kwin/decorations/org.brutallos.bru/`: metadados e QML.
- `${XDG_DATA_HOME:-$HOME/.local/share}/color-schemes/BruLight.colors` e `BruDark.colors`.
- `${XDG_CONFIG_HOME:-$HOME/.config}/kwinrc`, `auroraerc` e `kdeglobals`.

O controlador usa lock e substituição atômica. Configurações passam pelas ferramentas nativas; o KWin é recarregado por D-Bus. Não altera login, serviços, partições, drivers ou atalhos globais.

A reversão confere todos os hashes antes de restaurar qualquer arquivo. Mudanças posteriores bloqueiam a operação para preservá-las. Arquivos antes ausentes são removidos; os anteriores recuperam bytes e permissões. Diretórios vazios podem permanecer. Arquivos de destino gerenciados por links simbólicos bloqueiam a aplicação para não quebrar esses links.

Uma falha após o backup registra `incomplete` e os hashes disponíveis ao término. O caminho permanece no resultado do comando; a central oferece desfazer quando recebeu um backup. Interrupção abrupta durante escrita pode exigir recuperar manualmente os bytes guardados. Isso não substitui um snapshot completo do sistema.

Depois de restaurar, reabra outros apps ou entre novamente para recarregar integralmente a paleta anterior.

## Testado no laboratório

Debian 13, Plasma/KWin **6.3.6**, Qt **6.8.2**, sem alterar o desktop do host:

| Teste | Resultado |
| --- | --- |
| Suíte do projeto no Debian/Qt alvo | **31 testes aprovados** |
| Carregamento Aurorae/QML real | Passou |
| Verde | Maximizou e restaurou; estados nativos conferidos |
| Amarelo | Minimizou; estado nativo `HIDDEN` conferido |
| Vermelho | Fechou a janela e encerrou o app normalmente |
| Arraste da barra de título | Moveu a janela pelo mecanismo nativo |
| Redimensionamento | Janela redimensionada sem perder a decoração |
| Aplicar escuro pela UI | Ativou a decoração/paleta e a prévia escura |
| Desfazer pela UI | Restaurou o estado anterior e a prévia clara |
| Arquivos | Bytes anteriores recuperados na integração; permissões e conflitos cobertos nos testes unitários |
| Wayland HiDPI | Nova decoração/central renderizadas em tela física 3840×2160, DPR 2 |
| Artes originais | Nove PNGs passam no SHA-256 |

Os cliques usam XTest somente para testar os controles renderizados. A implementação usa as ações nativas do KDE. `lab/plasma/test-bru.py` verifica estados reais do KWin; `test-appearance-ui.py` opera a UI da central.

Capturas do desktop completo, sem edição ou montagem, em `docs/screenshots/bru-theme/`: seis em 1920×1080 e uma HiDPI em 3840×2160.

## Limites

- Os cantos inferiores usam uma borda nativa de 18 pixels, que mantém o cliente retangular acima da curva. Não há shader ou efeito de recorte universal; janelas maximizadas ficam retas e sem essa borda inferior.
- Apps com CSD próprio, como vários GTK/Electron, podem desenhar os próprios controles.
- Raio e Strikerzinho & Friends mantêm suas artes/variantes no Welcome. As prévias não representam três temas globais completos já implementados.
- Não foram adicionados gráficos fictícios ou botões simulando Gamer/Economia. O Striker continua mostrando os dados reais disponíveis.
- Os atalhos globais continuam com a pendência do relatório anterior; esta etapa não os reconfigura.
- A dock existente precisa ser recriada pelo fluxo de backup/reversão para adotar a nova ordem. O ícone aponta para o checkout, que deve permanecer acessível enquanto não houver empacotamento.
- Ainda é necessário uso prolongado e validação em uma sessão KDE completa e hardware real.

Referências: [DecorationButton nativo](https://github.com/KDE/kwin/blob/v6.3.6/src/plugins/kdecorations/aurorae/src/qml/DecorationButton.qml), [tema QML Plastik](https://github.com/KDE/kwin/blob/v6.3.6/src/plugins/kdecorations/aurorae/themes/plastik/package/contents/ui/main.qml). O projeto importa o módulo instalado sem substituir arquivos do KDE.
