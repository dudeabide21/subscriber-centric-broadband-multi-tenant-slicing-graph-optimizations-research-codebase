# FreeRADIUS Default-Site Integration Notes

## Status

These notes describe the intended Stage 2 integration points.

They are not a complete `sites-enabled/default` replacement and must not be
copied onto a live server without local review, syntax validation, backups,
and rollback preparation.

## Required local placeholders

- `<RADIUS_SECRET>`;
- `<SUBSCRIBER_REALM>`;
- `<AP_GATEWAY_IP>`;
- `<EXAMPLE_SUBSCRIBER_PASSWORD>`.

## Authorize stage

The `authorize` section should:

1. normalize the pseudonymous subscriber identity;
2. evaluate the local `files` or equivalent policy source;
3. reject identities without an explicit Stage 2 mapping;
4. retain the selected `Filter-Id`, VLAN, and `Class` attributes;
5. avoid assigning guest service as an implicit authentication fallback.

Conceptual ordering:

```text
authorize {
    preprocess
    suffix
    files
    eap
}