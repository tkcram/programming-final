import random

def pathfinder(row,column):
	global critialPath
	pathwayCell = str(row) + "-" + str(column)
	currentPath.append(pathwayCell)
	if len(currentPath) > len(critialPath):
		critialPath = currentPath.copy()
	cell = maze[row][column]
	cell['seen'] = True
	checkedSides = []
	while len(checkedSides) < 4:
		check = random.randint(1,4)
		if check not in checkedSides:
			checkedSides.append(check)
			newRow = 0
			newColumn = 0
			match check: #Find adjacent cell
				case 1: #Move up
					if row == 0:
						continue
					else:
						newRow = row - 1
						newColumn = column 
				case 2: #Move right
					if column == totalColumns - 1:
						continue
					else:
						newRow = row
						newColumn = column + 1
				case 3: #Move down
					if row == totalRows - 1:
						continue
					else:
						newRow = row + 1
						newColumn = column 
				case 4: #Move Left
					if column == 0:
						continue
					else:
						newRow = row
						newColumn = column - 1
			newCell = maze[newRow][newColumn]

			if newCell['seen'] != True:
				match check:
					case 1: #Ceiling current, floor new
						cell['walls'][0] = 0
						newCell['walls'][2] = 0
					case 2: #Right current, left new
						cell['walls'][1] = 0
						newCell['walls'][3] = 0
					case 3: #Floor current, ceiling new
						cell['walls'][2] = 0
						newCell['walls'][0] = 0
					case 4: #Left current, right new
						cell['walls'][3] = 0
						newCell['walls'][1] = 0
				pathfinder(newRow,newColumn)
	currentPath.pop()

# Create Maze
mazeSize = 47 #Maximum 47
totalRows = mazeSize
totalColumns = mazeSize

entranceRow = random.randint(0,totalRows-1)
entranceColumn = random.randint(0,totalColumns-1)

currentPath = []
critialPath = []


maze = [None]*totalRows
for row in range(totalRows):
	maze[row] = [None]*totalColumns
	for column in range(totalColumns):
		maze[row][column] = {
			'seen': False,
			'walls': [1,1,1,1], #Top, Right, Bottom, Left
		}

pathfinder(entranceRow,entranceColumn)

criticalPathLength = len(critialPath)
criticalPathEnd = critialPath[criticalPathLength-1]
endRow = int(criticalPathEnd.split('-')[0])
endColumn = int(criticalPathEnd.split('-')[1])

# Export Maze as HTML
from xml.etree.ElementTree import Element, SubElement, ElementTree
html = Element('html')
head = SubElement(html,'head')
body = SubElement(html,'body')
mazeDiv = SubElement(body, 'div')
for row in range(totalRows):
	rowDiv = SubElement(mazeDiv,'div style="display: flex;"')
	for column in range(totalColumns):
		styledDiv = 'div style="margin: 0; box-sizing: border-box; height: 10px;width: 10px;'
		if maze[row][column]['walls'][0]:
			styledDiv += "border-top: 0.5px solid black;"
		if maze[row][column]['walls'][1]:
			styledDiv += "border-right: 0.5px solid black;"
		if maze[row][column]['walls'][2]:
			styledDiv += "border-bottom: 0.5px solid black;"
		if maze[row][column]['walls'][3]:
			styledDiv += "border-left: 0.5px solid black;"
		if row == entranceRow and column == entranceColumn:
			styledDiv += "background-color: green;" 
		if row == endRow and column == endColumn:
			styledDiv += "background-color: red;"
		styledDiv += '"'
		cellDiv = SubElement(rowDiv,styledDiv)
		cellDiv.text = " "
ElementTree(html).write('test.html')

# Export maze as JSON


