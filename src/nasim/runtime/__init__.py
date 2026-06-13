"""Client-side runtime — the nasim start/stop toggle.

Each concern is one class:

- :class:`~nasim.runtime.tunnel.SSHTunnel` — the SSH ``-L`` forward.
- :class:`~nasim.runtime.picker.ModelPicker` — picker-cache inject/eject.
- :class:`~nasim.runtime.settings.ClaudeSettings` — model backup/restore.
- :class:`~nasim.runtime.state.StateStore` — backend state + env directives.
- :class:`~nasim.runtime.controller.NasimController` — orchestration.
"""
