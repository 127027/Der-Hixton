/** Polling may update the saved state, never an unsaved or in-flight edit. */
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
