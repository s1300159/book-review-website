## Why

The existing pages preserve the required workflows but lack a shared visual
system, responsive layout, and several basic accessibility affordances.
Exercise 9 requires a small interface-quality pass without changing Book,
Review, authentication, search, or session behavior.

## What Changes

- Render all public pages through the shared semantic base layout.
- Add one external stylesheet for readable cards, forms, messages, and actions.
- Support desktop, tablet, and mobile widths without horizontal scrolling.
- Improve focus visibility, form error placement, navigation state, and cover
  image alternatives.
- Add focused interface tests while retaining all existing behavior tests.

## Capabilities

### New Capabilities

- `interface-quality`: Defines the shared semantic, responsive, and accessible
  presentation requirements for existing pages.

### Modified Capabilities

None.

## Impact

The change affects Django templates, the home view's rendering path, one new
static CSS file, focused template tests, and concise project documentation. It
adds no dependency, model, migration, JavaScript, or application feature.
