async function main() {

  function rollDice(bonus = 0,dice = 20,isAttack = false){
    roll = Math.ceil(Math.random()*dice)
    console.log("pre roll of " + roll)
    if (isAttack){
      if (roll == 20){
        return 'critHit'
      }
      if (roll == 1){
        return 'critMiss'
      }
    }
    console.log("post roll of " + roll)
    total = roll + bonus
    return total
  }

  const mazeRes = await fetch('maze.json')
  const mazeData = await mazeRes.json()

  const heroRes = await fetch('character.json')
  const heroData = await heroRes.json()

  heroData['combat']['initiative'] += rollDice(heroData['combat']['initiative'])
  heroData['combat']['weilding'] = 'war-pick'


  const monsterRes = await fetch('monster.json')
  const monsterData = await monsterRes.json()

  const hero = document.getElementById('hero');
  const rooms = document.getElementsByClassName("map-item")

  const startRoom = document.getElementById('entry')
  startRoom.addEventListener("click", () => fliproom(startRoom), {once: true})

    function fliproom(room) {
      room.classList.toggle("map-card")
  }

  const exit = document.getElementById('exit')
  exit.addEventListener("click", () => clickExit())

  function clickExit(){
    console.log("You're a winner baby")
  }

  const doors = document.getElementsByClassName('door');
  for (let i=0; i < doors.length; i++) {
    const door = doors[i]
    door.addEventListener("click", () => clickDoor(door))
  }

  function goto(room){
    hero.remove()
    room.querySelector('.map-card-front').appendChild(hero);
  }

  function clickDoor(door){
    const isMonster = door.parentElement.querySelector('.monster')
    if (door.dataset.closed == 'true'){
      if (isMonster == null){
       openDoor(door)
      }
      else {
       alert('A monster guards the path')
      }
    }

  else if(door.dataset.closed == 'false'){

    const room = door.closest(".map-item")
    let row = parseInt(room.dataset.row)
    let col = parseInt(room.dataset.col)

    if (door.classList.contains('door-bottom')){
      row += 1
    } else if (door.classList.contains('door-right')){
      col += 1

    } else if (door.classList.contains('door-top')){
      row -= 1

    } else if (door.classList.contains('door-left')){
      col -= 1
    }

    const adjRoomSelect = `[data-row="${row}"][data-col="${col}"]`
    const adjRoom = document.querySelector(adjRoomSelect)

    if (isMonster){
      const room = isMonster.closest(".map-item")
      let row = parseInt(room.dataset.row)
      let col = parseInt(room.dataset.col)
      const monsterStats = mazeData[row][col]['monster']
      attack(monsterStats,heroData,isMonster)
    }
    goto(adjRoom)
    }
  }

  function openDoor(door){
    door.children[0].style.display = 'none';
    door.dataset.closed = 'false'

    const room = door.closest(".map-item")
    let row = parseInt(room.dataset.row)
    let col = parseInt(room.dataset.col)
    let adjDoorSelect = ""

    if (door.classList.contains('door-bottom')){
      row += 1
      adjDoorSelect = '.door-top'
    } else if (door.classList.contains('door-right')){
      col += 1
      adjDoorSelect = '.door-left'
    } else if (door.classList.contains('door-top')){
      row -= 1
      adjDoorSelect = '.door-bottom'
    } else if (door.classList.contains('door-left')){
      col -= 1
      adjDoorSelect = '.door-right'
    }

    const adjRoomSelect = `[data-row="${row}"][data-col="${col}"]`
    const adjRoom = document.querySelector(adjRoomSelect)
    const adjDoor = adjRoom.querySelector(adjDoorSelect)

    fliproom(adjRoom)

    adjDoor.children[0].style.display = 'none';
    adjDoor.dataset.closed = 'false'
  }

  const monsters = document.getElementsByClassName('monster');
  for (let i=0; i < monsters.length; i++) {
    const monster = monsters[i]

    const room = monster.closest(".map-item")
    let row = parseInt(room.dataset.row)
    let col = parseInt(room.dataset.col)
    const monsterStats = mazeData[row][col]['monster']

    monsterStats['combat']['initiative'] += rollDice(monsterStats['combat']['initiative'])
    monster.addEventListener("click", () => clickMonster(monsterStats,monster))
  }

  function damage(dice){ 
    const regex = /([0-9+])d([0-9+])\+([0-9+])/;
    const damageSplit = dice.split(regex)
    var damageDice = damageSplit.map(function (x) { 
      return parseInt(x, 10); 
    })
    let damageTotal = damageDice[3]
    for (let i=0; i < parseInt(damageDice[1]); i++){
      damageTotal += rollDice(0,damageDice[2])
    }
    return damageTotal
  }

  function heroDeath(){
    console.log('game over')
  }

  function attack(attacker,defender,monsterDiv){
    let attackerType = attacker['details']['entity']
    let defenderType = defender['details']['entity']
    let attackRoll = 0
    let damageTypes = ""

    if (attackerType == 'hero'){ 
      attackRoll = rollDice(5,20,true)
      damageTypes = Object.keys(attacker['inventory']['weapon']['war-pick']['damage'])
    } else if (attackerType == 'monster'){
      attackOptions = Object.keys(attacker['actions'])
      attackChoice = attackOptions[Math.floor(Math.random()*attackOptions.length)]
      attackRoll = rollDice(attacker['bonus'],20,true)
      damageTypes = Object.keys(attacker['actions'][attackChoice]['damage'])
    }
    console.log("attack roll of " + attackRoll)
    if (attackRoll == 'critHit'){
        for (let i=0; i < damageTypes.length; i++) {
          if (attackerType == 'hero'){
            damageAmount = attacker['inventory']['weapon']['war-pick']['damage'][damageTypes[i]]
          } else if (attackerType == 'monster') {
            damageAmount = attacker['actions'][attackChoice]['damage'][damageTypes[i]]
          }
          const damageDealt1 = damage(damageAmount)
          const damageDealt2 = damage(damageAmount)

          console.log(attackerType + " critical hits " + defenderType + " for " + damageDealt + " " + damageTypes[i] + " damage and " + damageDealt + " " + damageTypes[i] + " damage")

          defender['combat']['hp-current'] -= damageDealt1
          defender['combat']['hp-current'] -= damageDealt2
        }
    } else if (attackRoll == 'critMiss'){
      console.log(attackerType + " completely misses " + defenderType)

    } else if (attackRoll > defender['combat']['ac']){
        for (let i=0; i < damageTypes.length; i++) {
          if (attackerType == 'hero'){
            damageAmount = attacker['inventory']['weapon']['war-pick']['damage'][damageTypes[i]]
          } else if (attackerType == 'monster') {
            damageAmount = attacker['actions'][attackChoice]['damage'][damageTypes[i]]
          }
          const damageDealt = damage(damageAmount)

          console.log(attackerType + " hits " + defenderType + " for " + damageDealt + " " + damageTypes[i] + " damage")

          defender['combat']['hp-current'] -= damageDealt
        }
    } else {
      console.log(attackerType + " misses " + defenderType)
    }

    console.log(defenderType + " is at " + defender['combat']['hp-current'])

    if (defender['combat']['hp-current'] <= 0){
      if (defenderType == 'monster'){
        monsterDiv.remove()
      }
      if (defenderType == 'hero'){
        heroDeath()
        hero.remove()
      }
    }
  }

  function clickMonster(monster,monsterDiv){
    if (heroData['combat']['initiative'] >= monster['combat']['initiative']){
      attack(heroData,monster,monsterDiv)
      attack(monster,heroData,monsterDiv)
    } else {
      attack(monster,heroData,monsterDiv)
      attack(heroData,monster,monsterDiv)
    }
  }
}
/*todo

pickup(loot)
  add loot to inventory

search(room)
  if loot = hidden
    loot = visible
  else
    "nothing here"

levelUp()
  hero level ++
  buildMaze()
*/

main();