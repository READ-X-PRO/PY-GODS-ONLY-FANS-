import * as THREE from 'three';
import { gameState } from './gameState.js';

export function createTower(scene) {
    const towerGroup = new THREE.Group();

    // Base of the tower
    const baseGeometry = new THREE.CylinderGeometry(20, 25, 10, 32);
    const baseMaterial = new THREE.MeshStandardMaterial({
        color: 0x333355,
        metalness: 0.4,
        roughness: 0.6
    });
    const base = new THREE.Mesh(baseGeometry, baseMaterial);
    base.position.y = 5;
    base.castShadow = true;
    base.receiveShadow = true;
    towerGroup.add(base);

    // Main tower structure
    const segments = 100;
    for (let i = 0; i < segments; i++) {
        const radius = 20 - (i * 0.15);
        const height = 5;
        const segmentGeometry = new THREE.CylinderGeometry(radius, radius, height, 32);
        const segmentMaterial = new THREE.MeshStandardMaterial({
            color: i % 10 === 0 ? 0xaa5555 : 0x555577,
            metalness: 0.3,
            roughness: 0.7
        });
        const segment = new THREE.Mesh(segmentGeometry, segmentMaterial);
        segment.position.y = 10 + (i * height);
        segment.castShadow = true;
        segment.receiveShadow = true;
        towerGroup.add(segment);

        // Add windows
        if (i > 0 && i % 5 === 0) {
            for (let j = 0; j < 8; j++) {
                const angle = (j / 8) * Math.PI * 2;
                const windowGeometry = new THREE.BoxGeometry(2, 2, 1);
                const windowMaterial = new THREE.MeshBasicMaterial({
                    color: 0xffff00,
                    emissive: 0xffff00,
                    emissiveIntensity: 0.5
                });
                const window = new THREE.Mesh(windowGeometry, windowMaterial);
                window.position.set(
                    Math.cos(angle) * (radius - 1),
                    segment.position.y,
                    Math.sin(angle) * (radius - 1)
                );
                towerGroup.add(window);
            }
        }
    }

    // Tower top
    const topGeometry = new THREE.ConeGeometry(15, 30, 32);
    const topMaterial = new THREE.MeshStandardMaterial({
        color: 0xaa3333,
        metalness: 0.5,
        roughness: 0.5
    });
    const top = new THREE.Mesh(topGeometry, topMaterial);
    top.position.y = 10 + (segments * 5) + 15;
    top.castShadow = true;
    top.receiveShadow = true;
    towerGroup.add(top);

    // Add glowing effect to top
    const topLight = new THREE.PointLight(0xff5555, 2, 100);
    topLight.position.copy(top.position);
    towerGroup.add(topLight);

    towerGroup.position.set(0, 0, 50);
    scene.add(towerGroup);

    // Add interactive object for tower
    const towerInteractive = {
        mesh: base,
        type: 'tower',
        distance: 10,
        pageIndex: 0
    };
    gameState.interactiveObjects.push(towerInteractive);
}