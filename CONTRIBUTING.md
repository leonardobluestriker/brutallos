# Contribua com o brutallOS

O brutallOS quer reunir pessoas que gostem de Linux, software, arte e interfaces com personalidade. Você pode contribuir com código, ilustrações, ícones, testes, documentação, tradução, áudio ou uma ideia bem explicada. **Não é preciso ser especialista para começar.**

A IA pode ser uma ferramenta de apoio. O que queremos construir é um projeto com participação humana: pessoas criando, experimentando, revisando e tomando decisões sobre o sistema. Ao enviar uma contribuição, conte o que você fez, por que fez e o que conseguiu verificar.

## Por onde começar

1. Conheça a [direção atual do produto](docs/product-direction.md) e a [interface em desenvolvimento](docs/interface-colors.md).
2. Confira as [issues existentes](https://github.com/leonardobluestriker/brutallos/issues). Se sua ideia ainda não apareceu, [abra uma proposta](https://github.com/leonardobluestriker/brutallos/issues/new/choose).
3. Conte a área em que gostaria de ajudar e uma primeira entrega possível. Pode ser pequena. Para mudanças maiores ou novas direções visuais, compartilhe um esboço antes de investir muito tempo.
4. Para enviar arquivos ou código, faça um fork, crie uma branch e abra um pull request explicando a contribuição. Para ideias e relatos de teste, uma issue já é suficiente.

## Código e integração Linux

| Área | Onde olhar |
| --- | --- |
| Boas-vindas e preferências | `apps/brutall-welcome/` |
| Launcher, Central e monitoramento | `apps/brutall-center/` |
| Painel e dock | `plasma/layouts/` |
| Moldura e sinaleiro | `plasma/aurorae/` |
| Paletas e cores ajustáveis | `plasma/colors/` e `apps/brutall-welcome/identity.py` |
| Aplicação, backup e reversão | `scripts/` |
| Testes e laboratório descartável | `tests/` e `lab/plasma/` |

O [README](README.md#executar-sem-instalar-no-sistema) explica como executar com dependências locais. Para mudanças que afetam o desktop, use uma VM ou o [laboratório descartável](lab/plasma/README.md), com backup e caminho de reversão. Não inclua instalação ou alteração silenciosa do sistema do usuário.

Prefira mudanças focadas e descreva a validação relevante: qual comportamento mudou, em qual ambiente foi testado e quais limitações continuam presentes. Capturas de interface devem mostrar o desktop completo quando ajudarem a avaliar a integração com painel, dock e janelas. Os sensores e as métricas devem usar dados reais; recursos planejados precisam continuar identificados como planejados.

## Ilustração, personagens e identidade visual

As famílias de temas são **Bru**, **Raio** e **Strikerzinho & Friends**, com Blue Striker, Green Thunder e Purple Luna. As [nove imagens originais](assets/wallpapers/README.md) são a referência atual e devem permanecer intactas. Envie propostas novas em arquivos separados.

**Em breve serão publicadas as style sheets oficiais do Strikerzinho, do Thunder e da Luna.** Elas orientarão proporções, cores e detalhes dos personagens. Até lá, você já pode apresentar ideias, estudos ou propostas de colaboração em uma issue; as referências definitivas ainda serão disponibilizadas.

Ilustrações, ícones, wallpapers, animações e sons são bem-vindos. Inclua uma prévia, explique onde a peça se encaixa e dê crédito a quem participou. Quando possível, envie também o arquivo editável. Informe a autoria e a origem de materiais de terceiros para que o projeto possa avaliar sua inclusão. A política de licenciamento do código e das artes ainda precisa ser definida; este guia não atribui uma licença nova aos materiais existentes.

## Design, testes, documentação e tradução

Para sugestões de interface, descreva a situação que você quer melhorar e, se possível, apresente um esboço. Legibilidade, contraste, teclado, telas pequenas e escalas diferentes são boas áreas para começar.

Para relatar um problema, informe a distribuição, as versões do Plasma/KWin, X11 ou Wayland, resolução/escala, passos para reproduzir e resultado observado. Testes em hardware real, jogos e notebooks ajudam a verificar metas que o laboratório virtual não consegue medir.

Para documentação e tradução, procure uma instrução confusa, um termo inconsistente ou um guia que esteja faltando. Não precisa esperar uma tarefa grande: melhorar uma explicação para quem está começando já é uma contribuição útil.

## Convivência e reconhecimento

Trate as pessoas com respeito, explique críticas de forma construtiva e acolha quem está aprendendo. Dê crédito às contribuições e às referências usadas. A autoria deve aparecer na descrição da proposta ou do pull request; materiais criativos também podem acompanhar uma nota de créditos.

Obrigado por trazer seu tempo, suas ideias e seu trabalho para o brutallOS.
