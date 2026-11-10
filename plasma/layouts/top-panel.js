/* brutallOS top panel — Plasma 6.3 public desktop scripting API.
 * Called by scripts/brutall-top-panel after saving a backup.
 * No filesystem, shell, private API or replacement of existing panels.
 */
function brutallTopPanel(action, options) {
    var dock = options.layout === "dock";
    var role = dock ? "brutallos-dock-v1" : "brutallos-top-v1";
    var group = ["General"];
    var required = ["org.kde.plasma.kickoff", "org.kde.plasma.panelspacer",
                    "org.kde.plasma.systemtray", "org.kde.plasma.digitalclock"];
    if (dock) required = ["org.kde.plasma.kickoff", "org.kde.plasma.icontasks"];
    var globalMenu = "org.kde.plasma.appmenu";
    var statusItems = ["org.kde.plasma.networkmanagement", "org.kde.plasma.volume",
                       "org.kde.plasma.battery", "org.kde.plasma.bluetooth",
                       "org.kde.plasma.notifications", "org.kde.plasma.devicenotifier"];

    function available(plugin) {
        for (var i = 0; i < knownWidgetTypes.length; i++) {
            if (knownWidgetTypes[i] === plugin) return true;
        }
        return false;
    }
    function read(panel, key) {
        var previous = panel.currentConfigGroup;
        panel.currentConfigGroup = group;
        var result = panel.readConfig(key, "");
        panel.currentConfigGroup = previous;
        return result;
    }
    function describe(panel) {
        return {id: panel.id, screen: panel.screen, location: panel.location,
                role: read(panel, "brutallOSRole"), owner: read(panel, "brutallOSOwner")};
    }
    function configure(widget, configGroup, values) {
        widget.currentConfigGroup = configGroup;
        for (var key in values) widget.writeConfig(key, values[key]);
    }

    if (["plan", "status", "apply", "rollback"].indexOf(action) < 0) {
        throw new Error("Ação desconhecida.");
    }
    if (action !== "rollback" && (typeof options.screen !== "number" || options.screen < 0 ||
        options.screen % 1 !== 0 || options.screen >= screenCount)) {
        throw new Error("Tela Plasma inválida ou desconectada.");
    }
    var all = panels();
    var described = [];
    var ours = [];
    var conflicts = [];
    for (var i = 0; i < all.length; i++) {
        var entry = describe(all[i]);
        described.push(entry);
        // A migrated panel remains owned by its original transaction.
        if (entry.role === role && entry.screen === options.screen) ours.push(entry);
        if (entry.screen === options.screen && entry.location === (dock ? "bottom" : "top") && entry.role !== role) {
            conflicts.push(entry.id);
        }
    }
    var missing = required.filter(function (plugin) { return !available(plugin); });
    var warnings = [];
    if (!dock && !available(globalMenu)) warnings.push("Menu global não instalado; será omitido.");
    var trayItems = dock ? [] : statusItems.filter(available);
    var unavailable = dock ? [] : statusItems.filter(function (plugin) { return !available(plugin); });
    if (unavailable.length) warnings.push("Indicadores não instalados serão omitidos: " + unavailable.join(", "));
    var report = {action: action, screen: options.screen, screenCount: screenCount,
                  panels: described, existing: ours, conflicts: conflicts,
                  missing: missing, warnings: warnings, trayItems: trayItems,
                  canApply: !locked && !missing.length && !conflicts.length && ours.length <= 1};
    if (action === "status" || action === "plan") return report;
    if (locked) throw new Error("Widgets bloqueados; nenhuma alteração realizada.");

    if (action === "rollback") {
        if (!options.owner) throw new Error("Reversão exige identificador do backup.");
        var removed = [];
        // Use ownership, not location or screen: a user may have moved our panel.
        for (var r = 0; r < all.length; r++) {
            if (read(all[r], "brutallOSRole") === role &&
                read(all[r], "brutallOSOwner") === options.owner) {
                removed.push(all[r].id);
                all[r].remove();
            }
        }
        return {action: action, removed: removed, state: removed.length ? "removed" : "absent"};
    }
    if (ours.length === 1) return {action: action, state: "unchanged", id: ours[0].id};
    if (!report.canApply) {
        throw new Error("Aplicação recusada: painel existente nessa borda, widgets ausentes ou painel duplicado. Consulte plan.");
    }
    if (!options.owner || typeof options.height !== "number" ||
        options.height < 28 || options.height > 64 || options.height % 1 !== 0) {
        throw new Error("Backup ou altura do painel inválidos.");
    }

    var panel = null;
    try {
        panel = new Panel;
        configure(panel, group, {brutallOSRole: role, brutallOSOwner: options.owner,
                                 brutallOSLayoutVersion: 1});
        panel.screen = options.screen;
        panel.location = dock ? "bottom" : "top";
        panel.height = options.height;
        panel.lengthMode = dock ? "fit" : "fill";
        panel.alignment = dock ? "center" : "left";
        panel.hiding = "none";
        panel.floating = dock;
        panel.opacity = "opaque";

        if (dock) {
            panel.addWidget("org.kde.plasma.kickoff");
            var tasks = panel.addWidget("org.kde.plasma.icontasks");
            configure(tasks, ["General"], {launchers: options.launchers || [],
                separateLaunchers: false, hideLauncherOnStart: true, groupingStrategy: 1,
                groupPopups: true, groupedTaskVisualization: 3, onlyGroupWhenFull: false, showOnlyCurrentScreen: true,
                showOnlyCurrentDesktop: false});
            return {action: action, state: "created", id: panel.id, owner: options.owner};
        }
        var brand = panel.addWidget("org.kde.plasma.kickoff");
        configure(brand, ["General"], {menuLabel: "brutallOS", icon: "start-here-kde-symbolic"});
        if (available(globalMenu)) panel.addWidget(globalMenu);
        panel.addWidget("org.kde.plasma.panelspacer");
        var tray = panel.addWidget("org.kde.plasma.systemtray");
        configure(tray, ["General"], {extraItems: trayItems, showAllItems: false,
                                      scaleIconsToFit: false});
        var clock = panel.addWidget("org.kde.plasma.digitalclock");
        configure(clock, ["Appearance"], {showDate: true, showSeconds: 0,
                                          dateFormat: "custom", customDateFormat: "ddd d MMM",
                                          dateDisplayFormat: 1, autoFontAndSize: true});
        return {action: action, state: "created", id: panel.id, owner: options.owner,
                warnings: warnings};
    } catch (error) {
        if (panel) panel.remove();
        throw error;
    }
}
