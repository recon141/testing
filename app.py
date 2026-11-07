                function resizeCanvas() {
                    const dpr = Math.min(window.devicePixelRatio || 1, 2);
                    const width = canvas.clientWidth;
                    const height = canvas.clientHeight;

                    canvas.width = width * dpr;
                    canvas.height = height * dpr;
                    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
                }

                resizeCanvas();
                window.addEventListener("resize", resizeCanvas);

                const particles = [];
                const colors = ["#111111", "#444444", "#777777", "#aaaaaa"];

                function random(min, max) {
                    return Math.random() * (max - min) + min;
                }

                function createFirework(x, y) {
                    const color = colors[
                        Math.floor(Math.random() * colors.length)
                    ];
                    const particleCount = 65;

                    for (let i = 0; i < particleCount; i++) {
                        const angle = (Math.PI * 2 * i) / particleCount;
                        const speed = random(1.2, 4.2);

                        particles.push({
                            x: x,
                            y: y,
                            vx: Math.cos(angle) * speed,
                            vy: Math.sin(angle) * speed,
                            life: random(55, 90),
                            maxLife: 90,
                            radius: random(1.2, 2.5),
                            color: color
                        });
                    }
                }

                function launchRandomFirework() {
                    const width = canvas.clientWidth;
                    const height = canvas.clientHeight;

                    createFirework(
                        random(width * 0.15, width * 0.85),
                        random(height * 0.15, height * 0.6)
                    );
                }

                // 처음에 여러 폭죽을 연속으로 터뜨립니다.
                launchRandomFirework();
                setTimeout(launchRandomFirework, 300);
                setTimeout(launchRandomFirework, 650);
                setTimeout(launchRandomFirework, 1000);
                setTimeout(launchRandomFirework, 1400);
                setTimeout(launchRandomFirework, 1850);

                let frame = 0;

                function animate() {
                    const width = canvas.clientWidth;
                    const height = canvas.clientHeight;

                    ctx.clearRect(0, 0, width, height);

                    for (let i = particles.length - 1; i >= 0; i--) {
                        const p = particles[i];

                        p.x += p.vx;
                        p.y += p.vy;
                        p.vy += 0.025;
                        p.vx *= 0.992;
                        p.vy *= 0.992;
                        p.life -= 1;

                        ctx.globalAlpha = Math.max(0, p.life / p.maxLife);
                        ctx.fillStyle = p.color;
                        ctx.beginPath();
                        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                        ctx.fill();

                        if (p.life <= 0) {
                            particles.splice(i, 1);
                        }
                    }

                    ctx.globalAlpha = 1;

                    // 잠시 동안 추가 폭죽이 나타나도록 합니다.
                    frame += 1;
                    if (frame % 48 === 0 && frame < 420) {
                        launchRandomFirework();
                    }

                    requestAnimationFrame(animate);
                }

                animate();
            </script>
        </body>
        </html>
        """,
        height=400,
        scrolling=False,
    )
