import json, loot_test, random, re, requests, math

#*****Initialise*****
#Variables
url = 'https://www.dnd5eapi.co'

#API
raceData = json.loads(requests.get(url + '/api/races').text)
classData = json.loads(requests.get(url + '/api/classes').text)
backgroundData = json.loads(requests.get(url + '/api/backgrounds').text)

#Character
character = {
	'details': {},
	'stats': {
		'raw': {},
		'mod': {},
		'saves': {}
	},
	'skills':{},
	'inventory': {
		'weapon': {},
		'armor': {},
	},
	'combat': {}
}

#*****Details*****
#Variables
raceSelect = random.randint(0,raceData['count']-1)
charRace = raceData['results'][raceSelect]['index']
charSubrace = None

classSelect = random.randint(0,classData['count']-1)
charClass = classData['results'][classSelect]['index']

backgroundSelect = random.randint(0,backgroundData['count']-1)
charBackground = backgroundData['results'][backgroundSelect]['index']

charLevel = 1
charProf = math.ceil(charLevel/4)+1

charAlignment = random.choice(['Lawful','Neutral','Chaotic']) + ' ' + random.choice(['Good','Neutral','Evil'])
if charAlignment == 'Neutral Neutral':
	charAlignment = 'True Neutral'

#API
characterRaceData = json.loads(requests.get(url+ '/api/races/'+ charRace).text)
characterClassData = json.loads(requests.get(url + '/api/classes/' + charClass).text)
characterBackgroundData = json.loads(requests.get(url + '/api/backgrounds/' + charBackground).text)

#Working
if characterRaceData['subraces']:
	subraceSelect = random.randint(0, len(characterRaceData['subraces']) - 1)
	charSubrace = characterRaceData['subraces'][subraceSelect]['index']
	characterSubraceData = json.loads(requests.get(url + "/api/subraces/" + charSubrace).text)

#Character
character['details']['entity'] = 'hero'
character['details']['race'] = charRace
character['details']['subrace'] = charSubrace
character['details']['class'] = charClass
character['details']['background'] = charBackground
character['details']['level'] = charLevel
character['details']['proficiency'] = charProf
character['details']['alignment'] = charAlignment

#*****Stats*****
#Variables
statList = ['str','dex','con','int','wis','cha']
charStatBase = character['stats']['raw']
charStatMod = character['stats']['mod']
charStatSave = character['stats']['saves']
charStatBonus = {}
charStatSaveProf = []

#Functions
def statCalc():
	for stat in statList:
		charStatMod[stat] = math.floor((charStatBase[stat] - 10)/2) 
		charStatSave[stat]  = charStatMod[stat]
		if stat in charStatSaveProf:
			charStatSave[stat] += charProf

#Workings
for raceStatBonus in characterRaceData['ability_bonuses']:
	stat = raceStatBonus['ability_score']['index']
	statBonus = raceStatBonus['bonus']
	charStatBonus[stat] = statBonus

if charSubrace != None:
	for subraceStatBonus in characterSubraceData['ability_bonuses']:
		stat = subraceStatBonus['ability_score']['index']
		statBonus = subraceStatBonus['bonus']
		charStatBonus[stat] = statBonus

for save in characterClassData['saving_throws']:
	charStatSaveProf.append(save['index'])

#Character
for stat in statList:
	statRoll = random.randint(1,6) + random.randint(1,6) + random.randint(1,6)
	charStatBase[stat] = statRoll
	if stat in charStatBonus:
		charStatBase[stat] += charStatBonus[stat] 

statCalc()

#*****Skills*****
#Variables
skillAbilities = {
	'acrobatics': 'dex', 
	'animal-handling': 'wis', 
	'arcana': 'int', 
	'athletics': 'str', 
	'deception': 'cha', 
	'history': 'int', 
	'insight': 'wis', 
	'intimidation': 'cha', 
	'investigation': 'int', 
	'medicine': 'wis', 
	'nature': 'int', 
	'perception': 'wis', 
	'performance': 'cha', 
	'persuasion': 'cha', 
	'religion': 'int', 
	'sleight-of-hand': 'dex', 
	'stealth': 'dex', 
	'survival': 'wis'
}
charSkills = character['skills']

profOffset = 0
if charClass == 'monk':
	profOffset = 2

backgroundProfs = len(characterBackgroundData['starting_proficiencies'])
classProfs = characterClassData['proficiency_choices'][profOffset]['choose']
totalProfs = backgroundProfs + classProfs
charSkillProfs = []

#Functions
def skillCalc():
	for skillName in charSkills: 
		skillMod = skillAbilities[skillName] 
		charSkills[skillName] = charStatMod[skillMod]
		if skillName in charSkillProfs: 
			charSkills[skillName] += charProf

#Workings
for proficiency in characterBackgroundData['starting_proficiencies']: #Background Proficiencies
	charSkillProfs.append(proficiency['index'][6:])

while len(charSkillProfs) < totalProfs: #Class Proficiencies
	print(charRace,charClass)
	profList = characterClassData['proficiency_choices'][profOffset]['from']
	profNumber = random.randint(0,len(profList)-1)
	profTry = profList[profNumber]['index'][6:]
	if profTry not in charSkillProfs:
		charSkillProfs.append(profTry)

#JSON
for skill in skillAbilities: # Skills
	charSkills[skill] = 0

skillCalc()

#*****Equipment*****
#Variables
charInventory = character['inventory']
charWeapons = charInventory['weapon']
charArmor = charInventory['armor']
fullEquipmentList = []
armorClass = 10 + charStatMod['dex']

#Functions
def getEquipmentOptions(equipmentOptions):
	equipmentOptionsRequest = requests.get(url + equipmentOptions['url'])
	equipmentOptionsData = json.loads(equipmentOptionsRequest.text)

	options = []
	for equipment in equipmentOptionsData['equipment']:
		options.append({
			'equipment': equipment,
			'quantity': 1
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
		item = chosenItems[key]
		if item.get('equipment'):
			itemsToAdd.append(item) # add to the end of the list
		elif item.get('0'):
			for subItem in item.values():
				chosenItems.append(subItem) # add to the end of the list
		elif item.get('equipment_option'):
			equipmentOptions = getEquipmentOptions(item['equipment_option']['from']['equipment_category'])
			optionItemsToAdd = getEquipment(equipmentOptions, item['equipment_option']['choose'])
			itemsToAdd += optionItemsToAdd # join the two lists
		key += 1
	return itemsToAdd

def equipmentCalc():
	damageBonus = charStatMod['str']
	for weapon in charWeapons:
		if 'finesse' in charWeapons[weapon]['properties']:
			damageBonus = max(damageBonus,charStatMod['dex'])
		if 'ranged' in charWeapons[weapon]['properties']:
			damageBonus = charStatMod['dex']

		damageDice = charWeapons[weapon]['damage']
		charWeapons[weapon]['damage'] = damageDice + "+" + str(damageBonus)
		charWeapons[weapon]['bonus'] = damageBonus + charProf

	for armor in charArmor:
		if charArmor[armor]['category'] == 'Light':
			charArmor[armor]['ac'] += charStatMod['dex']
		elif charArmor[armor]['category'] == 'Medium':
			charArmor[armor]['ac'] += max(2,charStatMod['dex'])

#Workings
for equipment in characterClassData['starting_equipment']:
	fullEquipmentList.append(equipment)

for equipment in characterClassData['starting_equipment_options']: 
	itemList = getEquipment(equipment['from'], equipment['choose'])
	fullEquipmentList += itemList 

for equipment in fullEquipmentList:
	loot_test.itemAdd(equipment,charInventory)

randomWeapon = random.choice(list(charWeapons))
weaponChoice = charWeapons[randomWeapon]

#Character
equipmentCalc()

for armor in charArmor:
	maxAC = 0
	maxArmor = ""
	if charArmor[armor]['ac'] > maxAC:
		maxAC = charArmor[armor]['ac']
		maxArmor = armor

charArmor[maxArmor]['equipped'] = True
armorClass = charArmor[maxArmor]['ac']

weaponChoice['equipped'] = True
if 'two-handed' not in weaponChoice['properties']:
	if 'shield' in charArmor:
		armorClass += charArmor['shield']['ac']
		charArmor['shield']['equipped'] = True

#*****Combat*****
#Variables
charCombat = character['combat']
spellAbility = False
initiative = charStatMod['dex']
passivePerception = 10 + charSkills['perception']
hitDie = int(characterClassData['hit_die'])
maxHP = random.randint(1,hitDie) + charStatMod['con'] 

#Workings
if maxHP == 0:
	maxHP = 1

if 'spellcasting' in characterClassData:
	spellAbility = characterClassData['spellcasting']['spellcasting_ability']['index']

#Character
charCombat['spellcasting'] = spellAbility
charCombat['initiative'] = charStatMod['dex'] 
charCombat['ac'] = armorClass
charCombat['hit-die'] = charLevel
charCombat['hp-max'] = maxHP
charCombat['hp-current'] = maxHP
charCombat['initiative'] = initiative
charCombat['passive-perception'] = passivePerception

#*****Actions*****
#Variables
#API
#Workings
#Functions
#Character

#*****Level Up*****
#Variables
#API
#Workings
#Functions
#Character


#*****Export*****
with open('character.json','w') as out:
	json.dump(character,out,indent=2)