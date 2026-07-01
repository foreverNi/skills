---
name: product-ui-review
description: Product-grade UI design review and polish workflow for web apps, mobile apps, dashboards, admin tools, landing pages, games, and interactive prototypes. Use when Codex is asked to improve UI professionalism, beauty, visual hierarchy, layout, responsiveness, design system consistency, accessibility, screenshots, frontend polish, or to review whether an interface looks like a real product instead of a demo.
---

# Product UI Review

## Core Rule

Treat UI quality as a product design problem, not decoration. Start by identifying product type, user intent, workflow density, and platform expectations. Then review structure, hierarchy, visual system, states, responsiveness, accessibility, and implementation evidence.

Do not default to marketing-page composition, oversized hero sections, purple-blue gradients, glow effects, nested cards, or decorative blobs unless the product type explicitly calls for them.

## Workflow

1. **Classify the product**
   - Identify whether the UI is an operational tool, mobile app, consumer product, content site, landing page, game, portfolio, financial/security product, or internal dashboard.
   - Infer the desired tone from domain and task: utilitarian, premium, playful, calm, trustworthy, editorial, immersive, or brand-led.
   - If the request conflicts with product fit, state the tradeoff objectively before editing.

2. **Inspect the current UI**
   - Read the relevant routes, components, styles, theme files, and design-system primitives before changing code.
   - Prefer existing components, tokens, spacing scales, icon libraries, and interaction patterns.
   - Check whether states exist for loading, empty, error, disabled, hover, focus, selected, and active cases.

3. **Review against product-grade criteria**
   - For a compact checklist, use `references/ui-quality-checklist.md`.
   - Focus on hierarchy, alignment, density, spacing, typography, color roles, controls, content fit, responsive behavior, accessibility, and visual restraint.
   - Identify specific defects with evidence: route, component, selector, file path, screenshot, viewport size, or line reference.

4. **Implement scoped polish**
   - Make the smallest coherent changes that improve the real workflow.
   - Use stable dimensions for fixed-format controls such as boards, toolbars, icon buttons, grids, counters, and tiles.
   - Avoid adding abstractions unless they clearly match the local design system or remove real duplication.
   - Preserve app behavior unless the user explicitly asked for UX changes.

5. **Verify visually**
   - Run the app or open the artifact when possible.
   - Capture desktop and mobile screenshots, or at least inspect both viewport classes.
   - Check for blank screens, overflow, clipped text, overlapping elements, poor contrast, unclickable controls, broken assets, awkward wrapping, and layout shift.
   - Iterate once when screenshots reveal visible defects.

6. **Report the outcome**
   - Summarize the product type assumed, major design changes, files touched, and verification performed.
   - If visual verification was blocked, say exactly why and what risk remains.

## Product Type Guidance

- **Operational tools, SaaS, CRM, admin, developer tools**: prioritize scanability, density, predictable navigation, restrained color, clear tables/lists/forms, and efficient repeated actions. Avoid marketing-style hero sections and decorative card-heavy layouts.
- **Mobile apps**: respect platform conventions, touch target sizes, bottom navigation patterns, safe areas, one-handed reach, and high-contrast primary actions.
- **Landing pages and brand pages**: make the product, place, person, or offer visible in the first viewport. Use real or generated bitmap imagery when visuals matter. Do not hide the core subject behind abstract gradients.
- **Games and immersive tools**: prioritize responsive canvas sizing, immediate interaction, motion feedback, legible HUD, and asset loading checks.
- **Financial, security, health, or enterprise products**: use calm hierarchy, clear status language, high trust signals, and conservative visual treatment.

## Design Standards

- Use icons for tool actions when a familiar symbol exists; add tooltips for ambiguous icon-only controls.
- Use segmented controls for modes, toggles or checkboxes for binary settings, sliders or steppers for numeric values, menus for option sets, and tabs for peer views.
- Keep cards for repeated items, modals, and genuinely framed tools. Do not nest cards inside cards.
- Keep border radii restrained unless the existing system requires otherwise.
- Use a real palette with neutral backgrounds, semantic colors, and limited accent colors. Avoid one-note palettes dominated by one hue family.
- Do not scale font size directly with viewport width. Use fixed type steps and responsive layout instead.
- Ensure text fits its container across mobile and desktop. Prefer better layout, wrapping, or content hierarchy over shrinking everything.
- Include focus states and keyboard-visible interactions for interactive controls.

## Evidence Expectations

When editing code, pair visual claims with evidence:

- file paths and component names for structural changes
- screenshots or viewport checks for layout claims
- contrast, overflow, and interaction observations for quality claims
- build, lint, test, or browser-console results when available

Do not claim the UI is polished if it was not rendered or inspected. Say "implemented but not visually verified" when verification is not possible.
