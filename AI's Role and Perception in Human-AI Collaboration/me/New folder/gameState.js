export const gameState = {
    currentFloor: 99,
    player: {
        health: 100,
        maxHealth: 100,
        mana: 100,
        maxMana: 100,
        stamina: 100,
        maxStamina: 100,
        position: { x: 0, y: 10, z: 0 },
        velocity: { x: 0, y: 0, z: 0 },
        rotation: 0,
        isGrounded: false,
        isSprinting: false,
        isCrouching: false, // New: Crouch state
        isClimbing: false, // New: Climbing state
        height: 4, // Normal player height
        crouchHeight: 1 // Crouch height
    },
    enemies: [
        {
            name: "Velkisus",
            type: "Boss",
            health: 500,
            maxHealth: 500,
            position: { x: 0, y: 1, z: 50 },
            description: "The guardian of the 99th floor, Velkisus is a formidable foe with immense power."
        }
    ],
    storyPages: [
        {
            title: "CHAPTER 1 PROLOGUE",
            content: `
                <p>"Hey, if any one of y'all want to go back to the past, lemme know. I'll kill y'all."</p>
                <p class="quote">-From the records of <<Carpediem>></p>
                <p class="chapter-subtitle">Prologue. Carpediem</p>
                <p>A sky hidden by the sky-soaring towers. Various ruined structures. Faint sounds of moans and screams. Explosive smoke everywhere. And continued silence. Needless to say, this was the world after the apocalypse.</p>
            `
        },
        {
            title: "CHAPTER 2 MILLIONS OF STABS (1)",
            content: `
                <p>Ten years passed by. It had been a long time. Jaehwan had spent all that time alone on the 99th floor.</p>
                <p>He had gone through thousands of dangers that almost killed him. He faced many dangerous situations as he climbed from the 1st floor to the 99th floor, but the number of dangers he faced just on the 99th floor easily took the cake.</p>
                <p>The boss of 99th floor, Velkisus.</p>
            `
        },
        {
            title: "CHAPTER 3 MILLIONS OF STABS (2)",
            content: `
                <p>Tutorial game?</p>
                <p>So everything had been only a tutorial?</p>
                <p>Through the various floating hologram panels, a figure walked out.</p>
                <p>"Whew, there we go... OH?"</p>
                <p>The figure looked at Jaehwan.</p>
                <p>"WOW! We finally meet!"</p>
            `
        },
        {
            title: "CHAPTER 4 MILLIONS OF STABS (3)",
            content: `
                <p>No way to go back in time?</p>
                <p>"What do you mean? There must be an item that sends you back in this tower..."</p>
                <p>Then Jaehwan realized.</p>
                <p>Beastlain said that there were no items that could send anyone back in time. He also explained that Jaehwan could start from the beginning. It didn't make sense. But there was one thing would allow all of this to make sense.</p>
            `
        }
    ],
    currentStoryPage: 0,
    interactiveObjects: [],
    climbableObjects: [] // New: Array to store climbable objects
};
