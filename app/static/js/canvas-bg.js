/**
 * 3D Floating Medical Cross & EKG Heartbeat Canvas Visual Engine
 * Designed for PulseCare HMS (Hospital Management System)
 * Features 3D projected rotating Medical Plus (+) crosses, depth perspective scaling,
 * interactive cursor parallax, and smooth animated EKG heartbeat pulse waves.
 */

document.addEventListener("DOMContentLoaded", function () {
    const canvas = document.createElement("canvas");
    canvas.id = "medical-3d-canvas";
    canvas.style.position = "fixed";
    canvas.style.top = "0";
    canvas.style.left = "0";
    canvas.style.width = "100vw";
    canvas.style.height = "100vh";
    canvas.style.pointerEvents = "none";
    canvas.style.zIndex = "-1";
    document.body.prepend(canvas);

    const ctx = canvas.getContext("2d");
    let width, height;
    let medicalCrosses = [];
    let mouse = { x: 0, y: 0, targetX: 0, targetY: 0 };
    let ekgProgress = 0;

    function resize() {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
        initMedicalCrosses();
    }

    window.addEventListener("resize", resize);
    window.addEventListener("mousemove", function (e) {
        mouse.targetX = (e.clientX - width / 2) * 0.05;
        mouse.targetY = (e.clientY - height / 2) * 0.05;
    });

    // 3D Medical Cross Object Class
    class MedicalCross3D {
        constructor() {
            this.reset();
            // Start at random Z position
            this.z = Math.random() * 800 - 400;
        }

        reset() {
            this.x = (Math.random() - 0.5) * width * 1.5;
            this.y = (Math.random() - 0.5) * height * 1.5;
            this.z = 600; // Far in background
            this.size = Math.random() * 28 + 18; // Size of cross arms
            this.thickness = this.size * 0.38;

            // Rotation angles & speeds
            this.rotX = Math.random() * Math.PI * 2;
            this.rotY = Math.random() * Math.PI * 2;
            this.rotZ = Math.random() * Math.PI * 2;

            this.vRotX = (Math.random() - 0.5) * 0.018;
            this.vRotY = (Math.random() - 0.5) * 0.022;
            this.vRotZ = (Math.random() - 0.5) * 0.015;

            // Velocity towards viewer
            this.vz = (Math.random() * 0.6 + 0.3);

            // Palette: Cyan, Teal, Emerald Green
            const colors = [
                { main: '56, 189, 248', glow: '14, 165, 233' },   // Medical Cyan
                { main: '45, 212, 191', glow: '20, 184, 166' },   // Medical Teal
                { main: '52, 211, 153', glow: '16, 185, 129' },   // Health Emerald
                { main: '129, 140, 248', glow: '99, 102, 241' }   // Care Indigo
            ];
            this.color = colors[Math.floor(Math.random() * colors.length)];
        }

        update() {
            this.rotX += this.vRotX;
            this.rotY += this.vRotY;
            this.rotZ += this.vRotZ;

            // Move closer to camera
            this.z -= this.vz;

            // Loop back when passed camera
            if (this.z < -200) {
                this.reset();
            }
        }

        draw(theme) {
            const focalLength = 450;
            const perspective = focalLength / (focalLength + this.z);

            if (perspective <= 0) return;

            // Apply parallax offset
            const projX = (this.x + mouse.x * (this.z / 400)) * perspective + width / 2;
            const projY = (this.y + mouse.y * (this.z / 400)) * perspective + height / 2;
            const projSize = this.size * perspective;
            const projThick = this.thickness * perspective;

            if (projX < -100 || projX > width + 100 || projY < -100 || projY > height + 100) return;

            // Alpha based on depth
            const alpha = Math.min(1, Math.max(0, (600 - this.z) / 600)) * (theme === 'dark' ? 0.75 : 0.65);

            ctx.save();
            ctx.translate(projX, projY);

            // Apply 3D-like rotation transformation
            const cosX = Math.cos(this.rotX);
            const sinX = Math.sin(this.rotX);
            const cosY = Math.cos(this.rotY);
            const sinY = Math.sin(this.rotY);

            ctx.transform(cosY, sinX * sinY, 0, cosX, 0, 0);
            ctx.rotate(this.rotZ);

            // Draw Outer Glow
            ctx.shadowBlur = 16 * perspective;
            ctx.shadowColor = `rgba(${this.color.glow}, ${alpha * 0.8})`;

            // Draw Medical Cross Shape (+)
            ctx.fillStyle = theme === 'dark'
                ? `rgba(${this.color.main}, ${alpha})`
                : `rgba(${this.color.glow}, ${alpha * 0.85})`;

            ctx.beginPath();
            // Vertical arm
            ctx.roundRect(-projThick / 2, -projSize / 2, projThick, projSize, 4 * perspective);
            // Horizontal arm
            ctx.roundRect(-projSize / 2, -projThick / 2, projSize, projThick, 4 * perspective);
            ctx.fill();

            // Inner highlight for 3D bevel effect
            ctx.shadowBlur = 0;
            ctx.fillStyle = `rgba(255, 255, 255, ${alpha * 0.35})`;
            ctx.beginPath();
            ctx.roundRect(-projThick / 4, -projSize / 2.2, projThick / 2, projSize / 2.2, 2 * perspective);
            ctx.fill();

            ctx.restore();
        }
    }

    function initMedicalCrosses() {
        medicalCrosses = [];
        const count = Math.floor((width * height) / 26000) + 12;
        for (let i = 0; i < count; i++) {
            medicalCrosses.push(new MedicalCross3D());
        }
    }

    // EKG Heartbeat Waveform Renderer
    function drawEKGWave(theme) {
        ekgProgress += 2.5;
        if (ekgProgress > width + 300) {
            ekgProgress = -100;
        }

        const baseY = height * 0.82;
        const ekgColor = theme === 'dark' ? 'rgba(56, 189, 248, ' : 'rgba(14, 165, 233, ';

        ctx.save();
        ctx.beginPath();
        ctx.lineWidth = 2;

        const pulseWidth = 140;
        const startX = ekgProgress - pulseWidth;

        // Gradient line trailing
        const grad = ctx.createLinearGradient(startX, 0, ekgProgress, 0);
        grad.addColorStop(0, `${ekgColor}0)`);
        grad.addColorStop(0.7, `${ekgColor}0.25)`);
        grad.addColorStop(1, `${ekgColor}0.75)`);
        ctx.strokeStyle = grad;

        ctx.moveTo(Math.max(0, startX), baseY);

        // Draw flat line leading to heartbeat pulse
        for (let x = Math.max(0, startX); x <= Math.min(width, ekgProgress); x += 5) {
            let relX = x - (ekgProgress - pulseWidth / 2);
            let y = baseY;

            // EKG Pulse formula (P-Q-R-S-T wave)
            if (relX > -40 && relX < -25) {
                y -= 8 * Math.sin((relX + 32.5) / 15 * Math.PI); // P wave
            } else if (relX >= -25 && relX < -15) {
                y += 12 * Math.sin((relX + 20) / 10 * Math.PI); // Q wave
            } else if (relX >= -15 && relX < 10) {
                y -= 55 * Math.sin((relX + 2.5) / 25 * Math.PI); // R spike (high positive)
            } else if (relX >= 10 && relX < 25) {
                y += 22 * Math.sin((relX - 17.5) / 15 * Math.PI); // S wave (negative dip)
            } else if (relX >= 25 && relX < 50) {
                y -= 14 * Math.sin((relX - 37.5) / 25 * Math.PI); // T wave
            }

            ctx.lineTo(x, y);
        }

        ctx.stroke();

        // Glowing EKG Lead Dot
        if (ekgProgress > 0 && ekgProgress < width) {
            ctx.shadowBlur = 12;
            ctx.shadowColor = theme === 'dark' ? '#38bdf8' : '#0284c7';
            ctx.fillStyle = theme === 'dark' ? '#38bdf8' : '#0284c7';
            ctx.beginPath();
            ctx.arc(ekgProgress, baseY, 3.5, 0, Math.PI * 2);
            ctx.fill();
        }

        ctx.restore();
    }

    // Animation Loop
    function animate() {
        ctx.clearRect(0, 0, width, height);

        // Smooth mouse lerp
        mouse.x += (mouse.targetX - mouse.x) * 0.05;
        mouse.y += (mouse.targetY - mouse.y) * 0.05;

        const currentTheme = document.documentElement.getAttribute("data-bs-theme") || "dark";

        // Sort crosses by Z depth (draw furthest first)
        medicalCrosses.sort((a, b) => b.z - a.z);

        // Draw 3D Medical Crosses
        for (let cross of medicalCrosses) {
            cross.update();
            cross.draw(currentTheme);
        }

        // Draw Heartbeat EKG Pulse Wave
        drawEKGWave(currentTheme);

        requestAnimationFrame(animate);
    }

    resize();
    animate();
});
