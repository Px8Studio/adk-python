"""Utility helpers for regenerating the DNB OpenAPI clients."""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from pyopenapi_gen import generate_client, GenerationError


@dataclass(frozen=True)
class ClientSpec:
  key: str
  spec_path: Path
  output_path: Path


CLIENT_SPECS: tuple[ClientSpec, ...] = (
  ClientSpec(
    key="public_register",
    spec_path=Path("backend/apis/dnb/specs/openapi3_publicdatav1.yaml"),
    output_path=Path("backend/clients/dnb/public_register"),
  ),
  ClientSpec(
    key="statistics",
    spec_path=Path("backend/apis/dnb/specs/openapi3_statisticsdatav2024100101.yaml"),
    output_path=Path("backend/clients/dnb/statistics"),
  ),
  ClientSpec(
    key="echo",
    spec_path=Path("backend/apis/dnb/specs/openapi3-echo-api.yaml"),
    output_path=Path("backend/clients/dnb/echo"),
  ),
)


def _repo_root() -> Path:
  return Path(__file__).resolve().parents[2]


def _select_specs(selected_keys: Iterable[str]) -> list[ClientSpec]:
  lookup = {spec.key: spec for spec in CLIENT_SPECS}
  if not selected_keys:
    return list(CLIENT_SPECS)
  missing = [key for key in selected_keys if key not in lookup]
  if missing:
    raise ValueError(f"Unknown client keys requested: {', '.join(missing)}")
  return [lookup[key] for key in selected_keys]


def _generate_single(
  *,
  command: str,
  spec: ClientSpec,
  meta: str,
  overwrite: bool,
) -> None:
  repo_root = _repo_root()
  spec_path = repo_root / spec.spec_path
  output_path = repo_root / spec.output_path
  if not spec_path.exists():
    raise FileNotFoundError(spec_path)
  output_path.parent.mkdir(parents=True, exist_ok=True)
  cli_args = [
    command,
    "generate",
    "--path",
    str(spec_path),
    "--output-path",
    str(output_path),
    "--meta",
    meta,
  ]
  if overwrite:
    cli_args.append("--overwrite")
  print(f"Generating {spec.key} client -> {spec.output_path}")
  result = subprocess.run(cli_args, cwd=repo_root, check=False)
  if result.returncode != 0:
    raise RuntimeError(
      f"openapi-python-client failed for {spec.key} with exit code {result.returncode}"
    )


def main(argv: list[str] | None = None) -> int:
  parser = argparse.ArgumentParser(
    description="Generate Python clients for all configured DNB OpenAPI specs."
  )
  parser.add_argument(
    "--command",
    default="openapi-python-client",
    help="CLI executable to invoke (default: %(default)s)",
  )
  parser.add_argument(
    "--meta",
    default="poetry",
    choices=["poetry", "uv", "pdm", "setup", "none"],
    help="Metadata layout to use when generating the client",
  )
  parser.add_argument(
    "--no-overwrite",
    action="store_true",
    help="Do not pass --overwrite to the generator",
  )
  parser.add_argument(
    "--clients",
    nargs="*",
    metavar="CLIENT",
    help="Subset of client keys to generate (default: all)",
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
      _generate_single(
        command=args.command,
        spec=spec,
        meta=args.meta,
        overwrite=overwrite,
      )
    except (FileNotFoundError, RuntimeError) as exc:
      print(exc)
      return 1

  print("All requested clients generated successfully.")
  return 0


if __name__ == "__main__":
  sys.exit(main())

from pyopenapi_gen import generate_client, GenerationError

for spec, package in [
    ("backend/apis/dnb/specs/openapi3_publicdatav1.yaml", "dnb_clients.public_register"),
    ("backend/apis/dnb/specs/openapi3_statisticsdatav2024100101.yaml", "dnb_clients.statistics"),
    ("backend/apis/dnb/specs/openapi3-echo-api.yaml", "dnb_clients.echo"),
]:
    generate_client(
        spec_path=spec,
        project_root="backend",
        output_package=package,
        core_package="dnb_clients.core",
        force=True,
        verbose=True,
    )
