---
title: Nano-Banana Preset Reference
date: 2026-02-27
keywords: [presets, prompt-engineering, image-generation]
lastUpdated: 2026-02-27
---

# Nano-Banana Preset Reference

Complete reference for all 25 image generation presets, including prompt prefixes, use cases, and prompt engineering guidance.

---

## Prompt Engineering Principles

Six principles apply across all presets. Internalize these before crafting prompts — they determine whether output is usable on the first pass or requires iteration.

**1. Lead with medium then subject.**
State the image type at the front of every prompt: "watercolor illustration of...", "technical blueprint of...", "cinematic photograph of...". AI models weight the beginning of prompts heavily during token processing. Placing the medium first locks in the output class before subject tokens are evaluated. Placing subject first risks generating a realistic photograph when a diagram was intended.

**2. Name a reference aesthetic.**
Citing a known style ecosystem — ArtStation, Dribbble, The Economist, Behance — rapidly calibrates quality target and visual vocabulary. These terms carry dense implicit meaning: ArtStation signals painterly concept art with dramatic lighting; Dribbble signals flat vector work with bold outlines. Use a reference name when style specificity matters.

**3. Specify lighting explicitly.**
Lighting is the highest-impact variable after overall style. "Soft studio light", "golden hour", "volumetric light shafts", and "dramatic side light" each produce categorically different outputs from identical subjects. Never leave lighting to default — state it directly. For technical styles where lighting is irrelevant, use "no shadows" or "even illumination" to prevent unwanted depth effects.

**4. State what to exclude.**
Negative guidance is as important as positive for technical styles. "No perspective distortion" prevents isometric art from drifting into three-point perspective. "No gradients" keeps flat vectors flat. "No color" keeps pencil sketches monochrome. Include at least one explicit exclusion per prompt when working in constrained styles. Negative guidance narrows the generation space and dramatically reduces first-pass rejection rate.

**5. Add quality anchors.**
Appending "high detail", "professional quality", "print resolution", or "8K render" to prompts consistently improves output fidelity. These terms appear in high-quality training examples and act as quality gates. Use two to three anchors per prompt — excessive anchoring has diminishing returns past three terms.

**6. Be explicit about background.**
"White background", "transparent background", "dark studio background" prevents unwanted environmental noise. Without background specification, models default to contextually plausible but often distracting environments. For product photography, logos, icons, and technical diagrams, always specify white or transparent background.

---

## Presets by Category

### Technical

Technical presets generate diagrams, engineering drawings, and structured visual representations. These styles benefit most from explicit exclusions (no perspective distortion, no shadows, no color where appropriate) and precise subject naming.

---

#### blueprint

- **Slug:** `blueprint`
- **Default Aspect:** 3:2
- **Default Size:** 2K
- **Prompt Prefix:** "Orthographic projection technical blueprint: precise white linework on deep blueprint-blue background, ISO standard engineering drawing with dimension chains and tolerances, section hatching on cut planes, top/front/side views with projection lines, fine grid overlay, sans-serif Helvetica-style labels, title block in lower-right corner, no perspective distortion, technical pen precision. "
- **When to Use:** Generating engineering or mechanical drawings for technical documentation, product design review, or instructional materials. Ideal when a subject needs to be shown from multiple orthographic views simultaneously.
- **Tips:** Name the object precisely (e.g., "HVAC air handling unit" rather than "HVAC system") to get accurate part geometry. Add "exploded callout for [specific component]" to draw attention to a subsystem within the drawing.

---

#### exploded-view

- **Slug:** `exploded-view`
- **Default Aspect:** 1:1
- **Default Size:** 2K
- **Prompt Prefix:** "Exploded view technical illustration: isometric 30-degree exploded assembly diagram, components floating along dotted alignment axes with consistent separation distance, white background, numbered callouts with leader lines, clean uniform-weight linework, subtle drop shadows beneath each part, part hierarchy from outside-in, assembly manual reference quality, patent illustration style. "
- **When to Use:** Showing assembly order or internal components of a product, machine, or device. Works well for instruction manuals, sales materials, and manufacturing documentation.
- **Tips:** Specify the number of visible components (e.g., "12-part exploded view") to encourage the model to separate parts clearly. Add "IKEA manual style" as an aesthetic reference for clean consumer-product exploded diagrams.

---

#### anatomical

- **Slug:** `anatomical`
- **Default Aspect:** 3:4
- **Default Size:** 2K
- **Prompt Prefix:** "Anatomical cross-section medical illustration in the style of Frank Netter: precise pencil and ink rendering on warm cream paper, labeled with fine leader lines and Latin terminology, stippling and crosshatch shading for depth, scientific textbook quality, detailed internal structures with color-coded systems, subtle watercolor washes for tissue differentiation, publication-ready medical reference quality. "
- **When to Use:** Medical, biological, or structural cross-section illustrations for educational or scientific communication. Effective for showing internal anatomy of organisms, organs, geological strata, or structural engineering cross-sections.
- **Tips:** Specify the cut plane explicitly (e.g., "sagittal cross-section", "horizontal cut at mid-thorax"). Add "Gray's Anatomy style" for classical medical illustration or "Nature journal figure quality" for modern scientific publication aesthetics.

---

#### isometric

- **Slug:** `isometric`
- **Default Aspect:** 1:1
- **Default Size:** 2K
- **Prompt Prefix:** "Isometric view 3D miniature diorama: true 30-degree isometric projection, tilt-shift photography effect with shallow depth of field at edges, toy-like miniature scale, flat cutaway base showing cross-section, vivid saturated colors, warm ambient occlusion shadows, tiny detailed props and miniature people for scale, soft even studio lighting from upper-left, no vanishing point distortion, collectible model quality. "
- **When to Use:** Creating charming, accessible visualizations of environments, processes, or spaces. Effective for office diagrams, urban planning illustrations, game-like environment concepts, and technical scenes that benefit from approachable visual language.
- **Tips:** Describe the scene as a contained environment with clear boundaries (e.g., "a small office with four desks, a server rack, and a meeting table"). The tilt-shift effect is strongest when the scene has vertical depth — add "multi-story building" or "layered landscape" for maximum effect.

---

#### system-diagram

- **Slug:** `system-diagram`
- **Default Aspect:** 16:9
- **Default Size:** 2K
- **Prompt Prefix:** "Clean flat system architecture diagram: rounded-rectangle nodes with consistent icon set inside each, directional arrows with labeled data flows, muted color-coded zones with subtle background fills, sans-serif labels in dark gray, white background, legend in corner, logical left-to-right or top-to-bottom hierarchy, professional technical documentation quality, visually balanced spacing between components. "
- **When to Use:** Visualizing software architecture, data pipelines, network topology, or organizational workflows. Best when relationships and data flow between components are more important than internal component detail.
- **Tips:** List the top-level components in the prompt (e.g., "load balancer, application servers, message queue, database cluster, monitoring service") to guide node placement. Add "AWS architecture diagram style" or "Lucidchart diagram style" as aesthetic references for familiar technical audiences.

---

#### site-map

- **Slug:** `site-map`
- **Default Aspect:** 4:3
- **Default Size:** 2K
- **Prompt Prefix:** "Topographic map style aerial plan view: fine elevation contour lines with spot heights, land-use color coding following cartographic conventions, surveying map aesthetic with property boundary lines, north arrow and graphic scale bar, vegetation symbols and water features in blue, drawing border with coordinate grid ticks, professional cartographic quality, USGS or Ordnance Survey style, crisp linework on light background. "
- **When to Use:** Aerial or plan-view representations of land parcels, project sites, campuses, or geographic areas. Effective for real estate, infrastructure planning, environmental assessment, and urban design contexts.
- **Tips:** Specify land use types explicitly (e.g., "residential zone in yellow, commercial in red, green space in dark green, roadways in grey"). Add "USGS topographic map style" for natural terrain or "urban planning masterplan style" for built environment visualizations.

---

### Business

Business presets generate polished commercial and marketing visuals. These styles benefit from explicit content hierarchy guidance — specify headline placement, data being shown, and intended audience.

---

#### infographic

- **Slug:** `infographic`
- **Default Aspect:** 9:16
- **Default Size:** 2K
- **Prompt Prefix:** "Flat vector infographic: bold typography hierarchy with large statistic callouts, organized data visualization panels with charts and progress bars, icon-driven section layout with consistent line-icon set, limited 3-4 color palette with one accent color, generous whitespace, clear section dividers, editorial magazine layout quality, information flows top-to-bottom, clean visual storytelling. "
- **When to Use:** Summarizing a process, dataset, or argument in a single shareable vertical layout. Ideal for social media, reports, and presentations where data needs to be scannable at a glance.
- **Tips:** Specify the number of sections or steps (e.g., "6-step process infographic" or "5 data panels"). Name a color palette (e.g., "deep navy, coral, and cream palette") to keep the output on-brand rather than defaulting to generic choices.

---

#### slide

- **Slug:** `slide`
- **Default Aspect:** 16:9
- **Default Size:** 2K
- **Prompt Prefix:** "Single presentation slide layout: 16:9 widescreen format, clear title zone with large sans-serif heading, body text area with short bullet points, one prominent hero visual or chart, brand-consistent color blocking with accent bar, generous margins and breathing room, single key message per slide, slide number in corner, McKinsey or Apple keynote quality, minimal professional design. "
- **When to Use:** Generating a single slide visual for a presentation deck, particularly when a strong hero image with text placement zones is needed. Useful for title slides, section dividers, and key data slides.
- **Tips:** Describe the hero visual and the slide's purpose separately (e.g., "hero image of data center interior, slide title zone at bottom, slide for executive summary section"). Add "McKinsey consulting deck style" or "Apple keynote aesthetic" for premium presentation aesthetics.

---

#### hero-banner

- **Slug:** `hero-banner`
- **Default Aspect:** 16:9
- **Default Size:** 2K
- **Prompt Prefix:** "Social media hero banner: horizontal hero image with clear text-safe zone on left or center, bold headline placement area with high-contrast background, vibrant gradient or brand colors with smooth transitions, subtle CTA button area, platform-safe margins on all edges, lifestyle or abstract background imagery, professional marketing quality, web-optimized composition, eye-catching but not cluttered. "
- **When to Use:** Website headers, LinkedIn banners, email headers, and social media cover images. Effective when a strong visual with text overlay space is needed for a marketing campaign or brand announcement.
- **Tips:** Specify the platform (e.g., "LinkedIn company page banner 1128x191 layout" or "Twitter/X header proportions") to guide safe margin placement. Name the brand colors explicitly to override the default vibrant gradient tendency.

---

#### product-mockup

- **Slug:** `product-mockup`
- **Default Aspect:** 1:1
- **Default Size:** 2K
- **Prompt Prefix:** "Product mockup studio photography: clean white cyclorama background with subtle gradient, soft diffused shadow and gentle reflection on surface, 3/4 hero angle with slight elevation, professional three-point studio lighting with soft key light and rim highlight, photorealistic render quality, crisp material textures and surface details visible, commercial e-commerce product photography standard, brand-ready composition. "
- **When to Use:** Presenting a physical or digital product for e-commerce, pitch decks, or marketing materials. Suitable for packaging, consumer electronics, books, bottles, and any tangible product.
- **Tips:** Describe the product precisely including material and finish (e.g., "matte black aluminum water bottle with embossed logo"). Add "Amazon product listing photography style" for e-commerce contexts or "Apple product page render style" for premium positioning.

---

#### data-viz

- **Slug:** `data-viz`
- **Default Aspect:** 16:9
- **Default Size:** 2K
- **Prompt Prefix:** "Editorial data visualization: magazine-quality illustrated chart, annotated bar/line/area chart with clear gridlines and data point markers, muted earth-tone palette with one highlight color for key data, clear axis labels with units, narrative callout annotations pointing to insights, legend with clean typography, trend lines or annotations where relevant, New York Times or Economist visual journalism quality. "
- **When to Use:** Generating illustrated chart concepts for reports, articles, and presentations where data visualization needs editorial polish beyond standard charting tools. Best for conceptual chart mockups rather than precise data rendering.
- **Tips:** Specify chart type explicitly (e.g., "stacked area chart", "grouped bar chart", "small multiples scatter plot"). Add "The Economist data visualization style" or "New York Times chart aesthetic" for high editorial quality reference.

---

### Creative

Creative presets generate illustrative and artistic output. These styles have the widest variance in output — subject specificity and style reference naming produce the largest quality improvements.

---

#### watercolor

- **Slug:** `watercolor`
- **Default Aspect:** 3:2
- **Default Size:** 2K
- **Prompt Prefix:** "Watercolor illustration: loose wet-on-wet technique with visible pigment granulation and salt texture effects, cold-pressed paper texture showing through, soft bleed edges where colors meet, transparent layered washes building depth, limited harmonious palette of 4-5 colors, deliberate white paper areas preserved as highlights, color blooms and backruns as happy accidents, editorial illustration style, fine detail work with small round brush in focal areas. "
- **When to Use:** Editorial illustrations, book covers, greeting cards, nature illustrations, and any context where a warm, handcrafted aesthetic is preferred over digital precision. Particularly effective for botanical, architectural, and landscape subjects.
- **Tips:** Specify the color palette explicitly (e.g., "warm ochre, soft terracotta, and sage green palette") — watercolor presets tend toward oversaturated blues and greens by default. Add "Beatrix Potter style" for charming naturalist work or "New Yorker cover illustration style" for editorial sophistication.

---

#### pencil-sketch

- **Slug:** `pencil-sketch`
- **Default Aspect:** 1:1
- **Default Size:** 2K
- **Prompt Prefix:** "Pencil sketch graphite drawing on heavyweight drawing paper: varied line weight from 2H to 6B, crosshatching and contour shading for volume, loose confident gestural construction lines still visible, Conte crayon accents in darkest shadows, visible paper tooth texture, smudged tonal gradients in mid-tones, no color purely monochrome, sharp detail in focal area with looser marks at periphery, fine art life-drawing quality. "
- **When to Use:** Concept sketches, character studies, architectural ideation, and portrait work where a raw, handmade quality is desired. Effective in academic, design, and fine art contexts.
- **Tips:** Specify the sketch pressure feel (e.g., "loose gestural field sketch" vs. "tight rendered architectural study") to control finish level. Add "Leonardo da Vinci sketchbook style" for classical rendering or "concept art sketchbook style" for design/entertainment industry aesthetics.

---

#### flat-vector

- **Slug:** `flat-vector`
- **Default Aspect:** 1:1
- **Default Size:** 2K
- **Prompt Prefix:** "Flat vector illustration: clean geometric shapes with mathematically precise curves, bold uniform-weight outlines, limited 5-6 color palette with intentional color harmony, Dribbble and Behance trending style, no gradients or textures, consistent rounded line caps, systematic spacing and alignment, scalable design language, playful but professional, negative space used deliberately, modern Silicon Valley illustration style. "
- **When to Use:** Icons, spot illustrations, UI assets, and brand illustrations where clean, scalable, gradient-free art is required. Suitable for digital products, web design, and print collateral.
- **Tips:** Specify color count explicitly (e.g., "3-color illustration: deep indigo, warm coral, and off-white only"). Add "Material Design illustration style" for Google ecosystem aesthetics or "Stripe homepage illustration style" for modern SaaS product visual language.

---

#### cinematic

- **Slug:** `cinematic`
- **Default Aspect:** 21:9
- **Default Size:** 4K
- **Prompt Prefix:** "Cinematic photograph shot on anamorphic lens: golden hour or blue hour dramatic lighting, Kodak Vision3 film stock grain and color response, shallow depth of field with creamy oval bokeh, 2.39:1 letterbox framing, professional color grading with teal-and-orange split toning, volumetric light rays and atmospheric haze, moody emotional atmosphere, foreground silhouette framing, Roger Deakins cinematography quality, movie poster or film still composition. "
- **When to Use:** Hero images for films, events, branded campaigns, and any context requiring dramatic, emotionally evocative photography. Particularly effective for people, landscapes, architecture, and action scenarios.
- **Tips:** Specify the film color grade (e.g., "teal and orange Hollywood blockbuster grade", "cold desaturated thriller grade", "warm Kodak Portra 400 analog film grade") for distinct mood control. Reference a director or film (e.g., "Denis Villeneuve Dune cinematography style") for consistent visual language.

---

#### concept-art

- **Slug:** `concept-art`
- **Default Aspect:** 16:9
- **Default Size:** 4K
- **Prompt Prefix:** "Concept art matte painting: epic environment design with dramatic atmospheric perspective, volumetric god-rays through clouds or fog, ArtStation trending quality, richly detailed background world with painterly brushwork blended with photographic textures, strong value composition with clear focal hierarchy, mood-defining color key, sense of massive scale with tiny figures or structures for reference, cinematic wide establishing shot framing. "
- **When to Use:** Environment design, world-building visualization, game and film pre-production, and any context where an imaginative, detailed painted environment is needed. Effective for speculative futures, fantasy worlds, and science fiction settings.
- **Tips:** Describe scale and atmosphere before subject (e.g., "vast arctic megacity under aurora borealis, enormous brutalist towers casting long shadows"). Add a specific artist style reference (e.g., "Syd Mead retrofuturist style", "Ian McQue industrial sketch style") for strong aesthetic direction.

---

#### pixel-art

- **Slug:** `pixel-art`
- **Default Aspect:** 1:1
- **Default Size:** 1K
- **Prompt Prefix:** "Pixel art in 16-bit SNES era style: carefully curated 32-color palette with intentional hue ramps, visible crisp pixel grid with no anti-aliasing or sub-pixel rendering, dithering patterns for smooth gradients, retro game aesthetic with modern color sensibility, clean deliberate pixel placement, consistent light source with pixel-level shading, sprite-ready proportions, tile-friendly edges, nostalgic but polished. "
- **When to Use:** Game assets, retro-themed marketing materials, social media content targeting gaming audiences, and nostalgic brand communication. Effective for characters, environments, items, and UI elements.
- **Tips:** Specify resolution explicitly (e.g., "32x32 sprite", "64x64 tile", "128x128 portrait") — without this the model will often generate higher resolution with a pixel art texture rather than true low-resolution pixel art. Add "SNES era color palette" or "Game Boy 4-color palette" for specific era constraints.

---

### UI/UX

UI/UX presets generate interface mockups, design system assets, and digital product visuals. Specificity about platform, component type, and design system yields significantly better results.

---

#### app-mockup

- **Slug:** `app-mockup`
- **Default Aspect:** 9:16
- **Default Size:** 2K
- **Prompt Prefix:** "Mobile app UI design mockup: clean modern interface following iOS Human Interface Guidelines, SF Pro typography, system-standard navigation bar and tab bar, card-based content layout with consistent 8px grid spacing, status bar with time and indicators visible, safe area insets respected, frosted glass effects and subtle shadows, cohesive color system with accessible contrast ratios, professional Figma-quality design, realistic content not lorem ipsum. "
- **When to Use:** Generating UI concepts for mobile applications, app store screenshots, pitch deck visuals, and UX design exploration. Suitable for onboarding screens, dashboards, settings pages, and content feeds.
- **Tips:** Name the screen type precisely (e.g., "home feed screen", "user profile page", "checkout flow step 3 of 4"). Add "Material Design 3 Android style" for Android-native aesthetics or reference a specific app (e.g., "Airbnb listing page layout style") for familiar interaction patterns.

---

#### icon

- **Slug:** `icon`
- **Default Aspect:** 1:1
- **Default Size:** 1K
- **Prompt Prefix:** "Icon design on optical grid: consistent 2px stroke weight, 24x24 or 48x48 pixel grid with proper optical alignment, monochrome single-color, rounded corners and line caps, clear visual metaphor readable at small sizes, system icon aesthetic matching SF Symbols or Material Icons weight, balanced negative space, geometric construction, pixel-perfect alignment on grid, transparent background, UI icon library production quality. "
- **When to Use:** Generating icon concepts for UI libraries, app interfaces, presentations, and documentation. Effective for generating multiple thematically related icons in a consistent style.
- **Tips:** Request multiple icons in a single prompt (e.g., "icon set of 6: home, search, notifications, profile, settings, and help") to ensure stylistic consistency across the set. Add "Feather icons style" for lightweight line work or "SF Symbols style" for Apple-native aesthetics.

---

#### logo

- **Slug:** `logo`
- **Default Aspect:** 1:1
- **Default Size:** 1K
- **Prompt Prefix:** "Vector logo design: minimal precise geometry with golden ratio proportions, clever negative space concept, single flat color on transparent background, works at both 16px favicon and billboard scale, clean scalable mark with clear space around it, timeless not trendy, brand identity quality comparable to Pentagram or Wolff Olins, no gradients or effects, strong silhouette recognition, balanced visual weight. "
- **When to Use:** Generating logo mark concepts for brand identity exploration, startup naming exercises, and pitch materials. Best used as a concept generation tool for human refinement rather than production-ready output.
- **Tips:** Describe the brand concept rather than a literal image (e.g., "technology consulting firm logo: abstract mark suggesting precision and connectivity" rather than "a computer with a checkmark"). Add "Fortune 500 brand identity quality" or "Swiss graphic design modernist style" to elevate the output above generic clipart aesthetics.

---

#### wireframe

- **Slug:** `wireframe`
- **Default Aspect:** 16:9
- **Default Size:** 2K
- **Prompt Prefix:** "Website wireframe: lo-fi wireframe in grayscale with blue annotation overlay, placeholder image blocks marked with X, clear typographic hierarchy with varied box sizes for headings and body, visible CTA buttons with rounded rectangles, annotation arrows pointing to interactive elements, component labels in small text, responsive grid structure visible, UX documentation quality, Balsamiq or Whimsical style, content-first layout thinking. "
- **When to Use:** Generating website layout concepts, UX documentation, and stakeholder communication materials during early product design phases. Effective for landing pages, marketing sites, dashboards, and web applications.
- **Tips:** Specify the page type and primary goal (e.g., "SaaS product landing page wireframe, goal: email signup conversion"). Add "Balsamiq mockup style" for hand-drawn lo-fi aesthetics or "Figma wireframe kit style" for clean mid-fidelity output.

---

### Photography

Photography presets generate photorealistic images across portrait, lifestyle, and architectural contexts. Lighting specification is the most critical parameter for this category.

---

#### portrait

- **Slug:** `portrait`
- **Default Aspect:** 3:4
- **Default Size:** 2K
- **Prompt Prefix:** "Professional headshot portrait: Rembrandt lighting with soft key light creating triangle on far cheek, subtle fill light, clean catchlight reflections in eyes, shallow depth of field shot at 85mm equivalent, smooth neutral gray or dark background with slight vignette, DSLR full-frame sensor quality, natural skin tones with no over-retouching, confident approachable expression, shoulders slightly angled, corporate or editorial headshot standard. "
- **When to Use:** Professional headshots, speaker bios, team pages, LinkedIn profiles, and any context requiring a credible, approachable professional portrait. Effective for illustrating personas in UX research and character representation in presentations.
- **Tips:** Specify the subject's professional context (e.g., "technology executive in their 40s, business casual attire") rather than physical description to generate contextually appropriate styling. Add "Peter Hurley headshot lighting style" for high-end corporate portrait quality.

---

#### lifestyle

- **Slug:** `lifestyle`
- **Default Aspect:** 3:2
- **Default Size:** 2K
- **Prompt Prefix:** "Lifestyle photography: natural ambient window light or golden hour warmth, candid editorial style capturing an authentic unposed moment, rule-of-thirds composition with environmental context telling a story, warm Kodak Portra film-like color grade with lifted shadows, shallow depth of field with subject in focus and background softly blurred, magazine editorial quality, genuine human emotion, styled but not artificial. "
- **When to Use:** Marketing materials, brand storytelling, website content, and social media posts where authentic human connection and context matter. Effective for consumer brands, service businesses, and community-focused organizations.
- **Tips:** Describe the scene's emotional tone before the visual details (e.g., "warmth and belonging: family cooking together in a sunlit kitchen Sunday morning"). Add "Kinfolk magazine aesthetic" for artisanal/slow-living style or "Nike campaign photography" for active, aspirational energy.

---

#### architectural-viz

- **Slug:** `architectural-viz`
- **Default Aspect:** 16:9
- **Default Size:** 4K
- **Prompt Prefix:** "Architectural visualization: photorealistic 3D render with V-Ray or Corona quality, natural golden-hour HDRI lighting with warm sun and cool sky fill, physically accurate material textures including glass reflections and concrete roughness, professional landscaping with mature trees and ground cover, human figures for scale casually placed, interior warmth glowing through windows, two-point perspective with vertical lines corrected, award-winning archviz competition quality. "
- **When to Use:** Real estate marketing, architectural presentations, development proposals, and planning applications. Effective for both exterior and interior visualization of residential, commercial, and infrastructure projects.
- **Tips:** Specify time of day and season (e.g., "late afternoon summer light, mature trees with full canopy") — these details dramatically affect material rendering and scene mood. Add "Dezeen magazine editorial quality" or "architectural competition board render style" for premium presentation-grade output.

---

### Specialized

---

#### storyboard

- **Slug:** `storyboard`
- **Default Aspect:** 16:9
- **Default Size:** 2K
- **Prompt Prefix:** "Storyboard panel for film production: dynamic sketch-style illustration with confident ink linework, panel border with shot type label (WS/MS/CU/ECU) in corner, camera movement arrows and direction annotations, clear character staging and blocking, dramatic perspective matching the shot type, light/shadow indication with quick hatching, sequential narrative clarity, Ridley Scott or Spielberg production quality storyboard, action lines for movement. "
- **When to Use:** Pre-production planning for video, film, animation, and commercial production. Effective for communicating scene direction, camera angles, and narrative flow to production teams. Also useful for UX story mapping and service design journey visualization.
- **Tips:** Specify the number of panels and describe each panel's action briefly in sequence (e.g., "4-panel storyboard: panel 1 establishing wide shot of city, panel 2 close-up on protagonist's face, panel 3 action sequence, panel 4 resolution"). Add "feature film production storyboard style" for cinematic work or "UX user journey storyboard style" for product design contexts.

---

## Customization Guide

Presets establish a strong default style foundation. Three techniques allow precise customization without abandoning the preset's structure.

**Override aspect and size with explicit flags.**
Every preset has a default aspect ratio optimized for its typical use case, but any preset can be overridden at invocation time. A `blueprint` preset defaults to 3:2 but can be run at 1:1 for a square mechanical detail or at 16:9 for a panoramic site drawing. Pass `--aspect` and `--size` flags explicitly to override defaults. Size overrides should respect the aspect ratio to avoid distortion.

**Append additional style guidance after the preset prefix.**
The prompt prefix is prepended to the user-supplied prompt — everything in the user prompt is appended after the prefix. Use this to layer additional constraints onto the preset. A `watercolor` preset prompt of "cherry blossom branch, Japanese woodblock print influence, pink and white palette only" appends those constraints directly after the watercolor prefix, tightening the output toward a specific style within the broader watercolor category. Any quality anchor, lighting note, negative guidance, or aesthetic reference added in the user prompt supplements the prefix without replacing it.

**Combine presets conceptually by selecting one preset and manually injecting elements from another.**
Select the preset closest to the desired primary output type, then manually add key phrases from a second preset's prefix into the user prompt. For example, to generate an isometric city map with blueprint-style linework overlaid, invoke the `isometric` preset and add "blueprint technical annotation overlay, dimension callout lines, grid overlay" to the user prompt. Full preset stacking (using two `--preset` flags) is not supported, but manual cross-pollination achieves similar hybrid results. Identify the two or three most distinctive phrases from the secondary preset's prefix and incorporate them selectively.
