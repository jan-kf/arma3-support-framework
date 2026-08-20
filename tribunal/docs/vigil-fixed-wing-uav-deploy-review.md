# Vigil fixed-wing UAV deployment boundary review

Review outcome: **REFINED; ACCEPTED / COVERED for authoritative rejection**.

This review is deliberately narrower than fixed-wing reconnaissance. Vigil does
not currently support reconstructing a registered fixed-wing UAV. The stable
contract is therefore that a UAV which can be registered and displayed must not
cross the consequential server deployment boundary, even when a client bypasses
the disabled UI control.

## Twelve-question review

1. **What does the user observe?** Registered fixed-wing UAVs remain listed as
   stowed and unavailable for deployment. Manned fixed-wing assets still deploy.
2. **What are the positive and negative paths?** The normal UI rejects UAVs.
   The permanent negative test now sends a direct remote deployment request for
   an exact registered UAV; the server rejects it before registry mutation.
   The same run deploys a registered manned aircraft through the normal path.
3. **Which machines own the behavior?** The requesting player is client-owned;
   the server owns the registry, validates `remoteExecutedOwner`, classifies the
   authoritative stored vehicle type, records the result, and alone may rebuild
   an aircraft.
4. **Which mechanics are generic?** Request IDs, targeted acknowledgements and
   bounded server audit records are reusable transport mechanics. The decision
   that fixed-wing UAV deployment is disabled remains Vigil-owned.
5. **Which behavior is product-owned?** UAV eligibility, reconstruction and any
   future reconnaissance workflow belong to Vigil. Tribunal only drives the
   public request and observes the resulting registry/world behavior.
6. **Are unusual engine requirements proven?** No claim is made about why UAV
   reconstruction was unstable. Physical UAV deployment remains a separate
   controlled experiment.
7. **What was accidental or fragile?** The original guard existed only in the
   client presentation path. The globally callable server endpoint trusted an
   asset ID and caller reference and therefore allowed a direct request to
   bypass the advertised disabled policy.
8. **What native alternatives exist?** Native UAV ownership/control may support
   a future implementation, but choosing it is outside this rejection contract.
9. **What stable contract is tested?** An authenticated player may request
   deployment only as that exact player. A registered UAV remains stowed, keeps
   its snapshot, has no spawned registry object, and receives an explicit
   `uav_deploy_disabled` result. A registered manned aircraft remains deployable.
10. **Which details may vary?** The exact classifier, acknowledgement storage,
    audit size and UI wording are replaceable. Server-side fail-closed rejection
    before consequential mutation is not.
11. **What remains to characterize?** UAV reconstruction/control stability and
    the absent reconnaissance information product remain
    **NEEDS EXPERIMENTATION / PRODUCT DECISION REQUIRED**.
12. **What belongs in Tribunal?** The adversarial request, request-correlated
    result, unchanged authoritative entry and manned positive control belong in
    the Vigil scenario. No generic UAV policy was added to Tribunal.

## Refinement and evidence

`YSF_fwDeployAsset` now binds remote requests to a real player whose owner is
`remoteExecutedOwner`. It looks up the authoritative registry entry and applies
the disabled-type predicate to that stored class before setting the entry to
`deploying`. Rejections and acceptances use a request-correlated acknowledgement
and a bounded server-private audit record.

The permanent `vigil-fixed-wing` scenario registers an exact
`B_UAV_02_dynamicLoadout_F`, proves its stored class/snapshot, and sends a direct
client call rather than relying on the disabled button. It requires the request
to reach the server, the explicit rejection reason, literal false acceptance,
the same asset ID, an unchanged snapshot, stowed state and null spawned object.
The same fresh run then reconstructs, operates and returns the manned baseline,
which prevents a blanket-rejection false PASS.

This does not promote the current `isUav` implementation into product
specification and does not claim that every UAV must remain disabled forever.
It closes only the authority and fail-closed boundary for the current explicit
disabled policy.

## Deferred product work

- Decide whether fixed-wing reconnaissance should exist and what information it
  produces.
- Characterize native UAV reconstruction, crew/control and ownership before
  enabling deployment.
- Decide whether tablet access, side, role or another entitlement is required
  in addition to authenticated player ownership for manned deployment.

