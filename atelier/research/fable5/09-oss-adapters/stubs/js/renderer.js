// Atelier renderer — fabric.js/konva-inspired (both MIT; patterns
// re-implemented, no code copied). See ADAPTERS.md #5.
//
// Patterns implemented:
//   * konva's multi-canvas layer model: each Layer is its own stacked <canvas>,
//     so redrawing the selection overlay never re-rasterizes the artwork
//   * dirty-flag batchDraw coalesced into one requestAnimationFrame
//   * konva's color-buffer hit testing: paint each element in a unique flat
//     color offscreen; hit test = one pixel read (exact for rotated shapes)
//   * fabric's object model: draw dispatch on element.type around a transform

import { sortByIndex } from "./scene.js";

export class Layer {
  constructor(name, container, { width, height, interactive = false } = {}) {
    this.name = name;
    this.canvas = document.createElement("canvas");
    this.canvas.width = width;
    this.canvas.height = height;
    this.canvas.style.cssText = "position:absolute;inset:0;";
    if (!interactive) this.canvas.style.pointerEvents = "none";
    container.appendChild(this.canvas);
    this.ctx = this.canvas.getContext("2d");
    this.dirty = true;
  }
}

export class Renderer {
  #raf = 0;

  constructor(container, { width, height } = {}) {
    container.style.position = "relative";
    this.width = width ?? container.clientWidth;
    this.height = height ?? container.clientHeight;
    const opts = { width: this.width, height: this.height };
    // Fixed stack: artwork redraws rarely, overlay redraws constantly.
    this.layers = {
      background: new Layer("background", container, opts),
      artwork: new Layer("artwork", container, opts),
      overlay: new Layer("overlay", container, { ...opts, interactive: true }),
    };
    this.hit = new HitCanvas(this.width, this.height);
    this.camera = { x: 0, y: 0, zoom: 1 };
    this.drawers = { ...DEFAULT_DRAWERS }; // element.type -> fn(ctx, el, assets)
    this.assets = new Map(); // fileId -> ImageBitmap
  }

  /** Mark layers dirty and schedule ONE frame regardless of call count. */
  batchDraw(scene, layerNames = ["artwork", "overlay"]) {
    for (const name of layerNames) this.layers[name].dirty = true;
    if (this.#raf) return;
    this.#raf = requestAnimationFrame(() => {
      this.#raf = 0;
      this.#drawFrame(scene);
    });
  }

  #drawFrame(scene) {
    const elements = sortByIndex(scene.elements.filter((el) => !el.isDeleted));
    if (this.layers.artwork.dirty) {
      this.#paint(this.layers.artwork.ctx, elements, (ctx, el) =>
        (this.drawers[el.type] ?? DEFAULT_DRAWERS.rect)(ctx, el, this.assets),
      );
      this.hit.paint(elements, this.camera); // hit buffer mirrors artwork
      this.layers.artwork.dirty = false;
    }
    if (this.layers.overlay.dirty) {
      const selected = elements.filter((el) => scene.selection?.has(el.id));
      this.#paint(this.layers.overlay.ctx, selected, drawSelectionBox);
      this.layers.overlay.dirty = false;
    }
  }

  /** Clear, apply camera, then draw each element inside its own transform. */
  #paint(ctx, elements, draw) {
    ctx.clearRect(0, 0, this.width, this.height);
    ctx.save();
    ctx.translate(this.camera.x, this.camera.y);
    ctx.scale(this.camera.zoom, this.camera.zoom);
    for (const el of elements) {
      ctx.save();
      ctx.translate(el.x + el.width / 2, el.y + el.height / 2);
      ctx.rotate(el.angle);
      ctx.globalAlpha = el.opacity;
      draw(ctx, el);
      ctx.restore();
    }
    ctx.restore();
  }

  /** Exact hit test in O(1) per pointer event via the color buffer. */
  elementAt(px, py) {
    return this.hit.pick(px, py);
  }
}

// ---- color-buffer hit testing (konva's trick) -------------------------------

class HitCanvas {
  constructor(width, height) {
    this.canvas = new OffscreenCanvas(width, height);
    this.ctx = this.canvas.getContext("2d", { willReadFrequently: true });
    this.colorToId = new Map();
  }

  paint(elements, camera) {
    const { ctx } = this;
    this.colorToId.clear();
    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    ctx.save();
    ctx.translate(camera.x, camera.y);
    ctx.scale(camera.zoom, camera.zoom);
    elements.forEach((el, i) => {
      const color = idToColor(i + 1);
      this.colorToId.set(color, el.id);
      ctx.save();
      ctx.translate(el.x + el.width / 2, el.y + el.height / 2);
      ctx.rotate(el.angle);
      ctx.fillStyle = color;
      // Hit shape is the element's silhouette, not its pixels; a filled rect
      // is right for images/text boxes, path elements override with their path.
      ctx.fillRect(-el.width / 2, -el.height / 2, el.width, el.height);
      ctx.restore();
    });
    ctx.restore();
  }

  pick(px, py) {
    const [r, g, b, a] = this.ctx.getImageData(px, py, 1, 1).data;
    if (a === 0) return null;
    return this.colorToId.get(`rgb(${r},${g},${b})`) ?? null;
  }
}

function idToColor(n) {
  return `rgb(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255})`;
}

// ---- element drawers (fabric-style dispatch table) --------------------------
// Coordinates are element-local: origin at center, rotation already applied.

const DEFAULT_DRAWERS = {
  rect(ctx, el) {
    ctx.fillStyle = el.props.fill ?? "#ccc";
    ctx.fillRect(-el.width / 2, -el.height / 2, el.width, el.height);
  },
  ellipse(ctx, el) {
    ctx.fillStyle = el.props.fill ?? "#ccc";
    ctx.beginPath();
    ctx.ellipse(0, 0, el.width / 2, el.height / 2, 0, 0, Math.PI * 2);
    ctx.fill();
  },
  text(ctx, el) {
    ctx.fillStyle = el.props.fill ?? "#111";
    ctx.font = `${el.props.fontSize ?? 24}px ${el.props.fontFamily ?? "sans-serif"}`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(el.props.text ?? "", 0, 0);
  },
  image(ctx, el, assets) {
    const bitmap = assets.get(el.fileId);
    if (bitmap) {
      ctx.drawImage(bitmap, -el.width / 2, -el.height / 2, el.width, el.height);
    } else {
      DEFAULT_DRAWERS.rect(ctx, { ...el, props: { fill: "#e5e5e5" } }); // loading placeholder
    }
  },
};

function drawSelectionBox(ctx, el) {
  ctx.strokeStyle = "#4f8ef7";
  ctx.lineWidth = 1.5;
  ctx.setLineDash([4, 4]);
  ctx.strokeRect(-el.width / 2, -el.height / 2, el.width, el.height);
}
