pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Basic as Basic
import QtQuick.Layouts

ApplicationWindow {
    id: win
    required property var backend
    property bool launcherMode: false
    property int launcherCategory: 0
    property int themeIndex: 0
    property int variantIndex: 2
    property string customAccent: ""
    property bool tinted: true
    readonly property var chosenTheme: backend.themePreviews[themeIndex]
    readonly property var chosenVariant: chosenTheme.variants[variantIndex]
    visible: true
    flags: launcherMode ? (Qt.Tool | Qt.WindowStaysOnTopHint) : Qt.Window
    width: launcherMode ? 1040 : 1120; height: launcherMode ? 640 : 760
    minimumWidth: 840; minimumHeight: 600
    title: launcherMode ? qsTr("Aplicativos brutallOS") : qsTr("Central brutallOS")
    property int page: 0
    property bool dark: backend.systemDark
    readonly property var tones: backend.uiPalette(customAccent || chosenVariant.accent, dark, tinted)
    readonly property color paper: tones.paper
    readonly property color surface: tones.surface
    readonly property color ink: tones.ink
    readonly property color accent: tones.accent
    readonly property color accentText: tones.accentText
    readonly property color focusColor: tones.focus
    onAccentChanged: { if (!accentInput.activeFocus) accentInput.text = accent.toString() }
    color: paper
    palette.window: paper
    palette.base: paper
    palette.text: ink
    palette.button: surface
    palette.buttonText: ink
    palette.highlight: accent
    palette.accent: accent
    palette.highlightedText: accentText
    palette.link: tones.link
    palette.light: surface
    palette.mid: tones.border
    palette.dark: tones.border
    font.pixelSize: 14
    function updateMonitoring() { backend.setMonitoring(page === 2 && visibility !== Window.Minimized && visible) }
    onPageChanged: { updateMonitoring(); if (page === 3) backend.refreshWallpaperState() }
    function showWallpaperActions() {
        const flick = identityScroll.contentItem as Flickable
        if (flick) flick.contentY = Math.max(0, flick.contentHeight - flick.height)
    }
    function showWallpaperThemes() { identityScroll.contentItem.contentY = 0 }
    Shortcut { sequence: "Escape"; enabled: win.launcherMode; onActivated: win.close() }
    function loadInterface() {
        const p = backend.interfaceSettings
        variantIndex = 0
        themeIndex = Math.max(0, backend.themePreviews.findIndex(t => t.id === p.theme))
        variantIndex = Math.max(0, chosenTheme.variants.findIndex(v => v.id === p.variant))
        customAccent = p.accent || ""
        tinted = p.tinted
        dark = p.mode === "dark"
    }
    Component.onCompleted: {
        loadInterface()
        if (launcherMode) searchField.forceActiveFocus()
        backend.refreshWallpaperState()
    }
    onClosing: { if (launcherMode) Qt.quit() }
    onVisibilityChanged: updateMonitoring()

    component Copy: Label { color: win.ink; wrapMode: Text.WordWrap; textFormat: Text.PlainText }
    component Action: Button {
        id: control
        implicitHeight: 42
        padding: 12
        hoverEnabled: true
        opacity: enabled ? 1 : 0.45
        Accessible.name: text
        contentItem: Text { text: control.text; font: control.font; color: control.checked ? win.accentText : win.ink; wrapMode: Text.WordWrap; verticalAlignment: Text.AlignVCenter }
        background: Rectangle { radius: 20; color: control.checked ? win.accent : (control.hovered || control.down ? win.tones.hover : win.surface); border.width: control.visualFocus ? 3 : 1; border.color: control.visualFocus ? win.focusColor : win.tones.border }
    }
    header: Rectangle {
        height: 58; color: win.paper
        RowLayout {
            anchors.fill: parent; anchors.margins: 12
            Copy { text: "brutallOS"; font.pixelSize: 21; font.bold: true }
            Copy { text: win.launcherMode ? qsTr(" / aplicativos") : qsTr(" / central"); opacity: 0.7 }
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
                    model: win.launcherMode ? [] : [qsTr("Aplicativos"), qsTr("Configurações"), "Striker Tools", qsTr("Identidade")]
                    delegate: Action {
                        required property int index
                        required property string modelData
                        objectName: "nav" + index
                        width: parent.width; text: modelData; checked: win.page === index
                        onClicked: win.page = index
                    }
                }
                Repeater {
                    model: win.launcherMode ? [qsTr("Todos os apps"), qsTr("Criatividade"), qsTr("Mídia"), qsTr("Produtividade"), qsTr("Jogos"), qsTr("Internet"), qsTr("Utilitários"), qsTr("Sistema")] : []
                    delegate: Action {
                        required property int index
                        required property string modelData
                        width: parent.width; text: modelData; checked: win.launcherCategory === index
                        onClicked: { win.launcherCategory = index; win.backend.setCategory(["", "Graphics", "AudioVideo", "Office", "Game", "Network", "Utility", "System"][index]) }
                    }
                }
                Copy { visible: !win.launcherMode; width: parent.width; text: qsTr("Linux + Plasma 6\n\nFeito para criar.\nPronto para explorar."); opacity: 0.7; font.pixelSize: 13 }
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
                    placeholderTextColor: win.tones.muted
                    selectionColor: win.accent
                    selectedTextColor: win.accentText
                    leftPadding: 16
                    background: Rectangle { radius: 14; color: win.surface; border.color: searchField.activeFocus ? win.focusColor : win.tones.border; border.width: searchField.activeFocus ? 3 : 1 }
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
                        visible: !win.launcherMode
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
                    Flow {
                        width: parent.width - 56; spacing: 12
                        Repeater {
                            model: win.backend.themePreviews
                            delegate: Button {
                                id: themeCard
                                required property var modelData
                                width: (parent.width - 24) / 3; height: 112
                                required property int index
                                objectName: "wallpaperTheme" + index
                                checked: win.themeIndex === index
                                Accessible.name: modelData.name
                                onClicked: { win.variantIndex = 0; win.themeIndex = index }
                                background: Rectangle { radius: 14; color: win.surface; border.width: themeCard.checked || themeCard.visualFocus ? 3 : 1; border.color: themeCard.checked || themeCard.visualFocus ? win.focusColor : win.tones.border }
                                Column {
                                    anchors.fill: parent; anchors.margins: 12; spacing: 10
                                    Copy { width: parent.width; text: themeCard.modelData.name; font.bold: true; font.pixelSize: 12 }
                                    Image { width: parent.width; height: 60; source: themeCard.modelData.url; fillMode: Image.PreserveAspectFit }
                                }
                            }
                        }
                    }
                    Copy { text: qsTr("Wallpaper original"); font.bold: true }
                    Flow {
                        width: parent.width - 56; spacing: 10
                        Repeater {
                            model: win.chosenTheme.variants
                            delegate: Action {
                                required property var modelData
                                required property int index
                                objectName: "wallpaperVariant" + index
                                text: modelData.name; checked: win.variantIndex === index
                                onClicked: win.variantIndex = index
                            }
                        }
                    }
                    Image { objectName: "wallpaperPreview"; readonly property bool loaded: status === Image.Ready; width: parent.width - 56; height: 80; source: win.chosenVariant.url; fillMode: Image.PreserveAspectFit; Accessible.name: win.chosenTheme.name + " / " + win.chosenVariant.name }
                    Copy { text: qsTr("Cores da interface"); font.bold: true }
                    Flow {
                        width: parent.width - 56; spacing: 10
                        Repeater {
                            model: [{name: qsTr("Azul"), color: "#1557ff"}, {name: qsTr("Rosa"), color: "#e91e86"}, {name: qsTr("Roxo"), color: "#9333ea"}, {name: qsTr("Verde"), color: "#299447"}, {name: qsTr("Âmbar"), color: "#e99a18"}, {name: qsTr("Ciano"), color: "#0099b8"}]
                            delegate: Button {
                                id: swatch
                                required property var modelData
                                implicitWidth: 38; implicitHeight: 38
                                Accessible.name: qsTr("Destaque ") + modelData.name
                                onClicked: { win.customAccent = modelData.color; accentInput.text = win.accent.toString() }
                                background: Rectangle { radius: 19; color: swatch.modelData.color; border.width: swatch.visualFocus || win.accent.toString() === swatch.modelData.color ? 3 : 1; border.color: win.ink }
                                contentItem: Text { text: win.accent.toString() === swatch.modelData.color ? "✓" : ""; color: win.accentText; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; font.bold: true }
                                ToolTip.visible: hovered; ToolTip.text: modelData.name
                            }
                        }
                        Action { objectName: "automaticAccent"; text: qsTr("Usar cor do tema"); checked: win.customAccent === ""; onClicked: { win.customAccent = ""; accentInput.text = win.accent.toString() } }
                    }
                    Flow {
                        width: parent.width - 56; spacing: 10
                        TextField {
                            id: accentInput
                            objectName: "accentInput"
                            implicitWidth: 135; implicitHeight: 42; leftPadding: 14
                            text: win.accent.toString(); color: win.ink
                            Accessible.name: qsTr("Cor de destaque hexadecimal")
                            ToolTip.visible: hovered
                            ToolTip.text: qsTr("Digite #RGB ou #RRGGBB e pressione Enter.")
                            validator: RegularExpressionValidator { regularExpression: /^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$/ }
                            onEditingFinished: { if (acceptableInput && text.toLowerCase() !== win.accent.toString()) win.customAccent = text }
                            onAccepted: { if (acceptableInput) win.customAccent = text }
                            background: Rectangle { radius: 14; color: win.surface; border.width: accentInput.activeFocus ? 3 : 1; border.color: accentInput.activeFocus ? win.focusColor : win.tones.border }
                        }
                        Action { objectName: "tintedSurfaces"; text: qsTr("Colorir fundos e molduras"); checked: win.tinted; onClicked: win.tinted = !win.tinted }
                        Copy { text: win.customAccent === "" ? qsTr("Automático · ") + win.chosenVariant.name : qsTr("Cor personalizada"); height: 42; verticalAlignment: Text.AlignVCenter; opacity: 0.8 }
                    }
                    Flow {
                        width: parent.width - 56; spacing: 10
                        Action { objectName: "applyLight"; text: qsTr("Aplicar interface clara"); enabled: accentInput.acceptableInput && win.backend.canApplyAppearance && !win.backend.appearanceBusy; onClicked: win.backend.applyAppearance("light", win.chosenTheme.id, win.chosenVariant.id, win.customAccent || "auto", win.tinted) }
                        Action { objectName: "applyDark"; text: qsTr("Aplicar interface escura"); enabled: accentInput.acceptableInput && win.backend.canApplyAppearance && !win.backend.appearanceBusy; onClicked: win.backend.applyAppearance("dark", win.chosenTheme.id, win.chosenVariant.id, win.customAccent || "auto", win.tinted) }
                        Action { objectName: "undoAppearance"; text: qsTr("Desfazer cores"); visible: win.backend.canUndoAppearance; enabled: !win.backend.appearanceBusy; onClicked: win.backend.undoAppearance() }
                    }
                    Flow {
                        width: parent.width - 56; spacing: 10
                        Basic.ComboBox { id: wallpaperScreen; model: win.backend.screenChoices; implicitWidth: 190; Accessible.name: qsTr("Monitor para o wallpaper") }
                        Action { objectName: "applyWallpaper"; text: qsTr("Aplicar wallpaper"); enabled: win.backend.canApplyWallpaper && !win.backend.wallpaperBusy && !win.backend.appearanceBusy; onClicked: win.backend.applyWallpaper(win.chosenVariant.file, wallpaperScreen.currentIndex) }
                        Action { objectName: "undoWallpaper"; text: qsTr("Desfazer wallpaper"); visible: win.backend.canUndoWallpaper; enabled: !win.backend.wallpaperBusy; onClicked: win.backend.undoWallpaper() }
                    }
                    Copy { width: parent.width - 56; text: qsTr("Prévia ao escolher. Aplique a interface para salvar suas cores; aplique o wallpaper para mudar a imagem. Ambos têm backup e opção de desfazer."); opacity: 0.7 }
                    Action { text: qsTr("Reabrir o Welcome →"); onClicked: win.backend.openAppearance() }
                }
            }
        }
    }
    Connections {
        target: win.backend
        function onAppearanceApplied(darkMode) { win.dark = darkMode }
        function onLaunchRequested() { if (win.launcherMode) win.close() }
        function onWallpaperSelected(ti, vi) { win.variantIndex = 0; win.themeIndex = ti; win.variantIndex = vi }
        function onInterfaceChanged() { win.loadInterface() }
    }
    footer: Copy { padding: 16; text: win.backend.message; visible: text.length > 0 }
}
