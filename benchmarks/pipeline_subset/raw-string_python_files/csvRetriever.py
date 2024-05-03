import pandas as pd
import pandas as pd
import logging
import os
from neo4j import GraphDatabase
from PIL import Image


class graphDatabaseManager:

    def __init__(self, uri, user, pwd, db):
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__db = db
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd))
        except Exception as e:
            print("Failed to create the driver:", e)

    def close(self):
        if self.__driver is not None:
            self.__driver.close()

    def query(self, query, parameters=None, db=None):
        assert self.__driver is not None, "Driver not initialized!"
        session = None
        response = None
        try:
            session = self.__driver.session(database=db) if db is not None else self.__driver.session()
            response = list(session.run(query, parameters))
        except Exception as e:
            print("Query failed:", e)
        finally:
            if session is not None:
                session.close()
        return response

    def getAnnoted(self):
        nodes = self.query("""
                            MATCH (a:Annotation)<-[:MARK]-(u:User {userid:"Teresa"})
                            WITH a
                            MATCH (v:Video)<-[:BELONG_TO_VIDEO]-(f:Frame)<-[:BELONG_TO_FRAME]-(p:Patch)<-[:REGARD]-(a)-[:POINT_AT]->(c:Class)
                            WHERE v.video_id in ["th_150_h100_var6_mk5_merge1_maxRegion300_startFrame10", "22-03-10-14-09"]
                            RETURN p.patchid as patchid, c.class as class

        """, db=self.__db)
        return [node.get('patchid') for node in nodes], [node.get('class') for node in nodes]

    def getUnannoted(self):
        nodes = self.query(
            "MATCH (p:Patch) WITH p, size((p)<-[:REGARD]-()) as degree WHERE degree = 0 RETURN p.patchid as patchid",
            db=self.__db)
        return [node.get('patchid') for node in nodes]


querymanager = graphDatabaseManager('bolt://192.168.54.202:7687', 'neo4j', 'password', 'neo4j')
patchids_annoted, classes = querymanager.getAnnoted()
includePossible = True

df = pd.DataFrame(list(zip(patchids_annoted, classes)),columns=['patchids', 'classes'])
df = df[['patchids', 'classes']]
dataset_path = '/Users/beppe2hd/Data/Microplastiche/images'
maxSize = 300

if includePossible:
    ip = 'Possible'
    df['classes'].replace(['NoFiber', 'Fiber', 'possibleFiber'], [0, 1, 1], inplace=True)
else:
    ip = ''
    df['classes'].replace(['NoFiber', 'Fiber', 'possibleFiber'], [0, 1, 2], inplace=True)


deleteitem = []
for item in df.iterrows():
    img_id = f"{item[1].patchids}_P.bmp"
    img = Image.open(os.path.join(dataset_path, img_id)).convert("RGB")
    if img.width > maxSize or img.height > maxSize:
        deleteitem.append(1)
    else:
        deleteitem.append(0)
df['deleteitem'] = deleteitem
print("Original Num Of Items")
print(df.shape)
print(df[df.classes == 0].count())
print(df[df.classes == 1].count())
df = df.drop(df[df['deleteitem'] == 1].index)
print("Cleaned Num Of Items")
print(df.shape)
print(df[df.classes == 0].count())
print(df[df.classes == 1].count())

df = df.drop('deleteitem', axis=1)
numOfClassMicroplast = df[df.classes == 1].count().patchids

df2 = df[df.classes == 0].sample(n=numOfClassMicroplast).append(df[df.classes == 1])
df2.to_csv(f'gt{ip}.csv', index=False)