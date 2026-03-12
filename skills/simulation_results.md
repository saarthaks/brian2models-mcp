# Simulation Results Skill

Use this skill when reading, analyzing, or visualizing Brian2 simulation output.

---

## 1. SpikeMonitor

Records spike times and neuron indices.

```python
spike_mon = SpikeMonitor(neurons)
run(duration)
```

Key attributes:
- `spike_mon.t` — spike times (has Brian2 units, e.g., seconds)
- `spike_mon.i` — neuron indices (plain integers, no units)
- `spike_mon.count` — array of spike counts per neuron

To get plain float arrays, divide `.t` by units:
```python
spike_times = spike_mon.t / ms   # float array in milliseconds
spike_ids = spike_mon.i[:]       # integer array
```

---

## 2. StateMonitor

Records state variables (voltage, currents, etc.) over time.

```python
state_mon = StateMonitor(neurons, 'v', record=True)  # record all neurons
# or: record=[0, 1, 5] to record specific neurons
run(duration)
```

Key attributes:
- `state_mon.t` — time array (has units)
- `state_mon.v` — 2D array, `state_mon.v[i]` is the trace for neuron `i`
- Any recorded variable is accessible as an attribute: `state_mon.w`, `state_mon.ge`, etc.

Always divide by units when plotting:
```python
plt.plot(state_mon.t / ms, state_mon.v[0] / mV)
plt.xlabel('Time (ms)')
plt.ylabel('Voltage (mV)')
```

---

## 3. PopulationRateMonitor

Records the instantaneous firing rate of a population.

```python
pop_mon = PopulationRateMonitor(neurons)
run(duration)
```

Key attributes:
- `pop_mon.t` — time array
- `pop_mon.rate` — instantaneous rate (has units of Hz)

Smooth the rate for cleaner plots:
```python
# Using Brian2's built-in smoothing
pop_mon.smooth_rate(window='gaussian', width=1*ms)
plt.plot(pop_mon.t / ms, pop_mon.rate / Hz)
```

---

## 4. Loading Saved Results

Results saved with numpy can be loaded directly:

```python
import numpy as np
from pathlib import Path

outdir = Path.home() / "brian2_results"

# Load individual arrays
spike_times = np.load(outdir / "spike_times.npy")
spike_ids = np.load(outdir / "spike_ids.npy")

# Load from npz archive
data = np.load(outdir / "results.npz")
spike_times = data["spike_t"]
spike_ids = data["spike_i"]
voltage = data["state_v"]
```

These arrays are plain numpy — no Brian2 units attached. The units were stripped during saving (e.g., `spike_mon.t / ms`), so remember what units the data is in.

---

## 5. Three Canonical Plots

### Raster Plot (spike times vs neuron index)

```python
import matplotlib.pyplot as plt

spike_times = spike_mon.t / ms
spike_ids = spike_mon.i

plt.figure(figsize=(10, 4))
plt.plot(spike_times, spike_ids, '.k', markersize=2)
plt.xlabel('Time (ms)')
plt.ylabel('Neuron index')
plt.title('Raster plot')
plt.tight_layout()
plt.savefig(str(Path.home() / "brian2_results" / "raster.png"), dpi=150)
plt.show()
```

### Voltage Trace (single neuron membrane potential)

```python
plt.figure(figsize=(10, 3))
plt.plot(state_mon.t / ms, state_mon.v[0] / mV)
plt.xlabel('Time (ms)')
plt.ylabel('Membrane potential (mV)')
plt.title('Voltage trace — neuron 0')
plt.tight_layout()
plt.savefig(str(Path.home() / "brian2_results" / "voltage_trace.png"), dpi=150)
plt.show()
```

### Population Firing Rate

```python
pop_mon.smooth_rate(window='gaussian', width=1*ms)

plt.figure(figsize=(10, 3))
plt.plot(pop_mon.t / ms, pop_mon.rate / Hz)
plt.xlabel('Time (ms)')
plt.ylabel('Firing rate (Hz)')
plt.title('Population rate')
plt.tight_layout()
plt.savefig(str(Path.home() / "brian2_results" / "population_rate.png"), dpi=150)
plt.show()
```

---

## 6. Figure Saving

Always save figures to `~/brian2_results/` with descriptive filenames:

```python
from pathlib import Path

outdir = Path.home() / "brian2_results"
outdir.mkdir(exist_ok=True)

# Use descriptive names
plt.savefig(str(outdir / "hh_raster_100neurons_1s.png"), dpi=150, bbox_inches='tight')
```

For parameter sweeps, include parameter values in the filename:
```python
plt.savefig(str(outdir / f"fi_curve_tau{tau_val}ms.png"), dpi=150)
```
