# Vigil VLS target-knowledge handshake characterization

Review outcome: **KEEP; CHARACTERIZED ENGINE REQUIREMENT**.

Vigil's VLS path establishes launcher-side target knowledge before calling
`fireAtTarget`. A controlled retained-session A/B on the installed Arma build
shows that this is not redundant ceremony: direct fire emits a real missile but
does not guide it to the requested target, while the current combined handshake
produces the accepted guided flight and arrival.

## Twelve-question review

1. **What does the user observe?** A valid VLS request launches one cruise
   missile which climbs, guides horizontally, and terminates in the requested
   target region.
2. **What are the positive and negative paths?** The current target-report plus
   confirmation handshake is the positive. Otherwise-identical direct
   `fireAtTarget` is the controlled alternative; it fires but does not arrive.
3. **Which machines own the behavior?** Fresh VLS platforms, crew, targets and
   projectiles were server-local. The server issued both command variants and
   sampled the exact projectile trajectories.
4. **Which mechanics are generic?** Fired identity, locality, bounded trajectory
   sampling and terminal-distance measurement are Tribunal evidence mechanics.
   Establishing knowledge for this weapon is a Vigil/Arma adapter concern.
5. **Which behavior is product-owned?** Vigil owns the promise that an accepted
   VLS request reaches its requested region. It does not promise specific
   sensor-command names to users.
6. **Are unusual engine requirements proven?** Yes. On this build, the combined
   knowledge handshake changes the physical outcome from an unguided climbing
   missile to a guided arrival.
7. **What was accidental or fragile?** An initial calibration placed the
   launcher reference too low: both arms spawned below ASL zero and terminated
   immediately. Those phases are excluded. The valid fixture pins the launcher
   at ASL 5 and proves both arms emit live local projectiles.
8. **What native alternatives exist?** Direct `fireAtTarget` without preceding
   report/confirmation was tested first with a fresh target, launcher, crew and
   group in every pair. It was not behaviorally equivalent.
9. **What stable contract is tested?** The weapon must receive sufficient target
   knowledge before fire to produce a guided target-region arrival. Removing or
   changing the current handshake requires another physical A/B.
10. **Which details may vary?** The individual necessity and ordering of
    `reportRemoteTarget` and `confirmSensorTarget` were not isolated. The exact
    calls remain replaceable only after an equivalent physical comparison.
11. **What remains to characterize?** A report-only/confirm-only matrix is
    unnecessary for the current implementation, but would be required before
    simplifying one half of the combined handshake.
12. **What belongs in Tribunal?** Exact Fired/projectile/trajectory/arrival
    evidence belongs in Tribunal. Sensor-knowledge policy stays in Vigil.

## Controlled evidence

Live run `20260820T001108Z-c8edbbcc` used fresh object identities and ran the
direct arm before the handshake arm. The final exact-baseline pair used
`B_Ship_MRLS_01_F`, `weapon_VLS_01`,
`magazine_Missiles_Cruise_01_x18`, the same ASL 5 launcher pose, the same
terrain-level target and 2.24 km geometry, and independent 50 ms trajectory
sampling.

That pair produced:

- direct projectile `2:240`: 1,656 samples, 14,051.4 m maximum ASL,
  2,653.23 m horizontal travel, still alive at the 100-second bound, and
  4,634.79 m from its fresh target;
- handshake projectile `2:248`: 303 samples, 209.91 m maximum ASL,
  2,232.75 m horizontal travel, normal termination, and 0.74 m terminal
  distance from its fresh terrain-level target.

Three additional fresh direct-first pairs used a deliberately identical target
for each arm but accidentally forced that target below terrain. They are not
used as terminal-impact evidence. They do independently repeat the guidance
split: direct missiles ended 4.55--4.69 km away, while handshake missiles
converged to 26.0--32.4 m horizontally. One handshake missile terminated in
that region; two remained alive above the subterranean target at the
100-second bound. These secondary records strengthen only the knowledge/guidance
finding and do not replace the exact-baseline terminal proof.

The comparison does not use command return values, target-knowledge arrays, or
Vigil's `YSF_ordered` variable as the outcome oracle. Each phase must emit the
exact local missile, climb, travel laterally, and either reach the independently
known target region or exhaust the bounded flight away from it. The retained
structured records identify every launcher, target and projectile.
