/** Private controls: no localStorage/sessionStorage, no secret echo, no automatic enable. */
interface LiveStatus {
  state: string;
  ready: boolean;
  authenticated: boolean;
  password_configured: boolean;
  credentials: { configured: boolean; fingerprint?: string; saved_at_utc?: string };
  blockers: string[];
  account_check: { free_usdt: string; free_bnb: string; checked_at_utc: string; blockers: string[] } | null;
  paper_settings_preview?: {slot_count: number; target_notional_usdt: string} | null;
  trial?: {state: string; symbol?: string; reason?: string | null; net_pnl_usdt?: string | null};
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
  const controls = ["live-unlock", "live-save-key", "live-delete-key", "live-check", "live-request", "live-off", "live-lock", "live-trial-start", "live-trial-off"];
  const message = (value: string): void => { element("live-result").textContent = value; };
  const clearSecrets = (): void => {
    for (const id of ["live-password", "live-password-repeat", "live-api-key", "live-api-secret", "live-confirmation", "live-trial-confirmation"]) element<HTMLInputElement>(id).value = "";
  };
  const render = (status: LiveStatus): void => {
    if (last?.authenticated && !status.authenticated) clearSecrets();
    last = status;
    element("live-state").textContent = status.state === "LIVE_DISABLED"
      ? "LIVE AUS · Vorbereitung, keine Echtgeldfreigabe"
      : `EINMALTEST · ${status.state} · offene oder ungeklärte Ausführung beachten`;
    element("live-auth-panel").classList.toggle("hidden", status.authenticated);
    element<HTMLFieldSetElement>("live-protected").disabled = !status.authenticated;
    element("live-key-help").textContent = status.authenticated
      ? "Entsperrt. API-Key und zugehöriges Secret in die unten sichtbaren Felder eintragen, sicher speichern und danach das Binance-Konto prüfen. Kein automatischer Handelsstart."
      : "Die Binance-Key-Felder und Handelsaktionen sind unten sichtbar, aber gesperrt. Zuerst oben das lokale Hixton-Passwort festlegen bzw. damit entsperren; danach werden sie bedienbar.";
    element("live-password-repeat-label").classList.toggle("hidden", status.password_configured);
    element("live-unlock").textContent = status.password_configured ? "Geschützten Bereich entsperren" : "Lokales Passwort festlegen & entsperren";
    element("live-credentials-status").textContent = status.credentials.configured
      ? `Binance-Schlüssel gespeichert${status.credentials.fingerprint ? ` · Fingerprint ${status.credentials.fingerprint}` : ""}.`
      : "Binance API-Schlüssel nicht vorhanden. Zuerst den lokalen Bereich entsperren, dann hier eintragen.";
    const plan = status.paper_settings_preview;
    element("live-plan").textContent = plan
      ? `Gespeichertes Paper-Budget: ${plan.slot_count} × ${plan.target_notional_usdt} USDT. Das ist die spätere Live-Vorlage, noch keine Echtgeldfreigabe. Der Einmaltest bleibt davon unabhängig 1 × 50 USDT.`
      : "Gespeicherte Paper-Einstellungen derzeit nicht verfügbar; keine Live-Budgetfreigabe.";
    element("live-trial-status").textContent = status.trial?.state && status.trial.state !== "NOT_STARTED"
      ? `Einmaltest: ${status.trial.state}${status.trial.symbol ? ` · ${status.trial.symbol}` : ""}${status.trial.reason ? ` · ${status.trial.reason}` : ""}. Echtgeld-Abnahme nicht durch einen simulierten Test ersetzt.`
      : "Einmaltest nicht gestartet. Dieser Button prüft die Freigabe; bei fehlender Orderanbindung bleiben echte Orders gesperrt.";
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
    if (response.status === 409 && (path === "enable" || path === "trial/start")) {
      render(result as unknown as LiveStatus);
      message(path === "trial/start" ? "50-USDT-Einmaltest nicht gestartet. Technische Freigabe fehlt; Gründe unten. Kein Kauf ausgelöst." : "Live bleibt gesperrt. Die Gründe stehen unten. Keine Orders wurden ausgelöst.");
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
        element<HTMLFieldSetElement>("live-protected").disabled = true;
        clearSecrets();
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
    if (element<HTMLInputElement>("live-confirmation").value !== "SPEICHERN") {
      message("Zum Speichern/Ersetzen zuerst SPEICHERN in das Bestätigungsfeld eingeben. Live bleibt aus.");
      element<HTMLInputElement>("live-confirmation").focus(); return;
    }
    try {
      await request("credentials", { api_key, secret_key, confirmation: "SCHLUESSEL SPEICHERN" });
      message("Schlüssel sicher im Windows-Anmeldedatenspeicher gespeichert. Als Nächstes Konto prüfen; kein automatischer Live-Start.");
    } finally { clearSecrets(); }
  });
  action("live-delete-key", async () => {
    if (element<HTMLInputElement>("live-confirmation").value !== "ENTFERNEN") {
      message("Zum lokalen Entfernen zuerst ENTFERNEN eingeben. Dies widerruft den Key nicht bei Binance.");
      element<HTMLInputElement>("live-confirmation").focus(); return;
    }
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
    const result = await request("disable", {});
    message(typeof result.message === "string" ? result.message : "Neue Live-Einstiege gesperrt. Bestehende echte Positionen nicht automatisch verkauft; Paper bleibt unverändert.");
  });
  action("live-trial-start", async () => {
    if (!last?.credentials.configured) {
      message("Für den Einmaltest zuerst Binance API-Key und Secret in den sichtbaren Feldern speichern und das Konto prüfen.");
      element<HTMLInputElement>("live-api-key").focus(); return;
    }
    if (element<HTMLInputElement>("live-trial-confirmation").value !== "TEST 50 USDT") {
      message("Für genau einen signalgesteuerten 50-USDT-Einmaltest TEST 50 USDT eingeben. Das ersetzt keine technische Freigabe.");
      element<HTMLInputElement>("live-trial-confirmation").focus(); return;
    }
    try { await request("trial/start", {confirmation: "TEST 50 USDT", notional_usdt: "50.00"}); }
    finally { element<HTMLInputElement>("live-trial-confirmation").value = ""; }
  });
  action("live-trial-off", async () => {
    const result = await request("trial/stop", {});
    message(typeof result.message === "string" ? result.message : "Neue Test-Einstiege gesperrt; kein automatischer Verkauf.");
  });
  action("live-lock", async () => { await request("lock", {}); clearSecrets(); message("Geschützter Bereich gesperrt."); });
  window.addEventListener("pagehide", clearSecrets);
  void refresh();
  window.setInterval(() => { if (!busy) void refresh(); }, 5_000);
}
