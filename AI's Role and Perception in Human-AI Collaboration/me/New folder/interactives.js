import * as THREE from 'three';
import { gameState } from './gameState.js';

export function createInteractiveObjects(scene) {
    // Create story stones
    for (let i = 0; i < 4; i++) {
        const geometry = new THREE.DodecahedronGeometry(2, 0);
        const material = new THREE.MeshStandardMaterial({
            color: 0x5555ff,
            emissive: 0x4444ff,
            emissiveIntensity: 0.3,
            metalness: 0.7,
            roughness: 0.2
        });
        const stone = new THREE.Mesh(geometry, material);

        stone.position.set(
            -30 + i * 20,
            2,
            -30 + i * 10
        );
        stone.castShadow = true;
        stone.receiveShadow = true;
        scene.add(stone);

        // Add floating animation
        if (typeof animateStone === 'function') animateStone(stone);

        // Add to interactive objects
        const interactiveObj = {
            mesh: stone,
            type: 'story',
            distance: 5,
            pageIndex: i
        };
        gameState.interactiveObjects.push(interactiveObj);
    }
    // Add doors at four sides of the map
    const doorPositions = [
        { x: 240, y: 2, z: 0, name: "East Door", target: { x: -240, y: 2, z: 0 } },
        { x: -240, y: 2, z: 0, name: "West Door", target: { x: 240, y: 2, z: 0 } },
        { x: 0, y: 2, z: 240, name: "North Door", target: { x: 0, y: 2, z: -240 } },
        { x: 0, y: 2, z: -240, name: "South Door", target: { x: 0, y: 2, z: 240 } }
    ];

    doorPositions.forEach((door, i) => {
        const geometry = new THREE.BoxGeometry(4, 8, 1.5);
        const material = new THREE.MeshStandardMaterial({
            color: 0x885522,
            metalness: 0.5,
            roughness: 0.3,
            emissive: 0x222200,
            emissiveIntensity: 0.2
        });
        const mesh = new THREE.Mesh(geometry, material);
        mesh.position.set(door.x, door.y + 4, door.z); // y+4 to center door vertically
        mesh.castShadow = true;
        mesh.receiveShadow = true;
        scene.add(mesh);

        // Add to interactive objects
        gameState.interactiveObjects.push({
            mesh: mesh,
            type: 'door',
            distance: 7,
            name: door.name,
            targetPosition: door.target
        });
    });
}

export function createNPC(scene, x, y, z, name) {
    const bodyGeometry = new THREE.CylinderGeometry(1, 1, 3, 8);
    const bodyMaterial = new THREE.MeshStandardMaterial({ color: 0xaa4444 });
    const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
    body.position.set(x, y + 1.5, z);

    const headGeometry = new THREE.SphereGeometry(1, 16, 16);
    const headMaterial = new THREE.MeshStandardMaterial({ color: 0xffaa88 });
    const head = new THREE.Mesh(headGeometry, headMaterial);
    head.position.y = 2.5;

    const npcGroup = new THREE.Group();
    npcGroup.add(body);
    npcGroup.add(head);
    scene.add(npcGroup);

    // Add to interactive objects
    const interactiveObj = {
        mesh: npcGroup,
        type: 'npc',
        distance: 5,
        name: name
    };
    gameState.interactiveObjects.push(interactiveObj);

    // Add floating animation
    if (typeof animateNPC === 'function') animateNPC(npcGroup);
}