"""Utilities for regenerating the DNB OpenAPI Python clients."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from pyopenapi_gen import GenerationError, generate_client


@dataclass(frozen=True)
class ClientSpec:
  """Configuration describing a single generated client."""

  key: str
  spec_path: Path
  output_path: Path
  core_package: str | None = None

  def spec_file(self, repo_root: Path) -> Path:
    return repo_root / self.spec_path

  def project_root_dir(self, repo_root: Path) -> Path:
    parts = self.output_path.parts
    if not parts:
      raise ValueError("output_path must contain at least one segment")
    return repo_root / parts[0]

  def output_package_name(self) -> str:
    parts = self.output_path.parts
    if len(parts) < 2:
      raise ValueError(
        "output_path must contain at least two segments (project root and package)"
      )
    return ".".join(parts[1:])

  def output_directory(self, repo_root: Path) -> Path:
    return repo_root / self.output_path


CLIENT_SPECS: tuple[ClientSpec, ...] = (
  ClientSpec(
    key="public_register",
    spec_path=Path("backend/apis/dnb/specs/openapi3_publicdatav1.yaml"),
    output_path=Path("backend/clients/dnb/public_register"),
    core_package="clients.dnb.core",
  ),
  ClientSpec(
    key="statistics",
    spec_path=Path("backend/apis/dnb/specs/openapi3_statisticsdatav2024100101.yaml"),
    output_path=Path("backend/clients/dnb/statistics"),
    core_package="clients.dnb.core",
  ),
  ClientSpec(
    key="echo",
    spec_path=Path("backend/apis/dnb/specs/openapi3-echo-api.yaml"),
    output_path=Path("backend/clients/dnb/echo"),
    core_package="clients.dnb.core",
  ),
)


def _repo_root() -> Path:
  return Path(__file__).resolve().parents[2]


def _select_specs(selected_keys: Iterable[str]) -> list[ClientSpec]:
  lookup = {spec.key: spec for spec in CLIENT_SPECS}
  selected = list(selected_keys)
  if not selected:
    return list(CLIENT_SPECS)
  missing = [key for key in selected if key not in lookup]
  if missing:
    raise ValueError(f"Unknown client keys requested: {', '.join(missing)}")
  return [lookup[key] for key in selected]


def _generate_single(*, spec: ClientSpec, overwrite: bool) -> None:
  repo_root = _repo_root()
  spec_path = spec.spec_file(repo_root)
  if not spec_path.exists():
    raise FileNotFoundError(spec_path)

  output_dir = spec.output_directory(repo_root)
  output_dir.parent.mkdir(parents=True, exist_ok=True)

  project_root = spec.project_root_dir(repo_root)
  output_package = spec.output_package_name()

  kwargs = dict(
    spec_path=str(spec_path),
    project_root=str(project_root),
    output_package=output_package,
    force=overwrite,
    verbose=True,
  )
  if spec.core_package:
    kwargs["core_package"] = spec.core_package

  print(f"Generating {spec.key} client -> {spec.output_path}")
  try:
    generate_client(**kwargs)
  except GenerationError as exc:
    raise RuntimeError(f"Client generation failed for {spec.key}") from exc


def main(argv: list[str] | None = None) -> int:
  parser = argparse.ArgumentParser(
    description="Generate Python clients for the configured DNB OpenAPI specs."
  )
  parser.add_argument(
    "--no-overwrite",
    action="store_true",
    help="Do not overwrite existing generated files.",
  )
  parser.add_argument(
    "--clients",
    nargs="*",
    metavar="CLIENT",
    help="Subset of client keys to generate (default: all).",
  )
  args = parser.parse_args(argv)

  try:
    specs = _select_specs(args.clients or [])
  except ValueError as exc:
    parser.error(str(exc))
    return 2

  overwrite = not args.no_overwrite
  for spec in specs:
    try:
      _generate_single(spec=spec, overwrite=overwrite)
    except (FileNotFoundError, RuntimeError) as exc:
      print(exc, file=sys.stderr)
      return 1

  print("All requested clients generated successfully.")
  return 0


if __name__ == "__main__":
  sys.exit(main())
