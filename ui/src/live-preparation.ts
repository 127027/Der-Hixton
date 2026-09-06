/** Private controls: no localStorage/sessionStorage, no secret echo, no automatic enable. */
interface LiveStatus {
  state: string;
  ready: boolean;
  authenticated: boolean;
  password_configured: boolean;
  credentials: { configured: boolean; fingerprint?: string; saved_at_utc?: string };
  blockers: string[];
  account_check: { free_usdt: string; free_bnb: string; checked_at_utc: string; blockers: string[] } | null;
}

function element<T extends HTMLElement>(id: string): T {
  const item = document.getElementById(id);
  if (!item) throw new Error(`Missing control: ${id}`);
  return item as T;
}

export function initializeLivePreparation(): void {
  let last: LiveStatus | null = null;
  let generation = 0;
  let busy = false;
  const controls = ["live-unlock", "live-save-key", "live-delete-key", "live-check", "live-request", "live-off", "live-lock"];
  const message = (value: string): void => { element("live-result").textContent = value; };
  const clearSecrets = (): void => {
    for (const id of ["live-password", "live-password-repeat", "live-api-key", "live-api-secret"]) element<HTMLInputElement>(id).value = "";
  };
  const render = (status: LiveStatus): void => {
    if (last?.authenticated && !status.authenticated) clearSecrets();
    last = status;
    element("live-state").textContent = "LIVE AUS · Vorbereitung, keine Echtgeldfreigabe";
    element("live-auth-panel").classList.toggle("hidden", status.authenticated);
    element("live-protected").classList.toggle("hidden", !status.authenticated);
    element("live-password-repeat-label").classList.toggle("hidden", status.password_configured);
    element("live-unlock").textContent = status.password_configured ? "Geschützten Bereich entsperren" : "Lokales Passwort festlegen & entsperren";
    element("live-credentials-status").textContent = status.credentials.configured
      ? `Binance-Schlüssel gespeichert${status.credentials.fingerprint ? ` · Fingerprint ${status.credentials.fingerprint}` : ""}.`
      : "Binance API-Schlüssel nicht vorhanden. Zuerst den lokalen Bereich entsperren, dann hier eintragen.";
    const list = element("live-blockers");
    list.replaceChildren();
    for (const reason of [...status.blockers, ...(status.account_check?.blockers ?? [])]) {
      const item = document.createElement("li"); item.textContent = reason; list.append(item);
    }
  };
  const request = async (path: string, body: Record<string, unknown>): Promise<Record<string, unknown>> => {
    const response = await fetch(`/api/live/${path}`, { method: "POST", cache: "no-store", credentials: "same-origin",
      headers: { "Content-Type": "application/json", "X-Hixton-Action": "local-ui-v1" }, body: JSON.stringify(body) });
    const result = await response.json() as Record<string, unknown>;
    if (response.status === 409 && path === "enable") {
      render(result as unknown as LiveStatus);
      message("Live bleibt gesperrt. Die Gründe stehen unten. Keine Orders wurden ausgelöst.");
      return result;
    }
    if (!response.ok) throw new Error(typeof result.detail === "string" ? result.detail : `Aktion fehlgeschlagen (${response.status}).`);
    return result;
  };
  const refresh = async (): Promise<void> => {
    const current = ++generation;
    try {
      const response = await fetch("/api/live/status", { cache: "no-store", credentials: "same-origin" });
      const result = await response.json();
      if (current !== generation) return;
      if (!response.ok) throw new Error(typeof result.detail === "string" ? result.detail : "Live-Status nicht erreichbar.");
      render(result as LiveStatus);
    } catch {
      if (current === generation) {
        element("live-state").textContent = "Live-Status nicht erreichbar — keine Freigabe bestätigt.";
        element("live-protected").classList.add("hidden");
      }
    }
  };
  const action = (id: string, run: () => Promise<void>): void => {
    element<HTMLButtonElement>(id).addEventListener("click", async () => {
      if (busy) return;
      busy = true; ++generation;
      for (const control of controls) element<HTMLButtonElement>(control).disabled = true;
      try { await run(); }
      catch (error) { message(error instanceof Error ? error.message : "Aktion fehlgeschlagen."); }
      finally {
        busy = false;
        for (const control of controls) element<HTMLButtonElement>(control).disabled = false;
        await refresh();
      }
    });
  };
  action("live-unlock", async () => {
    const password = element<HTMLInputElement>("live-password").value;
    const repeat = element<HTMLInputElement>("live-password-repeat").value;
    element<HTMLInputElement>("live-password").value = "";
    element<HTMLInputElement>("live-password-repeat").value = "";
    await request("unlock", { password, repeat }); message("Geschützter Bereich für 15 Minuten entsperrt. Live bleibt aus.");
  });
  action("live-save-key", async () => {
    const api_key = element<HTMLInputElement>("live-api-key").value;
    const secret_key = element<HTMLInputElement>("live-api-secret").value;
    if (!window.confirm("Binance-Key im Windows-Anmeldedatenspeicher speichern? Ein vorhandener Key wird ersetzt. Live bleibt aus.")) return;
    try {
      await request("credentials", { api_key, secret_key, confirmation: "SCHLUESSEL SPEICHERN" });
      message("Schlüssel sicher im Windows-Anmeldedatenspeicher gespeichert. Als Nächstes Konto prüfen; kein automatischer Live-Start.");
    } finally { clearSecrets(); }
  });
  action("live-delete-key", async () => {
    if (!window.confirm("Gespeicherten Binance-Key lokal entfernen? Das widerruft ihn NICHT bei Binance.")) return;
    await request("credentials/delete", { confirmation: "SCHLUESSEL ENTFERNEN" }); clearSecrets();
    message("Lokalen Key entfernt. Falls nötig zusätzlich in Binance widerrufen. Lokales Hixton-Passwort bleibt erhalten.");
  });
  action("live-check", async () => {
    message("Binance-Konto und Rechte werden gelesen. Es werden keine Orders gesendet …");
    const result = await request("check", {});
    message(`Kontoprüfung abgeschlossen: ${String(result.free_usdt)} freie USDT, ${String(result.free_bnb)} freie BNB. ${result.account_checks_passed ? "Kontovorprüfung bestanden, Livefreigabe weiterhin separat." : "Blockierungen unten beachten."}`);
  });
  action("live-request", async () => {
    if (!last?.credentials.configured) {
      message("Binance API-Schlüssel fehlt. Bitte API-Key und Secret hier lokal eingeben und sicher speichern.");
      element<HTMLInputElement>("live-api-key").focus(); return;
    }
    await request("enable", {});
  });
  action("live-off", async () => {
    await request("disable", {}); message("Live ist aus. Der Paper-Test und sein Kontostand bleiben unverändert.");
  });
  action("live-lock", async () => { await request("lock", {}); clearSecrets(); message("Geschützter Bereich gesperrt."); });
  window.addEventListener("pagehide", clearSecrets);
  void refresh();
  window.setInterval(() => { if (!busy) void refresh(); }, 5_000);
}
