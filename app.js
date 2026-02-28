const STORAGE_KEY = "wf_trader_config_v1";

const DEFAULT_STATE = {
  active_region: "trade",
  m1_active: false,
  m1_plat_token: ":platinum:",
  m1_mode: "group",
  m1_g_bronze: "6",
  m1_g_fsilver: "7",
  m1_g_silver: "18",
  m1_g_fgold: "32",
  m1_g_gold: "55",
  m1_s_bronze: "1",
  m1_s_fsilver: "2",
  m1_s_silver: "3",
  m1_s_fgold: "5",
  m1_s_gold: "9",
  m2_active: false,
  m2_plat_token: ":platinum:",
  m2_lith: "4",
  m2_meso: "5",
  m2_neo: "5",
  m2_axi: "10",
  m2_rad: false,
  m3_active: false,
  m3_plat_token: ":platinum:",
  m3_aya: "33",
  m3_rad: false,
  m4_active: false,
  m4_plat_token: ":platinum:",
  m4_items: [],
  m5_plat_token: ":platinum:",
  m5_cn: "私聊即可",
  m5_en: "PM me",
  m6_epoch: "Lith",
  m6_code: "A1",
  m6_mode: "求拉",
  m6_count: "2",
  m6_note: "",
  m6_history: [],
  m7_items: [],
  m7_quick_cn: "",
  m7_quick_en: "",
  thanks_msg: "Tyvm, have a good day!"
};

const EPOCH_CN = { Lith: "古纪", Meso: "前纪", Neo: "中纪", Axi: "后纪" };
let state = loadState();

init();

function init() {
  bindNav();
  bindStaticInputs();
  bindButtons();
  syncStaticInputs();
  renderRegion();
  renderM4Items();
  renderM6History();
  renderM7Items();
  renderM7QuickButtons();
  updateOutputs();
}

function loadState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return structuredClone(DEFAULT_STATE);
    const parsed = JSON.parse(raw);
    return {
      ...structuredClone(DEFAULT_STATE),
      ...parsed,
      m4_items: Array.isArray(parsed.m4_items) ? parsed.m4_items.slice(0, 50) : [],
      m6_history: Array.isArray(parsed.m6_history) ? parsed.m6_history.slice(0, 100) : [],
      m7_items: Array.isArray(parsed.m7_items) ? parsed.m7_items.slice(0, 100) : []
    };
  } catch (_) {
    return structuredClone(DEFAULT_STATE);
  }
}

function saveState() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function bindNav() {
  document.querySelectorAll(".nav-btn[data-region-target]").forEach((btn) => {
    btn.addEventListener("click", () => {
      state.active_region = btn.dataset.regionTarget === "team" ? "team" : "trade";
      renderRegion();
      saveState();
    });
  });
}

function renderRegion() {
  const active = state.active_region === "team" ? "team" : "trade";
  document.querySelectorAll("[data-region]").forEach((el) => {
    el.classList.toggle("hidden", el.dataset.region !== active);
  });
  document.querySelectorAll(".nav-btn[data-region-target]").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.regionTarget === active);
  });
}

function bindStaticInputs() {
  document.querySelectorAll("[data-bind]").forEach((el) => {
    const key = el.dataset.bind;
    const evt = el.tagName === "SELECT" ? "change" : "input";
    el.addEventListener(evt, () => {
      state[key] = el.type === "checkbox" ? el.checked : el.value;
      updateOutputs();
      saveState();
    });
    if (el.type === "checkbox") {
      el.addEventListener("change", () => {
        state[key] = el.checked;
        updateOutputs();
        saveState();
      });
    }
  });
}

function syncStaticInputs() {
  document.querySelectorAll("[data-bind]").forEach((el) => {
    const key = el.dataset.bind;
    if (!(key in state)) return;
    if (el.type === "checkbox") el.checked = !!state[key];
    else el.value = state[key] ?? "";
  });
}

function bindButtons() {
  document.querySelectorAll(".copy-btn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const targetId = btn.dataset.copyTarget;
      const el = document.getElementById(targetId);
      await copyText((el?.value || "").trim());
    });
  });

  document.getElementById("m4_add_item").addEventListener("click", () => {
    if (state.m4_items.length >= 50) {
      toast("模块4最多50条");
      return;
    }
    state.m4_items.push({
      active: true,
      type: "WTB",
      item_cn: "",
      item_en: "",
      price: ""
    });
    renderM4Items();
    updateOutputs();
    saveState();
  });

  document.getElementById("m6_add_history").addEventListener("click", () => {
    const count = sanitizeCount(state.m6_count).toString();
    const item = {
      epoch: safeEpoch(state.m6_epoch),
      code: (state.m6_code || "A1").toUpperCase(),
      mode: state.m6_mode === "人数" ? "人数" : "求拉",
      count,
      note: state.m6_note || ""
    };
    state.m6_history.unshift(item);
    state.m6_history = state.m6_history.slice(0, 100);
    renderM6History();
    updateOutputs();
    saveState();
  });

  document.getElementById("m7_add_item").addEventListener("click", () => {
    if (state.m7_items.length >= 100) {
      toast("模块7最多100条");
      return;
    }
    state.m7_items.push({
      active: true,
      title: "",
      text_cn: "",
      text_en: ""
    });
    renderM7Items();
    renderM7QuickButtons();
    saveState();
  });
}

function renderM4Items() {
  const container = document.getElementById("m4_items_container");
  container.innerHTML = "";
  if (!state.m4_items.length) {
    container.textContent = "暂无条目";
    return;
  }
  state.m4_items.forEach((item, idx) => {
    const card = document.createElement("div");
    card.className = "item-card";
    card.innerHTML = `
      <div class="inline-grid">
        <label><input type="checkbox" data-action="active"> 启用</label>
        <label>类型
          <select data-action="type">
            <option value="WTB">WTB</option>
            <option value="WTS">WTS</option>
          </select>
        </label>
      </div>
      <div class="grid-2">
        <label>中文名<input type="text" data-action="item_cn"></label>
        <label>英文名<input type="text" data-action="item_en"></label>
      </div>
      <label>价格<input type="text" data-action="price"></label>
      <div class="item-actions">
        <button type="button" class="danger" data-action="delete">删除</button>
      </div>
    `;
    bindM4Card(card, idx, item);
    container.appendChild(card);
  });
}

function bindM4Card(card, idx, item) {
  const binders = ["active", "type", "item_cn", "item_en", "price"];
  binders.forEach((name) => {
    const el = card.querySelector(`[data-action="${name}"]`);
    if (!el) return;
    if (el.type === "checkbox") el.checked = !!item[name];
    else el.value = item[name] || "";
    const evt = el.tagName === "SELECT" ? "change" : "input";
    el.addEventListener(evt, () => {
      state.m4_items[idx][name] = el.type === "checkbox" ? el.checked : el.value;
      updateOutputs();
      saveState();
    });
    if (el.type === "checkbox") {
      el.addEventListener("change", () => {
        state.m4_items[idx][name] = el.checked;
        updateOutputs();
        saveState();
      });
    }
  });
  card.querySelector('[data-action="delete"]').addEventListener("click", () => {
    state.m4_items.splice(idx, 1);
    renderM4Items();
    updateOutputs();
    saveState();
  });
}

function renderM6History() {
  const container = document.getElementById("m6_history_container");
  container.innerHTML = "";
  if (!state.m6_history.length) {
    container.textContent = "暂无历史记录";
    return;
  }
  state.m6_history.forEach((item, idx) => {
    const card = document.createElement("div");
    card.className = "item-card";
    const relicCn = buildRelicCn(item.epoch, item.code);
    card.innerHTML = `
      <div><strong>${escapeHtml(relicCn)}</strong></div>
      <label>备注<input type="text" data-action="note"></label>
      <div class="item-actions">
        <button type="button" data-action="apply">应用</button>
        <button type="button" data-action="copy">复制遗物名(中文)</button>
        <button type="button" class="danger" data-action="delete">删除</button>
      </div>
    `;
    const noteInput = card.querySelector('[data-action="note"]');
    noteInput.value = item.note || "";
    noteInput.addEventListener("input", () => {
      state.m6_history[idx].note = noteInput.value;
      saveState();
    });
    card.querySelector('[data-action="apply"]').addEventListener("click", () => {
      state.m6_epoch = safeEpoch(item.epoch);
      state.m6_code = (item.code || "A1").toUpperCase();
      state.m6_mode = item.mode === "人数" ? "人数" : "求拉";
      state.m6_count = sanitizeCount(item.count).toString();
      state.m6_note = item.note || "";
      syncStaticInputs();
      updateOutputs();
      saveState();
    });
    card.querySelector('[data-action="copy"]').addEventListener("click", async () => {
      await copyText(relicCn.trim());
    });
    card.querySelector('[data-action="delete"]').addEventListener("click", () => {
      state.m6_history.splice(idx, 1);
      renderM6History();
      saveState();
    });
    container.appendChild(card);
  });
}

function renderM7Items() {
  const container = document.getElementById("m7_items_container");
  container.innerHTML = "";
  if (!state.m7_items.length) {
    container.textContent = "暂无短语";
    return;
  }
  state.m7_items.forEach((item, idx) => {
    const card = document.createElement("div");
    card.className = "item-card";
    card.innerHTML = `
      <div class="inline-grid">
        <label><input type="checkbox" data-action="active"> 启用</label>
        <label>标题<input type="text" data-action="title"></label>
      </div>
      <div class="grid-2">
        <label>中文短语<input type="text" data-action="text_cn"></label>
        <label>英文短语<input type="text" data-action="text_en"></label>
      </div>
      <div class="item-actions">
        <button type="button" data-action="apply">应用</button>
        <button type="button" data-action="copy_cn">复制中文</button>
        <button type="button" data-action="copy_en">复制英文</button>
        <button type="button" class="danger" data-action="delete">删除</button>
      </div>
    `;
    bindM7Card(card, idx, item);
    container.appendChild(card);
  });
}

function renderM7QuickButtons() {
  const container = document.getElementById("m7_quick_buttons");
  container.innerHTML = "";
  state.m7_items
    .filter((it) => it.active)
    .forEach((it, idx) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.textContent = (it.title || "").trim() || `短语${idx + 1}`;
      btn.addEventListener("click", () => {
        state.m7_quick_cn = it.text_cn || "";
        state.m7_quick_en = it.text_en || "";
        updateOutputs();
        saveState();
      });
      container.appendChild(btn);
    });
  if (!container.children.length) container.textContent = "暂无已启用快捷短语";
}

function bindM7Card(card, idx, item) {
  ["active", "title", "text_cn", "text_en"].forEach((name) => {
    const el = card.querySelector(`[data-action="${name}"]`);
    if (!el) return;
    if (el.type === "checkbox") el.checked = !!item[name];
    else el.value = item[name] || "";
    const evt = el.type === "checkbox" ? "change" : "input";
    el.addEventListener(evt, () => {
      state.m7_items[idx][name] = el.type === "checkbox" ? el.checked : el.value;
      renderM7QuickButtons();
      saveState();
    });
  });
  card.querySelector('[data-action="apply"]').addEventListener("click", () => {
    const row = state.m7_items[idx];
    state.m7_quick_cn = row.text_cn || "";
    state.m7_quick_en = row.text_en || "";
    updateOutputs();
    saveState();
  });
  card.querySelector('[data-action="copy_cn"]').addEventListener("click", async () => {
    await copyText((state.m7_items[idx].text_cn || "").trim());
  });
  card.querySelector('[data-action="copy_en"]').addEventListener("click", async () => {
    await copyText((state.m7_items[idx].text_en || "").trim());
  });
  card.querySelector('[data-action="delete"]').addEventListener("click", () => {
    state.m7_items.splice(idx, 1);
    renderM7Items();
    renderM7QuickButtons();
    saveState();
  });
}

function updateOutputs() {
  const { cn: m1cn, en: m1en } = buildM1();
  const { cn: m2cn, en: m2en } = buildM2();
  const { cn: m3cn, en: m3en } = buildM3();
  const { cn: m4cn, en: m4en } = buildM4();
  const { cn: m5cn, en: m5en } = buildM5();
  const tradeCnParts = [m1cn, m2cn, m3cn, m4cn, m5cn].filter(Boolean);
  const tradeEnParts = [m1en, m2en, m3en, m4en, m5en].filter(Boolean);
  setValue("trade_cn_preview", tradeCnParts.join(","));
  setValue("trade_en_preview", tradeEnParts.join("| "));

  const m6 = buildM6();
  setValue("m6_cn_preview", m6.cn);
  setValue("m6_en_preview", m6.en);
  setValue("m7_quick_cn_preview", state.m7_quick_cn || "");
  setValue("m7_quick_en_preview", state.m7_quick_en || "");
  setValue("team_cn_preview", [m6.cn, state.m7_quick_cn].filter(Boolean).join("\n"));
  setValue("team_en_preview", [m6.en, state.m7_quick_en].filter(Boolean).join("\n"));
  setValue("thanks_preview", state.thanks_msg || "");

  const ratio = buildM1RatioText();
  document.getElementById("m1_ratio_group").textContent = `组模式比值: ${ratio.group}`;
  document.getElementById("m1_ratio_single").textContent = `个模式比值: ${ratio.single}`;
}

function buildM1() {
  if (!state.m1_active) return { cn: "", en: "" };
  const plat = state.m1_plat_token || ":platinum:";
  const prices = state.m1_mode === "single"
    ? [state.m1_s_bronze, state.m1_s_fsilver, state.m1_s_silver, state.m1_s_fgold, state.m1_s_gold]
    : [state.m1_g_bronze, state.m1_g_fsilver, state.m1_g_silver, state.m1_g_fgold, state.m1_g_gold];
  const [b, fs, s, fg, g] = prices.map((v) => v || "");
  return {
    cn: `收铜/假银/银/假金/金垃圾 ${b}${plat}/${fs}${plat}/${s}${plat}/${fg}${plat}/${g}${plat}可混`,
    en: `WTB prime junk 15:ducats:=${b}${plat} 25:ducats:=${fs}${plat} 45:ducats:=${s}${plat} 65:ducats:=${fg}${plat} 100:ducats:=${g}${plat} canmix`
  };
}

function buildM1RatioText() {
  const ducats = [15, 25, 45, 65, 100];
  const gPrices = [state.m1_g_bronze, state.m1_g_fsilver, state.m1_g_silver, state.m1_g_fgold, state.m1_g_gold];
  const sPrices = [state.m1_s_bronze, state.m1_s_fsilver, state.m1_s_silver, state.m1_s_fgold, state.m1_s_gold];
  return {
    group: ducats.map((d, i) => calcRatio(d, gPrices[i], true)).join(" / "),
    single: ducats.map((d, i) => calcRatio(d, sPrices[i], false)).join(" / ")
  };
}

function calcRatio(ducat, rawPrice, groupMode) {
  const p = Number(rawPrice);
  if (!Number.isFinite(p) || p <= 0) return "无效";
  const val = groupMode ? ducat / (p / 6) : ducat / p;
  return val.toFixed(2);
}

function buildM2() {
  if (!state.m2_active) return { cn: "", en: "" };
  const plat = state.m2_plat_token || ":platinum:";
  const radCn = state.m2_rad ? " 光辉+1p" : "";
  const radEn = state.m2_rad ? " Rad+1p ea" : "";
  return {
    cn: `收Lith/Meso/Neo/Axi遗物 ${state.m2_lith}/${state.m2_meso}/${state.m2_neo}/${state.m2_axi}${plat}${radCn}`,
    en: `WTB Lith/Meso/Neo/Axi Relics ${state.m2_lith}/${state.m2_meso}/${state.m2_neo}/${state.m2_axi}${plat}${radEn}`
  };
}

function buildM3() {
  if (!state.m3_active) return { cn: "", en: "" };
  const plat = state.m3_plat_token || ":platinum:";
  const radCn = state.m3_rad ? " 光辉+1p" : "";
  const radEn = state.m3_rad ? " Rad+1p ea" : "";
  return {
    cn: `收Aya 6个${state.m3_aya}${plat}${radCn}`,
    en: `WTB[Aya] 6 for ${state.m3_aya}${plat}${radEn}`
  };
}

function buildM4() {
  if (!state.m4_active) return { cn: "", en: "" };
  const plat = state.m4_plat_token || ":platinum:";
  const activeItems = state.m4_items.filter((it) => it.active);
  const cnWtb = [];
  const cnWts = [];
  const enWtb = [];
  const enWts = [];

  activeItems.forEach((it) => {
    const price = it.price || "";
    if (it.type === "WTS") {
      if ((it.item_cn || "").trim()) cnWts.push(`[${it.item_cn.trim()}] ${price}${plat}`.trim());
      if ((it.item_en || "").trim()) enWts.push(`[${it.item_en.trim()}] ${price}${plat}`.trim());
    } else {
      if ((it.item_cn || "").trim()) cnWtb.push(`[${it.item_cn.trim()}] ${price}${plat}`.trim());
      if ((it.item_en || "").trim()) enWtb.push(`[${it.item_en.trim()}] ${price}${plat}`.trim());
    }
  });

  const cnParts = [];
  const enParts = [];
  if (cnWtb.length) cnParts.push(`收 ${cnWtb.join(" ")}`);
  if (cnWts.length) cnParts.push(`出 ${cnWts.join(" ")}`);
  if (enWtb.length) enParts.push(`WTB ${enWtb.join(" ")}`);
  if (enWts.length) enParts.push(`WTS ${enWts.join(" ")}`);
  return { cn: cnParts.join(" "), en: enParts.join(" ") };
}

function buildM5() {
  return {
    cn: (state.m5_cn || "").trim(),
    en: (state.m5_en || "").trim()
  };
}

function buildM6() {
  const epoch = safeEpoch(state.m6_epoch);
  const code = (state.m6_code || "A1").toUpperCase();
  const count = sanitizeCount(state.m6_count);
  state.m6_epoch = epoch;
  state.m6_code = code;
  if (String(state.m6_count) !== String(count)) {
    state.m6_count = String(count);
    const input = document.querySelector('[data-bind="m6_count"]');
    if (input) input.value = state.m6_count;
  }
  const relicCn = buildRelicCn(epoch, code);
  const relicEn = `[${epoch} ${code} Relic]`;
  if (state.m6_mode === "人数") {
    const wait = 4 - count;
    return {
      cn: `${relicCn} 光辉 ${count}/4，差${wait}`,
      en: `H ${relicEn} Rad ${count}/4`
    };
  }
  return {
    cn: `${relicCn} 光辉求拉`,
    en: `H ${relicEn} Rad`
  };
}

function buildRelicCn(epoch, code) {
  return `[${EPOCH_CN[epoch]} ${code} 遗物]`;
}

function safeEpoch(raw) {
  return ["Lith", "Meso", "Neo", "Axi"].includes(raw) ? raw : "Lith";
}

function sanitizeCount(raw) {
  const n = Number(raw);
  if (!Number.isFinite(n)) return 2;
  if (n < 1) return 1;
  if (n > 4) return 4;
  return Math.round(n);
}

function setValue(id, value) {
  const el = document.getElementById(id);
  if (!el) return;
  el.value = value || "";
  autosizeTextarea(el);
}

function autosizeTextarea(el) {
  if (!(el instanceof HTMLTextAreaElement)) return;
  const lines = (el.value.match(/\n/g)?.length || 0) + 1;
  el.rows = Math.max(2, Math.min(10, lines));
}

async function copyText(text) {
  if (!text) {
    toast("没有可复制内容");
    return;
  }
  try {
    await navigator.clipboard.writeText(text);
    toast("已复制");
  } catch (_) {
    try {
      const ta = document.createElement("textarea");
      ta.value = text;
      ta.style.position = "fixed";
      ta.style.left = "-9999px";
      document.body.appendChild(ta);
      ta.select();
      const ok = document.execCommand("copy");
      ta.remove();
      if (!ok) throw new Error("copy failed");
      toast("已复制");
    } catch (__){
      toast("复制失败，请手动复制");
    }
  }
}

let toastTimer = null;
function toast(msg) {
  const el = document.getElementById("toast");
  el.textContent = msg;
  el.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove("show"), 1800);
}

function escapeHtml(raw) {
  return String(raw)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}
