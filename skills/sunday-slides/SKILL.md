---
name: sunday-slides
description: Generate Slidev presentation decks in the Sunday Slides visual style with customisable background colour, logo icon, and image style. Creates Slidev projects with AI-generated graphics and PDF, SPA, and PPTX export.
---

# Sunday Slides

Generate Slidev presentations with customisable visuals — background colour, logo icon, and illustration style — plus AI-generated graphics and PDF, SPA, and PPTX export.

## Customisable Parameters

| Parameter | Default | Options |
|-----------|---------|---------|
| Background colour | `#2BD3EC` (cyan) | Any hex colour |
| Logo icon | Cute monkey SVG (bundled) | Any SVG file path |
| Image style | Artistic pencil sketch | Preset choices or free text (see below) |

### Image Style Presets

| Preset | Description |
|--------|-------------|
| **Artistic pencil sketch** (default) | Soft graphite pencil on textured paper, expressive hand-drawn lines with light shading and cross-hatching |
| **Retro pixel art** | Chunky pixel art in a limited palette, 16-bit retro game aesthetic with clean pixel edges |
| **Colour crayons sketch** | Vibrant waxy crayon strokes on paper, childlike and playful with bold colours and visible texture |
| **Modern technical drawing** | Precise CAD-style line art, clean geometric construction with thin uniform strokes |
| *Free text* | User can type any style description they wish |

## Target Style

| Element | Value |
|---------|-------|
| Background | `#2BD3EC` (cyan, customisable) |
| Font Family | Geist (sans-serif) |
| Text Colour | Black (`#000000`) |
| Graphics | **Artistic pencil sketch** (customisable): black lines on white (converted to background colour), vertical aspect ratio, **ABSOLUTELY NO TEXT/LETTERS/NUMBERS**, **must directly illustrate the specific slide content** |
| Layout | Two-column: text left, graphic right |
| Logo | Custom icon (default: monkey) in top-left of every slide |

## Workflow

### Step 0: Gather Customisation Parameters

**Use the AskUserQuestion tool** (if available) to collect customisation preferences before starting. If AskUserQuestion is not available, ask the user in plain chat.

Ask all three questions in a single AskUserQuestion call:

1. **Background colour**: "What background colour should the slides use?"
   - Options: "Cyan #2BD3EC (default)", "Custom hex colour"
   - header: "Background"

2. **Image style**: "What illustration style should the slide images use?"
   - Options: "Artistic pencil sketch (default)", "Retro pixel art", "Colour crayons sketch", "Modern technical drawing"
   - header: "Image style"
   - (The user can also pick "Other" to type any style freely)

3. **Logo icon**: "What logo/icon should appear on the slides?"
   - Options: "Monkey icon (default)", "Custom SVG file path"
   - header: "Logo"

Store the chosen values for use throughout the workflow:
- `SLIDE_BG` — hex colour string (default: `#2BD3EC`)
- `IMAGE_STYLE` — style description string (default: `Artistic pencil sketch`)
- `LOGO_SOURCE` — path to SVG file (default: skill bundled monkey SVG)

### Step 0b: Determine Image Generation Mode

Before starting, determine whether to regenerate images:

1. **Check user instructions** - If user explicitly says "regenerate images", "new images", or similar → regenerate
2. **Check user instructions** - If user explicitly says "without regenerating images", "keep images", "layout only" → skip image generation
3. **If unclear** - Use AskUserQuestion tool to ask:
   - Question: "Should I regenerate the slide images or keep the existing ones?"
   - Options: "Regenerate images (expensive)", "Keep existing images (layout only)"

**Default behaviour**: Keep existing images (skip Step 4) unless explicitly instructed otherwise.

### Step 1: Create Slidev Project

```bash
mkdir -p {project}_preso
cd {project}_preso

# Initialise with bun
bun init -y
bun add @slidev/cli @slidev/theme-default

# Create directory structure
mkdir -p public/images styles

# Copy the logo from skill assets (or custom path)
# If using default monkey logo:
cp {SKILL_DIR}/assets/logo.svg public/logo.svg
# If user specified a custom SVG:
cp {LOGO_SOURCE} public/logo.svg
```

Where `{SKILL_DIR}` is the path to this skill directory (the directory containing this SKILL.md file).

### Step 2: Configure Theme & Styles

Copy `assets/uno.config.ts` from the skill directory to the presentation directory.

Copy `assets/styles/index.css` from the skill directory to `styles/index.css`.

```bash
cp {SKILL_DIR}/assets/uno.config.ts .
cp {SKILL_DIR}/assets/styles/index.css styles/
```

**Then apply the chosen background colour** by replacing the default `#2BD3EC` in both files:

- In `uno.config.ts`: update `background: '#2BD3EC'` to `background: '{SLIDE_BG}'` and `bg-[var(--slide-bg)]` shortcut
- In `styles/index.css`: update `var(--slide-bg, #2BD3EC)` to `var(--slide-bg, {SLIDE_BG})`

If the user chose the default colour, no changes are needed.

### Step 3: Generate slides.md

Read the source content and convert each slide section to Slidev markdown.

#### Frontmatter and Title Slide (Combined)

**CRITICAL: The title slide content MUST follow immediately after the frontmatter to avoid an empty first page.**

```markdown
---
theme: none
fonts:
  sans: Geist
  mono: Geist Mono
title: '[PRESENTATION TITLE]'
background: '{SLIDE_BG}'
layout: center
class: text-center
---

<img src="/logo.svg" class="slide-logo" />

# [MAIN TITLE]

## [SUBTITLE]

[PRESENTER NAME(S)]
```

Note: The title slide uses `layout: center` and `class: text-center` in the frontmatter itself.

#### Content Slide Template

```markdown
---
layout: default
---

<img src="/logo.svg" class="slide-logo" />

<h2 class="slide-title">[SLIDE TITLE]</h2>

<div class="slide-grid">
<div class="slide-text-col">

- **First main point**
  - Supporting detail here
  - Another supporting detail
- **Second main point**
  - Supporting detail
- **Third main point**

</div>
<div class="slide-image-col">

<img src="/images/slide-NN.png" />

</div>
</div>

---
```

**CRITICAL Layout Rules:**
- Use `<h2 class="slide-title">` for titles - **MUST be ABOVE the grid** (outside and before the `slide-grid` div) so it spans the full slide width
- Grid container: `slide-grid` class (CSS-based grid: 1fr + auto columns, 2rem gap). Image column auto-sizes based on available height.
- Text column: `slide-text-col` class
- Image column: `slide-image-col` class (right-aligns the image)
- Image sizing: No extra classes needed (CSS handles max-height and aspect ratio)
- **MUST have blank lines** before and after markdown content inside `<div>` tags

#### Formatting Rules

- Use `<h2 class="slide-title">Title</h2>` for slide titles (HTML tag, not markdown)
- Use **bold** liberally to highlight important words and phrases throughout
- Bullet points with `-` and 2-space indentation for nesting (one or two levels)
- Numbered lists (`1.`, `2.`, etc.) where order matters
- **CRITICAL**: Blank lines before and after markdown content inside `<div>` tags
- Each slide separator is exactly `---` on its own line

### Step 4: Generate Graphics (USE SUBAGENT)

**CRITICAL: Always use the Task tool to spawn a subagent for image generation.** Each subagent handles one slide's image generation AND immediate post-processing. This ensures proper isolation and prevents context overflow.

For each slide, spawn a subagent with:
- Description: "Generate slide NN image"
- Subagent type: "Bash"
- Prompt: Include the full image generation command AND post-processing command

The subagent should execute both commands sequentially for each slide before returning.

#### Image Dimensions

Final images must be **480x720 pixels** (2:3 vertical ratio). The post-processing script resizes to this size automatically.

#### Content Sources and Deliberation

For each slide, follow this process:

**Step 4a: Gather Content**

1. **Slide Content** - The bullet points for this slide
2. **Background Context** - Any additional source material (documents, notes, references) relevant to the slide topic. Include **500-800 words** of context if available.

**Step 4b: Deliberate on Illustration Ideas**

Before writing the image prompt, think through **3-4 concrete illustration options** that directly reflect the slide content:

1. Read the slide content and background context carefully
2. Identify the core concepts that need visual representation
3. Brainstorm 3-4 distinct visual approaches. **Be as specific as possible** - describe exactly what objects, figures, or diagrams would appear and how they relate to the slide content:
   - Option A: [describe a specific scene with concrete objects/figures]
   - Option B: [describe an alternative approach]
   - Option C: [describe another angle]
   - Option D: [describe a simpler option]
4. **Pick the best option** - choose the one that most clearly and directly illustrates the slide's key points
5. Spell out the selected illustration in **complete detail** in your thinking before constructing the prompt - describe composition, positioning, and how the vertical format will be used

**Step 4c: Construct the Prompt**

Include in the prompt:
- The selected illustration idea (what specifically to draw)
- Style guidelines (using the chosen IMAGE_STYLE — see style-specific prompt blocks below)
- The slide content (for context)
- The background context (for deeper understanding)

#### Image Generation Command

```bash
uv run ~/.claude/skills/nano-banana-pro/scripts/generate_image.py \
  --prompt "[PROMPT]" \
  --filename "{project}_preso/public/images/slide-{NN}.png" \
  --resolution 1K
```

#### Post-Processing: White to Background Colour and Resize (IMMEDIATE)

**CRITICAL: Run this script IMMEDIATELY after each image is generated** - do not wait until all images are done.

```bash
uv run {SKILL_DIR}/scripts/white_to_background.py \
  "{project}_preso/public/images/slide-{NN}.png" \
  --colour '{SLIDE_BG}'
```

This script:
1. Converts white/near-white pixels to the chosen background colour
2. Resizes the image to 480x720 pixels (the default size, 2:3 ratio)

The script must run right after each image generation, before moving to the next slide.

#### Prompt Template

Adapt the style block below based on the chosen `IMAGE_STYLE`:

##### Style: Artistic pencil sketch (default)

```
STYLE: Artistic pencil sketch. Soft graphite pencil on textured paper. Expressive hand-drawn lines with light shading, cross-hatching, and visible pencil strokes. Like a sketchbook illustration by an artist — organic, slightly loose, with tonal variation from light to dark graphite. NOT digital, NOT vector art.

COLOUR: Primarily BLACK GRAPHITE PENCIL LINES on white paper background. Light gray shading and cross-hatching permitted for depth. No colour. No fills other than pencil shading.
```

##### Style: Retro pixel art

```
STYLE: Retro pixel art. Chunky pixel art in a limited colour palette, 16-bit retro game aesthetic. Clean pixel edges with no anti-aliasing. Think SNES or Mega Drive era sprite art. Visible grid of pixels. NOT smooth, NOT high-resolution.

COLOUR: Limited palette of bold flat colours with BLACK OUTLINES. Pixel-perfect edges. No gradients, no blending, no smooth transitions. Each pixel should be clearly visible.
```

##### Style: Colour crayons sketch

```
STYLE: Colour crayons sketch. Vibrant waxy crayon strokes on paper. Childlike and playful with bold primary and secondary colours. Visible crayon texture and paper grain showing through. Like a skilled illustration done in wax crayons — expressive, textured, warm. NOT digital, NOT clean.

COLOUR: Bold COLOURED CRAYON STROKES with BLACK crayon outlines. Rich waxy texture. Colours should be vivid but with natural crayon unevenness. White paper showing through in places.
```

##### Style: Modern technical drawing

```
STYLE: Modern technical drawing. Precise CAD-style line art with clean geometric construction. Thin uniform strokes, perfect circles and straight lines. Like an engineering diagram or architectural blueprint rendered digitally. Clean, precise, mathematical.

COLOUR: PURE BLACK LINES ONLY on white background. No gray. No shading. No fills. No gradients. Only crisp uniform-weight linework as if plotted by a technical pen or CAD plotter.
```

##### Style: Custom (free text)

Use the user's description directly as the STYLE block. Still enforce the same structural rules (no text, vertical format, etc.).

#### Full Prompt Structure

```
VERTICAL PORTRAIT FORMAT illustration.

IMPORTANT: This is a TALL, NARROW vertical image (2:3 ratio, portrait orientation). Compose the illustration to fill the vertical space from top to bottom. Stack elements vertically. Use the full height of the canvas.

{STYLE BLOCK FROM ABOVE — varies by IMAGE_STYLE}

COMPOSITION: NO FRAMES OR BORDERS. The illustration must fill the available space edge-to-edge. Do NOT draw:
- Decorative borders around the image
- Rectangular frames enclosing the content
- Boxes or containers around the main illustration
- Margins or padding between illustration and edges
The drawing should extend to the edges of the canvas. The main subject should occupy most of the image area.

###################################
### CRITICAL: ILLUSTRATION ONLY ###
###################################
This image must contain ZERO TEXT.
- NO letters (not A, B, C, not even single characters)
- NO numbers (not 1, 2, 3, not even single digits)
- NO words of any kind in any language
- NO labels or annotations
- NO captions or titles
- NO arrows with text
- NOTHING that can be read as language

ONLY pure visual elements: geometric shapes, icons, symbols, arrows, lines, boxes, circles, human silhouettes, abstract representations.

If the image contains ANY readable text, it has FAILED.
###################################

---

WHAT TO ILLUSTRATE:

[INSERT THE SELECTED ILLUSTRATION IDEA - describe the specific scene, diagram, or visual that was chosen during deliberation]

---

SLIDE CONTENT (for context):

[INSERT THE ACTUAL BULLET POINTS FOR THIS SLIDE]

---

BACKGROUND CONTEXT (to help you understand the concepts - DO NOT render any of this as text):

[INSERT RELEVANT BACKGROUND MATERIAL - 500-800 WORDS IF AVAILABLE]

---
```

#### Prompt Rules

1. **ZERO TEXT** - The most critical rule. No letters, numbers, words, labels, annotations, or anything readable. If the generated image contains ANY text, regenerate it.
2. **Chosen style** - Use the IMAGE_STYLE selected by the user (see style blocks above).
3. **No frames or borders** - Illustration must fill the canvas edge-to-edge. No decorative borders, frames, boxes, or margins around the main content.
4. **Deliberate first, then illustrate** - Think through 3-4 concrete illustration options, pick the best, then include it in the prompt.
5. **DIRECT content illustration** - The selected illustration must clearly support the slide content. NOT abstract art or busy compositions.
6. **Less is more** - Illustrations should be simple and clear, not busy. A few well-chosen visual elements are better than many competing ones.
7. **White background** - Generate with white background, then convert to background colour and resize to 480x720
8. **Copy slide content verbatim** - Include exact bullet points in the prompt
9. **Include background context** - Include relevant source material if available
10. **Vertical aspect ratio** - Always use portrait format (1024x1536 via 1K resolution, then resized to 480x720). Emphasize vertical composition in the prompt.
11. **USE SUBAGENT** - Always spawn a Bash subagent for each image generation + post-processing

### Step 5: Export & Verify

#### Export to PDF, SPA, and PPTX

**CRITICAL: Always generate ALL THREE outputs.**

```bash
cd {project}_preso

# Export PDF
bun slidev export --output {project}_slides.pdf

# Export PPTX
bun slidev export --format pptx --output {project}_slides.pptx

# Build SPA with relative base path
bun slidev build --out spa --base ./
```

The SPA output will be in `{project}_preso/spa/` directory.

#### Generate Preview Script

Create a shell script `preview.sh` to launch vite preview:

```bash
#!/bin/bash
cd "$(dirname "$0")"
bunx vite preview --outDir spa --port 8080
```

Make it executable:

```bash
chmod +x preview.sh
```

### Step 6: Commit (if in a git repository)

```bash
git add {project}_preso/
git commit -m "[AI] Generate {project} presentation"
git pull --rebase && git push
```

## Key Constraints

### Graphics (CRITICAL)
- **ZERO TEXT IN GRAPHICS** - If the generated image contains ANY letters, numbers, words, labels, or annotations, it MUST be regenerated. This is non-negotiable.
- **USE CHOSEN STYLE** - Apply the image style selected by the user (default: artistic pencil sketch). See style blocks in the prompt template section.
- **NO FRAMES OR BORDERS** - Illustration must fill the canvas edge-to-edge. No decorative borders, frames, boxes, or margins around the main content.
- **DELIBERATE FIRST** - Before writing the prompt, think through 3-4 illustration options, spell them out, and pick the best one.
- **LESS IS MORE** - Illustrations should be simple and clear, not busy. A few well-chosen visual elements are better than many competing ones.
- **DIRECTLY ILLUSTRATE SLIDE CONTENT** - The selected illustration must clearly support the slide content. NOT abstract art.
- **480x720 pixels** - Final image size (2:3 vertical ratio), achieved via post-processing resize
- **VERTICAL COMPOSITION** - Emphasize in prompts that this is a tall, narrow vertical image; stack elements from top to bottom
- **Background colour conversion** - Achieved via white_to_background.py with the chosen SLIDE_BG colour
- **Use verbatim slide content** in prompts
- **500-800 words of context** - Include relevant background material if available
- **USE SUBAGENT** - Always use Task tool to spawn a Bash subagent for each image

### Slides
- Slide background: `{SLIDE_BG}` (default `#2BD3EC`)
- Font: Geist
- Slide titles: `<h2 class="slide-title">` **above the grid** (outside and before `slide-grid` div) so it spans full width
- Title slide: Combined with frontmatter to avoid empty first page
- Use **bold** liberally throughout bullet points
- Bullet points with disc markers (first level), circle (second level), proper indentation
- Logo on every slide (absolute positioned top-left)
- Grid container: `slide-grid` class (CSS-based grid: 1fr + auto columns). Image column auto-sizes to fit available height.
- Text column: `slide-text-col` class
- Image column: `slide-image-col` class (right-aligned, height-constrained)

### Process
- **Customisation first**: Gather background colour, image style, and logo preferences before starting
- **Deliberation**: Think through 3-4 illustration options before writing each prompt; be as specific as possible
- **Use subagent**: Spawn a Bash subagent for each slide's image generation + post-processing
- Image generation: nano-banana-pro at 1K resolution (1024x1536, already 2:3 vertical)
- Post-processing: Run white_to_background.py **IMMEDIATELY** after each image (converts to background colour + resizes to 480x720)
- **Final output: ALWAYS generate ALL THREE exports (PDF, PPTX, SPA) plus preview script** - never skip any

## Resources

### scripts/

- `white_to_background.py` - Converts white backgrounds to the chosen background colour and resizes to 480x720 pixels. Accepts `--colour` flag for any hex colour.

Run this script IMMEDIATELY after each generated image, before generating the next slide.

### assets/

- `logo.svg` - Default cute monkey icon (copy to presentation's `public/logo.svg`, or use user's custom SVG)
- `uno.config.ts` - UnoCSS configuration template
- `styles/index.css` - CSS styling template

Copy these files to each new presentation directory during setup.
