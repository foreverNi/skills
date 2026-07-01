# UI Quality Checklist

Use this checklist after reading the actual UI code and before declaring a design polished.

## Product Fit

- Product type is identified: tool, mobile app, consumer app, landing page, game, content site, dashboard, portfolio, or specialized domain.
- Visual tone matches user intent and domain risk.
- Primary workflow is visible and efficient.
- Secondary content does not compete with the main task.

## Structure And Layout

- Page has a clear navigation model and information hierarchy.
- Layout uses stable constraints: grid tracks, aspect ratios, min/max widths, safe areas, and predictable container sizes.
- Repeated items align cleanly and do not resize unpredictably on hover or data changes.
- Sections are not styled as floating cards unless they are genuinely discrete surfaces.
- Mobile layout is intentionally designed, not only squeezed from desktop.

## Typography

- Type scale has clear roles: page title, section title, body, metadata, labels, helper text.
- Font sizes are appropriate to context; compact panels do not use hero-scale text.
- Line length, line height, and wrapping are comfortable.
- Letter spacing is not negative.
- Text does not overflow, clip, overlap, or become unreadably small.

## Color And Contrast

- Palette has neutral surfaces, border colors, semantic state colors, and restrained accents.
- Interactive states are distinguishable without relying only on color.
- Text contrast is sufficient for primary, secondary, disabled, and destructive states.
- Large areas are not dominated by purple-blue gradients, decorative glows, beige/brown themes, or one hue unless brand context requires it.

## Controls And Interaction

- Tool actions use familiar icons when available, with accessible labels or tooltips.
- Primary action is obvious; destructive actions are visually and spatially separated.
- Form fields have labels, validation, error messages, disabled states, and useful focus styles.
- Tables and lists support scanning, comparison, and repeated action.
- Loading, empty, error, success, selected, hover, focus, and disabled states are handled.

## Visual Assets

- Websites, games, and object-focused pages use meaningful visual assets when visuals affect quality.
- Images show the actual product, place, object, state, gameplay, or person when inspection matters.
- Assets are not broken, overly dark, badly cropped, or used only as vague atmosphere.
- Canvas or 3D scenes are checked for nonblank rendering and correct framing.

## Responsiveness

- Desktop, tablet or narrow desktop, and mobile widths are inspected when feasible.
- Touch targets are large enough on mobile.
- Fixed toolbars, sidebars, overlays, and bottom bars do not cover important content.
- Long labels, numbers, filenames, and translated strings are stress-tested.

## Accessibility

- Interactive elements have accessible names.
- Keyboard focus order is logical.
- Focus indicators are visible.
- Color contrast and hit targets are acceptable.
- Motion is not required to understand the UI.

## Verification

- App renders without blank screens or console errors that affect UI.
- Screenshots or manual viewport checks were performed for at least desktop and mobile when possible.
- Any unverified claims are marked as unverified.
- Remaining risks are specific, not generic.
