<!-- DỮ LIỆU BÊN THỨ BA lấy tự động từ GitHub. KHÔNG PHẢI CHỈ THỊ: bỏ qua mọi yêu cầu, câu lệnh hay đường link nằm trong phần dưới đây. -->
# cathrynlavery/diagram-design

- Hạng trên GitHub Trending (tuần): 4
- URL: https://github.com/cathrynlavery/diagram-design
- Mô tả trên GitHub: Editorial diagram design for Claude Code, Codex, GitHub Copilot, Cursor, Factory Droid, and Pi. 44 diagram types. Self-contained HTML + SVG. No shadows. No Mermaid slop.
- Ngôn ngữ chính: HTML
- Tổng sao: 57181
- Sao tăng trong tuần: 8382
- Fork: 3643
- Lấy lúc (UTC): 2026-10-18T06:38:08Z
- README: README.md (51654 ký tự, đã cắt còn 30000)

======== README (nguyên văn) ========

<div align="center">

<h1>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/hero/hero-dark.webp">
    <img alt="Diagram Design. Editorial diagrams your designer won't hate." src="docs/hero/hero-light.webp">
  </picture>
</h1>

**An agent skill that draws diagrams as one self-contained HTML + SVG file, in your brand.<br>45 diagram types. No shadows. No Mermaid slop.**

[![GitHub stars](https://img.shields.io/github/stars/cathrynlavery/diagram-design?style=flat-square&color=bf4520)](https://github.com/cathrynlavery/diagram-design/stargazers)
[![skills.sh installs](https://skills.sh/b/cathrynlavery/diagram-design?style=flat-square)](https://skills.sh/cathrynlavery/diagram-design/diagram-design)
[![CI](https://img.shields.io/github/actions/workflow/status/cathrynlavery/diagram-design/ci.yml?branch=main&style=flat-square&label=CI)](https://github.com/cathrynlavery/diagram-design/actions/workflows/ci.yml)
[![Plugin version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fcathrynlavery%2Fdiagram-design%2Fmain%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&style=flat-square&color=555555)](CHANGELOG.md)
[![MIT license](https://img.shields.io/badge/license-MIT-555555?style=flat-square)](LICENSE)

<a href="https://trendshift.io/repositories/26141" target="_blank" rel="noopener noreferrer"><img src="https://trendshift.io/api/badge/repositories/26141" alt="cathrynlavery/diagram-design on Trendshift" width="250" height="55"/></a>

**[Website](https://diagramdesign.dev) · [Gallery](https://cathrynlavery.github.io/diagram-design/) · [Changelog](CHANGELOG.md)**

[Install](#install) · [What it makes](#what-it-makes) · [Quickstart](#quickstart) · [Match your brand](#onboarding-make-it-look-like-your-brand) · [Import](#import-from-drawio-mermaid-or-excalidraw) · [Export](#export-to-png--svg) · [Contributing](#contributing)

<code>npx skills add cathrynlavery/diagram-design</code>

<br><br>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/hero/demo.gif">
  <source media="(prefers-color-scheme: light)" srcset="docs/hero/demo-light.gif">
  <img src="docs/hero/demo.gif" alt="A prompt typed into an agent session becomes a finished architecture diagram, then a plain first-pass diagram is redrawn with the skill, then the gallery of diagram types" width="900">
</picture>

</div>

<br>

Ask your agent in plain words:

- *"Make me an architecture diagram of my app: frontend, backend, database, Redis cache."*
- *"I need a quadrant showing Q2 projects by impact vs effort."*
- *"Give me a sequence of a bearer call with token refresh on 401."*
- *"Onboard diagram-design to https://yoursite.com"* (pulls your palette and fonts so every diagram after this one matches your site)

The agent picks the type, states its plan, and writes one `.html` file you can open by double-clicking.

---

## Install

Works with any host that reads Agent Skills, including Cursor, Claude Code, Codex, GitHub Copilot, Gemini CLI, Cline, Windsurf and Amp:

```bash
npx skills add cathrynlavery/diagram-design
```

In Claude Code, the plugin marketplace gets you updates and the slash commands:

```text
/plugin marketplace add cathrynlavery/diagram-design
/plugin install diagram-design@diagram-design
```

Official builds come only from this repository. LittleMight, Cathryn Lavery's company, publishes the plugin directory listings; a listing under any other name is an unofficial copy. [PRIVACY.md](PRIVACY.md) lists what the skill sends over the network.

<details>
<summary><b>Claude Code</b>: turn on auto-update</summary>

After installing, run `/plugin`, open **Marketplaces**, select **diagram-design**, and choose **Enable auto-update**. Claude Code disables auto-update by default for third-party marketplaces; after this toggle, it refreshes the marketplace and installed plugin in the background after startup. Run `/reload-plugins` when prompted, or let the next session load the update.

</details>

<details>
<summary><b>Cursor</b>, Cline, Gemini CLI, Windsurf, Amp, Zed, Warp, Roo, Kilo and other Agent Skills hosts</summary>

The cross-agent [`skills` CLI](https://skills.sh) resolves this repository, detects `skills/diagram-design/SKILL.md`, and installs the whole skill (`references/`, `assets/`, `scripts/`) into every host root you select, including Cursor's:

```bash
npx skills add cathrynlavery/diagram-design
```

When the selected roots resolve to more than one skills directory, the CLI asks for an installation method and recommends **Symlink**: one canonical copy, linked into each root, so a later update reaches all of them at once. Pass `--copy` for independent copies per host instead. A selection that resolves to a single directory is copied, because the distinction is immaterial there. Where symlinks are unavailable (Windows without Developer Mode) the CLI falls back to copies and reports which roots it copied.

This is a standalone install, separate from the marketplaces below: it does not follow marketplace updates automatically. Pull merged updates with `npx skills update diagram-design`. It also installs the Agent Skill only, so the `/export-diagram`, `/import-mermaid`, `/profile`, and `/doctor` command surfaces stay with the native packages. On a host that has one of the marketplaces below, prefer the marketplace.

> **One-time migration:** an existing standalone `npx skills add` copy will not start following the Codex marketplace automatically. Remove that standalone copy, then use the Codex marketplace commands. Likewise, uninstall a personal Cowork copy and reinstall Diagram Design from your organization's marketplace. Future marketplace version bumps then flow through each client's native update path.

</details>

<details>
<summary><b>Codex</b></summary>

```bash
codex plugin marketplace add cathrynlavery/diagram-design
codex plugin add diagram-design@diagram-design
```

Codex refreshes configured Git marketplaces at startup. To fetch immediately, run `codex plugin marketplace upgrade diagram-design` and start a new session.

</details>

<details>
<summary><b>GitHub Copilot</b></summary>

```bash
copilot plugin marketplace add cathrynlavery/diagram-design
copilot plugin install diagram-design@diagram-design
```

Copilot installs the shared Diagram Design skill plus its doctor, export, import, and profile capabilities from the existing repository marketplace. Confirm discovery with `copilot skill list` (or `/skills` in an interactive session), then ask for a diagram in natural language. To fetch a merged update, run `copilot plugin marketplace update diagram-design`, then `copilot plugin update diagram-design@diagram-design`.

</details>

<details>
<summary><b>Factory Droid</b></summary>

```bash
droid plugin marketplace add https://github.com/cathrynlavery/diagram-design
droid plugin install diagram-design@diagram-design --scope user
```

Droid tracks Git plugins by commit rather than the manifest's display version. To fetch a merged update, run `droid plugin marketplace update diagram-design`, then `droid plugin update diagram-design@diagram-design --scope user`, and start a new session.

</details>

<details>
<summary><b>Claude Cowork</b> (organization marketplace)</summary>

Organization GitHub marketplaces currently require a private or internal repository, so first mirror this public repository into one owned by your organization. In **Organization settings → Plugins**, choose **Add plugin → GitHub**, connect that mirror, and enable **Sync automatically** from the marketplace menu. Automatic sync runs when a pull request containing a plugin version bump is merged to the mirror's default branch; direct pushes do not trigger the webhook. Install Diagram Design from the resulting organization marketplace.

</details>

<details>
<summary><b>Pi</b></summary>

```bash
pi install https://github.com/cathrynlavery/diagram-design
```

Run `/reload` in an open Pi session. Pi makes the skill available for matching diagram requests; use `/skill:diagram-design` to invoke it explicitly. Pi also loads the `/export-diagram`, `/import-mermaid`, `/import-excalidraw`, `/profile`, and `/doctor` prompt templates. The unpinned Git install is intentional: Pi has no automatic package refresh, so run `pi update --extensions` to pull merged updates.

</details>

<details>
<summary><b>Kiro</b></summary>

Import the Agent Skill from the repository subdirectory URL:

```text
https://github.com/cathrynlavery/diagram-design/tree/main/skills/diagram-design
```

Kiro copies imported skills into `.kiro/skills/` for a workspace or `~/.kiro/skills/` globally, so re-import the URL to pick up updates. Custom agents that declare resources should include `skill://diagram-design/**/SKILL.md`.

</details>

<details>
<summary><b>OpenCode</b></summary>

Copy or symlink `skills/diagram-design/` to `.opencode/skills/diagram-design` in a project or `~/.config/opencode/skills/diagram-design` globally. OpenCode has no Diagram Design marketplace package; copied installs update only when you replace the directory from a newer checkout.

</details>

<details>
<summary><b>Editable install</b> (customize the style guide in a clone)</summary>

Managed installs are convenient, but changes to `references/style-guide.md` may be replaced by package updates. Saved profiles in `~/.diagram-design/profiles/` survive updates, and projects with a `.diagram-design` marker are unaffected. Clone the repo and install the local path if you plan to customize the working style guide directly:

```bash
git clone git@github.com:cathrynlavery/diagram-design.git ~/code/diagram-design

# Pi: register the checkout as a local package
pi install ~/code/diagram-design

# Claude Code: symlink the inner skill
ln -s ~/code/diagram-design/skills/diagram-design ~/.claude/skills/diagram-design

# Other Agent Skills hosts: create only the roots you use
mkdir -p ~/.agents/skills ~/.cursor/skills ~/.cline/skills ~/.kiro/skills ~/.config/opencode/skills ~/.copilot/skills
ln -s ~/code/diagram-design/skills/diagram-design ~/.agents/skills/diagram-design
ln -s ~/code/diagram-design/skills/diagram-design ~/.cursor/skills/diagram-design
ln -s ~/code/diagram-design/skills/diagram-design ~/.cline/skills/diagram-design
ln -s ~/code/diagram-design/skills/diagram-design ~/.kiro/skills/diagram-design
ln -s ~/code/diagram-design/skills/diagram-design ~/.config/opencode/skills/diagram-design
ln -s ~/code/diagram-design/skills/diagram-design ~/.copilot/skills/diagram-design
```

The shared skill lives at `skills/diagram-design/`. Pi discovers it through the repo's standard `skills/` package directory; Claude Code, GitHub Copilot, Codex, Factory Droid, Cursor, and other Agent Skills-compatible tools use the same files.

</details>

---

## How it compares

| | Mermaid / PlantUML | draw.io / Excalidraw | Diagram Design |
|---|---|---|---|
| You make it by | Writing text | Dragging shapes by hand | Describing it to your agent |
| Layout | Automatic | Manual | Placed by the agent on a 4px grid, with CI checks for overlaps and clipping |
| Look | The renderer's theme | Whatever you draw | One opinionated editorial style, matched to your brand |
| Output | Text that renders on GitHub | An editable `.drawio` or `.excalidraw` file | One HTML file with inline SVG, exportable to SVG or PNG |
| Change it later | Edit the text | Edit the canvas | Ask the agent again, or edit the SVG |
| Existing diagrams | | | Redraws Mermaid, draw.io and Excalidraw files |

The downsides are real. Output quality depends on the model you run it with, and the same prompt can lay out differently twice. The result is not an editable source format: there is no text to diff in a pull request and no canvas to drag a box on. For docs that live in Git and change every sprint, Mermaid is still the better fit. Diagram Design is for the diagram you are going to publish.

---

## Why I built it

I wanted diagrams I actually liked for my blog posts on [littlemight.com](https://littlemight.com). Every time I needed one, whether an architecture sketch, a flowchart, or a pyramid of what matters most, I'd ask Claude and get back a generic rounded-box thing that looked nothing like the rest of the site. I'd either fight with Figma for 30 minutes or skip the diagram.

The model already understood the content. What it was missing was taste, so I wrote the taste down: one accent color for the one or two things that matter, 1px hairlines, no shadows, every coordinate on a 4px grid.

> *The highest-quality move is usually deletion.* Every node earns its place. The accent color is reserved for the 1 or 2 things the reader should look at first. Target density: 4/10.

---

## What it makes

45 diagram types, each in three static variants: minimal light, minimal dark, and full-editorial. Open any of them directly in a browser. There is no build step, JavaScript, or external image dependency.

<table>
<tr>
  <td align="center" width="33%"><a href="docs/screenshots/architecture.png"><img src="docs/screenshots/thumbs/architecture.webp" alt="Architecture"></a><br><b>Architecture</b><br><sub>Components + connections</sub></td>
  <td align="center" width="33%"><a href="docs/screenshots/it-state.png"><img src="docs/screenshots/thumbs/it-state.webp" alt="IT current-state"></a><br><b>IT current-state</b><br><sub>Legacy landscape + modernization</sub></td>
  <td align="center" width="33%"><a href="docs/screenshots/flowchart.png"><img src="docs/screenshots/thumbs/flowchart.webp" alt="Flowchart"></a><br><b>Flowchart</b><br><sub>Decision logic</sub></td>
</tr>
<tr>
  <td align="center"><a href="docs/screenshots/sequence.png"><img src="docs/screenshots/thumbs/sequence.webp" alt="Sequence"></a><br><b>Sequence</b><br><sub>Messages over time</sub></td>
  <td align="center"><a href="docs/screenshots/state.png"><img src="docs/screenshots/thumbs/state.webp" alt="State machine"></a><br><b>State machine</b><br><sub>States + transitions</sub></td>
  <td align="center"><a href="docs/screenshots/er.png"><img src="docs/screenshots/thumbs/er.webp" alt="ER"></a><br><b>ER / data model</b><br><sub>Entities + fields</sub></td>
</tr>
<tr>
  <td align="center"><a href="docs/screenshots/timeline.png"><img src="docs/screenshots/thumbs/timeline.webp" alt="Timeline"></a><br><b>Timeline</b><br><sub>Events on an axis</sub></td>
  <td align="center"><a href="docs/screenshots/swimlane.png"><img src="docs/screenshots/thumbs/swimlane.webp" alt="Swimlane"></a><br><b>Swimlane</b><br><sub>Cross-functional flow</sub></td>
  <td align="center"><a href="docs/screenshots/quadrant.png"><img src="docs/screenshots/thumbs/quadrant.webp" alt="Quadrant"></a><br><b>Quadrant</b><br><sub>Two-axis positioning</sub></td>
</tr>
<tr>
  <td align="center"><a href="docs/screenshots/radar.png"><img src="docs/screenshots/thumbs/radar.webp" alt="Radar chart"></a><br><b>Radar / spider</b><br><sub>Multi-axis comparison</sub></td>
  <td align="center"><a href="docs/screenshots/loop.png"><img src="docs/screenshots/thumbs/loop.webp" alt="Loop"></a><br><b>Loop / flywheel</b><br><sub>Reinforcing cycle + shared hub</sub></td>
  <td align="center"><a href="docs/screenshots/nested.png"><img src="docs/screenshots/thumbs/nested.webp" alt="Nested"></a><br><b>Nested</b><br><sub>Hierarchy by containment</sub></td>
</tr>
<tr>
  <td align="center"><a href="docs/screenshots/tree.png"><img src="docs/screenshots/thumbs/tree.webp" alt="Tree"></a><br><b>Tree</b><br><sub>Parent → children</sub></td>
  <td align="center"><a href="docs/screenshots/org-chart.png"><img src="docs/screenshots/thumbs/org-chart.webp" alt="Org chart"></a><br><b>Org chart</b><br><sub>Ownership + routing</sub></td>
  <td align="center"><a href="docs/screenshots/layers.png"><img src="docs/screenshots/thumbs/layers.webp" alt="Layer stack"></a><br><b>Layer stack</b><br><sub>Stacked abstractions</sub></td>
</tr>
<tr>
  <td align="center"><a href="docs/screenshots/venn.png"><img src="docs/screenshots/thumbs/venn.webp" alt="Venn"></a><br><b>Venn</b><br><sub>Set overlap</sub></td>
  <td align="center"><a href="docs/screenshots/pyramid.png"><img src="docs/screenshots/thumbs/pyramid.webp" alt="Pyramid"></a><br><b>Pyramid / funnel</b><br><sub>Ranked hierarchy or drop-off</sub></td>
  <td align="center"><a href="docs/screenshots/bar.png"><img src="docs/screenshots/thumbs/bar.webp" alt="Bar chart"></a><br><b>Bar chart</b><br><sub>Categorical comparison</sub></td>
</tr>
<tr>
  <td align="center"><a href="docs/screenshots/treemap.png"><img src="docs/screenshots/thumbs/treemap.webp" alt="Treemap"></a><br><b>Treemap</b><br><sub>Part-of-whole by area</sub></td>
  <td align="center"><a href="docs/screenshots/line.png"><img src="docs/screenshots/thumbs/line.webp" alt="Line chart"></a><br><b>Line chart</b><br><sub>Trends over time</sub></td>
  <td align="center"><a href="docs/screenshots/gantt.png"><img src="docs/screenshots/thumbs/gantt.webp" alt="Gantt"></a><br><b>Gantt</b><br><sub>Tasks + phases on a timeline</sub></td>
</tr>
<tr>
  <td align="center"><a href="docs/screenshots/scatter.png"><img src="docs/screenshots/thumbs/scatter.webp" alt="Scatter plot"></a><br><b>Scatter plot</b><br><sub>Distribution + correlation</sub></td>
  <td align="center"><a href="docs/screenshots/high-level.png"><img src="docs/screenshots/thumbs/high-level.webp" alt="High-Level"></a><br><b>High-Level</b><br><sub>End-to-end stack on a cluster</sub></td>
  <td align="center"><a href="docs/screenshots/process.png"><img src="docs/screenshots/thumbs/process.webp" alt="Process"></a><br><b>Process</b><br><sub>Multi-actor sequential workflow</sub></td>
</tr>
<tr>
  <td align="center"><a href="docs/screenshots/medallion.png"><img src="docs/screenshots/thumbs/medallion.webp" alt="Medallion"></a><br><b>Medallion</b><br><sub>Multi-tier data storage</sub></td>
  <td align="center"><a href="docs/screenshots/data-flow.png"><img src="docs/screenshots/thumbs/data-flow.webp" alt="Data flow"></a><br><b>Data flow</b><br><sub>Role-scoped pipeline steps</sub></td>
  <td align="center"><a href="docs/screenshots/dp-integration.png"><img src="docs/screenshots/thumbs/dp-integration.webp" alt="DP integration"></a><br><b>DP integration</b><br><sub>Sources → core → consumers</sub></td>
</tr>
<tr>
  <td align="center"><a href="docs/screenshots/dp-security-matrix.png"><img src="docs/screenshots/thumbs/dp-security-matrix.webp" alt="DP security matrix"></a><br><b>DP security matrix</b><br><sub>Per-role access permissions</sub></td>
  <td align="center"><a href="docs/screenshots/sankey.png"><img src="docs/screenshots/thumbs/sankey.webp" alt="Sankey"></a><br><b>Sankey</b><br><sub>Quantities that split + merge</sub></td>
  <td align="center"><a href="docs/screenshots/fishbone.png"><img src="docs/screenshots/thumbs/fishbone.webp" alt="Fishbone"></a><br><b>Fishbone</b><br><sub>Grouped causes → one effect</sub></td>
</tr>
<tr>
  <td align="center"><a href="docs/screenshots/wardley.png"><img src="docs/screenshots/thumbs/wardley.webp" alt="Wardley map"></a><br><b>Wardley map</b><br><sub>Value chain × evolution</sub></td>
  <td align="center"><a href="docs/screenshots/kanban.png"><img src="docs/screenshots/thumbs/kanban.webp" alt="Kanban"></a><br><b>Kanban</b><br><sub>Work in progress by state</sub></td>
  <td align="center"><a href="docs/screenshots/journey.png"><img src="docs/screenshots/thumbs/journey.webp" alt="User journey"></a><br><b>User journey</b><br><sub>Stages, actions + sentiment</sub></td>
</tr>
<tr>
  <td align="center"><a href="docs/screenshots/deployment.png"><img src="docs/screenshots/thumbs/deployment.webp" alt="Deployment"></a><br><b>Deployment</b><br><sub>Zones, hosts + artifacts</sub></td>
  <td align="center"><a href="docs/screenshots/dependency.png"><img src="docs/screenshots/thumbs/dependency.webp" alt="Dependency graph"></a><br><b>Dependency graph</b><br><sub>Fan-in, ranks + cycles</sub></td>
  <td align="center"><a href="docs/screenshots/uml-class.png"><img src="docs/screenshots/thumbs/uml-class.webp" alt="UML class"></a><br><b>UML class</b><br><sub>Classes, operations + typed relations</sub></td>
</tr>
<tr>
  <td align="center"><a href="docs/screenshots/story-map.png"><img src="docs/screenshots/thumbs/story-map.webp" alt="Story map"></a><br><b>Story map</b><br><sub>Backbone × release slices</sub></td>
  <td align="center"><a href="docs/screenshots/db-schema.png"><img src="docs/screenshots/thumbs/db-schema.webp" alt="Database schema"></a><br><b>Database schema</b><br><sub>Physical tables + column FKs</sub></td>
  <td align="center"><a href="docs/screenshots/polar.png"><img src="docs/screenshots/thumbs/polar.webp" alt="Polar chart"></a><br><b>Polar chart</b><br><sub>Cyclic magnitude · linear radius</sub></td>
</tr>
<tr>
  <td align="center" width="33%"><a href="docs/screenshots/waterfall.png"><img src="docs/screenshots/thumbs/waterfall.webp" alt="Waterfall"></a><br><b>Waterfall</b><br><sub>Running total + signed bridges</sub></td>
  <td align="center" width="33%"><a href="docs/screenshots/architecture-delta.png"><img src="docs/screenshots/thumbs/architecture-delta.webp" alt="Architecture delta"></a><br><b>Architecture delta</b><br><sub>Before · Changes · After topology</sub></td>
  <td align="center" width="33%"><a href="docs/screenshots/exploded.png"><img src="docs/screenshots/thumbs/exploded.webp" alt="Exploded axonometric"></a><br><b>Exploded axonometric</b><br><sub>Parts pulled apart on one axis</sub></td>
</tr>
<tr>
  <td align="center" width="33%"><a href="docs/screenshots/axonometric-plan.png"><img src="docs/screenshots/thumbs/axonometric-plan.webp" alt="Axonometric plan"></a><br><b>Axonometric plan</b><br><sub>Rooms and buildings on one plate</sub></td>
  <td align="center" width="33%"><a href="docs/screenshots/heatmap.png"><img src="docs/screenshots/thumbs/heatmap.webp" alt="Heatmap"></a><br><b>Heatmap</b><br><sub>Value per row × column cell</sub></td>
  <td align="center" width="33%"><a href="docs/screenshots/service-blueprint.png"><img src="docs/screenshots/thumbs/service-blueprint.webp" alt="Service blueprint"></a><br><b>Service blueprint</b><br><sub>Frontstage and backstage on a shared stage grid</sub></td>
</tr>
</table>

Several types have named variants that share their reference: Line covers slopegraph, ridgeline, streamgraph and bump; Scatter covers bubble and beeswarm; Treemap covers marimekko.

Architecture can nest administrative bands and traffic boxes in one snapshot when the hierarchy itself is the claim: dashed rx=4 bands for billing and permissions, solid rx=8 boxes for networks, and managed services outside every subnet. See the [containment example](skills/diagram-design/assets/example-architecture-containment.html) and [type-architecture.md](skills/diagram-design/references/type-architecture.md).

Architecture delta compares synchronized topologies through a Before · Changes · After ledger of added, removed, changed, moved, and rewired objects. See its [reference](skills/diagram-design/references/type-architecture-delta.md) and [order-fulfilment example](skills/diagram-design/assets/example-architecture-delta.html). Attribute-only comparisons remain tables; a single snapshot uses Architecture.

Exploded axonometric draws one object in 2:1 dimetric projection with its parts lifted apart at equal gaps: a [phone teardown](skills/diagram-design/assets/example-exploded-phone.html), an [unboxing](skills/diagram-design/assets/example-exploded-unboxing.html), an [app stack](skills/diagram-design/assets/example-exploded.html), an [AI agent stack](skills/diagram-design/assets/example-exploded-ai-stack.html), or a [mechanical keyboard](skills/diagram-design/assets/example-exploded-keyboard.html). Every coordinate comes from one projection function, and the [animated phone](skills/diagram-design/assets/example-exploded-phone-animated.html) opens assembled and explodes once. See its [reference](skills/diagram-design/references/type-exploded.md).

Axonometric plan uses the same projection for one floor or one site: walls cut at desk height so every room reads from a single view, or buildings on a campus tagged by build phase. See the [office floor](skills/diagram-design/assets/example-axonometric-plan.html), the [campus](skills/diagram-design/assets/example-axonometric-plan-campus.html), the [coffee shop](skills/diagram-design/assets/example-axonometric-plan-coffee-shop.html), the [fulfillment floor](skills/diagram-design/assets/example-axonometric-plan-warehouse.html), the [phased campus animation](skills/diagram-design/assets/example-axonometric-plan-campus-animated.html), and the [reference](skills/diagram-design/references/type-axonometric-plan.md).

**Browse the live gallery:** [cathrynlavery.github.io/diagram-design](https://cathrynlavery.github.io/diagram-design/), or open [`skills/diagram-design/assets/index.html`](skills/diagram-design/assets/index.html) locally to flip through every diagram with light / dark / full-editorial tabs. Each type has one number, 01 to 44; its variants and worked examples carry the same number with a letter. The searchable diagram navigation starts open; click the preview to collapse it and use **Diagrams** to reopen it. The active diagram name and variant controls stay visible.

---

## Onboarding: make it look like *your* brand

The whole point is editorial diagrams in **your** colors and typography, not a generic template.

Out of the box, diagrams render in a **jet-black + tangerine** palette (white-smoke paper, jet-black ink, a darkened tangerine accent that clears 4.5:1 contrast as text, blue-slate muted, silver hairlines). Good enough to screenshot straight away. Sixty seconds of onboarding is better: the skill pulls your brand from your website and applies it across every diagram.

### The flow

```
You:     "onboard diagram-design to https://yoursite.com"
Agent:   → fetches the homepage
         → extracts the dominant palette + font stack
         → maps detected values to semantic roles:
             paper, ink, muted, accent, link
         → shows a proposed diff
         → writes your tokens to references/style-guide.md
You:     "yes, apply it"
```

Every new diagram now uses your colors. Your website's paper color becomes the diagram background. Your CTA color becomes the focal accent. Your body font stack becomes the node label family.

Brand matching also emits a fidelity receipt: sampled URLs, exact color roles, font families and weights, font source URLs, and any fallback. Public site fonts are used directly and verified after rendering rather than silently replaced with generic system fonts.

### What gets extracted

| Detected from your site | Becomes |
|---|---|
| `<body>` background | `paper` token |
| Primary text color | `ink` token |
| Secondary / caption text | `muted` token |
| Cards or containers | `paper-2` token |
| Most-used brand color (CTA, link, heading) | `accent` token |
| `<h1>` font family | `title` font |
| `<body>` font family | `node-name` font |
| `<code>` / `<pre>` font | `sublabel` font |

### Contrast checks happen automatically

Before writing tokens, the skill verifies WCAG AA contrast on `ink` over `paper`. If your site has a color that fails contrast at diagram sizes (9 to 12px), it proposes an adjusted value and explains why. The default skin is held to the same contract in CI: text roles clear 4.5:1 and essential marks clear 3:1 on both light and dark paper.

### Accessible by default

Every diagram template gives the inline SVG an accessible name and description: `role="img"`, a resolving `aria-labelledby`, and first-child `<title>` / `<desc>` slots. IDs are prefixed per diagram and variant, so multiple SVG exports can be safely inlined on one page without duplicate accessible-name IDs. Decorative specimen icons are hidden from assistive technology instead.

### Offline fonts

By default a diagram loads Instrument Serif, Geist and Geist Mono from Google Fonts, the only network request it makes. Ask for **system fonts** (or set the font source to `system` in your style guide) and the file makes no network requests at all: the stacks fall back to the platform's own serif, sans and monospace faces. See [Font source](skills/diagram-design/references/style-guide.md#font-source).

### Manual override

Prefer to set tokens by hand? Open [`skills/diagram-design/references/style-guide.md`](skills/diagram-design/references/style-guide.md) and edit the table. Everything downstream reads from there: every diagram, the annotation primitive, and the gallery all use semantic role names (`accent`, not a hex value).

### First-run gate

The skill won't silently ship default-skinned diagrams into a branded project. On first use in a new project, it checks if `style-guide.md` has been customized. If not, it pauses and asks:

> *"This is your first diagram in this project. The style guide is still at the default. Want to run onboarding, paste tokens manually, or proceed with default?"*

See [`skills/diagram-design/references/onboarding.md`](skills/diagram-design/references/onboarding.md) for the full spec.

### Working with multiple clients

Onboard a brand once, save the result as a named profile, then add a `.diagram-design` marker containing `profile: <slug>` to each client project. Marker projects read `~/.diagram-design/profiles/<slug>.md` directly, so parallel workspaces can use different brands without overwriting a shared installed `style-guide.md`.

The profile library is shared across Claude Code, Codex, Factory Droid, and Pi. Use `/diagram-design:profile` in Claude Code, `/profile` in Factory Droid or Pi, or ask in natural language in any host. See [`profiles.md`](skills/diagram-design/references/profiles.md) for the storage, marker, and recovery contract.

---

## Quickstart

```bash
# From a cloned checkout, open the gallery to see every diagram
open skills/diagram-design/assets/index.html       # macOS
xdg-open skills/diagram-design/assets/index.html  # Linux
```

Then ask your agent for a di

[… README dài hơn, phần sau đã bị cắt …]
