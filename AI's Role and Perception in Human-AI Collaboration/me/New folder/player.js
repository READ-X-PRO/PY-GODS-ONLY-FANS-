import * as THREE from 'three';
import { gameState } from './gameState.js';

export let player;

export function createPlayer(scene) {
    const loader = new THREE.GLTFLoader();
    loader.load('enemy.glb', function (gltf) {
        player = gltf.scene;
        let leftArm, rightArm, leftLeg, rightLeg, hair;
        player.traverse(function (child) {
            if (child.isBone) {
                if (child.name.toLowerCase().includes('leftarm')) leftArm = child;
                if (child.name.toLowerCase().includes('rightarm')) rightArm = child;
                if (child.name.toLowerCase().includes('leftleg')) leftLeg = child;
                if (child.name.toLowerCase().includes('rightleg')) rightLeg = child;
                if (child.name.toLowerCase().includes('hair')) hair = child;
            }
        });
        player.userData = { leftArm, rightArm, leftLeg, rightLeg, hair };

        player.traverse(function (child) {
            if (child.isMesh) {
                child.castShadow = true;
                child.receiveShadow = true;
            }
        });
        player.scale.set(2, 2, 2); // Adjust scale as needed
        player.position.set(0, 10, 0);
        scene.add(player);
    }, undefined, function (error) {
        console.error('Error loading player model:', error);
    });
}

// Remove the broken updatePlayer export (should be handled in game.js/main.js)