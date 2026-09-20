#!/usr/bin/env python3
"""
Convert presentazione.md (Marp Markdown format) into presentation.html
with pure slide transitions, keyboard arrow navigation, 16:10 aspect ratio,
and clean borderless light-mode layout.
"""

from pathlib import Path
import re

BASE_DIR = Path(__file__).parent
MD_PATH = BASE_DIR / "presentazione.md"
HTML_PATH = BASE_DIR / "presentazione.html"


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>2D Ultrasonic Hand Tracker & Classifier - Presentazione</title>
  <style>
    :root {{
      --bg: #0b1120;
      --slide-bg: #f8fafc;
      --text: #0f172a;
      --text-muted: #475569;
      --primary: #0369a1;
      --primary-light: #0284c7;
      --border: #e2e8f0;
      --accent: #10b981;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      background-color: var(--slide-bg);
      font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
      min-height: 100vh;
      width: 100vw;
      margin: 0;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      overflow: hidden;
      color: var(--text);
    }}

    /* 16:10 Slide Aspect Ratio Container - Clean Full Window */
    .deck-container {{
      position: relative;
      width: 100vw;
      height: 100vh;
      box-shadow: none;
      border: none;
      border-radius: 0;
      overflow: hidden;
      background: var(--slide-bg);
    }}

    .slide {{
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      padding: 36px 64px;
      background: var(--slide-bg);
      display: flex;
      flex-direction: column;
      justify-content: flex-start;
      visibility: hidden;
      transform: translateX(100%);
      transition: transform 0.4s cubic-bezier(0.25, 1, 0.5, 1), visibility 0.4s;
      z-index: 1;
    }}

    .slide.active {{
      visibility: visible;
      transform: translateX(0);
      z-index: 2;
    }}

    .slide.prev {{
      visibility: hidden;
      transform: translateX(-100%);
      z-index: 0;
    }}

    /* Headings */
    h1 {{
      color: var(--primary);
      font-size: 34px;
      margin-bottom: 6px;
      letter-spacing: -0.02em;
      line-height: 1.2;
    }}

    h2 {{
      color: var(--primary-light);
      font-size: 25px;
      border-bottom: 2px solid var(--border);
      padding-bottom: 6px;
      margin-bottom: 16px;
      font-weight: 700;
      line-height: 1.25;
    }}

    h3 {{
      color: #1e293b;
      font-size: 18px;
      margin-bottom: 6px;
      font-weight: 600;
      line-height: 1.3;
    }}

    p {{
      color: var(--text-muted);
      line-height: 1.45;
      font-size: 16px;
    }}

    ul {{
      margin-top: 4px;
      margin-bottom: 10px;
      padding-left: 20px;
    }}

    li {{
      margin-bottom: 7px;
      line-height: 1.35;
      font-size: 16.5px;
      color: #1e293b;
    }}

    /* 2-Column Responsive Layout */
    .grid-2 {{
      display: grid;
      grid-template-columns: 1.05fr 0.95fr;
      gap: 32px;
      align-items: center;
      width: 100%;
      flex: 1;
      min-height: 0;
    }}

    .grid-video {{
      display: grid;
      grid-template-columns: 0.8fr 1.2fr;
      gap: 28px;
      align-items: center;
      width: 100%;
      flex: 1;
      min-height: 0;
    }}

    .grid-2 > div:first-child,
    .grid-video > div:first-child {{
      display: flex;
      flex-direction: column;
      justify-content: center;
    }}

    .highlight-box {{
      background: #e0f2fe;
      border-left: 5px solid var(--primary-light);
      padding: 10px 14px;
      border-radius: 6px;
      margin: 10px 0;
      font-size: 15.5px;
      color: #0369a1;
      line-height: 1.4;
    }}

    .svg-card {{
      display: flex;
      justify-content: center;
      align-items: center;
      width: 100%;
      height: 100%;
      max-height: 520px;
    }}

    .svg-card img,
    .svg-card video {{
      max-width: 100%;
      max-height: 460px;
      width: auto;
      height: auto;
      border-radius: 10px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
      object-fit: contain;
    }}

    /* Hero / Centered Slide Types */
    .slide.hero,
    .slide.closing {{
      justify-content: center;
      align-items: center;
      text-align: center;
      padding: 36px 64px;
    }}

    .slide.hero h1 {{
      font-size: 40px;
      margin-bottom: 8px;
    }}

    .slide.hero h3,
    .slide.closing h3 {{
      font-size: 20px;
      color: var(--text-muted);
      font-weight: 500;
      margin-bottom: 16px;
    }}

    .slide.closing h1 {{
      font-size: 40px;
      margin-bottom: 8px;
    }}

    .hero-tag {{
      display: inline-block;
      background: #e2e8f0;
      color: #334155;
      font-size: 14px;
      font-weight: 600;
      padding: 7px 20px;
      border-radius: 9999px;
      margin-top: 14px;
      letter-spacing: 0.02em;
    }}

    .github-link {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      color: #0284c7;
      text-decoration: none;
      font-family: monospace;
      font-size: 13.5px;
      font-weight: 600;
      margin-top: 12px;
      background: #ffffff;
      border: 1px solid #cbd5e1;
      padding: 6px 16px;
      border-radius: 6px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
      transition: color 0.2s, border-color 0.2s, box-shadow 0.2s;
    }}

    .github-link:hover {{
      color: #0369a1;
      border-color: #0284c7;
      box-shadow: 0 2px 6px rgba(2, 132, 199, 0.15);
    }}

    /* Page number watermark on slide */
    .slide-footer-page {{
      position: absolute;
      bottom: 20px;
      right: 30px;
      font-size: 13px;
      color: #94a3b8;
      font-weight: 600;
    }}

    /* Minimal Slide Controls Overlay */
    .slide-controls {{
      position: fixed;
      bottom: 24px;
      left: 50%;
      transform: translateX(-50%);
      display: flex;
      align-items: center;
      gap: 8px;
      background: rgba(15, 23, 42, 0.72);
      backdrop-filter: blur(8px);
      -webkit-backdrop-filter: blur(8px);
      padding: 6px 10px;
      border-radius: 9999px;
      border: 1px solid rgba(255, 255, 255, 0.12);
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
      z-index: 1000;
      opacity: 1;
      visibility: visible;
      transition: opacity 0.35s ease, visibility 0.35s ease, transform 0.35s ease;
    }}

    .slide-controls.hidden {{
      opacity: 0;
      visibility: hidden;
      transform: translate(-50%, 10px);
      pointer-events: none;
    }}

    .ctrl-btn {{
      background: transparent;
      border: none;
      outline: none;
      color: #f8fafc;
      width: 32px;
      height: 32px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: background 0.15s, transform 0.15s, color 0.15s;
    }}

    .ctrl-btn:hover {{
      background: rgba(255, 255, 255, 0.18);
      color: #ffffff;
      transform: scale(1.08);
    }}

    .ctrl-btn:active {{
      transform: scale(0.95);
    }}

    .ctrl-btn svg {{
      width: 17px;
      height: 17px;
      stroke: currentColor;
      stroke-width: 2.2;
      stroke-linecap: round;
      stroke-linejoin: round;
      fill: none;
    }}

    .ctrl-divider {{
      width: 1px;
      height: 16px;
      background: rgba(255, 255, 255, 0.2);
      margin: 0 2px;
    }}

    /* Mobile Responsive Optimizations */
    @media (max-width: 820px) {{
      .slide {{
        padding: 24px 20px 70px 20px;
        overflow-y: auto;
        -webkit-overflow-scrolling: touch;
      }}

      .slide.hero,
      .slide.closing {{
        padding: 24px 20px 70px 20px;
      }}

      h1 {{
        font-size: 26px;
      }}

      .slide.hero h1,
      .slide.closing h1 {{
        font-size: 28px;
      }}

      h2 {{
        font-size: 21px;
        margin-bottom: 12px;
      }}

      h3 {{
        font-size: 16px;
      }}

      li, p {{
        font-size: 14px;
      }}

      /* Stack 2-column layouts vertically */
      .grid-2,
      .grid-video {{
        grid-template-columns: 1fr;
        gap: 20px;
        align-items: stretch;
      }}

      .svg-card {{
        max-height: 280px;
      }}

      .svg-card img,
      .svg-card video {{
        max-height: 260px;
        width: auto;
      }}

      /* Slide Controls for Mobile Touch */
      .slide-controls {{
        bottom: 16px;
        padding: 6px 12px;
        gap: 12px;
      }}

      .ctrl-btn {{
        width: 38px;
        height: 38px;
      }}

      .ctrl-btn svg {{
        width: 20px;
        height: 20px;
      }}

      .slide-footer-page {{
        bottom: 16px;
        right: 18px;
        font-size: 11px;
      }}
    }}
  </style>
</head>
<body>

  <!-- Slide Deck Presentation -->
  <div class="deck-container" id="deck">
{slides_html}
  </div>

  <!-- Minimal Floating Navigation Controls -->
  <div class="slide-controls" id="slide-controls" aria-label="Controlli presentazione">
    <button class="ctrl-btn" id="ctrl-prev" title="Slide precedente (Freccia Sinistra)" aria-label="Precedente">
      <svg viewBox="0 0 24 24"><polyline points="15 18 9 12 15 6"></polyline></svg>
    </button>
    <button class="ctrl-btn" id="ctrl-next" title="Slide successiva (Freccia Destra / Spazio)" aria-label="Successiva">
      <svg viewBox="0 0 24 24"><polyline points="9 18 15 12 9 6"></polyline></svg>
    </button>
    <div class="ctrl-divider"></div>
    <button class="ctrl-btn" id="ctrl-fs" title="Schermo intero (F)" aria-label="Schermo intero">
      <svg id="fs-enter-icon" viewBox="0 0 24 24">
        <path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"></path>
      </svg>
      <svg id="fs-exit-icon" viewBox="0 0 24 24" style="display: none;">
        <path d="M4 14h6m0 0v6m0-6L3 21m17-7h-6m0 0v6m0-6l7 7M10 4v6m0 0H4m6 0L3 3m10 7h6m-6 0V4m0 6l7-7"></path>
      </svg>
    </button>
  </div>

  <script>
    (function () {{
      const slides = Array.from(document.querySelectorAll('.slide'));
      let currentIndex = 0;

      // Add page numbering to content slides
      slides.forEach((slide, idx) => {{
        if (!slide.classList.contains('hero') && !slide.classList.contains('closing')) {{
          const footerPage = document.createElement('div');
          footerPage.className = 'slide-footer-page';
          footerPage.textContent = `${{idx + 1}} / ${{slides.length}}`;
          slide.appendChild(footerPage);
        }}
      }});

      function updateSlide(newIndex, direction = 1) {{
        if (newIndex < 0 || newIndex >= slides.length || newIndex === currentIndex) return;

        const currentSlide = slides[currentIndex];
        const nextSlideEl = slides[newIndex];

        // Prepare incoming slide position without animation if needed
        if (direction < 0) {{
          nextSlideEl.style.transition = 'none';
          nextSlideEl.classList.remove('active');
          nextSlideEl.classList.add('prev');
          void nextSlideEl.offsetWidth;
          nextSlideEl.style.transition = '';
        }} else {{
          nextSlideEl.style.transition = 'none';
          nextSlideEl.classList.remove('active', 'prev');
          void nextSlideEl.offsetWidth;
          nextSlideEl.style.transition = '';
        }}

        // Move current slide out
        if (direction > 0) {{
          currentSlide.classList.remove('active');
          currentSlide.classList.add('prev');
        }} else {{
          currentSlide.classList.remove('active', 'prev');
        }}

        // Animate target slide in
        nextSlideEl.classList.remove('prev');
        nextSlideEl.classList.add('active');

        currentIndex = newIndex;
        window.location.hash = `#slide-${{currentIndex + 1}}`;
      }}

      function nextSlide() {{
        if (currentIndex < slides.length - 1) {{
          updateSlide(currentIndex + 1, 1);
        }}
      }}

      function prevSlide() {{
        if (currentIndex > 0) {{
          updateSlide(currentIndex - 1, -1);
        }}
      }}

      // Keyboard navigation
      window.addEventListener('keydown', (e) => {{
        switch (e.key) {{
          case 'ArrowRight':
          case 'ArrowDown':
          case ' ':
          case 'PageDown':
            e.preventDefault();
            nextSlide();
            break;
          case 'ArrowLeft':
          case 'ArrowUp':
          case 'PageUp':
            e.preventDefault();
            prevSlide();
            break;
          case 'Home':
            e.preventDefault();
            updateSlide(0, -1);
            break;
          case 'End':
            e.preventDefault();
            updateSlide(slides.length - 1, 1);
            break;
          case 'f':
          case 'F':
            toggleFullScreen();
            break;
        }}
      }});

      // Minimal Slide Controls Interaction
      const controls = document.getElementById('slide-controls');
      const btnPrev = document.getElementById('ctrl-prev');
      const btnNext = document.getElementById('ctrl-next');
      const btnFs = document.getElementById('ctrl-fs');
      const fsEnterIcon = document.getElementById('fs-enter-icon');
      const fsExitIcon = document.getElementById('fs-exit-icon');

      btnPrev.addEventListener('click', (e) => {{
        e.stopPropagation();
        prevSlide();
      }});

      btnNext.addEventListener('click', (e) => {{
        e.stopPropagation();
        nextSlide();
      }});

      function toggleFullScreen() {{
        if (!document.fullscreenElement) {{
          document.documentElement.requestFullscreen().catch(() => {{}});
        }} else {{
          if (document.exitFullscreen) {{
            document.exitFullscreen().catch(() => {{}});
          }}
        }}
      }}

      btnFs.addEventListener('click', (e) => {{
        e.stopPropagation();
        toggleFullScreen();
      }});

      document.addEventListener('fullscreenchange', () => {{
        const isFs = !!document.fullscreenElement;
        fsEnterIcon.style.display = isFs ? 'none' : 'block';
        fsExitIcon.style.display = isFs ? 'block' : 'none';
      }});

      // Auto fade-out after mouse stops moving for a few seconds
      let fadeTimer = null;
      const FADE_DELAY_MS = 2500;

      function showControls() {{
        controls.classList.remove('hidden');
        if (fadeTimer) clearTimeout(fadeTimer);
        fadeTimer = setTimeout(() => {{
          controls.classList.add('hidden');
        }}, FADE_DELAY_MS);
      }}

      window.addEventListener('mousemove', showControls);
      window.addEventListener('mousedown', showControls);
      window.addEventListener('touchstart', showControls, {{ passive: true }});

      // Touch swipe gestures for mobile
      let touchStartX = 0;
      let touchStartY = 0;

      window.addEventListener('touchstart', (e) => {{
        if (e.touches.length === 1) {{
          touchStartX = e.touches[0].clientX;
          touchStartY = e.touches[0].clientY;
        }}
      }}, {{ passive: true }});

      window.addEventListener('touchend', (e) => {{
        if (e.changedTouches.length === 1) {{
          const deltaX = e.changedTouches[0].clientX - touchStartX;
          const deltaY = e.changedTouches[0].clientY - touchStartY;
          // Trigger slide only if horizontal swipe dominates vertical scrolling
          if (Math.abs(deltaX) > 45 && Math.abs(deltaX) > Math.abs(deltaY) * 1.5) {{
            if (deltaX < 0) {{
              nextSlide();
            }} else {{
              prevSlide();
            }}
          }}
        }}
      }}, {{ passive: true }});

      // Start fade timer on load
      showControls();

      // Handle initial hash link
      const hashMatch = window.location.hash.match(/#slide-(\\d+)/);
      if (hashMatch) {{
        const targetIndex = parseInt(hashMatch[1], 10) - 1;
        if (targetIndex >= 0 && targetIndex < slides.length) {{
          updateSlide(targetIndex, 1);
        }} else {{
          updateSlide(0, 1);
        }}
      }} else {{
        updateSlide(0, 1);
      }}
    }})();
  </script>
</body>
</html>
"""


def parse_inline_markdown(text: str) -> str:
    """Converts bold, math-like variables and inline formatting."""
    # Bold **text** -> <strong>text</strong>
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # Math expressions like $49 \times 51\text{ cm}$ -> plain clean text
    text = text.replace(r"\times", "&times;")
    text = text.replace(r"\to", "&rarr;")
    text = text.replace(r"\text{ cm}", " cm")
    text = text.replace(r"\text{cm}", "cm")
    text = re.sub(r"\$(.+?)\$", r"\1", text)
    return text


def parse_markdown_blocks(content: str) -> str:
    """Converts slide markdown content (headers, lists, tags) into HTML."""
    lines = content.strip().split("\n")
    html_lines = []
    in_list = False

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            if in_list:
                html_lines.append("          </ul>")
                in_list = False
            continue

        # Check if line is already HTML
        if line.startswith("<") or line.endswith(">"):
            if in_list:
                html_lines.append("          </ul>")
                in_list = False
            html_lines.append("        " + parse_inline_markdown(line))
            continue

        # H1
        if line.startswith("# "):
            if in_list:
                html_lines.append("          </ul>")
                in_list = False
            html_lines.append(f"      <h1>{parse_inline_markdown(line[2:])}</h1>")
        # H2
        elif line.startswith("## "):
            if in_list:
                html_lines.append("          </ul>")
                in_list = False
            html_lines.append(f"      <h2>{parse_inline_markdown(line[3:])}</h2>")
        # H3
        elif line.startswith("### "):
            if in_list:
                html_lines.append("          </ul>")
                in_list = False
            html_lines.append(f"          <h3>{parse_inline_markdown(line[4:])}</h3>")
        # List items
        elif line.startswith("* ") or line.startswith("- "):
            if not in_list:
                html_lines.append("          <ul>")
                in_list = True
            item_text = parse_inline_markdown(line[2:])
            html_lines.append(f"            <li>{item_text}</li>")
        else:
            if in_list:
                html_lines.append("          </ul>")
                in_list = False
            html_lines.append(f"          <p>{parse_inline_markdown(line)}</p>")

    if in_list:
        html_lines.append("          </ul>")

    return "\n".join(html_lines)


def convert_presentation():
    if not MD_PATH.exists():
        raise FileNotFoundError(f"{MD_PATH} not found.")

    text = MD_PATH.read_text(encoding="utf-8")

    # Strip YAML frontmatter
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            text = parts[2]

    # Split slides by Marp separator '---'
    raw_slides = [s.strip() for s in text.split("\n---\n") if s.strip()]
    slides_output = []

    for idx, raw_slide in enumerate(raw_slides, start=1):
        classes = ["slide"]

        # Check Marp classes in comments <!-- _class: hero -->
        if "_class: hero" in raw_slide or idx == 1:
            classes.append("hero")
        elif "_class: closing" in raw_slide or idx == len(raw_slides):
            classes.append("closing")

        if idx == 1:
            classes.append("active")

        # Remove HTML comments like <!-- _paginate: false -->
        clean_content = re.sub(r"<!--.*?-->", "", raw_slide).strip()

        # Parse markdown within this slide
        rendered_body = parse_markdown_blocks(clean_content)

        slide_class_str = " ".join(classes)
        slide_html = f'    <!-- Slide {idx} -->\n    <div class="{slide_class_str}" data-slide="{idx}">\n{rendered_body}\n    </div>'
        slides_output.append(slide_html)

    full_slides_html = "\n\n".join(slides_output)
    final_html = HTML_TEMPLATE.format(slides_html=full_slides_html)

    HTML_PATH.write_text(final_html, encoding="utf-8")
    print(f"Successfully converted {MD_PATH.name} -> {HTML_PATH.name} ({len(raw_slides)} slides).")


if __name__ == "__main__":
    convert_presentation()

