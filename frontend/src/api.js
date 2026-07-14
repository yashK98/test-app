const BASE = "/api";

async function req(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    throw new Error(`Request failed: ${res.status} ${path}`);
  }
  return res.json();
}

export const api = {
  dashboardSummary: () => req("/dashboard/summary"),
  triggerScan: () => req("/drift/scan", { method: "POST" }),
  getReport: (app) => req(`/drift/reports/${app}`),
  getTrend: (app) => req(`/drift/trend/${app}`),
  getSuggestions: (app) => req(`/remediation/suggestions/${app}`),
  applyRemediation: (app, action) =>
    req(`/remediation/apply/${app}/${action}`, { method: "POST" }),
  getAppEnvironments: (app) => req(`/environments/${app}`),
};
