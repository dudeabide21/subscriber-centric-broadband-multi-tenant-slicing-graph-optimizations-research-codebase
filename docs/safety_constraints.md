# Safety constraints

## Safe action set
`U_safe(x) = {u in U(x): Auth=1, Pol=1, Iso=1, Acct=1, EdgeFeas=1}`

## Edge feasibility
`EdgeFeas(x,u)=1` only if the CPU, RAM, IRQ, control-plane load, and service-capacity conditions are all satisfied.

## Operational safety
- Shell scripts must default to dry-run behavior.
- Network changes require `APPLY=1`.
- No live tc, firewall, or wireless changes should occur by default.
