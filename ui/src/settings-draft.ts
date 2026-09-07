/** Polling may update the saved state, never an unsaved or in-flight edit. */
export interface TradingSettings {
  slot_count: number;
  target_notional_usdt: string;
  emergency_stop: boolean;
}

export interface TradingLimits { max_slots: number; max_position_budget_usdt: string }

export function settingsProblem(settings: TradingSettings, limits: TradingLimits): string | null {
  const amount = Number(settings.target_notional_usdt);
  if (!Number.isInteger(settings.slot_count) || settings.slot_count < 1 || settings.slot_count > limits.max_slots)
    return `Freigegeben sind 1 bis ${limits.max_slots} Slots. Dieser Entwurf kann nicht übernommen werden.`;
  if (!Number.isFinite(amount) || amount <= 0)
    return "Positionsgröße muss eine positive, endliche USDT-Zahl sein.";
  if (settings.slot_count * amount > Number(limits.max_position_budget_usdt))
    return `Positionsbudget über der freigegebenen Grenze von ${formatBudget(limits.max_position_budget_usdt)} USDT. Kein zusätzliches Kontoguthaben durch Einstellen einer größeren Zahl.`;
  return null;
}

function formatBudget(value: string | number): string {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? new Intl.NumberFormat("de-DE", { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(parsed) : "ungültig";
}

export function describeSettings(value: TradingSettings): string {
  return `${value.slot_count} × ${formatBudget(value.target_notional_usdt)} USDT · Positionsbudget ${formatBudget(value.slot_count * Number(value.target_notional_usdt))} USDT · Einstiegspause ${value.emergency_stop ? "EIN" : "AUS"}`;
}

export function describeLivePlan(saved: TradingSettings | null, draft: TradingSettings, dirty: boolean, saving: boolean, limits: TradingLimits | null): string {
  if (!saved || !limits) return "Gemeinsame Einstellungen nicht verfügbar. Keine Live-Freigabe.";
  const active = `Gemeinsam gespeichert: ${describeSettings(saved)}.`;
  if (dirty || saving) return `${active} ${saving ? "Wird gespeichert" : "Ungespeicherter Entwurf"}: ${describeSettings(draft)}. ${settingsProblem(draft, limits) ?? "Zuerst ANWENDEN oder verwerfen; Live an ist mit ungespeicherten Änderungen blockiert."}`;
  return `${active} Paper verwendet diese Werte; normaler Livebetrieb muss nach technischer Freigabe dieselben Werte verwenden. Live ist dadurch nicht eingeschaltet. Der separate Einmaltest bleibt 1 × 50 USDT.`;
}

export class SettingsDraft {
  dirty = false;
  saving = false;

  edit(): void { this.dirty = true; }
  get acceptsPolling(): boolean { return !this.dirty && !this.saving; }
  beginSave(): boolean {
    if (this.saving) return false;
    this.saving = true;
    return true;
  }
  finishSave(success: boolean): void {
    this.saving = false;
    if (success) this.dirty = false;
  }
  discard(): void { if (!this.saving) this.dirty = false; }
}
