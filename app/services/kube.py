"""Talks to the cluster the same way you do by hand: authenticate with skectl,
then run `kubectl get <kind> -n <ns> -o json` and parse the result.

The auth seam is configurable (see config.py) because how skectl hands its
token to kubectl varies by setup:
  * token mode off (default): running skectl updates your kubeconfig, so plain
    kubectl calls are authenticated afterwards.
  * token mode on: skectl prints a bearer token we pass via `kubectl --token`.
"""
import json
import subprocess
import time

from ..config import settings

# friendly name -> kubectl resource name
RESOURCE_KINDS = {
    "configmap": "configmaps",
    "deployment": "deployments",
    "secret": "secrets",
    "service": "services",
    "ingress": "ingresses",
}

_token_cache = {"token": None, "ts": 0.0}


class KubeError(Exception):
    """Raised for any auth/kubectl failure, carrying a user-friendly message."""


def authenticate() -> tuple[bool, str, str | None]:
    """Run the configured skectl command. Returns (ok, message, token|None)."""
    if not settings.skectl_cmd:
        return True, "No skectl command configured — assuming kubectl is already authenticated.", None

    try:
        proc = subprocess.run(
            settings.skectl_cmd, shell=True, capture_output=True,
            text=True, timeout=settings.auth_timeout)
    except subprocess.TimeoutExpired:
        raise KubeError(
            "skectl timed out. If it requires interactive login (SSO/browser), "
            "run it manually in your terminal first, then leave skectl_cmd blank.")

    if proc.returncode != 0:
        raise KubeError(f"skectl failed: {(proc.stderr or proc.stdout).strip()}")

    token = proc.stdout.strip() if settings.skectl_token_mode else None
    if settings.skectl_token_mode and not token:
        raise KubeError("skectl_token_mode is on but skectl produced no token on stdout.")
    return True, "Authenticated via skectl.", token


def _get_token() -> str | None:
    """Cached token for token-mode; None otherwise (kubeconfig handles auth)."""
    if not settings.skectl_token_mode:
        return None
    now = time.time()
    if _token_cache["token"] and now - _token_cache["ts"] < settings.token_ttl:
        return _token_cache["token"]
    _, _, token = authenticate()
    _token_cache.update(token=token, ts=now)
    return token


def _base_cmd(token: str | None) -> list[str]:
    cmd = [settings.kubectl_bin]
    if settings.kubectl_context:
        cmd += ["--context", settings.kubectl_context]
    if token:
        cmd += ["--token", token]
    return cmd


def _interpret_error(stderr: str) -> str:
    low = stderr.lower()
    if "unauthorized" in low or "you must be logged in" in low or "invalid bearer token" in low:
        return ("Cluster rejected the credentials (token expired?). Re-authenticate "
                "with skectl, then retry. Original: " + stderr)
    if "forbidden" in low:
        return "Access forbidden for this namespace/resource. Original: " + stderr
    if "not found" in low and "namespaces" in low:
        return stderr  # namespace doesn't exist — pass through, it's already clear
    if "refused" in low or "no such host" in low or "timeout" in low:
        return "Could not reach the cluster API server. Original: " + stderr
    return stderr


def _clean(obj: dict) -> dict:
    """Drop the noisiest server-managed field so payloads stay readable."""
    md = obj.get("metadata")
    if isinstance(md, dict):
        md.pop("managedFields", None)
    return obj


def _redact_secret(obj: dict) -> dict:
    data = obj.get("data")
    if isinstance(data, dict):
        obj["data"] = {k: "<redacted>" for k in data}
    return obj


def fetch(kind: str, namespace: str, reveal_secrets: bool = False) -> list[dict]:
    if kind not in RESOURCE_KINDS:
        raise KubeError(
            f"Unsupported kind '{kind}'. Allowed: {', '.join(RESOURCE_KINDS)}")

    token = _get_token()
    cmd = _base_cmd(token) + ["get", RESOURCE_KINDS[kind], "-n", namespace, "-o", "json"]

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=settings.kubectl_timeout)
    except FileNotFoundError:
        raise KubeError(
            f"'{settings.kubectl_bin}' not found. Set KUBECTL_BIN to its full path "
            r"(e.g. C:\Users\you\bin\kubectl.exe).")
    except subprocess.TimeoutExpired:
        raise KubeError(f"kubectl timed out after {settings.kubectl_timeout}s.")

    if proc.returncode != 0:
        raise KubeError(_interpret_error(proc.stderr.strip()))

    items = (json.loads(proc.stdout or "{}") or {}).get("items", [])
    items = [_clean(it) for it in items]
    if kind == "secret" and not reveal_secrets:
        items = [_redact_secret(it) for it in items]
    return items


def fetch_all(namespace: str, reveal_secrets: bool = False) -> dict[str, list[dict]]:
    return {kind: fetch(kind, namespace, reveal_secrets) for kind in RESOURCE_KINDS}
