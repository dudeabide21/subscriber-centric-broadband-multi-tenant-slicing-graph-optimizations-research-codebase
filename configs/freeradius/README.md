# FreeRADIUS examples

These files are examples only and should be adapted to the local lab setup.
They are not production policy and must not be treated as field-validated results.

## Stage 2 prototype role

The FreeRADIUS examples represent the controller side of the minimum
subscriber evidence spine:

`subscriber identity -> authentication result -> policy mapping
-> slice attributes -> accounting identity`

Stage 2 templates must include both:

- an accepted subscriber path with explicit policy, slice, rate, and
  accounting attributes;
- a rejected subscriber path that does not assign subscriber service.

All shared secrets, passwords, certificates, and private material must remain
placeholders and must never be committed.

Operational templates are added in Stage 2.3. This README does not authorize
deployment to a live RADIUS server.
