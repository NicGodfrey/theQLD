(function (global) {
  const Meridian = {
    save(key, value) {
      localStorage.setItem(`meridian:${key}`, JSON.stringify(value));
    },
    load(key, fallback) {
      try {
        const raw = localStorage.getItem(`meridian:${key}`);
        return raw ? JSON.parse(raw) : fallback;
      } catch {
        return fallback;
      }
    },
    download(filename, text, type = "text/plain") {
      const blob = new Blob([text], { type });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(url);
    },
    uid(prefix = "id") {
      return `${prefix}_${Math.random().toString(36).slice(2, 9)}`;
    },
    seed(text) {
      let h = 2166136261;
      const s = String(text || "");
      for (let i = 0; i < s.length; i++) {
        h ^= s.charCodeAt(i);
        h = Math.imul(h, 16777619);
      }
      return () => {
        h += 0x6d2b79f5;
        let t = Math.imul(h ^ (h >>> 15), 1 | h);
        t ^= t + Math.imul(t ^ (t >>> 7), 61 | t);
        return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
      };
    },
    fill(template, vars) {
      return String(template || "").replace(/\{\{(\w+)\}\}/g, (_, k) =>
        vars[k] != null ? String(vars[k]) : ""
      );
    },
    toast(msg) {
      let el = document.getElementById("meridian-toast");
      if (!el) {
        el = document.createElement("div");
        el.id = "meridian-toast";
        el.style.cssText =
          "position:fixed;bottom:1.2rem;right:1.2rem;z-index:99;background:#0B1F2A;color:#F3F0E7;padding:.8rem 1rem;border-radius:999px;font-weight:600;opacity:0;transition:opacity .2s ease";
        document.body.appendChild(el);
      }
      el.textContent = msg;
      el.style.opacity = "1";
      clearTimeout(el._t);
      el._t = setTimeout(() => (el.style.opacity = "0"), 1800);
    },
  };
  global.Meridian = Meridian;
})(window);
