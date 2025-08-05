// === RPG Webtoon Game with Three.js ===

// === Global Variables & Constants ===
const clock = new THREE.Clock();
let gameStarted = false;
let animationPaused = true;
const DEMON_URL = 'https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/master/2.0/CesiumMan/glTF-Binary/CesiumMan.glb';

let renderer, scene, camera, ambientLight, directionalLight, ground, player, vampire;
let sky, sun, moon;
let animateId;
let demonMixer;
let demonTower;

// === DOM Elements ===
const startMenu = document.getElementById('start-menu');
const settingsModal = document.getElementById('settings-modal');
const helpModal = document.getElementById('help-modal');
const godgameModal = document.getElementById('godgame-modal');

// === Start Menu Logic ===
document.getElementById('btn-newgame').onclick = () => {
    startMenu.style.display = 'none';
    animationPaused = false;
    if (!gameStarted) { initGame(); gameStarted = true; }
};
document.getElementById('btn-continue').onclick = () => {
    startMenu.style.display = 'none';
    animationPaused = false;
    if (!gameStarted) { initGame(); gameStarted = true; }
    setTimeout(() => loadGame(), 500);
};
document.getElementById('btn-settings').onclick = () => { settingsModal.style.display = 'block'; };
document.getElementById('btn-help').onclick = () => { helpModal.style.display = 'block'; };
window.closeSettings = () => { settingsModal.style.display = 'none'; };
window.closeHelp = () => { helpModal.style.display = 'none'; };
function showMenu() {
    startMenu.style.display = 'flex';
    animationPaused = true;
}
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        if (startMenu.style.display === 'none') showMenu();
        else startMenu.style.display = 'none', animationPaused = false;
    }
});

// === Storyline & Characters ===
const storyline = [
    { chapter: 1, title: "Prologue: The Prophecy", description: "The legend of the Chosen One is revealed." },
    { chapter: 2, title: "A Village in Peril", description: "The hero’s hometown is attacked by shadow beasts." },
    { chapter: 3, title: "First Steps", description: "Tutorial: basic movement, combat, and inventory." },
    { chapter: 4, title: "The Lost Heirloom", description: "Retrieve a family relic from goblin caves." },
    { chapter: 5, title: "Meeting the Mentor", description: "Guided by a mysterious mage." },
    { chapter: 6, title: "Forest of Whispers", description: "Learn stealth and magic basics." },
    { chapter: 7, title: "Bandit Ambush", description: "First boss fight; rescue a merchant." },
    { chapter: 8, title: "The Ancient Ruins", description: "Solve puzzles to unlock hidden powers." },
    { chapter: 9, title: "A Friend in Need", description: "Recruit the first party member." },
    { chapter: 10, title: "Departure", description: "Leave the village, beginning the true journey." },
    { chapter: 100, title: "Bonus: The Next Adventure", description: "Tease a sequel or spin-off." }
];
for (let i = 11; i <= 99; i++) {
    storyline.splice(i - 1, 0, { chapter: i, title: `Chapter ${i}`, description: `Story event for chapter ${i}.` });
}
const characters = [
    { name: "Alden", role: "Hero", description: "The chosen one destined to save Eldoria." },
    { name: "Lyra", role: "Mage Mentor", description: "A wise mage who guides the hero." },
    { name: "Garrick", role: "Warrior Companion", description: "A loyal friend and skilled swordsman." },
    { name: "Selene", role: "Rogue", description: "A stealthy thief with a mysterious past." },
    { name: "Vampire Lord", role: "Antagonist", description: "A powerful foe who commands the shadows." }
];
let currentChapter = 1;
function showStoryChapter(chapterNum) {
    const chapter = storyline.find(c => c.chapter === chapterNum);
    if (!chapter) return;
    let infoDiv = document.getElementById('info');
    if (!infoDiv) {
        infoDiv = document.createElement('div');
        infoDiv.id = 'info';
        document.body.appendChild(infoDiv);
    }
    infoDiv.innerHTML = `<h2>Chapter ${chapter.chapter}: ${chapter.title}</h2><p>${chapter.description}</p>`;
}
window.nextChapter = function () {
    currentChapter++;
    if (currentChapter > storyline.length) currentChapter = 1;
    showStoryChapter(currentChapter);
};
showStoryChapter(currentChapter);

// === Party System ===
let party = [characters[0], characters[2]]; // Alden and Garrick
function addToParty(characterName) {
    const char = characters.find(c => c.name === characterName);
    if (char && !party.includes(char)) {
        party.push(char);
        showPartyHUD();
    }
}
function showPartyHUD() {
    let partyDiv = document.getElementById('party');
    if (!partyDiv) {
        partyDiv = document.createElement('div');
        partyDiv.id = 'party';
        document.body.appendChild(partyDiv);
    }
    partyDiv.innerHTML = `<b>Party:</b><br>` + party.map((c, i) =>
        `<span style="cursor:pointer;color:${i === 0 ? '#ffd700' : '#fff'}" onclick="switchActiveCharacter(${i})">${c.name}</span><br>`
    ).join('');
}
window.switchActiveCharacter = function (idx) {
    if (idx > 0 && idx < party.length) {
        const temp = party[0];
        party[0] = party[idx];
        party[idx] = temp;
        showPartyHUD();
        showStoryChapter(currentChapter);
    }
};
showPartyHUD();

// === Inventory System ===
class MedievalInventory {
    constructor() {
        this.items = [];
        this.slots = 20;
        this.initInventory();
    }
    initInventory() {
        const container = document.querySelector('.inventory-slots');
        for (let i = 0; i < this.slots; i++) {
            const slot = document.createElement('div');
            slot.className = 'slot';
            slot.dataset.index = i;
            container.appendChild(slot);
        }
    }
    addItem(item) {
        if (this.items.length >= this.slots) return;
        this.items.push(item);
        this.updateSlot(this.items.length - 1, item);
    }
    updateSlot(index, item) {
        const slot = document.querySelector(`.slot[data-index="${index}"]`);
        slot.innerHTML = `
            <img src="${item.icon}" alt="${item.name}">
            <div class="item-count">${item.stack || ''}</div>
        `;
    }
}
const inventorySystem = new MedievalInventory();
inventorySystem.addItem({
    name: 'Steel Sword',
    icon: 'https://i.imgur.com/5X2Q9yP.png',
    type: 'weapon',
    damage: 35
});
inventorySystem.addItem({
    name: 'Health Potion',
    icon: 'https://i.imgur.com/8zJ3Z7y.png',
    type: 'consumable',
    effect: 'heal'
});

// === Player & Enemy Stats ===
let velocityY = 0;
const gravity = -0.01;
let isOnGround = true;
let playerStats = {
    hp: 100,
    maxHp: 100,
    attack: 35,
    defense: 10
};
let vampireStats = {
    hp: 80,
    maxHp: 80,
    attack: 20,
    defense: 5,
    isAlive: true
};

// === Battle UI & Logic ===
function showBattleUI() {
    let battleDiv = document.getElementById('battle');
    if (!battleDiv) {
        battleDiv = document.createElement('div');
        battleDiv.id = 'battle';
        document.body.appendChild(battleDiv);
    }
    battleDiv.innerHTML = `
        <b>Battle!</b><br>
        <span>Player HP: ${playerStats.hp}/${playerStats.maxHp}</span> |
        <span>Vampire HP: ${vampireStats.hp}/${vampireStats.maxHp}</span><br>
        <button onclick="playerAttack()">Attack</button>
        <button onclick="playerUsePotion()">Use Potion</button>
        <button onclick="endBattle()">Run</button>
    `;
    battleDiv.style.display = 'block';
}
window.showBattleUI = showBattleUI;
function hideBattleUI() {
    const battleDiv = document.getElementById('battle');
    if (battleDiv) battleDiv.style.display = 'none';
}
window.hideBattleUI = hideBattleUI;

window.playerAttack = function () {
    if (!vampireStats.isAlive) return;
    let dmg = Math.max(0, playerStats.attack - vampireStats.defense + Math.floor(Math.random() * 6 - 3));
    vampireStats.hp -= dmg;
    vampire.material.color.set(0xff0000);
    setTimeout(() => vampire.material.color.set(0xffffff), 200);
    showBattleUI();
    if (vampireStats.hp <= 0) {
        vampireStats.isAlive = false;
        vampire.visible = false;
        hideBattleUI();
        alert("You defeated the Vampire Lord!");
        addToParty("Vampire Lord");
        return;
    }
    setTimeout(enemyAttack, 500);
};
window.playerUsePotion = function () {
    const potionIdx = inventorySystem.items.findIndex(i => i.type === 'consumable' && i.effect === 'heal');
    if (potionIdx !== -1) {
        playerStats.hp = Math.min(playerStats.maxHp, playerStats.hp + 40);
        inventorySystem.items.splice(potionIdx, 1);
        document.querySelectorAll('.slot').forEach(slot => slot.innerHTML = '');
        inventorySystem.items.forEach((item, idx) => inventorySystem.updateSlot(idx, item));
        showBattleUI();
        setTimeout(enemyAttack, 500);
    } else {
        alert("No potions left!");
    }
};
function enemyAttack() {
    if (!vampireStats.isAlive) return;
    let dmg = Math.max(0, vampireStats.attack - playerStats.defense + Math.floor(Math.random() * 6 - 3));
    playerStats.hp -= dmg;
    // ...attack scene/video logic...
    // ...damage effect...
    document.getElementById('health').innerText = `Health: ${playerStats.hp}`;
    if (playerStats.hp <= 0) {
        playerStats.hp = 0;
        endBattle();
        return;
    }
    // ...flash player color...
    showBattleUI();
    if (playerStats.hp <= 0) {
        hideBattleUI();
        alert("You were defeated! Reload to try again.");
    }
}
window.endBattle = function () {
    hideBattleUI();
    player.position.x -= 2;
    player.position.z -= 2;
};

// === Movement Controls ===
const moveSpeed = 0.2;
const keys = {};
document.addEventListener('keydown', (e) => {
    keys[e.key.toLowerCase()] = true;
    if (e.key === ' ') {
        if (isOnGround) {
            velocityY = 0.25;
            isOnGround = false;
        }
    }
    if (e.key === 'i') {
        const inv = document.querySelector('.inventory');
        inv.style.display = inv.style.display === 'block' ? 'none' : 'block';
    }
    if (e.key === 'c') {
        const partyDiv = document.getElementById('party');
        if (partyDiv) partyDiv.style.display = partyDiv.style.display === 'none' ? 'block' : 'none';
    }
    if (e.key === 'p') {
        addToParty("Lyra");
    }
});
document.addEventListener('keyup', (e) => { keys[e.key.toLowerCase()] = false; });

// === Demon Tower System ===
// ...DemonTower class definition here (unchanged, see your original code)...

// === Tower UI ===
// ...showTowerUI, showBossUI, hideBossUI, fightTowerMonster, fightTowerBoss...

// === Animation Loop & Game Setup ===
// ...initGame, animate, updateDayNightCycle, loadGame...

// === God Game Modal & Demo Logic ===
// ...godgameModal logic, world state, updateWorldState, logEvent, usePower...

// === Event Listeners for God Game Modal ===
// ...modal open/close logic...

// === End of File ===