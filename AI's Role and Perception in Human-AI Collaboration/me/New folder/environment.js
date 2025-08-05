import * as THREE from 'three';
import { gameState } from './gameState.js';

export function createEnvironment(scene) {
    // Create ground
    const groundGeometry = new THREE.PlaneGeometry(500, 500);
    const groundMaterial = new THREE.MeshStandardMaterial({
        color: 0x1a3a1a,
        roughness: 0.9,
        metalness: 0.1
    });
    const ground = new THREE.Mesh(groundGeometry, groundMaterial);
    ground.rotation.x = -Math.PI / 2;
    ground.receiveShadow = true;
    scene.add(ground);

    // Create mountains in the distance
    const mountainGroup = new THREE.Group();
    for (let i = 0; i < 20; i++) {
        const size = 50 + Math.random() * 100;
        const mountainGeometry = new THREE.ConeGeometry(size, 100 + Math.random() * 200, 4);
        const mountainMaterial = new THREE.MeshStandardMaterial({
            color: 0x333355,
            roughness: 0.8
        });
        const mountain = new THREE.Mesh(mountainGeometry, mountainMaterial);

        mountain.position.set(
            -250 + Math.random() * 500,
            -50,
            -250 + Math.random() * 500
        );
        mountain.rotation.y = Math.random() * Math.PI;
        mountain.castShadow = true;
        mountain.receiveShadow = true;

        mountainGroup.add(mountain);
    }
    scene.add(mountainGroup);

    // Create skybox
    const skyGeometry = new THREE.SphereGeometry(1000, 32, 32);
    const skyMaterial = new THREE.MeshBasicMaterial({
        color: 0x0a1a3a,
        side: THREE.BackSide
    });
    const skybox = new THREE.Mesh(skyGeometry, skyMaterial);
    scene.add(skybox);

    // Add stars
    const starsGeometry = new THREE.BufferGeometry();
    const starsMaterial = new THREE.PointsMaterial({
        color: 0xffffff,
        size: 1.5,
        sizeAttenuation: true
    });

    const starsVertices = [];
    for (let i = 0; i < 10000; i++) {
        const x = THREE.MathUtils.randFloatSpread(2000);
        const y = THREE.MathUtils.randFloatSpread(2000);
        const z = THREE.MathUtils.randFloatSpread(2000);
        starsVertices.push(x, y, z);
    }

    starsGeometry.setAttribute('position', new THREE.Float32BufferAttribute(starsVertices, 3));
    const starField = new THREE.Points(starsGeometry, starsMaterial);
    scene.add(starField);

    // Add some vegetation
    for (let i = 0; i < 100; i++) {
        const height = 2 + Math.random() * 5;
        const geometry = new THREE.CylinderGeometry(0.1, 0.1, height, 8);
        const material = new THREE.MeshStandardMaterial({ color: 0x2a8a2a });
        const plant = new THREE.Mesh(geometry, material);

        plant.position.set(
            -200 + Math.random() * 400,
            height / 2,
            -200 + Math.random() * 400
        );
        plant.castShadow = true;
        scene.add(plant);
    }

    // Add statue (assume addStatue is globally available or imported)
    if (typeof addStatue === 'function') addStatue(scene);

    // Example climbable wall
    const wallGeometry = new THREE.BoxGeometry(10, 20, 1);
    const wallMaterial = new THREE.MeshStandardMaterial({ color: 0x888888 });
    const climbableWall = new THREE.Mesh(wallGeometry, wallMaterial);
    climbableWall.position.set(30, 10, 0); // Position it
    climbableWall.castShadow = true;
    climbableWall.receiveShadow = true;
    scene.add(climbableWall);
    gameState.climbableObjects.push(climbableWall); // Add to climbable objects
}
