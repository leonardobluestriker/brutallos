# Direção atual do produto

Decisões confirmadas pelo projeto após a entrega inicial do Welcome:

- brutallOS será um **Linux tematizado baseado em outra distribuição**, evoluindo para distribuição própria. Não se trata de escrever um kernel próprio. A distro-base definitiva ainda não foi escolhida; o laboratório informado usa Debian 13 / Plasma 6.3.6 / KWin 6.3.6.
- A referência visual combina barra superior e dock inspiradas no macOS com atalhos e comportamento de janelas familiares ao Windows. Janelas e painéis próprios terão acabamento arredondado, temas marcantes e controles funcionais.
- Console de configurações próprio, launcher e Striker Tools fazem parte do objetivo. As interfaces deverão reutilizar serviços reais do Linux/KDE.
- Bru: padrão, dark e lite. Raio: padrão, dark e lite. Strikerzinho & Friends: Blue Striker, Green Thunder e Purple Luna. Usar os nove PNGs originais de `assets/wallpapers`.
- ArtCraft de edição: Photocraft e Filmcraft por padrão. Escritório: Wordcraft, Gridcraft e Deckcraft por padrão. ArtCraft Launcher opcional. Fonte indicada: https://github.com/storytold; disponibilidade, licenças e dependências ainda precisam ser auditadas antes do empacotamento.
- Striker Tools: monitoramento e sensores reais, benchmarks e perfis Equilibrado/Gamer/Economia. RAM mínima, jogos, facilidade de instalação/atualização e autonomia são metas a medir. Não há garantia universal de cinco horas adicionais de bateria, undervolt ou fechamento/restauração transparente de qualquer processo.
- Toda mudança no ambiente deve ter backup e reversão. Implementação por etapas: Welcome → painel superior → dock → launcher → configurações → Striker Tools.

`design-4.md` permanece intacto como referência técnica. A direção atual e os pedidos explícitos do projeto prevalecem sobre o roteiro histórico contido no anexo.
