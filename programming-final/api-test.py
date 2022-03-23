import json
import requests
import random
import math

url = "https://www.dnd5eapi.co"

# General API call
raceRequest = requests.get(url + "/api/races")
raceData = json.loads(raceRequest.text)
raceList = raceData['results']
raceCount = raceData['count']-1

classRequest = requests.get(url + "/api/classes")
classData = json.loads(classRequest.text)
classList = classData['results']
classCount = classData['count']-1

backgroundRequest = requests.get(url + "/api/backgrounds")
backgroundData = json.loads(backgroundRequest.text)
backgroundList = backgroundData['results']
backgroundCount = backgroundData['count']-1

skillsRequest = requests.get(url + "/api/skills")
skillsData = json.loads(skillsRequest.text)
skillAbilities = {}
for skill in skillsData['results']:
	skillsURL = skill['url']
	skillsNameRequest = requests.get(url + skillsURL)
	skillsNameData = json.loads(skillsNameRequest.text)
	skillsName = skillsNameData['index']
	skillsAbility = skillsNameData['ability_score']['index']
	skillAbilities[skillsName] = skillsAbility

alignment1 = random.choice(['Lawful','Neutral','Chaotic'])
alignment2 = random.choice(['Good','Neutral','Evil'])

### Character ###
character = {
	'Specifics': {
		'race': raceList[random.randint(0,raceCount)]['index'],
		'class': classList[random.randint(0,classCount)]['index'],
		'background': backgroundList[random.randint(0,backgroundCount)]['index'],
		'level': 1,
		'alignment': alignment1 + "-" + alignment2,
		'proficiency': 2,
	},
	'stats': {
		'raw': {
			'str': 0,
			'dex': 0,
			'con': 0,
			'int': 0,
			'wis': 0,
			'cha': 0
		},
		'mod': {
		},
		'saves': {
		}
	},
	'skills':{
	},
	'combat': {
		'ac': 10,
	},
	'equipment': {
		'weapon': {},
		'armor': {},
	}
}

### Variables ###
charRace = character['Specifics']['race']
charClass = character['Specifics']['class']
charBackground = character['Specifics']['background']
charStats = character['stats']['raw']
charStatsBonus = {}
for statType in charStats:
	charStatsBonus[statType] = 0
charStatsMod = character['stats']['mod']
charStatsSave = character['stats']['saves']
charSkills = character['skills']
charProf = character['Specifics']['proficiency']
charProfsSaves = []
charProfSkills = []
charCombat = character['combat']

# Specific API calls
raceSpecificRequest = requests.get(url+ "/api/races/"+ charRace)
raceSpecificData = json.loads(raceSpecificRequest.text)

classSpecificRequest = requests.get(url + "/api/classes/" + charClass)
classSpecificData = json.loads(classSpecificRequest.text)

backgroundSpecificRequest = requests.get(url + "/api/backgrounds/" + charBackground)
backgroundSpecificData = json.loads(backgroundSpecificRequest.text)

### Baselines ###
for statType in charStats: # Stats
	statRoll = random.randint(1,6) + random.randint(1,6) + random.randint(1,6)
	charStats[statType] = statRoll

for skills in skillsData['results']: # Skills
	skillName = skills['index']
	charSkills[skillName] = 0

### Functions ###
def statCalc(): # For updating stats
	for statName in charStats: 	# Stats
		charStats[statName] += charStatsBonus[statName] #Base Stat + Racial Bonuses
		charStatsMod[statName] = math.floor((charStats[statName] - 10)/2) #Stat Modifiers based on stat
		charStatsSave[statName]  = charStatsMod[statName] # Saving throws = Modifier + Proficiency bonus
		if statName in charProfsSaves:
			charStatsSave[statName] += charProf

	for skillName in charSkills: # Skills
		skillMod = skillAbilities[skillName] # What stat the skill uses
		charSkills[skillName] = charStatsMod[skillMod] # Stat bonus
		if skillName in charProfSkills: # Proficiency bonus
			charSkills[skillName] += charProf


### Race ###
# Racial bonuses 
for raceStatBonus in raceSpecificData['ability_bonuses']:
	statName = raceStatBonus['ability_score']['index']
	statBonus = raceStatBonus['bonus']
	charStatsBonus[statName] += statBonus

#  Subrace & bonuses (if available)
if raceSpecificData['subraces']:
	subraceCount = len(raceSpecificData['subraces']) - 1
	subraceChoose = random.randint(0, subraceCount)
	subraceSelect = raceSpecificData['subraces'][subraceChoose]
	character['Specifics']['subrace'] = subraceSelect['index']

	# Get subrace data
	subraceRequest = requests.get(url + subraceSelect['url'])
	subraceData = json.loads(subraceRequest.text)

	# Apply subrace bonuses
	for subraceStatBonus in subraceData['ability_bonuses']:
		statName = subraceStatBonus['ability_score']['index']
		statBonus = subraceStatBonus['bonus']
		charStatsBonus[statName] += statBonus

### Class ###
# Proficiencies
for proficiency in backgroundSpecificData['starting_proficiencies']: #Proficiencies from background
	proficiencyName = proficiency['index'][6:]
	charProfSkills.append(proficiencyName)

if charClass == 'Monk': # Edge case 
	numberProfs = classSpecificData['proficiency_choices'][2]['choose']
	totalProfs = len(charProfSkills) + numberProfs
	while len(charProfSkills) < totalProfs:
		print('monks gone wild')
		optionsCount = len(classSpecificData['proficiency_choices'][2]['from'])-1
		profNumber = random.randint(0,optionsCount)
		profTry = classSpecificData['proficiency_choices'][2]['from'][profNumber]['index'][6:]
		if profTry not in charProfSkills:
			charProfSkills.append(profTry)
else:
	numberProfs = classSpecificData['proficiency_choices'][0]['choose']
	totalProfs = len(charProfSkills) + numberProfs
	while len(charProfSkills) < totalProfs:
		print(charClass,"gone wild")
		optionsCount = len(classSpecificData['proficiency_choices'][0]['from'])-1
		profNumber = random.randint(0,optionsCount)
		profTry = classSpecificData['proficiency_choices'][0]['from'][profNumber]['index'][6:]
		if profTry not in charProfSkills:
			charProfSkills.append(profTry)

for save in classSpecificData['saving_throws']:
	saveName = save['index']
	charProfsSaves.append(saveName)

# Spellcasting
if 'spellcasting' in classSpecificData:
	character['combat']['spellcasting_ability'] = classSpecificData['spellcasting']['spellcasting_ability']['index']

### Equipment ###
def itemAdd(item): # For updating equipment
	itemURL = item['equipment']['url']
	quantity = item['quantity']
	itemSpecificRequest = requests.get(url + itemURL)
	itemSpecificData = json.loads(itemSpecificRequest.text)
	itemName = itemSpecificData['index']
	itemType = itemSpecificData['equipment_category']['index']

	#Adding a new item to the inventory if it doesn't already exist
	if itemType in character['equipment']:
		if itemName not in character['equipment'][itemType]: 
			item = {}
			if itemType == 'weapon': # For Weapons
				props = []
				for prop in itemSpecificData['properties']:
					props.append(prop['index'])
				item = {
					itemName: {
						'damage': itemSpecificData['damage']['damage_dice'],
						'category':itemSpecificData['weapon_category'],
						'range': itemSpecificData['weapon_range'],
						'properties': props,
						'quantity': quantity
					}
				}
			elif itemType == 'armor': # For Armour
				item = {
					itemName: {
						'ac': itemSpecificData['armor_class']['base'],
						'category':itemSpecificData['armor_category'],
						'quantity': quantity
					}
				}
			character['equipment'][itemType].update(item)

		#Updating item quantity if item already exists in inventory
		else:
			character['equipment'][itemType][itemName]['quantity'] += quantity

def getEquipmentOptions(equipmentOptions):
	equipmentOptionsRequest = requests.get(url + equipmentOptions["url"])
	equipmentOptionsData = json.loads(equipmentOptionsRequest.text)

	options = []
	for equipment in equipmentOptionsData["equipment"]:
		options.append({
			"equipment": equipment,
			"quantity": 1
		})
	return options

def getEquipment(items, count):
	chosenItems = []
	for x in range(count):
		choice = random.randint(0, len(items) - 1)
		chosenItems.append(items[choice])

	itemsToAdd = []
	key = 0
	while key < len(chosenItems):
		print('infinite equipment')
		item = chosenItems[key]
		if item.get("equipment"):
			itemsToAdd.append(item) # add to the end of the list
		elif item.get("0"):
			for subItem in item.values():
				chosenItems.append(subItem) # add to the end of the list
		elif item.get("equipment_option"):
			equipmentOptions = getEquipmentOptions(item["equipment_option"]["from"]["equipment_category"])

			optionItemsToAdd = getEquipment(equipmentOptions, item["equipment_option"]["choose"])
			itemsToAdd += optionItemsToAdd # join the two lists

		key += 1
	return itemsToAdd

fullEquipmentList = []

for item in classSpecificData['starting_equipment']: #Items you always get
	itemAdd(item)

for equipment in classSpecificData["starting_equipment_options"]: #Items you choose from
	itemList = getEquipment(equipment["from"], equipment["choose"])
	fullEquipmentList += itemList # add to a single equipment list to be added to the character

for equipment in fullEquipmentList:
	itemAdd(equipment) 

# Combat Details
statCalc() #calculate the actual stats
charCombat['hit-die-value'] = classSpecificData['hit_die'] 
charCombat['hit-die-total'] = character['Specifics']['level']
charCombat['hp-max'] = random.randint(1,int(charCombat['hit-die-value'])) + charStatsMod['con']
if charCombat['hp-max'] == 0:
	charCombat['hp-max'] = 1
charCombat['hp-current'] = charCombat['hp-max']
character['combat']['initiative'] = 10 + character['stats']['mod']['dex']
character['combat']['passive-perception'] = 10 + character['skills']['perception']

# Other Details (and odd cases)
if character['Specifics']['alignment'] == 'Neutral-Neutral':
	character['Specifics']['alignment'] = 'True Neutral'

# Export
with open('character.json','w') as out:
	json.dump(character,out,indent=2)

#Things this code needs to generate
# 1) Player info from API - pulls from various endpoints
	# a) info - how do we handle level up?
	# b) stats 
	# c) AC/DPS/HP
	# d) saving throws/skills?
	# e) abilities?
# 2) The Map
	# a) Generation - Randomised DFS?
	# b) what's on the tiles?
# 3) Monster info from API - comes as one large blob
	# a) Health/Armour/Attack(s)
	# b) abilities?
	# c) loot? 
# 4) Other maps features not from api
	# a) Items/Healing potions/Weapons (May have to do magic weapons myself)
	# b) doors (locks?)
	# c) traps
# 5) Expose endpoint