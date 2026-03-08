/**
 * Systemair Topvex - Custom Lovelace Card
 * SVG schematic of the ventilation unit with live data overlay and controls.
 */

class SystemairTopvexCard extends HTMLElement {
  setConfig(config) {
    this.config = config;
    this._prefix = config.entity_prefix || 'sensor.topvex_tc_c03_el_cav';
    this._dev = this._prefix.replace('sensor.', '');
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

  _getNum(entity_id) {
    const s = this._hass.states[entity_id];
    if (!s || s.state === 'unknown' || s.state === 'unavailable') return null;
    const v = parseFloat(s.state);
    return isNaN(v) ? null : v;
  }

  _callService(domain, service, data) {
    this._hass.callService(domain, service, data);
  }

  _setAhuMode(option) {
    this._callService('select', 'select_option', {
      entity_id: `select.${this._dev}_ahu_modus`,
      option: option,
    });
  }

  _setNumber(entityId, value) {
    this._callService('number', 'set_value', {
      entity_id: entityId,
      value: value,
    });
  }

  _render() {
    const p = this._prefix;
    const dev = this._dev;

    // Sensor data
    const outdoor = this._getNumState(`${p}_utetemperatur`, 1, ' \u00b0C');
    const supply = this._getNumState(`${p}_tillufttemperatur`, 1, ' \u00b0C');
    const exhaust = this._getNumState(`${p}_avkasttemperatur`, 1, ' \u00b0C');
    const extract = this._getNumState(`${p}_avtrekkstemperatur`, 1, ' \u00b0C');
    const afterRecovery = this._getNumState(`${p}_temperatur_etter_veksler`, 1, ' \u00b0C');
    const safFlow = this._getNumState(`${p}_tilluft_luftmengde`, 0, ' m\u00b3/h');
    const eafFlow = this._getNumState(`${p}_avtrekk_luftmengde`, 0, ' m\u00b3/h');
    const safPct = this._getNumState(`${p}_tilluftvifte_utgang`, 1, ' %');
    const eafPct = this._getNumState(`${p}_avtrekksvifte_utgang`, 1, ' %');
    const recovery = this._getNumState(`${p}_gjenvinningsgrad`, 0, ' % \u03b7');
    const frost = this._getNumState(`${p}_frostsikring`, 0, ' %');
    const bypass = this._getNumState(`${p}_bypass`, 0, ' %');
    const exchPressure = this._getNumState(`${p}_vekslertrykk`, 0, ' Pa');
    const unitMode = this._getState(`${p}_driftsmodus`, '--');

    // Control states
    const ahuMode = this._getState(`select.${dev}_ahu_modus`, '--');
    const supplySetpoint = this._getNum(`number.${dev}_tilluft_settpunkt`);
    const safFlowLow = this._getNum(`number.${dev}_saf_flow_lav`);
    const safFlowNormal = this._getNum(`number.${dev}_saf_flow_normal`);
    const safFlowHigh = this._getNum(`number.${dev}_saf_flow_hoy`);
    const eafFlowLow = this._getNum(`number.${dev}_eaf_flow_lav`);
    const eafFlowNormal = this._getNum(`number.${dev}_eaf_flow_normal`);
    const eafFlowHigh = this._getNum(`number.${dev}_eaf_flow_hoy`);

    const boostRemaining = this._getNum(`${p}_komfyravtrekk_gjenstaaende`) || 0;
    const spDisplay = supplySetpoint !== null ? supplySetpoint.toFixed(1) : '--';

    const modes = ['Av', 'Auto', 'Lav', 'Normal', 'H\u00f8y'];

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

        /* Controls */
        .controls { border-top: 1px solid rgba(126,200,227,0.15); margin-top: 12px; padding-top: 12px; }
        .ctrl-section { margin-bottom: 12px; }
        .ctrl-label { color: rgba(255,255,255,0.5); font-size: 11px; font-family: sans-serif; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px; }

        .mode-btns { display: flex; gap: 4px; }
        .mode-btn {
          flex: 1; padding: 7px 0; border: 1px solid rgba(126,200,227,0.3); border-radius: 6px;
          background: rgba(255,255,255,0.05); color: rgba(255,255,255,0.7); font-size: 12px;
          font-family: sans-serif; cursor: pointer; text-align: center; transition: all 0.15s;
        }
        .mode-btn:hover { background: rgba(126,200,227,0.15); }
        .mode-btn.active { background: rgba(126,200,227,0.25); color: #7ec8e3; border-color: #7ec8e3; font-weight: 600; }
        .mode-btn.off { border-color: rgba(255,100,100,0.3); }
        .mode-btn.off.active { background: rgba(255,100,100,0.2); color: #ff8888; border-color: #ff8888; }

        .temp-row { display: flex; align-items: center; gap: 8px; }
        .temp-btn {
          width: 36px; height: 36px; border-radius: 8px; border: 1px solid rgba(126,200,227,0.3);
          background: rgba(255,255,255,0.05); color: #7ec8e3; font-size: 18px; cursor: pointer;
          display: flex; align-items: center; justify-content: center; font-family: sans-serif;
        }
        .temp-btn:hover { background: rgba(126,200,227,0.15); }
        .temp-val { color: #fff; font-size: 20px; font-weight: 600; font-family: sans-serif; min-width: 70px; text-align: center; }

        .flow-row { display: flex; align-items: center; gap: 8px; }
        .flow-lbl { color: rgba(255,255,255,0.6); font-size: 12px; font-family: sans-serif; min-width: 50px; }
        .flow-input {
          width: 100%; padding: 5px 4px; border: 1px solid rgba(126,200,227,0.2); border-radius: 5px;
          background: rgba(0,0,0,0.3); color: #7ec8e3; font-size: 13px; font-family: sans-serif;
          text-align: center; box-sizing: border-box; -moz-appearance: textfield;
        }
        .flow-input::-webkit-inner-spin-button, .flow-input::-webkit-outer-spin-button { -webkit-appearance: none; }
        .flow-input:focus { outline: none; border-color: #7ec8e3; }

        .boost-row { display: flex; gap: 4px; flex-wrap: wrap; }
        .boost-btn {
          padding: 6px 12px; border: 1px solid rgba(255,180,50,0.3); border-radius: 6px;
          background: rgba(255,180,50,0.08); color: rgba(255,180,50,0.8); font-size: 12px;
          font-family: sans-serif; cursor: pointer;
        }
        .boost-btn:hover { background: rgba(255,180,50,0.2); }
        .boost-btn.cancel { border-color: rgba(255,100,100,0.3); background: rgba(255,100,100,0.08); color: rgba(255,100,100,0.8); }
        .boost-btn.cancel:hover { background: rgba(255,100,100,0.2); }
        .boost-active { color: #ffb432; font-size: 12px; font-family: sans-serif; padding: 6px 0; }
      </style>
      <ha-card>
        <div class="card">
          <div class="title">Topvex TC/C03 EL CAV</div>
          <div class="mode">Driftsmodus: ${unitMode}</div>
          <svg viewBox="0 0 1000 420" xmlns="http://www.w3.org/2000/svg">
            <rect width="1000" height="420" fill="#0d2137" rx="8"/>
            <rect x="20" y="300" width="280" height="24" rx="2" class="duct-outdoor" opacity="0.8"/>
            <rect x="470" y="300" width="510" height="24" rx="2" class="duct-supply" opacity="0.8"/>
            <polygon points="75,312 30,292 30,332" fill="#5abf5f" opacity="0.95"/>
            <polygon points="145,312 100,292 100,332" fill="#5abf5f" opacity="0.45"/>
            <polygon points="970,312 925,292 925,332" fill="#3ac4e8" opacity="0.95"/>
            <polygon points="860,312 815,292 815,332" fill="#3ac4e8" opacity="0.45"/>
            <rect x="20" y="96" width="280" height="24" rx="2" class="duct-exhaust" opacity="0.8"/>
            <rect x="470" y="96" width="510" height="24" rx="2" class="duct-extract" opacity="0.8"/>
            <polygon points="30,108 75,88 75,128" fill="#c49a2a" opacity="0.95"/>
            <polygon points="100,108 145,88 145,128" fill="#c49a2a" opacity="0.45"/>
            <polygon points="925,108 970,88 970,128" fill="#e8c830" opacity="0.95"/>
            <polygon points="815,108 860,88 860,128" fill="#e8c830" opacity="0.45"/>
            <rect x="155" y="285" width="50" height="50" rx="4" class="component-fill"/>
            <rect x="155" y="285" width="50" height="50" rx="4" class="component-box"/>
            <polyline points="165,290 175,330 185,290 195,330" class="filter-line"/>
            <rect x="680" y="81" width="50" height="50" rx="4" class="component-fill"/>
            <rect x="680" y="81" width="50" height="50" rx="4" class="component-box"/>
            <polyline points="690,86 700,126 710,86 720,126" class="filter-line"/>
            <rect x="320" y="75" width="130" height="268" rx="6" class="recovery-box"/>
            <line x1="335" y1="90" x2="435" y2="328" class="recovery-x"/>
            <line x1="435" y1="90" x2="335" y2="328" class="recovery-x"/>
            <rect x="300" y="300" width="170" height="24" rx="2" fill="#2a6e4e" opacity="0.5"/>
            <rect x="300" y="96" width="170" height="24" rx="2" fill="#6e5a14" opacity="0.5"/>
            <rect x="330" y="148" width="110" height="110" rx="4" fill="rgba(0,0,0,0.5)"/>
            <circle cx="540" cy="312" r="22" class="fan-circle"/>
            <polygon points="530,300 530,324 555,312" style="fill:none;stroke:rgba(255,255,255,0.7);stroke-width:1.5"/>
            <circle cx="240" cy="108" r="22" class="fan-circle"/>
            <polygon points="250,96 250,120 225,108" style="fill:none;stroke:rgba(255,255,255,0.7);stroke-width:1.5"/>
            <rect x="650" y="290" width="45" height="44" rx="4" class="heater-box"/>
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
            <text x="385" y="172" style="fill:#ffffff;font-size:22px;font-weight:700;font-family:sans-serif" text-anchor="middle">${recovery}</text>
            <text x="385" y="190" style="fill:rgba(255,255,255,0.7);font-size:12px;font-family:sans-serif" text-anchor="middle">Gjenvinning</text>
            <text x="385" y="218" style="fill:#7ec8e3;font-size:16px;font-weight:600;font-family:sans-serif" text-anchor="middle">${frost}</text>
            <text x="385" y="234" style="fill:rgba(255,255,255,0.7);font-size:11px;font-family:sans-serif" text-anchor="middle">Frostsikring</text>
            <text x="385" y="252" style="fill:rgba(255,255,255,0.5);font-size:11px;font-family:sans-serif" text-anchor="middle">${exchPressure}</text>
            <rect x="330" y="268" width="110" height="28" rx="4" fill="rgba(0,0,0,0.4)"/>
            <text x="385" y="265" style="fill:rgba(255,255,255,0.5);font-size:10px;font-family:sans-serif" text-anchor="middle">Bypass</text>
            <text x="385" y="287" style="fill:#fde68a;font-size:13px;font-weight:600;font-family:sans-serif" text-anchor="middle">${bypass}</text>
            <text x="540" y="290" class="label-value" text-anchor="middle">${safFlow}</text>
            <text x="540" y="360" class="label-pct" text-anchor="middle">${safPct}</text>
            <text x="240" y="155" class="label-pct" text-anchor="middle">${eafPct}</text>
            <text x="160" y="88" class="label-value">${eafFlow}</text>
            <text x="790" y="327" class="label-value" text-anchor="middle">${spDisplay}\u00b0C</text>
            <text x="790" y="340" class="label-dim" text-anchor="middle">Settpunkt</text>
            <text x="180" y="350" class="label-dim" text-anchor="middle">Filter</text>
            <text x="705" y="145" class="label-dim" text-anchor="middle">Filter</text>
            <text x="540" y="345" class="label-dim" text-anchor="middle">Vifte SAF</text>
            <text x="240" y="142" class="label-dim" text-anchor="middle">Vifte EAF</text>
            <text x="672" y="345" class="label-dim" text-anchor="middle">Varmer</text>
            <text x="385" y="68" style="fill:rgba(255,255,255,0.6);font-size:11px;font-family:sans-serif" text-anchor="middle">Veksler</text>
            <rect x="130" y="55" width="620" height="320" rx="8" style="fill:none;stroke:rgba(126,200,227,0.15);stroke-width:1;stroke-dasharray:4,4"/>
            <text x="140" y="48" class="label-dim" style="font-size:10px">Topvex TC/C03 - Ventilasjonsaggregat</text>
          </svg>

          <div class="controls">
            <div class="ctrl-section">
              <div class="ctrl-label">Modus</div>
              <div class="mode-btns">
                ${modes.map(m => `<button class="mode-btn${m === 'Av' ? ' off' : ''}${ahuMode === m ? ' active' : ''}" data-mode="${m}">${m}</button>`).join('')}
              </div>
            </div>

            <div class="ctrl-section">
              <div class="ctrl-label">Tilluft settpunkt</div>
              <div class="temp-row">
                <button class="temp-btn" data-delta="-0.5">\u2212</button>
                <div class="temp-val">${spDisplay}\u00b0C</div>
                <button class="temp-btn" data-delta="0.5">+</button>
              </div>
            </div>

            <div class="ctrl-section">
              <div class="ctrl-label">Normal luftmengder (m\u00b3/h)</div>
              <div class="flow-row">
                <span class="flow-lbl">Tilluft</span>
                <input type="number" class="flow-input" data-entity="number.${dev}_saf_flow_normal" value="${safFlowNormal ?? ''}" step="10">
                <span class="flow-lbl">Avtrekk</span>
                <input type="number" class="flow-input" data-entity="number.${dev}_eaf_flow_normal" value="${eafFlowNormal ?? ''}" step="10">
              </div>
            </div>

            <div class="ctrl-section">
              <div class="ctrl-label">Komfyravtrekk</div>
              ${boostRemaining > 0
                ? `<div class="boost-active">Aktiv \u2014 ${Math.ceil(boostRemaining / 60)} min igjen</div>`
                : ''}
              <div class="boost-row">
                <button class="boost-btn" data-minutes="10">10 min</button>
                <button class="boost-btn" data-minutes="20">20 min</button>
                <button class="boost-btn" data-minutes="30">30 min</button>
                ${boostRemaining > 0
                  ? `<button class="boost-btn cancel" data-action="cancel">Avbryt</button>`
                  : ''}
              </div>
            </div>
          </div>
        </div>
      </ha-card>
    `;

    this._attachListeners();
  }

  _attachListeners() {
    const root = this.shadowRoot;
    const dev = this._dev;

    // AHU mode buttons
    root.querySelectorAll('.mode-btn').forEach(btn => {
      btn.addEventListener('click', () => this._setAhuMode(btn.dataset.mode));
    });

    // Temperature +/- buttons
    root.querySelectorAll('.temp-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const current = this._getNum(`number.${dev}_tilluft_settpunkt`);
        if (current === null) return;
        const delta = parseFloat(btn.dataset.delta);
        const next = Math.max(10, Math.min(30, current + delta));
        this._setNumber(`number.${dev}_tilluft_settpunkt`, next);
      });
    });

    // Flow inputs
    root.querySelectorAll('.flow-input').forEach(input => {
      input.addEventListener('change', () => {
        const val = parseFloat(input.value);
        if (!isNaN(val) && val >= 50 && val <= 2000) {
          this._setNumber(input.dataset.entity, val);
        }
      });
    });

    // Boost buttons
    root.querySelectorAll('.boost-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        if (btn.dataset.action === 'cancel') {
          this._callService('systemair_topvex', 'cancel_kitchen_boost', {});
        } else {
          this._callService('systemair_topvex', 'kitchen_boost', {
            minutes: parseInt(btn.dataset.minutes),
          });
        }
      });
    });
  }

  getCardSize() {
    return 8;
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
  description: 'SVG schematic with controls for Systemair Topvex ventilation unit',
});
