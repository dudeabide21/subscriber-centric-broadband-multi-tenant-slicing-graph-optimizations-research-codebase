# Mathematical model

This repository treats the following quantities as research abstractions, not validated field estimates unless later supported by measured traces.

## Effective service capacity
`C_eff_k(t) = min(C_tc, C_air, C_cpu, C_tun, C_bh)`

## Diffusion coefficient estimate
`sigma_hat^2_{k,tau} = (1 / Delta) * Var[A_k(t+Delta) - A_k(t) - lambda_hat_{k,tau} * Delta]`

## Effective bandwidth
`E_k(theta) = (1/(theta t)) log E[exp(theta A_k(t))]`

## Overflow-risk indicator
`theta_star = sup{theta > 0 : E_k(theta) < C_eff_k}`
`risk_indicator = exp(-theta_star * B_k)`

This is an exponential-order risk indicator, not a calibrated finite-buffer probability unless validated against measured loss traces.

## LEO backoff
`Delta_t_eff_LEO = clip_[Delta_t_macro, Delta_t_max](Delta_t_macro * exp(psi1 * sigma2_RTT/(sigma2_RTT_ref + eps) + psi2 * Drop_LEO/(Drop_ref + eps)))`

## Graph edge feature normalization
`x_bar = (x - min(x)) / (max(x) - min(x) + eps)`
