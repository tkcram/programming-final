async function importMaze(){
	const mazeRes = await fetch('maze.json')
	const mazeData = await mazeRes.json()

	function createDoor(direction){
		return `
			<div class = "door door-${direction}" data-closed="true">
	      <img src="http://www.clker.com/cliparts/2/7/f/d/1220546286832083251ajvdvegt_2D_components_-_door_(85cm).svg.hi.png"/>
	    </div>
		`
	}
	function createRoom(row, col, doors, danger) {
	  const doorsDom = []
	  if (doors[0]) {
	  	doorsDom.push(createDoor('top'))
	  } 
	  if (doors[1]) {
	  	doorsDom.push(createDoor('right'))
	  } 
	  if (doors[2]) {
	  	doorsDom.push(createDoor('bottom'))
	  } 
	  if (doors[3]) {
	  	doorsDom.push(createDoor('left'))
	  }

	  let hero = ''
	  if(row === 0 && col === 0 ){
	  	hero = `
	  	  <div class = "hero" id="hero"> 
		      <img src="https://www.pinclipart.com/picdir/big/541-5413340_transparent-character-traits-clipart-joy-inside-out-png.png"/>
		    </div>
			`
		}
		let monster = ''
		if (danger){
			monster = `
	  	  <div class = "monster"> 
		      <img src="https://i.pinimg.com/originals/c9/20/b4/c920b4408d20a6150b902ac435ebd2cc.png"/>
		    </div>
			`
		}
		let exit = ''
		if (row === 4 && col === 4 ){
			monster = `
	  	  <div id = "exit"> 
		      <img src="https://media.istockphoto.com/vectors/closed-door-drawing-vector-id865663698"/>
		    </div>
			`
		}

	  const room = `
			<div class="map-item" id="entry" data-row="${row}" data-col="${col}">
	      <div class="map-card-inner">
	        <div class="map-card-back">
	          <img class="map-image" src="https://r1.ilikewallpaper.net/ipad-air-wallpapers/download/104429/outrun-abstract-square-4k-ipad-air-wallpaper-ilikewallpaper_com.jpg" alt="<%= title2 %> by <%= creator2 %>" />
	        </div>
	        <div class="map-card-front test-outer">
	        	${hero}
		        ${doorsDom.join('')}
		        ${monster}
	        </div>
	      </div>
	    </div>
	  ` 
	  return room
	}

	function createRow(row, rooms){
		return `
			<div id="row-${row}" class="row">
				${rooms.join('')}
			</div>
		`
	}

	const maze = mazeData.forEach((row, rowIndex) => {
		const rooms = row.map((col, colIndex) => {
			return createRoom(rowIndex, colIndex, col.doors, col.monster)
		})

		const rowDom = createRow(rowIndex, rooms);
		document.getElementById('map').insertAdjacentHTML('beforeend', rowDom)
	})
}

importMaze()
