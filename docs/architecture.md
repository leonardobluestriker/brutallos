# Welcome: decisões e limites

## Fonte de requisitos

`design-4.md` foi preservado integralmente. O pedido atual estabelece a ordem de implementação e acrescenta os temas e apps ArtCraft. As instruções históricas contidas no anexo não são autorização para instalar, ativar temas ou modificar o sistema.

## Arquivos e responsabilidades

| Caminho | Responsabilidade |
| --- | --- |
| `apps/brutall-welcome/main.py` | Bootstrap Qt, ligação QML e mensagens de resultado |
| `apps/brutall-welcome/qml/Main.qml` | Cinco etapas, revisão e confirmação de gravação |
| `apps/brutall-welcome/catalog.py` | IDs estáveis de temas, variantes, presets e apps ArtCraft |
| `apps/brutall-welcome/preferences.py` | Validação, escrita atômica, lock e backup/reversão |
| `assets/wallpapers/` | Nove PNGs originais e hashes |
| `scripts/brutall-welcome` | Execução a partir do checkout, sem instalação |

O frontend usa controles Qt Quick e a decoração padrão. Não desenha outro X ou sinaleiro no conteúdo da janela. O compositor controla fechar, minimizar e maximizar/restaurar. Não há APIs privadas, shell com entrada de usuário, privilégios elevados ou conexões de rede no app.

## Preferências

`welcome.json` tem `schemaVersion: 1`, `theme`, `variant`, `preset`, `appearance`, `highContrast`, `reducedMotion` e `completed`. O catálogo valida os valores antes de gravar. Abrir o app apenas lê; uma preferência ausente usa defaults em memória. Conteúdo inválido produz mensagem e pode ser preservado exatamente no backup da próxima gravação.

`welcome.previous.json` contém os bytes anteriores e os bytes esperados após a gravação, codificados em hexadecimal. O lock coordena instâncias do Welcome. Gravações usam arquivo temporário com permissão 0600, fsync e substituição atômica no mesmo diretório. A reversão verifica o resultado atual para não sobrescrever mudanças posteriores. Isso não é um backup do desktop; ele será necessário antes de implementar a aplicação de presets ao Plasma.

## Aparência, acessibilidade e tradução

Os tokens vêm da especificação: ink, cobalt, lime, superfícies claras/escuras, bordas e raios. Estados de foco, seleção, hover, pressão e indisponibilidade estão definidos; a interface usa Tab/Shift+Tab e Space/Enter nos controles Qt. O conteúdo tem rolagem em janelas menores e imagens com `PreserveAspectFit`. A escala da tela é fornecida pelo Qt. Não há animações; `reducedMotion` fica registrado para integrações futuras.

A interface desta entrega é pt-BR. Strings QML estão marcadas com `qsTr`, e o bootstrap pode carregar catálogos Qt `.qm` em `translations/`. Traduções completas, incluindo o catálogo e mensagens Python, ainda precisam ser extraídas e revisadas antes de publicar outros idiomas. Não foi incluída fonte de terceiros; usa a sans-serif do sistema.

## Integração do shell

O painel superior está implementado como layout Plasma 6, com ferramenta de plano, backup, aplicação e reversão seletiva. Consulte `docs/top-panel.md` para os limites da validação e os testes na VM. A próxima etapa é a dock com o gerenciador de tarefas nativo. O Welcome poderá entregar suas preferências a uma camada explícita de aplicação de presets, com prévia das mudanças. Trocar de espaço não deverá trocar o tema global automaticamente.
