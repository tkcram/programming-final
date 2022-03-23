const cards = document.getElementsByClassName("map-item")
for (let i=0; i < cards.length; i++) {
  const card = cards[i]

  card.addEventListener("click", () => flipcard(card), {once: true})
}

function flipcard(card) {
  card.classList.toggle("map-card")
  card.addEventListener("click", () => goTo(card))
}

function goTo(card) {
  let dungeonCleared = false;
  if (card.classList.contains('monster')) {
    var monsterHealth = document.getElementById("monster-health").value;
    console.log(monsterHealth)
    if (monsterHealth > 0) {
      document.getElementById("monster-health").value -= 25;
      document.getElementById("hero-health").value -= 20;
    }
    if (monsterHealth <= 0) {
      const monster = document.getElementById("monster")
      monster.remove();
    } else {
      return;
    }
  }
  if (card.classList.contains('door')) {
    const door = document.getElementById("door")
    door.remove();
    dungeonCleared = true;
  }
  const hero = document.getElementById('hero'); 
  hero.remove();
  card.getElementsByClassName('map-card-front')[0].appendChild(hero);
  if (dungeonCleared){
    alert("You escaped the Dungeon!!!")
  }
}

// What else has to be done here...
// Need to check if the character is adjacent to a card to see if they can access it
// Need to introduce RNG to the attack rolls
// Need to connect to the backend
//  Recieve character updates
//   Receive map (is that done here?)