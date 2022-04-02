import json, math, random, re, requests

url = 'https://www.dnd5eapi.co'

def itemAdd(item, inventoryList):
	itemURL = item['equipment']['url']
	quantity = item['quantity']
	characteritemRequest = requests.get(url + itemURL)
	characteritemData = json.loads(characteritemRequest.text)
	itemName = characteritemData['index']
	itemType = characteritemData['equipment_category']['index']

	if itemType in inventoryList:
		if itemName not in inventoryList[itemType]: 
			item = {}
			if itemType == 'weapon': # For Weapons
				props = []
				for prop in characteritemData['properties']:
					props.append(prop['index'])

				item = {
					itemName: {
						'damage': characteritemData['damage']['damage_dice'],
						'category':characteritemData['weapon_category'],
						'range': characteritemData['weapon_range'],
						'properties': props,
						'quantity': quantity,
						'equipped': False
					}
				}
			elif itemType == 'armor': # For armor
				acBase = characteritemData['armor_class']['base']
				item = {
					itemName: {
						'ac': acBase,
						'category':characteritemData['armor_category'],
						'quantity': quantity,
						'equipped': False
					}
				}
			inventoryList[itemType].update(item)
		else:
			inventoryList[itemType][itemName]['quantity'] += quantity
	return inventoryList