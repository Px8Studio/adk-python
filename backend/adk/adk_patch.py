"""Runtime patches for upstream ADK behaviour.

This module applies small compatibility fixes that are safe to
remove once the upstream google-adk package ships the same patches.
"""

from __future__ import annotations

from typing import Iterable

from google.adk.cli.utils import cleanup as _adk_cleanup


def _patch_close_runners_skip_none() -> None:
  """Wrap ``cleanup.close_runners`` so it tolerates ``None`` entries.

  With ``adk web --reload_agents`` the file watcher currently marks an
  agent runner for cleanup even if a runner was never started. The
  upstream helper then receives ``[None]`` and tries to call ``close`` on
  it, which raises ``AttributeError``. Filtering out ``None`` keeps the
  reload loop stable until the upstream package includes the fix.
  """
  if getattr(_adk_cleanup, "_orkhon_close_runner_patch", False):
    return

  original_close_runners = _adk_cleanup.close_runners

  async def _close_runners_skip_none(runners: Iterable) -> None:
    filtered_runners = [runner for runner in runners if runner is not None]
    if not filtered_runners:
      return
    await original_close_runners(filtered_runners)

  _adk_cleanup.close_runners = _close_runners_skip_none  # type: ignore[assignment]
  _adk_cleanup._orkhon_close_runner_patch = True


def apply_runtime_patches() -> None:
  """Apply all runtime patches safely (idempotent)."""
  _patch_close_runners_skip_none()
