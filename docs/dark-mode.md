# Dark mode

The sun/moon button in the Navbar switches themes. Auth pages show the same
button at the top right. It has an accessible label, pressed state, keyboard
focus outline and a 44px target.

An explicit preference is saved in `localStorage` under `easy-econ-theme`.
Without a saved preference, the initial theme follows the system setting.
The document theme is set before app rendering; an early dark background avoids
a white initial canvas. Unavailable localStorage does not prevent switching.

`useTheme.js` owns shared theme state. `ThemeToggle.vue` renders the button.
`assets/theme.css` supplies light/dark surface, text, border, tint and shadow
values. White text on colored actions remains white; surface white has a
separate token. Existing literal colors in component styles use shared tokens
with their exact original light values. Pink/green/orange brand banners remain.

All views, shared components and lesson content styles support the palette,
including auth, Navbar/Footer, student course/module/exam, teacher editors,
results, profile and admin. Existing content and image assets are unchanged.
No API, backend, payload, database, authentication, permission, route or
package changes. Layout and feature actions remain the same apart from the
new theme button.

## Files

- Added `frontend/src/composables/useTheme.js`, `components/ThemeToggle.vue`,
  `assets/theme.css`.
- Updated `frontend/index.html`, `src/App.vue`, `components/Navbar.vue` to
  initialize/expose the theme.
- Converted literal surface/text/border colors in existing Vue component/view
  styles, `src/style.css` and `assets/lesson-content.css` to theme tokens.
- No files deleted or feature pages added.

## Verification

- Production build, import/reachability audit and whitespace checks pass.
- 38 existing stylesheets retain identical light CSS after resolving the new
  color tokens (with equivalent CSS color/whitespace normalization).
- Browser checks at 1440px and 390px: system default, explicit override, refresh
  persistence, auth theme button and three actual role logins pass.
- Student dashboard/course/modules/exams/reader/taking exam, teacher courses/
  course editor/lesson editor/exam editor and admin pass navigation with retained
  dark state, dark Navbar and no horizontal overflow or page errors.
- Final mobile checks pass for the 44px toggle, closed filter contrast, dark
  exam confirmation dialog, next-lesson button and switching back to light.
- Desktop screenshots reviewed for lesson reader, teacher editor and signup;
  adjusted editor tint and dark placeholders for readability.

Arbitrary colors authored inside lesson HTML and raster images are not rewritten;
the editor's built-in content layouts use the shared theme. This is a frontend
color theme; it does not introduce additional teacher creation steps.
