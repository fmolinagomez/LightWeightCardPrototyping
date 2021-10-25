import json
import pathlib

cardDb = dict()
i = 0
with open(pathlib.Path(__file__).parent / 'AllCards.json', encoding='utf-8') as dbFile:
    db = json.load(dbFile)

for level1 in db['data'].keys():
    i = i + 1
    print (level1)
    print ('\n')
    if i > 5:
        break
