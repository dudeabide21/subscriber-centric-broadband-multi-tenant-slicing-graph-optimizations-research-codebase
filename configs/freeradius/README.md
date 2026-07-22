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

## Stage 2.3 template inventory

The controlled-lab template set contains:

- `users.example` — accepted and explicitly rejected subscriber examples;
- `clients.conf.example` — AP/gateway RADIUS client placeholder;
- `policy_mapping.example` — deterministic subscriber-to-policy mapping;
- `sites-enabled-default-notes.md` — non-operational integration notes.

The accepted path represents:

`subscriber -> accept -> policy -> slice -> VLAN -> tc class -> accounting ID`

The rejected path represents:

`subscriber -> reject -> no slice -> no shaping class -> no successful
accounting-start identity`

Before any local use:

1. copy examples outside the repository-managed template path;
2. replace placeholders locally;
3. keep secrets and certificates outside Git;
4. validate FreeRADIUS syntax;
5. prepare rollback before restarting any service.
