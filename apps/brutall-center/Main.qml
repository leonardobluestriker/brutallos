pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: win
    required property var backend
    visible: true
    width: 1120; height: 760
    minimumWidth: 840; minimumHeight: 600
    title: qsTr("Central brutallOS")
    property int page: 0
    property bool dark: true
    readonly property color paper: dark ? "#101322" : "#ffffff"
    readonly property color surface: dark ? "#1c2235" : "#f4f5f9"
    readonly property color ink: dark ? "#f4f5f9" : "#101322"
    readonly property color accent: "#dfff00"
    color: paper
    font.pixelSize: 15
    function updateMonitoring() { backend.setMonitoring(page === 2 && visibility !== Window.Minimized && visible) }
    onPageChanged: updateMonitoring()
    onVisibilityChanged: updateMonitoring()

    component Copy: Label { color: win.ink; wrapMode: Text.WordWrap; textFormat: Text.PlainText }
    component Action: Button {
        id: control
        implicitHeight: 48
        padding: 12
        hoverEnabled: true
        opacity: enabled ? 1 : 0.45
        Accessible.name: text
        contentItem: Text { text: control.text; font: control.font; color: control.checked ? "#101322" : win.ink; wrapMode: Text.WordWrap; verticalAlignment: Text.AlignVCenter }
        background: Rectangle { radius: 12; color: control.checked ? win.accent : (control.hovered || control.down ? (win.dark ? "#30394f" : "#e3e6ed") : win.surface); border.width: control.visualFocus ? 3 : 1; border.color: control.visualFocus ? "#1557ff" : (win.dark ? "#59617b" : "#9da4b5") }
    }
    header: Rectangle {
        height: 76; color: win.paper
        RowLayout {
            anchors.fill: parent; anchors.margins: 24
            Copy { text: "brutallOS"; font.pixelSize: 26; font.bold: true }
            Copy { text: qsTr(" / central"); opacity: 0.7 }
            Item { Layout.fillWidth: true }
            Action { text: win.dark ? qsTr("Aparência clara") : qsTr("Aparência escura"); onClicked: win.dark = !win.dark }
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
                Copy { Layout.margins: 24; text: qsTr("Suas ferramentas, à mão."); font.pixelSize: 30; font.bold: true }
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
                Copy { Layout.leftMargin: 24; text: win.backend.apps.length + qsTr(" aplicativos encontrados"); opacity: 0.7 }
                GridView {
                    id: appsGrid
                    Layout.fillWidth: true; Layout.fillHeight: true; Layout.margins: 24
                    clip: true; cellWidth: width / Math.max(1, Math.floor(width / 210)); cellHeight: 92
                    model: win.backend.apps
                    ScrollBar.vertical: ScrollBar {}
                    delegate: Action {
                        required property var modelData
                        width: appsGrid.cellWidth - 12; height: 80
                        text: modelData.name
                        enabled: win.backend.canLaunch
                        onClicked: win.backend.launch(modelData.id)
                        ToolTip.visible: hovered; ToolTip.text: modelData.description || modelData.name
                    }
                }
            }
            ScrollView {
                id: settingsScroll
                contentWidth: availableWidth; clip: true
                Column {
                    width: settingsScroll.availableWidth; padding: 24; spacing: 16
                    Copy { width: parent.width - 48; text: qsTr("Seu sistema, do seu jeito."); font.pixelSize: 30; font.bold: true }
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
            ScrollView {
                id: metricsScroll
                contentWidth: availableWidth; clip: true
                Column {
                    width: metricsScroll.availableWidth; padding: 24; spacing: 16
                    Copy { text: "Striker Tools"; font.pixelSize: 30; font.bold: true }
                    Copy { width: parent.width - 48; text: qsTr("MONITORAMENTO / LEITURA REAL"); font.pixelSize: 12; font.letterSpacing: 1.5 }
                    Repeater {
                        model: [{name: "CPU", key: "cpu"}, {name: "RAM", key: "ram"}, {name: "Disco /", key: "disk"}, {name: "Rede agregada", key: "network"}, {name: "GPU (sysfs)", key: "gpu"}]
                        delegate: Rectangle {
                            id: metricCard
                            required property var modelData
                            width: parent.width - 48; height: 76; radius: 16; color: win.surface
                            RowLayout {
                                anchors.fill: parent; anchors.margins: 20
                                Copy { text: metricCard.modelData.name; font.bold: true }
                                Item { Layout.fillWidth: true }
                                Copy { text: win.backend.metrics[metricCard.modelData.key]; font.pixelSize: 19 }
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
            Column {
                padding: 32; spacing: 24
                Copy { width: parent.width - 64; text: qsTr("Uma identidade. Nove possibilidades."); font.pixelSize: 30; font.bold: true }
                Copy { width: parent.width - 64; text: qsTr("Bru · Raio · Strikerzinho & Friends\n\nSuas nove imagens originais continuam no Welcome, com seleção de variantes e backup das preferências.") }
                Action { text: qsTr("Abrir personalização no Welcome →"); onClicked: win.backend.openAppearance() }
                Copy { width: parent.width - 64; text: qsTr("ArtCraft padrão\nPhotocraft · Filmcraft · Wordcraft · Gridcraft · Deckcraft\n\nO launcher lista apenas o que está instalado. Nenhum app ArtCraft é instalado automaticamente."); opacity: 0.7 }
            }
        }
    }
    footer: Copy { padding: 16; text: win.backend.message; visible: text.length > 0 }
}
