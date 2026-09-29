# Design

Inventory: spec node 85:1999 (spec), screen node 203:13054 (screen, Figma screenshot cited).

## Visual contract

| Region | Screen node-id | Facts |
| --- | --- | --- |
| Modal | 203:13054 | FIXED 480x320, radius 16, DROP_SHADOW 0 8 24 rgba(0, 0, 0, 0.2) |
| Close button | 203:13060 | ABSOLUTE top 16 right 16, 24x24 |
| Title | 203:13061 | font Inter 20/28 600, copy "Pay now" |

## Files

- `src/checkout/PayModal.tsx`
