# Vigil tablet access review

Review outcome: **KEEP AS-IS; ACCEPTED / COVERED**.

The access contract is intentionally data-first. The permanent scenario calls
the real public open API for the access matrix and independently inspects the
live display/control state. It retains one real Ctrl+Home plus framebuffer path
for the user-visible shell; repeating keyboard and camera interaction for every
item variant would test CBA/Arma input plumbing rather than Vigil policy.

## Twelve-question review

1. **What does the user observe?** With Tablet Required enabled, the combat
   tablet opens only when a configured VIGIL terminal is assigned in the GPS
   slot. With the setting disabled, it opens without an assigned terminal.
2. **What are the positive and negative paths?** Empty assigned items plus the
   requirement rejects. Empty items plus override opens. Each BLUFOR,
   Independent and OPFOR VIGIL terminal opens. The existing real keybind path
   opens, navigates, closes and reopens the dialog.
3. **Which machines own the behavior?** The access check, assigned items,
   display and controls are client-local. The dedicated server never creates a
   tablet display.
4. **Which mechanics are generic?** Assigned-item manipulation and live display
   observation are reusable Tribunal mechanics. Terminal eligibility and the
   optional requirement are Vigil product policy.
5. **Which behavior is product-owned?** The three supported terminal classes,
   GPS-slot requirement, override and dialog are Vigil-owned.
6. **Are unusual engine requirements proven?** Arma does not reliably recreate
   the dialog from the scheduled worker that observed Escape destruction. The
   accepted UI scenario therefore opens from a fresh worker after each proven
   close; this characterized requirement remains bounded to the adapter.
7. **What was accidental or fragile?** The setting tooltip claimed support for
   unspecified “Rugged Tablets,” while the gate and repository define only the
   three VIGIL terminals. The unsupported claim was removed rather than
   expanding policy without a named compatibility contract.
8. **What native alternatives exist?** CBA keybinds and Arma assigned-item slots
   provide the entry mechanics. One real keybind proof is sufficient; the
   product matrix does not duplicate those mechanics.
9. **What stable contract is tested?** Exact precondition data plus the resulting
   live IDD/page/tab controls determine each outcome. A stale existing dialog,
   failed item link, failed close, nil setting or missing control fails closed.
10. **Which details may vary?** Hint wording, control IDs used as adapter
    anchors, textures and exact keybind may change without changing access
    policy. The current variants are not required to match the player's side.
11. **What remains to characterize?** The itemless override's cosmetic fallback
    skin is not separately specified. Fixed-wing availability has a duplicated
    terminal predicate and ignores the override; that cross-feature consistency
    question is not part of opening the tablet.
12. **What belongs in Tribunal?** Exact assigned-items/display-state observation
    and framebuffer verification belong in Tribunal. Eligibility policy remains
    in Vigil and is exercised only through its public API.

## Permanent evidence

`vigil-ui` executes five isolated access phases. Every phase begins with a
proved-null display and exact assigned-item state, opens in a fresh scheduled
worker, and destroys the dialog before the next phase:

- required + no VIGIL terminal: no dialog;
- override + no VIGIL terminal: live IDD 88000 with page/tabs;
- required + `YSF_VigilTerminal_B`: live dialog;
- required + `YSF_VigilTerminal_I`: live dialog;
- required + `YSF_VigilTerminal_O`: live dialog.

The scenario then restores the default required/BLU state and performs its
existing real Ctrl+Home, framebuffer navigation, close and reopen proof. This
separates access-policy evidence from visual-shell evidence without weakening
either.

