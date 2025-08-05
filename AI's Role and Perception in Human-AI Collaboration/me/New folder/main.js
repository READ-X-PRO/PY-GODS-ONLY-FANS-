import * as THREE from 'three';
import { createEnvironment } from './environment.js';
import { createPlayer } from './player.js';
import { createTower } from './tower.js';
import { createInteractiveObjects, createNPC } from './interactives.js';
import { gameState } from './gameState.js';

let scene, camera, renderer, controls;
let player, ground, tower, skybox;
let directionalLight, ambientLight;
let clock = new THREE.Clock();
let cameraMode = 'follow';
let cameraTarget = new THREE.Vector3();
let cameraLerpAlpha = 0.12; // Smoothing factor

function init() {
    // Initialize scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0a1a);
    scene.fog = new THREE.Fog(0x0a0a1a, 50, 300);

    // Initialize camera
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(0, 15, 20);
    camera.lookAt(0, 0, 0);

    // Initialize renderer
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.shadowMap.enabled = true;
    document.getElementById('gameCanvas').appendChild(renderer.domElement);

    // Initialize lights
    ambientLight = new THREE.AmbientLight(0x404040);
    scene.add(ambientLight);

    directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(50, 100, 50);
    directionalLight.castShadow = true;
    directionalLight.shadow.mapSize.width = 1024;
    directionalLight.shadow.mapSize.height = 1024;
    scene.add(directionalLight);

    // Create environment
    createEnvironment(scene);

    // Create player
    createPlayer(scene);

    // Create Tower of Nightmares
    createTower(scene);

    // Create NPCs
    createNPC(scene, -20, 0, -20, 'Yoonhwan');
    createNPC(scene, 25, 0, -15, 'Seoyul');
    createNPC(scene, 0, 0, 25, 'Jay');

    // Create interactive objects
    createInteractiveObjects(scene);

    // Add event listeners
    window.addEventListener('resize', onWindowResize);
    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);
    window.addEventListener('keydown', function (event) {
        if (event.key.toLowerCase() === 'c') {
            cameraMode = cameraMode === 'follow' ? 'free' : 'follow';
            controls.enabled = cameraMode === 'free';
        }
    });
    window.addEventListener('keydown', function (event) {
        if (event.key === 'Escape') {
            toggleGameUI();
        }
    });
    // Initialize controls
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enabled = cameraMode === 'free'; // Only enable OrbitControls in free mode
    controls.target.set(0, 5, 50);
    controls.update();

    // Hide loading screen and start animation
    setTimeout(() => {
        document.getElementById('loadingScreen').style.display = 'none';
        animate();
    }, 3000);

    // Simulate loading progress
    simulateLoading();
}

function animate() {
    requestAnimationFrame(animate);

    const delta = Math.min(clock.getDelta(), 0.1) * 60;

    // Update game state
    updatePlayer(delta);

    // Rotate the tower slowly
    if (tower) {
        tower.rotation.y += 0.001 * delta;
    }

    // Camera logic
    if (cameraMode === 'follow') {
        // Smoothly follow the player
        const playerHeightAdjust = gameState.player.isCrouching ? gameState.player.crouchHeight : gameState.player.height;
        const targetPos = new THREE.Vector3(
            gameState.player.position.x,
            gameState.player.position.y + playerHeightAdjust + 10,
            gameState.player.position.z + 20
        );
        camera.position.lerp(targetPos, cameraLerpAlpha);

        cameraTarget.set(
            gameState.player.position.x,
            gameState.player.position.y + playerHeightAdjust / 2,
            gameState.player.position.z
        );
        camera.lookAt(cameraTarget);
    } else if (controls) {
        // OrbitControls target is always the player
        controls.target.set(
            gameState.player.position.x,
            gameState.player.position.y + (gameState.player.isCrouching ? gameState.player.crouchHeight / 2 : gameState.player.height / 2),
            gameState.player.position.z
        );
        controls.update();
    }

    // Player animation (simple walk animation, add crouch/climb animations here)
    if (player && player.userData) {
        const t = performance.now() * 0.002;
        if (gameState.player.isClimbing) {
            // Simple climbing animation (e.g., arms/legs moving up/down)
            if (player.userData.leftArm) player.userData.leftArm.rotation.x = Math.sin(t * 8) * 0.5;
            if (player.userData.rightArm) player.userData.rightArm.rotation.x = -Math.sin(t * 8) * 0.5;
            if (player.userData.leftLeg) player.userData.leftLeg.rotation.x = Math.sin(t * 8) * 0.5;
            if (player.userData.rightLeg) player.userData.rightLeg.rotation.x = -Math.sin(t * 8) * 0.5;
        } else if (Math.abs(gameState.player.velocity.x) > 0.01 || Math.abs(gameState.player.velocity.z) > 0.01) {
            // Simple walk animation if moving horizontally
            if (player.userData.leftArm) player.userData.leftArm.rotation.x = Math.sin(t * 4) * 0.5;
            if (player.userData.rightArm) player.userData.rightArm.rotation.x = -Math.sin(t * 4) * 0.5;
            if (player.userData.leftLeg) player.userData.leftLeg.rotation.x = -Math.sin(t * 4) * 0.5;
            if (player.userData.rightLeg) player.userData.rightLeg.rotation.x = Math.sin(t * 4) * 0.5;
        } else {
            // Reset pose when idle
            if (player.userData.leftArm) player.userData.leftArm.rotation.x = 0;
            if (player.userData.rightArm) player.userData.rightArm.rotation.x = 0;
            if (player.userData.leftLeg) player.userData.leftLeg.rotation.x = 0;
            if (player.userData.rightLeg) player.userData.rightLeg.rotation.x = 0;
        }
        // Hair sway
        if (player.userData.hair) player.userData.hair.rotation.z = Math.sin(t) * 0.1;
    }
    // Render the scene
    renderer.render(scene, camera);
}

init();