def init():
    global spawndialog, selectedSpawnXYZ, selectedSpawnPoint3D, spawn_list, hasClickedSpawn, exploreMode, insertMode, editMode, currentZone
    spawndialog, selectedSpawnXYZ, selectedSpawnPoint3D, spawn_list = None

def addspawntolist(spawn):
    globals.spawn_list.append(spawn)
