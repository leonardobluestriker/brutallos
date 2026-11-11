pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: win
    required property var backend
    objectName: "welcomeWindow"
    visible: true
    width: 1080; height: 760
    minimumWidth: 840; minimumHeight: 600
    title: qsTr("Bem-vindo ao brutallOS")
    // Standard window decoration: KWin owns the traffic lights.
    property int step: 0
    property int themeIndex: 0
    property int variantIndex: 0
    property int presetIndex: 0
    property string appearance: "system"
    property bool contrast: false
    property bool reduced: false
    readonly property bool dark: appearance === "dark" || (appearance === "system" && win.backend.systemDark)
    readonly property color ink: dark ? "#f8f9ff" : "#101322"
    readonly property var tones: win.backend.uiPalette(chosenTheme.id, chosenVariant.id, dark)
    readonly property color paper: tones.paper
    readonly property color muted: tones.surface
    readonly property color secondary: contrast ? ink : (dark ? "#c7cedf" : "#50576b")
    readonly property color accent: tones.accent
    readonly property color accentText: tones.accentText
    readonly property var chosenTheme: win.backend.themes[themeIndex]
    readonly property var chosenVariant: chosenTheme.variants[variantIndex]
    readonly property var chosenPreset: win.backend.presets[presetIndex]
    readonly property var steps: [qsTr("Boas-vindas"), qsTr("Seu desktop"), qsTr("Sua identidade"), qsTr("Seu espaço"), qsTr("Tudo pronto")]
    color: paper
    palette.window: paper
    palette.base: paper
    palette.button: muted
    palette.text: ink
    palette.buttonText: ink
    palette.highlight: accent
    palette.accent: accent
    palette.highlightedText: accentText
    palette.link: tones.link
    font.family: "sans-serif"
    font.pixelSize: 15

    function loadPreferences() {
        const p = win.backend.preferences
        themeIndex = Math.max(0, win.backend.themes.findIndex(t => t.id === p.theme))
        variantIndex = Math.max(0, chosenTheme.variants.findIndex(v => v.id === p.variant))
        presetIndex = Math.max(0, win.backend.presets.findIndex(v => v.id === p.preset))
        appearance = p.appearance; contrast = p.highContrast; reduced = p.reducedMotion
    }
    Component.onCompleted: loadPreferences()

    component Copy: Label {
        color: win.secondary
        wrapMode: Text.WordWrap
        lineHeight: 1.25
        textFormat: Text.PlainText
    }
    component Heading: Copy {
        color: win.ink
        font.pixelSize: 36
        font.bold: true
        lineHeight: 1.05
    }
    component BruButton: Button {
        id: control
        property bool primary: false
        implicitHeight: Math.max(44, contentItem.implicitHeight + 22)
        implicitWidth: contentItem.implicitWidth + 32
        hoverEnabled: true
        padding: 12
        opacity: enabled ? 1 : 0.45
        Accessible.name: text
        contentItem: Text {
            text: control.text
            color: control.primary || control.checked ? win.accentText : win.ink
            font: control.font
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            wrapMode: Text.WordWrap
        }
        background: Rectangle {
            radius: 8
            color: control.primary || control.checked ? win.accent : (control.hovered || control.down ? win.muted : win.paper)
            border.color: control.visualFocus ? win.tones.focus : win.ink
            border.width: control.visualFocus || win.contrast ? 3 : 1
            Rectangle {
                visible: control.visualFocus
                anchors.fill: parent; anchors.margins: -4
                color: "transparent"; radius: 11
                border.width: 2; border.color: win.accent
            }
        }
    }
    component ChoiceCard: BruButton {
        id: card
        property string detail: ""
        checkable: true
        implicitHeight: 112
        contentItem: Column {
            spacing: 6
            Text { width: parent.width; text: card.text; color: card.checked ? win.accentText : win.ink; font.bold: true; font.pixelSize: 18; wrapMode: Text.WordWrap }
            Text { width: parent.width; text: card.detail; color: card.checked ? win.accentText : win.secondary; font.pixelSize: 14; wrapMode: Text.WordWrap }
        }
        Accessible.description: detail
    }

    header: Rectangle {
        height: 68; color: win.paper
        Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: win.ink }
        RowLayout {
            anchors.fill: parent; anchors.leftMargin: 28; anchors.rightMargin: 28
            Label { text: "brutallOS"; color: win.ink; font.pixelSize: 25; font.bold: true }
            Label { text: " / welcome"; color: win.secondary; font.pixelSize: 16 }
            Item { Layout.fillWidth: true }
            Label { text: qsTr("UM ESPAÇO PARA FAZER."); color: win.secondary; font.pixelSize: 11; font.letterSpacing: 1.5 }
        }
    }

    RowLayout {
        anchors.fill: parent; spacing: 0
        Rectangle {
            Layout.preferredWidth: 212; Layout.fillHeight: true; color: win.muted
            Column {
                anchors.fill: parent; anchors.margins: 24; spacing: 14
                Copy { text: qsTr("COMECE POR AQUI"); font.pixelSize: 10; font.bold: true; font.letterSpacing: 1.4 }
                Repeater {
                    model: win.steps
                    delegate: BruButton {
                        required property int index
                        required property string modelData
                        objectName: "step" + index
                        width: parent.width
                        text: (index + 1) + "  " + modelData
                        checked: win.step === index
                        onClicked: win.step = index
                    }
                }
                Rectangle { width: parent.width; height: 1; color: win.secondary; opacity: 0.4 }
                Copy { width: parent.width; text: qsTr("Seu desktop.\nSeu ritmo.\nSua identidade."); font.pixelSize: 20; color: win.ink; font.bold: true }
                Copy { width: parent.width; text: qsTr("Construído sobre Linux + KDE Plasma 6."); font.pixelSize: 12 }
            }
        }
        ScrollView {
            id: scroller
            Layout.fillWidth: true; Layout.fillHeight: true
            clip: true
            contentWidth: availableWidth
            ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
            Column {
                width: scroller.availableWidth
                padding: 32; spacing: 20
                Column {
                    visible: win.step === 0; width: parent.width - 64; spacing: 20
                    Copy { text: qsTr("OLÁ, ESTE É O SEU COMEÇO."); color: win.tones.link; font.bold: true; font.pixelSize: 12; font.letterSpacing: 1.4 }
                    Heading { width: parent.width; text: qsTr("Ideias grandes.\nUm desktop à altura.") }
                    Rectangle {
                        width: parent.width; height: Math.min(width * 9 / 16, 200)
                        color: win.muted; border.width: 1; border.color: win.ink; radius: 12
                        Image { anchors.fill: parent; anchors.margins: 2; source: win.backend.asset("BRU1.png"); fillMode: Image.PreserveAspectFit; Accessible.name: qsTr("Wallpaper Bru original") }
                    }
                    Copy { width: parent.width; text: qsTr("Conheça o brutallOS e escolha como quer começar. Uma experiência para criar, desenvolver e viver o dia a dia.") }
                    Copy { width: parent.width; text: qsTr("Esta primeira versão registra suas escolhas. A aplicação de temas, painéis e espaços virá nas próximas etapas."); font.pixelSize: 13 }
                }
                Column {
                    visible: win.step === 1; width: parent.width - 64; spacing: 20
                    Heading { width: parent.width; text: qsTr("Encontre seu caminho.") }
                    Copy { width: parent.width; text: qsTr("Um tour pela experiência planejada para Plasma 6.") }
                    Repeater {
                        model: [
                            [qsTr("01 / Barra superior"), qsTr("Marca, rede, áudio, energia e relógio. Menus de aplicativos apenas quando suportados.")],
                            [qsTr("02 / Dock + launcher"), qsTr("Seus apps e janelas com o gerenciador de tarefas nativo do Plasma. Busca inicial com Kickoff e KRunner.")],
                            [qsTr("03 / Quatro espaços"), qsTr("Criativo, Desenvolvedor, Produtividade e Mídia. Desktops virtuais sem trocar o tema a cada mudança.")],
                            [qsTr("04 / Sinaleiro à esquerda"), qsTr("Vermelho fecha, amarelo minimiza e verde maximiza ou restaura. Ações nativas do KWin nas janelas compatíveis.")]
                        ]
                        delegate: Rectangle {
                            id: tourCard
                            required property var modelData
                            width: parent.width; height: tourText.implicitHeight + 32
                            radius: 12; color: win.muted; border.width: win.contrast ? 2 : 0; border.color: win.ink
                            Column {
                                id: tourText
                                anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 16; spacing: 8
                                Copy { text: tourCard.modelData[0]; color: win.ink; font.bold: true }
                                Copy { width: parent.width; text: tourCard.modelData[1] }
                            }
                        }
                    }
                    Copy { width: parent.width; text: qsTr("Depois: configurações e Striker Tools. Este tour não altera o seu desktop."); font.pixelSize: 13 }
                }
                Column {
                    visible: win.step === 2; width: parent.width - 64; spacing: 16
                    Heading { width: parent.width; text: qsTr("Escolha sua identidade.") }
                    Copy { width: parent.width; text: qsTr("As imagens originais, do jeito que você criou.") }
                    Flow {
                        width: parent.width; spacing: 8
                        Repeater {
                            model: win.backend.themes
                            delegate: BruButton {
                                required property int index
                                required property var modelData
                                objectName: "theme" + index
                                text: modelData.name; checked: win.themeIndex === index
                                onClicked: { win.variantIndex = 0; win.themeIndex = index }
                            }
                        }
                    }
                    Rectangle {
                        width: parent.width; height: Math.min(width * 9 / 16, 260)
                        color: win.muted; border.width: 1; border.color: win.ink
                        Image {
                            objectName: "wallpaperPreview"
                            readonly property bool loaded: status === Image.Ready
                            anchors.fill: parent; anchors.margins: 2
                            source: win.backend.asset(win.chosenVariant.file)
                            fillMode: Image.PreserveAspectFit
                            Accessible.name: win.chosenTheme.name + " / " + win.chosenVariant.name
                        }
                    }
                    Flow {
                        width: parent.width; spacing: 8
                        Repeater {
                            model: win.chosenTheme.variants
                            delegate: BruButton {
                                required property int index
                                required property var modelData
                                objectName: "variant" + index
                                text: modelData.name; checked: win.variantIndex === index
                                onClicked: win.variantIndex = index
                            }
                        }
                    }
                    Copy { text: qsTr("Aparência do Welcome"); color: win.ink; font.bold: true }
                    Flow {
                        width: parent.width; spacing: 8
                        Repeater {
                            model: [{key: "system", title: qsTr("Sistema")}, {key: "light", title: qsTr("Claro")}, {key: "dark", title: qsTr("Escuro")}]
                            delegate: BruButton {
                                required property var modelData
                                text: modelData.title; checked: win.appearance === modelData.key
                                onClicked: win.appearance = modelData.key
                            }
                        }
                    }
                    BruButton { text: qsTr("Alto contraste") + (win.contrast ? " ✓" : ""); checked: win.contrast; onClicked: win.contrast = !win.contrast }
                    BruButton { text: qsTr("Reduzir movimento") + (win.reduced ? " ✓" : ""); checked: win.reduced; onClicked: win.reduced = !win.reduced }
                    Copy { width: parent.width; text: qsTr("O Welcome não usa animações. A preferência de movimento fica registrada para os próximos componentes."); font.pixelSize: 12 }
                }
                Column {
                    visible: win.step === 3; width: parent.width - 64; spacing: 16
                    Heading { width: parent.width; text: qsTr("O que move você?") }
                    Copy { width: parent.width; text: qsTr("Escolha seu ponto de partida. Os quatro espaços continuam fazendo parte do projeto.") }
                    Repeater {
                        model: win.backend.presets
                        delegate: ChoiceCard {
                            required property int index
                            required property var modelData
                            objectName: "preset" + index
                            width: parent.width
                            text: modelData.name; detail: modelData.description + "\n" + modelData.detail
                            checked: win.presetIndex === index
                            onClicked: win.presetIndex = index
                        }
                    }
                    Copy { width: parent.width; text: qsTr("Seleção de preferência: não instala apps nem cria desktops virtuais nesta etapa."); font.pixelSize: 13 }
                }
                Column {
                    visible: win.step === 4; width: parent.width - 64; spacing: 20
                    Heading { width: parent.width; text: qsTr("Seu próximo começo.") }
                    Copy { width: parent.width; text: qsTr("Revise suas escolhas antes de salvar.") }
                    Rectangle {
                        width: parent.width; height: summary.implicitHeight + 40
                        color: win.muted; radius: 12; border.color: win.ink; border.width: 1
                        Column {
                            id: summary
                            anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 20; spacing: 14
                            Copy { width: parent.width; color: win.ink; font.bold: true; text: qsTr("IDENTIDADE  /  ") + win.chosenTheme.name + " · " + win.chosenVariant.name }
                            Copy { width: parent.width; color: win.ink; text: qsTr("ESPAÇO INICIAL  /  ") + win.chosenPreset.name }
                            Copy { width: parent.width; text: qsTr("ARTCRAFT PADRÃO\n") + win.backend.artcraft.join(" · ") }
                            Copy { width: parent.width; text: qsTr("Aparência: ") + (win.appearance === "system" ? qsTr("Sistema") : win.appearance === "dark" ? qsTr("Escuro") : qsTr("Claro")) + "\n" + qsTr("Alto contraste: ") + (win.contrast ? qsTr("Sim") : qsTr("Não")) + " · " + qsTr("Reduzir movimento: ") + (win.reduced ? qsTr("Sim") : qsTr("Não")) }
                        }
                    }
                    Copy { width: parent.width; text: qsTr("Suas escolhas serão salvas apenas nas preferências do brutallOS, com cópia da gravação anterior. Nenhum tema ou configuração do Plasma será aplicado.") }
                    BruButton {
                        objectName: "saveButton"
                        text: qsTr("Salvar preferências"); primary: true
                        onClicked: {
                            if (win.backend.save(win.chosenTheme.id, win.chosenVariant.id, win.chosenPreset.id, win.appearance, win.contrast, win.reduced)) win.step = 5
                        }
                    }
                }
                Column {
                    visible: win.step === 5; width: parent.width - 64; spacing: 24
                    Copy { text: qsTr("PRIMEIRO PASSO, FEITO."); color: win.tones.link; font.bold: true; font.letterSpacing: 1.5 }
                    Heading { width: parent.width; text: qsTr("Agora, é com você.") }
                    Copy { width: parent.width; text: qsTr("Suas escolhas estão salvas. Você pode reabrir o Welcome para revisá-las ou desfazer a última gravação.") }
                    BruButton { text: qsTr("Revisar escolhas"); onClicked: win.step = 2 }
                    BruButton { objectName: "closeButton"; text: qsTr("Concluir"); primary: true; onClicked: win.close() }
                }
                Copy {
                    objectName: "statusMessage"
                    width: parent.width - 64
                    text: win.backend.message
                    visible: text.length > 0
                    color: win.ink
                    Accessible.role: Accessible.StaticText
                }
                BruButton {
                    objectName: "restoreButton"
                    visible: win.backend.canRestore
                    text: qsTr("Desfazer última gravação")
                    onClicked: { if (win.backend.restore()) { win.loadPreferences(); win.step = 4 } }
                }
            }
        }
    }
    footer: Rectangle {
        color: win.paper; height: 76
        Rectangle { width: parent.width; height: 1; color: win.ink }
        RowLayout {
            anchors.fill: parent; anchors.margins: 16; spacing: 16
            Copy { text: win.step < 5 ? (win.step + 1) + " / 5" : qsTr("Salvo"); Layout.leftMargin: 12 }
            Item { Layout.fillWidth: true }
            BruButton { objectName: "backButton"; text: qsTr("Voltar"); visible: win.step > 0 && win.step < 5; onClicked: win.step-- }
            BruButton { objectName: "nextButton"; text: win.step === 0 ? qsTr("Vamos começar →") : qsTr("Continuar →"); primary: true; visible: win.step < 4; onClicked: win.step++ }
        }
    }
    onStepChanged: { scroller.ScrollBar.vertical.position = 0 }
}
