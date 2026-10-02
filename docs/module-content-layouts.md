# Module reader and teacher content layouts

The supplied Postman Academy screenshot is the layout reference. The existing
EasyEcon navbar, brand colors and fonts remain. The student reader has the module
title above a compact flat lesson outline, status/document icons and active row;
a centered article with a plain title; an Up Next action; and a thin fixed
Previous / Next footer. Up Next uses the same existing completion/navigation
handler as Next Lesson.

No teacher data model change is required. Existing sections already store HTML
in `content_blocks[].data.html` with type `rich_text_section`. Three one-click
editor actions insert editable HTML: Callout, Two columns, Highlight. Their CSS
classes are presentation only; section types, request keys and API endpoints
are unchanged. Existing lessons still render without conversion.

`LessonRichText.vue` and `assets/lesson-content.css` provide shared rendering
for student content and the teacher content preview. The editor uses the same
content CSS. Two-column cards stack on small screens. Preview opens a native
modal dialog, supports Escape and restores focus to its trigger; it displays
unsaved lesson text across all sections. It is a content preview, not an
interactive preview of the mini quiz.

Complete blocks are inserted at the section level to prevent the browser's
rich-text command from flattening grid/callout markup. Existing Undo/Redo buttons
and Ctrl/Cmd+Z also handle the inserted blocks. No new UI dependency is used.

## Files

- Added `frontend/src/components/LessonRichText.vue`.
- Added `frontend/src/assets/lesson-content.css`.
- Modified `LearningChapter.vue`, `LearningLessonSidebar.vue`,
  `LearningEditor.vue`.
- No files deleted; no backend, API service, database, auth or permission changes.

## Validation

- Production build and import/reachability audit pass (38 reachable Vue files).
- Browser checks at 1440px and 390px: insert/edit all three layouts, Undo/Redo,
  preview/student CSS parity, responsive columns, Escape/focus restoration,
  original request keys/types, and saving/reloading the generated HTML.
- Existing mobile multi-section lesson save passes with original payload keys.
- Reader direct/legacy URLs, active outline, fixed footer, Next/Previous,
  actual local completion saving, quiz payload/score and empty modules pass.
- Layout save tests intercept requests and do not change server records.

Course and exam creation click counts are unchanged. Inserting each content
layout takes one click; preview takes one click. Screenshot matching is for
layout and content composition; it does not replace the EasyEcon brand with
Postman's colors/logo or populate existing lessons with Postman's article text.
