# Product decisions — 2026-08-20

This is the authoritative disposition of product questions raised during the
2026-08-19/20 Tribunal inventory review. Feature reviews remain the source for
evidence and acceptance status.

## Field Utilities

- Bridge lengthwise mode is a narrow end-to-end pedestrian/catwalk layout.
  Wide mode is materially wider and intended for vehicles. Ramp count is per
  end. Keep Level ignores source tilt; Match Box preserves it. Automatic mode
  stops only at opposite terrain or building/structure support, never vehicles,
  trees, or incidental objects. Slight support embedding is intentional;
  excessive underground/interior placement is not. One player may plan from a
  box at a time; contention names the holder. Use a physically validated
  bounded span around 50 metres.
- Physical-contact object handling and explicit cargo loading are separate
  features and must be reviewed independently.
- Towing generally supports land vehicles. Active rope/tow relationships reject
  conflicts; rope disappearance or breakage detaches cleanly. Preserve current
  distance/motion policy absent contrary physical evidence.
- Small-UAV payloads use the native Pontifex Payload Manager, not ACE interaction. Eligible `UAV_01_base_F` vehicles have eight capacity units. Real uniform, vest, and backpack items remain visibly separate and are assembled into an ordered proposal; grenades generally cost one and satchels cost eight. Apply is server-authoritative and atomic, installed entries belong to the UAV, and only occupied entries are cycled by configurable Next Payload and Deploy Payload controls while actually controlling the UAV. The compact themed HUD shows the current entry and the user’s live configured bindings. Mortars remain deferred until they have a coherent inventory representation. Broader ACE dependency removal is separate.

## Advanced Systems

- APS operators are nearby players and operational crew (driver, gunner, or
  commander; exclude arbitrary cargo where possible). Disable is an idempotent
  temporary suspension: preserve modes, voice, anti-drone, charges, and fuel;
  never resupply on re-enable. Anti-drone defaults on only at first install.
- APS beam, particles, voice, and audio are contractual feedback. One
  coordinated event must be perceived consistently without per-client stacking.
  Prefer actual audible proof when reliable, but do not block unrelated work.
- CBR clusters are spatial predicted-impact threat zones with dynamic
  reconciliation. Multiple launchers aimed together combine. Warning cadence
  is per zone after inactivity (20–30 seconds is an experimental hypothesis).
  Markers are global. Confirmed origins persist with timestamps until ordinary
  Arma marker deletion.

## Core and Vigil

- CORDIS is a trusted broker for cooperating Pontifex functions, not a public
  adversarial RPC API, but must remain reasonably safe. Dedupe is
  operation-aware; derive result semantics from actual consumers.
- Vigil clients send declarative task parameters and the server owns executable
  handlers. A new task may replace the current vehicle task; richer planning
  must be deliberate rather than an accidental queue.
- UI/request errors are requester-only. Operational communications may be
  side-wide where appropriate; select audience per message.
- The helicopter stabilizer should automatically mitigate AI pitch-up/climb/
  overshoot on final approach only if controlled physical A/B proves it safe
  and useful. It is not user-selectable.
- The homepage remains deferred; governor cancellation/finalization defects do
  not.

## Mission modules

- Every legitimately assigned curator is authorized; Zeus feedback goes to the
  placing curator.
- Multiple same-type modules are valid and aggregate or are idempotent: APS may
  cover groups/areas, Fabricator/Storage modules and stations combine, and CBR
  initialization remains one system.
- Multiple fixed-wing points use ingress nearest the requester/relevant start
  and exfil nearest the aircraft when leaving.
- Retain or remove non-disposable logic based on measured gameplay effects.
