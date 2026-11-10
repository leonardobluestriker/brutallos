pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Basic as Basic
import QtQuick.Layouts

ApplicationWindow {
    id: win
    required property var backend
    visible: true
    width: 1120; height: 760
    minimumWidth: 840; minimumHeight: 600
    title: qsTr("Central brutallOS")
    property int page: 0
    property bool dark: backend.systemDark
    readonly property color paper: dark ? "#101322" : "#f6f7fc"
    readonly property color surface: dark ? "#1c2235" : "#edf0f8"
    readonly property color ink: dark ? "#f4f5f9" : "#101322"
    readonly property color accent: "#dfff00"
    color: paper
    palette.window: paper
    palette.base: paper
    palette.text: ink
    palette.button: surface
    palette.buttonText: ink
    palette.highlight: accent
    palette.highlightedText: "#101322"
    font.pixelSize: 14
    function updateMonitoring() { backend.setMonitoring(page === 2 && visibility !== Window.Minimized && visible) }
    onPageChanged: updateMonitoring()
    onVisibilityChanged: updateMonitoring()

    component Copy: Label { color: win.ink; wrapMode: Text.WordWrap; textFormat: Text.PlainText }
    component Action: Button {
        id: control
        implicitHeight: 42
        padding: 12
        hoverEnabled: true
        opacity: enabled ? 1 : 0.45
        Accessible.name: text
        contentItem: Text { text: control.text; font: control.font; color: control.checked ? "#101322" : win.ink; wrapMode: Text.WordWrap; verticalAlignment: Text.AlignVCenter }
        background: Rectangle { radius: 20; color: control.checked ? win.accent : (control.hovered || control.down ? (win.dark ? "#30394f" : "#e3e6ed") : win.surface); border.width: control.visualFocus ? 3 : 1; border.color: control.visualFocus ? "#1557ff" : (win.dark ? "#59617b" : "#9da4b5") }
    }
    header: Rectangle {
        height: 58; color: win.paper
        RowLayout {
            anchors.fill: parent; anchors.margins: 12
            Copy { text: "brutallOS"; font.pixelSize: 21; font.bold: true }
            Copy { text: qsTr(" / central"); opacity: 0.7 }
            Item { Layout.fillWidth: true }
            Action {
                text: win.dark ? qsTr("Prévia clara") : qsTr("Prévia escura")
                onClicked: win.dark = !win.dark
                ToolTip.visible: hovered
                ToolTip.text: qsTr("Prévia da central. Para alterar o desktop, use Identidade.")
            }
        }
    }
    RowLayout {
        anchors.fill: parent; spacing: 0
        Rectangle {
            Layout.preferredWidth: 205; Layout.fillHeight: true; color: win.surface
            Column {
                anchors.fill: parent; anchors.margins: 20; spacing: 12
                Copy { text: qsTr("SEU ESPAÇO"); font.pixelSize: 11; font.letterSpacing: 2 }
                Repeater {
                    model: [qsTr("Aplicativos"), qsTr("Configurações"), "Striker Tools", qsTr("Identidade")]
                    delegate: Action {
                        required property int index
                        required property string modelData
                        objectName: "nav" + index
                        width: parent.width; text: modelData; checked: win.page === index
                        onClicked: win.page = index
                    }
                }
                Copy { width: parent.width; text: qsTr("Linux + Plasma 6\n\nFeito para criar.\nPronto para explorar."); opacity: 0.7; font.pixelSize: 13 }
            }
        }
        StackLayout {
            Layout.fillWidth: true; Layout.fillHeight: true; currentIndex: win.page
            ColumnLayout {
                spacing: 16
                Copy { Layout.margins: 24; text: qsTr("Suas ferramentas, à mão."); font.pixelSize: 27; font.bold: true }
                TextField {
                    id: searchField
                    objectName: "appSearch"
                    Layout.leftMargin: 24; Layout.rightMargin: 24; Layout.fillWidth: true
                    implicitHeight: 48
                    color: win.ink
                    placeholderTextColor: win.dark ? "#bac2d9" : "#50576b"
                    leftPadding: 16
                    background: Rectangle { radius: 14; color: win.surface; border.color: searchField.activeFocus ? "#1557ff" : "#59617b"; border.width: searchField.activeFocus ? 3 : 1 }
                    placeholderText: qsTr("Buscar aplicativos instalados…")
                    Accessible.name: placeholderText
                    onTextChanged: win.backend.search(text)
                    onAccepted: { if (win.backend.apps.length > 0) win.backend.launch(win.backend.apps[0].id) }
                    Keys.onEscapePressed: text = ""
                }
                RowLayout {
                    Layout.leftMargin: 24; Layout.rightMargin: 24; spacing: 16
                    Basic.ComboBox {
                        id: categories
                        implicitWidth: 180
                        implicitHeight: 40
                        Accessible.name: qsTr("Categoria de aplicativos")
                        model: [qsTr("Todos os apps"), qsTr("Criatividade"), qsTr("Mídia"), qsTr("Produtividade"), qsTr("Jogos"), qsTr("Internet"), qsTr("Utilitários"), qsTr("Sistema")]
                        onActivated: win.backend.setCategory(["", "Graphics", "AudioVideo", "Office", "Game", "Network", "Utility", "System"][currentIndex])
                    }
                    Copy { text: win.backend.apps.length + qsTr(" aplicativos"); opacity: 0.7 }
                }
                GridView {
                    id: appsGrid
                    Layout.fillWidth: true; Layout.fillHeight: true; Layout.margins: 24
                    clip: true; cellWidth: width / Math.max(1, Math.floor(width / 140)); cellHeight: 132
                    model: win.backend.apps
                    ScrollBar.vertical: Basic.ScrollBar {}
                    delegate: Action {
                        id: appTile
                        required property var modelData
                        width: appsGrid.cellWidth - 12; height: 120
                        text: modelData.name
                        contentItem: Column {
                            spacing: 10
                            Image {
                                anchors.horizontalCenter: parent.horizontalCenter
                                width: 52; height: 52; source: appTile.modelData.iconUrl || ""
                                fillMode: Image.PreserveAspectFit
                                visible: source.toString().length > 0
                            }
                            Text {
                                width: parent.width; text: appTile.modelData.name; color: win.ink
                                horizontalAlignment: Text.AlignHCenter; wrapMode: Text.WordWrap
                                font.pixelSize: 13; maximumLineCount: 2; elide: Text.ElideRight
                            }
                        }
                        enabled: win.backend.canLaunch
                        onClicked: win.backend.launch(modelData.id)
                        ToolTip.visible: hovered; ToolTip.text: modelData.description || modelData.name
                    }
                }
            }
            Basic.ScrollView {
                id: settingsScroll
                contentWidth: availableWidth; clip: true
                Column {
                    width: settingsScroll.availableWidth; padding: 24; spacing: 16
                    Copy { width: parent.width - 48; text: qsTr("Seu sistema, do seu jeito."); font.pixelSize: 27; font.bold: true }
                    Copy { width: parent.width - 48; text: qsTr("Abra os controles nativos do KDE. As alterações são feitas nos próprios módulos de configuração.") }
                    Repeater {
                        model: win.backend.settings
                        delegate: Action {
                            required property var modelData
                            width: parent.width - 48; text: modelData.name + (modelData.available ? "  →" : qsTr("  · indisponível"))
                            enabled: modelData.available
                            onClicked: win.backend.openSettings(modelData.module)
                        }
                    }
                }
            }
            Basic.ScrollView {
                id: metricsScroll
                contentWidth: availableWidth; clip: true
                Column {
                    width: metricsScroll.availableWidth; padding: 24; spacing: 16
                    Copy { text: "Striker Tools"; font.pixelSize: 27; font.bold: true }
                    Copy { width: parent.width - 48; text: qsTr("MONITORAMENTO / LEITURA REAL"); font.pixelSize: 12; font.letterSpacing: 1.5 }
                    Flow {
                        id: metricsGrid
                        width: parent.width - 48; spacing: 16
                    Repeater {
                        model: [{name: "CPU", key: "cpu"}, {name: "RAM", key: "ram"}, {name: "Disco /", key: "disk"}, {name: "Rede agregada", key: "network"}, {name: "GPU (sysfs)", key: "gpu"}]
                        delegate: Rectangle {
                            id: metricCard
                            required property var modelData
                            width: (metricsGrid.width - 16) / 2; height: 116; radius: 16; color: win.surface
                            Column {
                                anchors.fill: parent; anchors.margins: 18; spacing: 16
                                Copy { text: metricCard.modelData.name; font.bold: true }
                                Copy { text: win.backend.metrics[metricCard.modelData.key]; font.pixelSize: 21 }
                            }
                        }
                    }
                    }
                    Copy { text: qsTr("Temperaturas"); font.bold: true }
                    Copy { visible: win.backend.metrics.temperatures.length === 0; text: qsTr("Nenhum sensor de temperatura acessível.") }
                    Repeater {
                        model: win.backend.metrics.temperatures
                        delegate: Copy { required property var modelData; width: parent.width - 48; text: modelData.name + "  /  " + modelData.value }
                    }
                    Copy { width: parent.width - 48; text: qsTr("Atualiza a cada 2 segundos enquanto esta página está aberta. CPU e RAM são as informações expostas pelo kernel; em contêineres podem refletir o host. Rede soma interfaces, incluindo virtuais."); opacity: 0.7 }
                    Copy { width: parent.width - 48; text: qsTr("Perfis Gamer/Economia e benchmarks ainda não estão implementados. Esta versão não altera clocks, processos ou energia."); opacity: 0.7 }
                }
            }
            Basic.ScrollView {
                id: identityScroll
                contentWidth: availableWidth; clip: true
                Column {
                    width: identityScroll.availableWidth; padding: 28; spacing: 20
                    Copy { width: parent.width - 56; text: qsTr("Aparência"); font.pixelSize: 27; font.bold: true }
                    Copy { width: parent.width - 56; text: qsTr("Sua identidade, em cada detalhe."); opacity: 0.7 }
                    Flow {
                        width: parent.width - 56; spacing: 12
                        Repeater {
                            model: win.backend.themePreviews
                            delegate: Rectangle {
                                id: themeCard
                                required property var modelData
                                width: (parent.width - 24) / 3; height: 152
                                radius: 14; color: win.surface; border.color: win.dark ? "#59617b" : "#9da4b5"
                                Column {
                                    anchors.fill: parent; anchors.margins: 12; spacing: 10
                                    Copy { width: parent.width; text: themeCard.modelData.name; font.bold: true; font.pixelSize: 12 }
                                    Image { width: parent.width; height: 90; source: themeCard.modelData.url; fillMode: Image.PreserveAspectFit }
                                }
                            }
                        }
                    }
                    Copy { text: qsTr("Bru · moldura e cores"); font.bold: true }
                    Row {
                        spacing: 12
                        Action { objectName: "applyLight"; text: qsTr("Aplicar Bru claro"); enabled: win.backend.canApplyAppearance && !win.backend.appearanceBusy; onClicked: win.backend.applyAppearance("light") }
                        Action { objectName: "applyDark"; text: qsTr("Aplicar Bru escuro"); enabled: win.backend.canApplyAppearance && !win.backend.appearanceBusy; onClicked: win.backend.applyAppearance("dark") }
                        Action { objectName: "undoAppearance"; text: qsTr("Desfazer"); visible: win.backend.canUndoAppearance; enabled: !win.backend.appearanceBusy; onClicked: win.backend.undoAppearance() }
                    }
                    Copy { width: parent.width - 56; text: qsTr("Aplica o sinaleiro Aurorae e a paleta Bru na sessão Plasma, com backup e opção de desfazer. Seu wallpaper é preservado."); opacity: 0.7 }
                    Action { text: qsTr("Wallpapers e variantes no Welcome →"); onClicked: win.backend.openAppearance() }
                    Copy { width: parent.width - 56; text: qsTr("ArtCraft padrão\nPhotocraft · Filmcraft · Wordcraft · Gridcraft · Deckcraft"); opacity: 0.7 }
                }
            }
        }
    }
    Connections {
        target: win.backend
        function onAppearanceApplied(darkMode) { win.dark = darkMode }
    }
    footer: Copy { padding: 16; text: win.backend.message; visible: text.length > 0 }
}
