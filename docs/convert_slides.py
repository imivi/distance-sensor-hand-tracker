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
  </style>
</head>
<body>

  <!-- Slide Deck Presentation -->
  <div class="deck-container" id="deck">
{slides_html}
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
        }}
      }});

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

