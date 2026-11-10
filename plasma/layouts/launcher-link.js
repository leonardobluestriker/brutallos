function brutallLauncher(action, options) {
    function read(w, key) {
        w.currentConfigGroup = ["General"];
        return w.readConfig(key, "");
    }
    function dump(w) {
        w.currentConfigGroup = ["General"];
        var config = {};
        for(var i=0;i<w.configKeys.length;i++) config[w.configKeys[i]] = w.readConfig(w.configKeys[i], "");
        return {id:w.id, type:w.type, config:config, tree:tree(w,[]), shortcut:w.globalShortcut};
    }
    function tree(w,path) {
        w.currentConfigGroup=path;
        var result={values:{},groups:{}};
        var keys=w.configKeys;
        var groups=w.configGroups;
        for(var i=0;i<keys.length;i++) result.values[keys[i]]=w.readConfig(keys[i],"");
        for(var j=0;j<groups.length;j++) result.groups[groups[j]]=tree(w,path.concat([groups[j]]));
        return result;
    }
    function restoreTree(w,node,path) {
        w.currentConfigGroup=path;
        for(var key in node.values) w.writeConfig(key,node.values[key]);
        for(var group in node.groups) restoreTree(w,node.groups[group],path.concat([group]));
    }
    function transfer(old,replacement,shortcut) {
        if(shortcut) {old.globalShortcut="";replacement.globalShortcut=shortcut;}
        old.remove();
    }
    function write(w, config) {
        w.currentConfigGroup = ["General"];
        for(var key in config) w.writeConfig(key, config[key]);
    }
    var matches = panels().filter(function(p) {return p.screen===options.screen && read(p,"brutallOSRole")==="brutallos-dock-v1";});
    if (matches.length !== 1) throw new Error("É necessária uma dock brutallOS nesta tela.");
    var panel=matches[0];
    var candidates=panel.widgets().filter(function(w){return w.type==="org.kde.plasma.kickoff" || (w.type==="org.kde.plasma.icon" && read(w,"brutallOSLauncher"));});
    if(candidates.length!==1) throw new Error("Launcher da dock ambíguo; nenhuma alteração realizada.");
    var current=dump(candidates[0]);
    if(action==="status") return {panel:panel.id, launcher:current};
    if(locked) throw new Error("Widgets bloqueados.");
    if(action==="connect") {
        if(current.type==="org.kde.plasma.icon" && current.config.url===options.url) return {state:"unchanged"};
        if(current.id!==options.before.id) throw new Error("A dock mudou desde o backup.");
        var available=false;
        for(var i=0;i<knownWidgetTypes.length;i++) if(knownWidgetTypes[i]==="org.kde.plasma.icon") available=true;
        if(!available) throw new Error("Widget nativo de ícone indisponível.");
        var added=panel.addWidget("org.kde.plasma.icon");
        try {write(added,{url:options.url, brutallOSLauncher:options.owner});}
        catch(error) {added.remove();throw error;}
        transfer(candidates[0],added,current.shortcut);
        return {state:"connected", id:added.id};
    }
    if(action==="restore") {
        if(current.type!=="org.kde.plasma.icon" || current.config.url!==options.url || current.config.brutallOSLauncher!==options.owner) throw new Error("O launcher foi alterado. Reversão recusada.");
        if(["org.kde.plasma.kickoff","org.kde.plasma.icon"].indexOf(options.before.type)<0) throw new Error("Backup inválido.");
        var old=panel.addWidget(options.before.type);
        try {
            if(options.before.tree) restoreTree(old,options.before.tree,[]);
            else write(old, options.before.config);
        } catch(error) {old.remove();throw error;}
        transfer(candidates[0],old,options.before.shortcut);
        return {state:"restored",id:old.id};
    }
    throw new Error("Ação inválida.");
}
