/**
 * Systemair Topvex - Custom Lovelace Card
 * SVG schematic of the ventilation unit with live data overlay.
 */

class SystemairTopvexCard extends HTMLElement {
  setConfig(config) {
    this.config = config;
    this._prefix = config.entity_prefix || 'sensor.topvex_tc_c03_el_cav';
  }

  set hass(hass) {
    this._hass = hass;
    if (!this.shadowRoot) {
      this.attachShadow({ mode: 'open' });
    }
    this._render();
  }

  _getState(entity_id, fallback) {
    const s = this._hass.states[entity_id];
    return s ? s.state : (fallback || '--');
  }

  _getNumState(entity_id, decimals, unit) {
    const s = this._hass.states[entity_id];
    if (!s || s.state === 'unknown' || s.state === 'unavailable') return '--';
    const v = parseFloat(s.state);
    if (isNaN(v)) return '--';
    return v.toFixed(decimals) + (unit || '');
  }

  _render() {
    const p = this._prefix;
    const outdoor = this._getNumState(`${p}_utetemperatur`, 1, ' °C');
    const supply = this._getNumState(`${p}_tillufttemperatur`, 1, ' °C');
    const exhaust = this._getNumState(`${p}_avkasttemperatur`, 1, ' °C');
    const extract = this._getNumState(`${p}_avtrekkstemperatur`, 1, ' °C');
    const afterRecovery = this._getNumState(`${p}_temperatur_etter_veksler`, 1, ' °C');
    const safFlow = this._getNumState(`${p}_tilluft_luftmengde`, 0, ' m³/h');
    const eafFlow = this._getNumState(`${p}_avtrekk_luftmengde`, 0, ' m³/h');
    const safPct = this._getNumState(`${p}_tilluftvifte_utgang`, 1, ' %');
    const eafPct = this._getNumState(`${p}_avtrekksvifte_utgang`, 1, ' %');
    const recovery = this._getNumState(`${p}_gjenvinningsgrad`, 0, ' % η');
    const frost = this._getNumState(`${p}_frostsikring`, 0, ' %');
    const bypass = this._getNumState(`${p}_bypass`, 0, ' %');
    const exchPressure = this._getNumState(`${p}_vekslertrykk`, 0, ' Pa');
    const supplySP = this._getNumState(`${p}_tilluft_settpunkt`, 1, '°C');
    const unitMode = this._getState(`${p}_driftsmodus`, '--');

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; }
        .card { background: #0d2137; border-radius: 12px; padding: 16px; }
        .title { color: #7ec8e3; font-size: 14px; font-weight: 600; margin-bottom: 8px; font-family: sans-serif; }
        .mode { color: #5a9ab5; font-size: 12px; font-family: sans-serif; }
        svg { width: 100%; height: auto; }
        .duct-outdoor { fill: #3a8c3f; }
        .duct-supply { fill: #0099cc; }
        .duct-extract { fill: #d4a017; }
        .duct-exhaust { fill: #8b6914; }
        .component-box { fill: none; stroke: rgba(255,255,255,0.5); stroke-width: 1.5; }
        .component-fill { fill: rgba(255,255,255,0.08); }
        .recovery-box { fill: rgba(255,255,255,0.05); stroke: rgba(255,255,255,0.4); stroke-width: 1.5; }
        .fan-circle { fill: none; stroke: rgba(255,255,255,0.7); stroke-width: 1.5; }
        .heater-box { fill: rgba(255,255,255,0.05); stroke: rgba(255,255,255,0.5); stroke-width: 1.5; }
        .filter-line { stroke: rgba(255,255,255,0.6); stroke-width: 1; fill: none; }
        .recovery-x { stroke: rgba(255,255,255,0.5); stroke-width: 2; fill: none; }
        .label-dim { fill: rgba(255,255,255,0.5); font-size: 11px; font-family: sans-serif; }
        .label-value { fill: #7ec8e3; font-size: 14px; font-weight: 600; font-family: sans-serif; }
        .label-temp { fill: #ffffff; font-size: 14px; font-weight: 600; font-family: sans-serif; }
        .label-pct { fill: #7ec8e3; font-size: 13px; font-weight: 600; font-family: sans-serif; }
      </style>
      <ha-card>
        <div class="card">
          <div class="title">Topvex TC/C03 EL CAV</div>
          <div class="mode">Driftsmodus: ${unitMode}</div>
          <svg viewBox="0 0 1000 420" xmlns="http://www.w3.org/2000/svg">
            <rect width="1000" height="420" fill="#0d2137" rx="8"/>

            <!-- BOTTOM: Friskulft inn (green) → Tilluft ut (blue) -->
            <rect x="20" y="300" width="280" height="24" rx="2" class="duct-outdoor" opacity="0.8"/>
            <rect x="470" y="300" width="510" height="24" rx="2" class="duct-supply" opacity="0.8"/>
            <polygon points="75,312 30,292 30,332" fill="#5abf5f" opacity="0.95"/>
            <polygon points="145,312 100,292 100,332" fill="#5abf5f" opacity="0.45"/>
            <polygon points="970,312 925,292 925,332" fill="#3ac4e8" opacity="0.95"/>
            <polygon points="860,312 815,292 815,332" fill="#3ac4e8" opacity="0.45"/>

            <!-- TOP: Avkast ut (brown) ← Avtrekk inn (yellow) -->
            <rect x="20" y="96" width="280" height="24" rx="2" class="duct-exhaust" opacity="0.8"/>
            <rect x="470" y="96" width="510" height="24" rx="2" class="duct-extract" opacity="0.8"/>
            <polygon points="30,108 75,88 75,128" fill="#c49a2a" opacity="0.95"/>
            <polygon points="100,108 145,88 145,128" fill="#c49a2a" opacity="0.45"/>
            <polygon points="925,108 970,88 970,128" fill="#e8c830" opacity="0.95"/>
            <polygon points="815,108 860,88 860,128" fill="#e8c830" opacity="0.45"/>

            <!-- Supply filter -->
            <rect x="155" y="285" width="50" height="50" rx="4" class="component-fill"/>
            <rect x="155" y="285" width="50" height="50" rx="4" class="component-box"/>
            <polyline points="165,290 175,330 185,290 195,330" class="filter-line"/>

            <!-- Extract filter -->
            <rect x="680" y="81" width="50" height="50" rx="4" class="component-fill"/>
            <rect x="680" y="81" width="50" height="50" rx="4" class="component-box"/>
            <polyline points="690,86 700,126 710,86 720,126" class="filter-line"/>

            <!-- Heat recovery -->
            <rect x="320" y="75" width="130" height="268" rx="6" class="recovery-box"/>
            <line x1="335" y1="90" x2="435" y2="328" class="recovery-x"/>
            <line x1="435" y1="90" x2="335" y2="328" class="recovery-x"/>
            <rect x="300" y="300" width="170" height="24" rx="2" fill="#2a6e4e" opacity="0.5"/>
            <rect x="300" y="96" width="170" height="24" rx="2" fill="#6e5a14" opacity="0.5"/>
            <rect x="330" y="148" width="110" height="110" rx="4" fill="rgba(0,0,0,0.5)"/>

            <!-- SAF fan -->
            <circle cx="540" cy="312" r="22" class="fan-circle"/>
            <polygon points="530,300 530,324 555,312" style="fill:none;stroke:rgba(255,255,255,0.7);stroke-width:1.5"/>

            <!-- EAF fan -->
            <circle cx="240" cy="108" r="22" class="fan-circle"/>
            <polygon points="250,96 250,120 225,108" style="fill:none;stroke:rgba(255,255,255,0.7);stroke-width:1.5"/>

            <!-- Heater -->
            <rect x="650" y="290" width="45" height="44" rx="4" class="heater-box"/>

            <!-- DATA LABELS -->
            <text x="50" y="280" style="fill:#5abf5f;font-size:12px;font-weight:600;font-family:sans-serif">Friskulft inn</text>
            <text x="50" y="295" class="label-temp">${outdoor}</text>

            <text x="950" y="280" style="fill:#3ac4e8;font-size:12px;font-weight:600;font-family:sans-serif" text-anchor="end">Tilluft til hus</text>
            <text x="950" y="295" class="label-temp" text-anchor="end">${supply}</text>

            <text x="50" y="75" style="fill:#c49a2a;font-size:12px;font-weight:600;font-family:sans-serif">Avkast ut</text>
            <text x="50" y="88" class="label-temp">${exhaust}</text>

            <text x="950" y="75" style="fill:#e8c830;font-size:12px;font-weight:600;font-family:sans-serif" text-anchor="end">Avtrekk fra hus</text>
            <text x="950" y="88" class="label-temp" text-anchor="end">${extract}</text>

            <text x="480" y="280" class="label-dim" text-anchor="middle">Etter veksler</text>
            <text x="480" y="295" class="label-temp" text-anchor="middle">${afterRecovery}</text>

            <!-- Recovery info -->
            <text x="385" y="172" style="fill:#ffffff;font-size:22px;font-weight:700;font-family:sans-serif" text-anchor="middle">${recovery}</text>
            <text x="385" y="190" style="fill:rgba(255,255,255,0.7);font-size:12px;font-family:sans-serif" text-anchor="middle">Gjenvinning</text>
            <text x="385" y="218" style="fill:#7ec8e3;font-size:16px;font-weight:600;font-family:sans-serif" text-anchor="middle">${frost}</text>
            <text x="385" y="234" style="fill:rgba(255,255,255,0.7);font-size:11px;font-family:sans-serif" text-anchor="middle">Frostsikring</text>
            <text x="385" y="252" style="fill:rgba(255,255,255,0.5);font-size:11px;font-family:sans-serif" text-anchor="middle">${exchPressure}</text>

            <!-- Bypass -->
            <rect x="330" y="268" width="110" height="28" rx="4" fill="rgba(0,0,0,0.4)"/>
            <text x="385" y="265" style="fill:rgba(255,255,255,0.5);font-size:10px;font-family:sans-serif" text-anchor="middle">Bypass</text>
            <text x="385" y="287" style="fill:#fde68a;font-size:13px;font-weight:600;font-family:sans-serif" text-anchor="middle">${bypass}</text>

            <!-- Fan info -->
            <text x="540" y="290" class="label-value" text-anchor="middle">${safFlow}</text>
            <text x="540" y="360" class="label-pct" text-anchor="middle">${safPct}</text>
            <text x="240" y="155" class="label-pct" text-anchor="middle">${eafPct}</text>
            <text x="160" y="88" class="label-value">${eafFlow}</text>

            <!-- Setpoint -->
            <text x="790" y="340" class="label-dim" text-anchor="middle">Settpunkt</text>
            <text x="790" y="327" class="label-value" text-anchor="middle">${supplySP}</text>

            <!-- Component labels -->
            <text x="180" y="350" class="label-dim" text-anchor="middle">Filter</text>
            <text x="705" y="145" class="label-dim" text-anchor="middle">Filter</text>
            <text x="540" y="345" class="label-dim" text-anchor="middle">Vifte SAF</text>
            <text x="240" y="142" class="label-dim" text-anchor="middle">Vifte EAF</text>
            <text x="672" y="345" class="label-dim" text-anchor="middle">Varmer</text>
            <text x="385" y="68" style="fill:rgba(255,255,255,0.6);font-size:11px;font-family:sans-serif" text-anchor="middle">Veksler</text>

            <!-- AHU outline -->
            <rect x="130" y="55" width="620" height="320" rx="8" style="fill:none;stroke:rgba(126,200,227,0.15);stroke-width:1;stroke-dasharray:4,4"/>
            <text x="140" y="48" class="label-dim" style="font-size:10px">Topvex TC/C03 - Ventilasjonsaggregat</text>
          </svg>
        </div>
      </ha-card>
    `;
  }

  getCardSize() {
    return 6;
  }

  static getStubConfig() {
    return { entity_prefix: 'sensor.topvex_tc_c03_el_cav' };
  }
}

customElements.define('systemair-topvex-card', SystemairTopvexCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: 'systemair-topvex-card',
  name: 'Systemair Topvex',
  description: 'SVG schematic for Systemair Topvex ventilation unit',
});
