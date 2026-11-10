// Public Plasma desktop scripting. Only wallpaper plugin and Image are changed.
function brutallWallpaper(action, options) {
    function read(d) {
        var previous = d.currentConfigGroup;
        d.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
        var result = {id: d.id, screen: d.screen, plugin: d.wallpaperPlugin,
                      image: d.readConfig("Image", "")};
        d.currentConfigGroup = previous;
        return result;
    }
    function same(a, b) { return a.plugin === b.plugin && a.image === b.image; }
    function set(d, state) {
        d.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
        d.writeConfig("Image", state.image);
        d.wallpaperPlugin = state.plugin;
    }
    if (action === "status") {
        var targets = [];
        for (var i=0; i<screenCount; i++) targets.push(read(desktopForScreen(i)));
        return {screens: screenCount, targets: targets};
    }
    if (action === "apply" || action === "rollback") {
        if (locked) throw new Error("Widgets bloqueados.");
        var targets = options.targets;
        if (!targets || !targets.length) throw new Error("Nenhuma área de trabalho selecionada.");
        // Check all targets before touching any, including topology/config changes.
        for (var t=0; t<targets.length; t++) {
            var d = desktopById(targets[t].before.id);
            if (!d || !same(read(d), action === "apply" ? targets[t].before : targets[t].after)) {
                throw new Error("Wallpaper alterado ou área removida. Operação cancelada para preservar alterações.");
            }
            if (action === "apply" && d.screen !== targets[t].before.screen) throw new Error("A tela mudou desde a prévia.");
        }
        for (var j=0; j<targets.length; j++) set(desktopById(targets[j].before.id), action === "apply" ? targets[j].after : targets[j].before);
        return {state: action === "apply" ? "applied" : "reverted", desktops: targets.length};
    }
    throw new Error("Ação inválida.");
}
