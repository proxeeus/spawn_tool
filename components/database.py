import MySQLdb
import globals

class Database:
    host = ""
    user = ""
    password = ""
    port = ""
    db = ""
    conn = None

    lastinsertedspawn2id = 0
    lastinsertedspawngroupid = 0

    def __init__(self, host, user, password, port, db):
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.db = db

    # Establishes a connection to the EQEmu database
    def ConnectToDatabase(self):
        self.conn = MySQLdb.Connection(
            self.host,
            self.user,
            self.password,
            self.db)

        return self.conn

    # Queries the Database in order to get spawn data
    # (this should be refactored at some point)
    def GetDbSpawnData(self):
        cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)

        query = """SELECT nt.name as NpcName, nt.id as NpcId, s2.id as Spawn2Id, s2.zone as Spawn2Zone, s2.x as Spawn2X, s2.y as Spawn2Y, s2.z as Spawn2Z, 
                s2.heading as Spawn2Heading, s2.respawntime as Spawn2Respawn, s2.variance as Spawn2Variance, s2._condition as Spawn2Condition,
                s2.cond_value as Spawn2CondValue, s2.pathgrid as Spawn2Grid, s2.enabled as Spawn2Enabled,
                s2.version as Spawn2Version, s2.animation as Spawn2Animation,
                sg.name as spawngroup_name,sg.id as Spawngroup_id, sg.min_x as Spawngroup_minX, sg.max_x as Spawngroup_maxX,
                sg.min_y as Spawngroup_minY, sg.max_y as Spawngroup_maxY, sg.dist as Spawngroup_dist, sg.mindelay as Spawngroup_mindelay,
                sg.delay as Spawngroup_delay, sg.despawn_timer as Spawngroup_despawntimer,
                sg.spawn_limit as Spawngroup_spawnlimit, se.chance as Spawnentry_chance FROM spawn2 s2
                JOIN spawngroup sg ON sg.id = s2.spawngroupid
                JOIN spawnentry se
                ON se.spawngroupid = sg.id
                JOIN npc_types nt
                ON nt.id = se.npcid
                WHERE s2.zone = '""" + globals.currentZone + "'"
        cursor.execute(query)
        return cursor

    # Gets the next available id value for the Spawn2 table
    def GetNextSpawn2Id(self):
        cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)

        query = "SELECT * FROM spawn2 ORDER BY ID DESC LIMIT 1"
        cursor.execute(query)

        row = cursor.fetchone()
        lastId = 0
        if row:
            lastId = row["id"] + 1
        return lastId

    # Gets the next available id value for the Spawngroup table
    def GetNextSpawnGroupId(self):
        cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)

        query = "SELECT * FROM spawngroup ORDER BY ID DESC LIMIT 1"
        cursor.execute(query)
        row = cursor.fetchone()
        lastId = 0
        if row:
            lastId = row["id"] + 1
        return lastId

    # Gets the name of an NPC based on its ID
    def GetNpcNameById(self, npcid):
        cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)

        query = "SELECT name FROM npctypes where id = " + npcid
        cursor.execute(query)
        row = cursor.fetchone()
        name = ""
        if row:
            name = row["name"]
        return name

    # Inserts a new row into the Spawn2 table with the provided Spawn data
    # 1. Insert a new spawngroup entry
    # 2. Insert a new spawn2 entry referencing the previously inserted spawngroupID
    # 3. Inser a new spawnentry referencing both previously inserted spawn IDs
    def InsertNewSpawn(self, spawn):

        cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)

        query = """ INSERT INTO spawngroup(name, spawn_limit, dist, max_x, min_x, max_y, min_y, delay, mindelay, despawn, despawn_timer)
                    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"""
        values = (spawn.spawngroup_name, spawn.spawngroup_spawnlimit, spawn.spawngroup_dist, spawn.spawngroup_maxx, spawn.spawngroup_minx, spawn.spawngroup_maxy, spawn.spawngroup_miny, spawn.spawngroup_delay, spawn.spawngroup_mindelay, spawn.spawngroup_despawn, spawn.spawngroup_despawntimer)
        cursor.execute(query, values)
        self.conn.commit()
        print("1 spawngroup inserted, ID:", cursor.lastrowid)
        self.lastinsertedspawngroupid = cursor.lastrowid

        query = """INSERT INTO spawn2(spawngroupID,zone, version, x,y,z,heading,respawntime,variance,pathgrid,_condition,cond_value,enabled, 
        animation) VALUES (%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s, %s,%s,%s);"""
        values = (self.lastinsertedspawngroupid, spawn.spawnentry_zone, spawn.spawnentry_version ,spawn.spawnentry_x,spawn.spawnentry_y ,spawn.spawnentry_z , spawn.spawnentry_heading,spawn.spawnentry_respawn ,spawn.spawnentry_variance ,spawn.spawnentry_pathgrid ,spawn.spawnentry_condition ,spawn.spawnentry_condvalue ,spawn.spawnentry_enabled ,spawn.spawnentry_animation )
        cursor.execute(query, values)
        self.conn.commit()
        print("1 record inserted, ID:", cursor.lastrowid)
        self.lastinsertedspawn2id = cursor.lastrowid

        query = "INSERT INTO spawnentry(spawngroupID, npcID, chance) VALUES (%s, %s, %s);"
        values = self.lastinsertedspawngroupid, spawn.spawnentry_npcid, spawn.spawngroup_chance
        cursor.execute(query, values)

    # Deletes a complete spawn from the database and all its associated Spawngroup, Spawn2 and Spawnentry entries
    def DeleteSpawn(self, spawn):
        cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)

        query = """DELETE FROM spawnentry WHERE spawngroupID = %t and npcID = %t;"""
        values = (spawn.spawngroup_id, spawn.spawnentry_id)
        cursor.execute(query, values)
        self.conn.commit()
        print("Spawn entry deleted successfully.")

        query = """DELETE FROM spawn2 where spawngroupID = %s AND id = %s"""
        values = (spawn.spawngroup_id, spawn.spawnentry_id)
        cursor.execute(query, values)
        self.conn.commit()
        print("Spawn2 deleted successfully.")

        query = """DELETE FROM spawngroup where id = %s"""
        values = (spawn.spawngroup_id)
        cursor.execute(query, values)
        self.conn.commit()
        print ("Spawngroup deleted successfully.")

    def GetNpcNameById(self, npcid):
        cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)

        query = "SELECT name FROM npc_types where id =" + str(npcid) + ";"
        cursor.execute(query)
        row = cursor.fetchone()
        if row:
            return row["name"]


