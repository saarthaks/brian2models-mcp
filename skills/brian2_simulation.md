# Brian2 Simulation Skill

Use this skill whenever writing, debugging, or modifying a Brian2 neural simulation.

---

## 1. Always Search the Library First

Before writing any Brian2 model from scratch:

1. Call `list_brian2_models()` to orient yourself on what's available
2. Call `search_brian2_models(query)` with a description of what you need
3. Read the docstrings of returned models and pick the closest match
4. Adapt the existing model rather than writing from zero

This avoids reinventing patterns that already exist and ensures you start from tested code.

---

## 2. start_scope() — Required at the Top of Every Script

```python
from brian2 import *
start_scope()
```

`start_scope()` resets Brian2's internal state (default network, magic namespace, etc.). Without it, objects from previous simulations leak into the current one, causing:
- Unexpected extra neurons or synapses
- `BrianObjectException` from duplicate names
- Silent corruption of results

**Rule:** Every simulation script or cell starts with `start_scope()`. No exceptions.

---

## 3. Units Discipline

Every quantity with physical dimensions MUST use Brian2 units. Bare numbers silently produce wrong results.

```python
# WRONG — bare numbers
tau = 10          # What unit? Seconds? Milliseconds?
v_rest = -65      # Volts? Millivolts?

# CORRECT — explicit Brian2 units
tau = 10*ms
v_rest = -65*mV
duration = 1*second
weight = 0.5*nS
rate = 100*Hz
```

Common units: `ms`, `mV`, `nA`, `nS`, `uS`, `Hz`, `second`, `volt`, `amp`, `siemens`, `cm`, `um`.

When extracting numeric values (e.g., for plotting), divide by the unit:
```python
times_ms = spike_mon.t / ms        # float array in milliseconds
voltages_mV = state_mon.v[0] / mV  # float array in millivolts
```

If you see `DimensionMismatchError`, check every quantity in the offending equation for missing units.

---

## 4. Namespace Behavior in run()

Brian2 captures variable values at `run()` time from the local/global namespace, NOT at definition time. This matters for parameter sweeps:

```python
# WRONG — stale capture
param = 0.5*nS
group = NeuronGroup(N, eqs)  # eqs references 'param'
for val in [0.1*nS, 0.5*nS, 1.0*nS]:
    param = val
    run(100*ms)  # May not see updated 'param' reliably

# CORRECT — explicit namespace
for val in [0.1*nS, 0.5*nS, 1.0*nS]:
    run(100*ms, namespace={'param': val})
```

**Rule:** For any parameter sweep, always pass `namespace={...}` to `run()`.

---

## 5. store()/restore() for Parameter Sweeps

Building a network is expensive. For sweeps over parameters that don't change network structure, use `store()`/`restore()` to avoid rebuilding:

```python
start_scope()

# Build network once
group = NeuronGroup(N, eqs, threshold='v > v_th', reset='v = v_rest')
# ... synapses, monitors, etc.

# Store initial state
store()

results = {}
for param_val in param_range:
    restore()  # Reset to stored state
    run(duration, namespace={'param': param_val})
    results[param_val] = spike_mon.count[:]
```

This is dramatically faster than reconstructing the network each iteration.

---

## 6. Saving Results to Disk

Simulation objects (monitors, groups) are ephemeral — they vanish when the script ends. Always save results before analysis:

```python
import numpy as np
from pathlib import Path

outdir = Path.home() / "brian2_results"
outdir.mkdir(exist_ok=True)

# Save spike data
np.save(outdir / "spike_times.npy", spike_mon.t / ms)
np.save(outdir / "spike_ids.npy", spike_mon.i)

# Save state data
np.save(outdir / "time.npy", state_mon.t / ms)
np.save(outdir / "voltage.npy", state_mon.v / mV)
```

For complex results, consider using `np.savez` or pickle:
```python
np.savez(outdir / "results.npz",
         spike_t=spike_mon.t/ms,
         spike_i=spike_mon.i,
         state_t=state_mon.t/ms,
         state_v=state_mon.v/mV)
```

---

## 7. Common Tracebacks and Fixes

### DimensionMismatchError
```
DimensionMismatchError: Cannot calculate v + 10, units do not match (units are V, 1).
```
**Cause:** A bare number where Brian2 expects a dimensioned quantity.
**Fix:** Add the correct unit: `v + 10*mV`.

### "Variable X not found"
```
KeyError: "Variable 'param' not found in the namespace"
```
**Cause:** Brian2 can't find a variable referenced in equations at `run()` time.
**Fix:** Pass it explicitly: `run(duration, namespace={'param': value})`.

### RecursionError during code generation
```
RecursionError: maximum recursion depth exceeded
```
**Cause:** Usually a circular reference in differential equations (e.g., `dv/dt` depends on `w`, `dw/dt` depends on `v` through an intermediate that creates a cycle in code generation).
**Fix:** Simplify equations, break circular dependencies, or use `(clock-driven)` for synaptic variables.

### BrianObjectException: "Object with name X already exists"
**Cause:** Missing `start_scope()` — objects from a previous run still exist.
**Fix:** Add `start_scope()` at the top of the script.

---

## 8. Summed Variables for Multiple Synapse Types

When multiple synapse groups target the same postsynaptic neuron, 
each must write to a SEPARATE summed variable. Sharing one variable 
causes a BrianObjectException or silent overwriting.

# WRONG — two synapse groups both writing to I_syn
neurons = NeuronGroup(N, 'dv/dt = (I_syn - v)/tau : volt')
exc_syn = Synapses(exc, neurons, on_pre='I_syn += w')
inh_syn = Synapses(inh, neurons, on_pre='I_syn -= w')

# CORRECT — separate summed variables
eqs = '''
dv/dt = (I_exc + I_inh - v) / tau : volt
I_exc : volt (summed)
I_inh : volt (summed)
'''
exc_syn = Synapses(exc, neurons, on_pre='I_exc_post += w')
inh_syn = Synapses(inh, neurons, on_pre='I_inh_post += w')

---

## 9. String Expressions with Units

When initializing neuron variables using Brian2 string expressions,
do NOT reference Brian2 unit variables inside the string. Use bare 
floats and multiply by the unit at the end.

# WRONG — unit variable inside string expression
tau_mean = 20*ms
neurons.tau_m = 'clip(tau_mean + tau_std * randn(), tau_min, tau_max)'

# CORRECT — bare floats, unit applied at end
neurons.tau_m = 'clip(20.0 + 5.0 * randn(), 5.0, 50.0) * ms'

---

## 10. Stale Cython Cache

If you see a ZeroDivisionError or unexpected behavior immediately 
after a failed run, suspect a stale compiled cache before debugging 
the code itself. Brian2 compiles neuron/synapse code to Cython and 
caches it. A failed run that leaves objects in a bad state can 
corrupt the cache for subsequent runs.

Fix: delete the cache directory and rerun.
    import shutil, brian2
    shutil.rmtree(brian2.__file__.replace('__init__.py', '') + 
                  '../brian2_build', ignore_errors=True)

Or simply: restart the Python process entirely. The cache is 
process-local in most configurations.