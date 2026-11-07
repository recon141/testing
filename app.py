
# 버튼을 누르면 환영 문구와 폭죽 애니메이션을 표시합니다.
if "entered" not in st.session_state:
    st.session_state.entered = False

_, center_col, _ = st.columns([1, 1.2, 1])
with center_col:
    if st.button("들어가기", use_container_width=True):
        st.session_state.entered = True

if st.session_state.entered:
    st.markdown(
        """
        <h1 style="
            color:#111111;
            text-align:center;
            font-size:clamp(2.2rem, 6vw, 3.8rem);
            font-weight:800;
            letter-spacing:-0.05em;
            margin-top:2.5rem;
            ">
            환영합니다!
        </h1>
        """,
        unsafe_allow_html=True,
    )

    components.html(
        """
        <div style="width:100%; height:390px; position:relative; overflow:hidden;
                    background:#ffffff;">
          <canvas id="fireworks" style="width:100%;height:100%;display:block;"></canvas>
        </div>
        <script>
        (() => {
          const canvas = document.getElementById("fireworks");
          const ctx = canvas.getContext("2d");
          const resize = () => {
            const dpr = Math.min(window.devicePixelRatio || 1, 2);
            canvas.width = canvas.clientWidth * dpr;
            canvas.height = canvas.clientHeight * dpr;
            ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
          };
          resize();

          const colors = ["#111111", "#555555", "#888888", "#b0b0b0"];
          const particles = [];
          const bursts = [];
          const random = (min, max) => Math.random() * (max - min) + min;

          function burst(x, y) {
            const color = colors[Math.floor(Math.random() * colors.length)];
            const count = 65;
            for (let i = 0; i < count; i++) {
              const angle = (Math.PI * 2 * i) / count + random(-0.08, 0.08);
              const speed = random(1.2, 4.2);
              particles.push({
                x, y,
                vx: Math.cos(angle) * speed,
                vy: Math.sin(angle) * speed,
                life: random(55, 95),
                maxLife: 95,
                radius: random(1.2, 2.7),
                color
              });
            }
          }

          function launch() {
            const w = canvas.clientWidth;
            const h = canvas.clientHeight;
            burst(random(w * 0.16, w * 0.84), random(h * 0.16, h * 0.58));
          }

          // 첫 화면에서 여러 차례 폭죽이 터지도록 예약합니다.
          launch();
          setTimeout(launch, 350);
          setTimeout(launch, 750);
          setTimeout(launch, 1200);
          setTimeout(launch, 1750);
          setTimeout(launch, 2350);

          let frame = 0;
          function animate() {
            const w = canvas.clientWidth;
            const h = canvas.clientHeight;
            ctx.clearRect(0, 0, w, h);

            for (let i = particles.length - 1; i >= 0; i--) {
              const p = particles[i];
              p.x += p.vx;
              p.y += p.vy;
              p.vy += 0.025;
              p.vx *= 0.992;
              p.vy *= 0.992;
              p.life--;

              const alpha = Math.max(0, p.life / p.maxLife);
              ctx.globalAlpha = alpha;
              ctx.fillStyle = p.color;
              ctx.beginPath();
              ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
              ctx.fill();

              if (p.life <= 0) particles.splice(i, 1);
            }
            ctx.globalAlpha = 1;

            // 애니메이션이 길게 이어지도록 가끔 새 폭죽을 추가합니다.
            frame++;
            if (frame % 48 === 0 && frame < 420) launch();
            requestAnimationFrame(animate);
          }
          animate();

          window.addEventListener("resize", resize);
        })();
        </script>
        """,
        height=400,
        scrolling=False,
    )
