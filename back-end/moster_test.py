import json, math, random, re, requests

url = "https://www.dnd5eapi.co"
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

def generator(monsterName):			
	monsterRequest = requests.get(url + "/api/monsters/" + monsterName)
	monsterData = json.loads(monsterRequest.text)

	monster = {
		'details':{
			'entity': 'monster',
			'name': monsterData['index'],
			'size': monsterData['size'],
			'type': monsterData['type'],
			'alignment': monsterData['alignment'],
			'rating':monsterData['challenge_rating']
		},
		'stats':{
			'raw':{
				'str': monsterData['strength'],
				'dex': monsterData['dexterity'],
				'con': monsterData['constitution'],
				'int': monsterData['intelligence'],
				'wis': monsterData['wisdom'],
				'cha': monsterData['charisma']
			},
			'mod':{

			},
			'saves':{

			}
		},
		'skills':{

		},
		'combat':{
			'ac': monsterData['armor_class'],
			'hp-max': monsterData['hit_points'],
			'hp-current': monsterData['hit_points'],
			'damage-vulnerability': monsterData['damage_vulnerabilities'],
			'damage-resistance': monsterData['damage_resistances'],
			'damage-immunity': monsterData['damage_immunities'],
			'condition-immunity': monsterData['condition_immunities'],
		},
		'actions':{

		}
	}

	for skills in skillAbilities: # Skills
		monster['skills'][skills] = 0

	for statName in monster['stats']['raw']: 	# Stats
		monster['stats']['mod'][statName] = math.floor((monster['stats']['raw'][statName] - 10)/2) #Stat Modifiers based on stat
		monster['stats']['saves'][statName]  = monster['stats']['mod'][statName] # Saving throws = Modifier + Proficiency bonus
	
	for skillName in monster['skills']: # Skills
		skillMod = skillAbilities[skillName] # What stat the skill uses
		monster['skills'][skillName] = monster['stats']['mod'][skillMod] # Stat bonus

	for profs in monsterData['proficiencies']:
		if profs['proficiency']['index'].startswith('saving-throw'):
			statName = profs['proficiency']['index'].split('-')
			monster['stats']['saves'][statName[-1]] = profs['value']
		if profs['proficiency']['index'].startswith('skill'):
			statName = profs['proficiency']['index'].split('-')
			monster['skills'][statName[-1]] = profs['value']

	monster['combat']['initiative'] = monster['stats']['mod']['dex'] 

	for action in monsterData['actions']:
		if len(action['damage']) > 0:
			monster['actions'][action['name']] = {'damage':{}}
			if 'attack_bonus' in action:
				monster['actions'][action['name']]['bonus'] = action['attack_bonus']
			for damage in action['damage']:
				try: 
					damageType = damage['damage_type']['index']
					damageDice = damage['damage_dice']
					if re.search("[0-9]*d[0-9]*\+[0-9]*", damageDice):
						damageDice = damageDice
					elif re.search("[0-9]*d[0-9]*", damageDice):
						damageDice = damageDice + "+0"
					elif re.search("[0-9]*", damageDice):
						damageDice = damageDice + "d1+0"
					else:
						print('fail')
					monster['actions'][action['name']]['damage'][damageType] = damageDice
				except: #some monsters allow you to choose bonus damage or can multi wield
					# {'djinni': 'Scimitar',
					# 'drider': 'Longsword',
					# 'druid': 'Quarterstaff',
					# 'erinyes': 'Longsword',
					# 'gladiator': 'Spear',
					# 'gnoll': 'Spear',
					# 'guard': 'Spear',
					# 'half':-'red',-dragon-veteran Longsword
					# 'hobgoblin': 'Longsword',
					# 'merfolk': 'Spear',
					# 'sahuagin': 'Spear',
					# 'salamander': 'Spear',
					# 'tribal':-'warrior', Spear
					# 'veteran': 'Longsword',
					# 'werewolf':-'human', Spear
					# 'wight': 'Longsword',}
					pass
			if 'dc' in action:
				dcType = action['dc']['dc_type']['index']
				dcValue = action['dc']['dc_value']
				monster['actions'][action['name']]['dc'] = {'save-type': dcType, 'save-value':dcValue}
			if 'usage' in action:
				monster['actions'][action['name']]['recharge'] = action['usage']['min_value']

	return monster		

with open('monster.json','w') as out:
	json.dump(generator('adult-red-dragon'),out,indent=2)