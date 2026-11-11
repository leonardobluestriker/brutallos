import QtQuick
import org.kde.kwin.decoration

Decoration {
    id: frame
    alpha: true
    property bool dark: decoration.readConfig("dark", false)
    property color paper: decoration.readConfig("paper", dark ? "#151827" : "#f6f7fc")
    property color ink: decoration.readConfig("ink", dark ? "#f5f6ff" : "#101322")
    readonly property bool maximized: decoration.client.maximized

    DecorationOptions { id: options; deco: decoration }
    Rectangle {
        anchors.fill: parent
        color: frame.paper
        radius: frame.maximized ? 0 : 18
        border.width: frame.maximized ? 0 : 2
        border.color: "#101322"
    }
    Item {
        id: titleArea
        x: 2; y: 2
        width: parent.width - 4; height: 38
        Component.onCompleted: decoration.installTitleItem(titleArea)
        Row {
            id: lights
            x: 10; anchors.verticalCenter: parent.verticalCenter
            spacing: 2
            Light { buttonType: DecorationOptions.DecorationButtonClose; tone: "#ff5b58"; symbol: "×"; Accessible.name: qsTr("Fechar") }
            Light { buttonType: DecorationOptions.DecorationButtonMinimize; tone: "#ffd74a"; symbol: "−"; Accessible.name: qsTr("Minimizar") }
            Light { buttonType: DecorationOptions.DecorationButtonMaximizeRestore; tone: "#42d884"; symbol: frame.maximized ? "▣" : "+"; Accessible.name: qsTr("Maximizar ou restaurar") }
        }
        Text {
            anchors.centerIn: parent
            width: Math.max(0, parent.width - 220)
            horizontalAlignment: Text.AlignHCenter
            text: decoration.client.caption
            textFormat: Text.PlainText
            font: options.titleFont
            color: frame.ink
            opacity: decoration.client.active ? 1 : 0.65
            elide: Text.ElideRight
        }
    }
    component Light: DecorationButton {
        id: light
        property color tone
        property string symbol
        width: 26; height: 32
        opacity: enabled ? (decoration.client.active ? 1 : 0.6) : 0.25
        Rectangle {
            anchors.centerIn: parent
            width: 16; height: 16; radius: 8
            color: light.pressed ? Qt.darker(light.tone, 1.25) : light.tone
            border.color: "#101322"; border.width: 1.3
            Text {
                anchors.centerIn: parent
                text: light.symbol; font.pixelSize: 14; font.bold: true; color: "#101322"
                visible: light.hovered || light.pressed
            }
        }
    }
    Component.onCompleted: {
        // The 18px lower frame keeps the rectangular client outside the curved
        // corners, so all four outer corners round without a compositor effect.
        borders.left = 2; borders.right = 2; borders.bottom = 18; borders.top = 40
        maximizedBorders.left = 0; maximizedBorders.right = 0; maximizedBorders.bottom = 0; maximizedBorders.top = 40
        extendedBorders.left = 6; extendedBorders.right = 6; extendedBorders.bottom = 6
    }
    Connections {
        target: decoration
        function onConfigChanged() {
            frame.dark = decoration.readConfig("dark", false)
            frame.paper = decoration.readConfig("paper", frame.dark ? "#151827" : "#f6f7fc")
            frame.ink = decoration.readConfig("ink", frame.dark ? "#f5f6ff" : "#101322")
        }
    }
}
