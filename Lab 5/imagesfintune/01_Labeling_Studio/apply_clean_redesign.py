import re
import os

HTML_PATH = r"g:/Desktop/2026-8-7/image_processing/01_Labeling_Studio/index.html"

with open(HTML_PATH, "r", encoding="utf-8") as f:
    full_code = f.read()

# Extract JavaScript from <script> tag onwards
script_idx = full_code.find("<script>")
if script_idx == -1:
    raise ValueError("Could not find <script> in index.html!")

script_part = full_code[script_idx:]

new_head_and_body = """<!DOCTYPE html>
<html lang="ar" dir="rtl" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>استوديو التوسيم الأثري المتطور | Epigraphy AI Studio</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800;900&family=Noto+Sans+Nabataean&family=Outfit:wght@500;600;700&family=JetBrains+Mono:wght@500;700&display=swap">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
  
  <style>
    @font-face {
      font-family: 'NabataeanLocal';
      src: url('SyntheticDatasetGenerator/fonts/nabataean.ttf') format('truetype');
      font-display: swap;
    }

    :root {
      --bg-main: #090d15;
      --bg-panel: #0f1523;
      --bg-card: #151e2e;
      --bg-card-hover: #1c273c;
      --bg-input: #0b101a;
      
      --border-subtle: rgba(255, 255, 255, 0.06);
      --border-card: #1f2a3e;
      --border-active: #f77f00;

      --accent-orange: #f77f00;
      --accent-cyan: #00f5d4;
      --accent-amber: #ffbe0b;
      --accent-purple: #9d4edd;
      --accent-blue: #3a86ff;
      --accent-danger: #ef476f;
      --accent-success: #06d6a0;

      --text-primary: #f1f5f9;
      --text-secondary: #94a3b8;
      --text-muted: #5e6f88;

      --font-nabataean: 'NabataeanLocal', 'Noto Sans Nabataean', 'Segoe UI Historic', system-ui, sans-serif;
      --font-ui: 'Cairo', system-ui, sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
    }

    *, *::before, *::after {
      box-sizing: border-box;
      margin: 0; padding: 0;
      user-select: none;
    }

    html, body {
      height: 100vh !important;
      max-height: 100vh !important;
      width: 100vw !important;
      max-width: 100vw !important;
      overflow: hidden !important;
      position: fixed !important;
      inset: 0 !important;
      font-family: var(--font-ui);
      background-color: var(--bg-main);
      color: var(--text-primary);
      display: flex !important;
      flex-direction: column !important;
    }

    * {
      scrollbar-width: none !important;
      -ms-overflow-style: none !important;
    }
    *::-webkit-scrollbar {
      display: none !important;
      width: 0 !important;
      height: 0 !important;
    }

    /* 1. TOP HEADER (42px) */
    .app-header {
      flex: 0 0 42px;
      height: 42px;
      min-height: 42px;
      background: #0e1422;
      border-bottom: 1px solid var(--border-subtle);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 0.6rem;
      z-index: 100;
      gap: 0.5rem;
    }

    .brand-section {
      display: flex;
      align-items: center;
      gap: 0.45rem;
      flex-shrink: 0;
    }
    .brand-icon {
      width: 28px;
      height: 28px;
      border-radius: 6px;
      background: linear-gradient(135deg, #f77f00, #d62828);
      color: #fff;
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: var(--font-nabataean);
      font-size: 1.15rem;
      box-shadow: 0 0 10px rgba(247, 127, 0, 0.35);
    }
    .brand-text {
      display: flex;
      align-items: center;
      gap: 6px;
      line-height: 1.1;
    }
    .brand-title {
      font-size: 0.82rem;
      font-weight: 800;
      color: #fff;
      white-space: nowrap;
    }
    .brand-model-badge {
      font-size: 0.60rem;
      color: var(--accent-cyan);
      font-family: var(--font-mono);
      display: flex;
      align-items: center;
      gap: 3px;
      background: rgba(0, 245, 212, 0.08);
      padding: 1px 5px;
      border-radius: 4px;
      border: 1px solid rgba(0, 245, 212, 0.2);
    }
    .status-dot-pulse {
      width: 4px;
      height: 4px;
      border-radius: 50%;
      background: var(--accent-cyan);
      box-shadow: 0 0 4px var(--accent-cyan);
    }

    /* Center Image Navigator */
    .image-navigator {
      display: flex;
      align-items: center;
      gap: 0.3rem;
      background: rgba(10, 15, 25, 0.8);
      border: 1px solid var(--border-card);
      border-radius: 6px;
      padding: 2px 4px;
      flex-shrink: 0;
    }
    .nav-btn {
      width: 24px;
      height: 24px;
      border-radius: 4px;
      background: #172031;
      border: 1px solid var(--border-card);
      color: var(--text-primary);
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      font-size: 0.65rem;
      transition: all 0.12s ease;
    }
    .nav-btn:hover {
      background: var(--accent-orange);
      color: #fff;
      border-color: var(--accent-orange);
    }
    .image-status-card {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 1px 8px;
      border-radius: 4px;
      background: #101623;
      border: 1px solid transparent;
    }
    .image-status-card.is-labeled {
      border-color: rgba(0, 245, 212, 0.35) !important;
      background: rgba(0, 245, 212, 0.05) !important;
    }
    .image-status-card.is-unlabeled {
      border-color: rgba(239, 71, 111, 0.3) !important;
      background: rgba(239, 71, 111, 0.05) !important;
    }
    .status-img-name {
      font-size: 0.72rem;
      font-weight: 700;
      color: #fff;
      max-width: 170px;
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
      font-family: var(--font-mono);
    }
    .status-indicator-badge {
      display: flex;
      align-items: center;
      font-size: 0.62rem;
      font-weight: 800;
      padding: 1px 5px;
      border-radius: 3px;
    }
    .status-indicator-badge.is-labeled {
      background: rgba(0, 245, 212, 0.18);
      color: #00f5d4;
    }
    .status-indicator-badge.is-unlabeled {
      background: rgba(239, 71, 111, 0.18);
      color: #ef476f;
    }
    .counter-badge {
      font-family: var(--font-mono);
      font-size: 0.67rem;
      color: var(--text-muted);
      min-width: 38px;
      text-align: center;
    }

    /* Header Actions (Left) */
    .header-actions {
      display: flex;
      align-items: center;
      gap: 0.35rem;
      flex-shrink: 0;
    }
    .labels-dir-box {
      display: flex;
      align-items: center;
      gap: 3px;
      background: #080c14;
      border: 1px solid var(--border-card);
      border-radius: 5px;
      padding: 1px 4px;
    }
    .labels-dir-box input {
      width: 65px;
      background: transparent;
      border: none;
      color: var(--accent-cyan);
      font-size: 0.65rem;
      font-family: var(--font-mono);
      outline: none;
      cursor: pointer;
      text-overflow: ellipsis;
    }
    .btn-browse {
      background: #141c2b;
      border: 1px solid var(--border-card);
      color: var(--text-secondary);
      font-size: 0.62rem;
      padding: 1px 5px;
      border-radius: 3px;
      cursor: pointer;
    }
    .btn-browse:hover {
      color: #fff;
      background: #1f2b42;
    }

    .btn {
      display: inline-flex;
      align-items: center;
      gap: 0.25rem;
      padding: 0.25rem 0.55rem;
      border-radius: 5px;
      font-size: 0.68rem;
      font-weight: 700;
      cursor: pointer;
      border: 1px solid var(--border-card);
      background: var(--bg-card);
      color: var(--text-primary);
      transition: all 0.12s ease;
      font-family: inherit;
      white-space: nowrap;
    }
    .btn:hover {
      background: var(--bg-card-hover);
      border-color: var(--accent-orange);
      color: var(--accent-orange);
    }
    .btn-primary {
      background: linear-gradient(135deg, #00f5d4, #00b4d8);
      color: #05070a;
      border: none;
      box-shadow: 0 0 8px rgba(0, 245, 212, 0.2);
    }
    .btn-primary:hover {
      background: linear-gradient(135deg, #2bf8dd, #33c6e6);
      color: #000;
    }
    .btn-ai-magic {
      background: linear-gradient(135deg, #7b2cbf, #9d4edd);
      color: #fff;
      border: 1px solid rgba(199, 125, 255, 0.3);
      box-shadow: 0 0 10px rgba(157, 78, 221, 0.3);
    }
    .btn-ai-magic:hover {
      background: linear-gradient(135deg, #9d4edd, #c77dff);
      color: #fff;
    }

    .ui-scale-group {
      display: inline-flex;
      align-items: center;
      background: #080c14;
      border: 1px solid var(--border-card);
      border-radius: 5px;
      padding: 1px;
      gap: 1px;
    }
    .scale-btn {
      background: transparent;
      border: none;
      color: var(--text-muted);
      font-size: 0.60rem;
      font-weight: 700;
      font-family: var(--font-mono);
      padding: 1px 5px;
      border-radius: 3px;
      cursor: pointer;
      transition: all 0.12s ease;
    }
    .scale-btn:hover {
      color: #fff;
      background: #162030;
    }
    .scale-btn.active {
      background: var(--accent-orange);
      color: #fff;
    }

    /* 2. SUB-HEADER WORKFLOW TOOLBAR (38px) */
    .workflow-bar {
      flex: 0 0 38px;
      height: 38px;
      min-height: 38px;
      background: #0b101c;
      border-bottom: 1px solid var(--border-subtle);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 0.6rem;
      z-index: 95;
      gap: 0.4rem;
    }
    .workflow-group {
      display: flex;
      align-items: center;
      gap: 0.25rem;
      flex-shrink: 0;
    }
    .workflow-sep {
      width: 1px;
      height: 18px;
      background: rgba(255, 255, 255, 0.08);
      margin: 0 0.15rem;
    }
    .ai-conf-box {
      display: flex;
      align-items: center;
      gap: 4px;
      background: #101624;
      border: 1px solid var(--border-card);
      border-radius: 5px;
      padding: 1px 6px;
      font-size: 0.65rem;
    }
    .ai-conf-box input[type="range"] {
      width: 45px;
      height: 3px;
      accent-color: #9d4edd;
      cursor: pointer;
    }

    .tool-btn {
      display: inline-flex;
      align-items: center;
      gap: 0.2rem;
      padding: 0.20rem 0.45rem;
      border-radius: 4px;
      font-size: 0.67rem;
      font-weight: 700;
      cursor: pointer;
      border: 1px solid var(--border-card);
      background: #131a2a;
      color: var(--text-secondary);
      transition: all 0.12s ease;
      font-family: inherit;
    }
    .tool-btn:hover {
      background: #1b263c;
      color: #fff;
      border-color: var(--accent-orange);
    }
    .tool-btn.active {
      background: var(--accent-orange);
      color: #fff;
      border-color: var(--accent-orange);
      box-shadow: 0 0 8px rgba(247, 127, 0, 0.35);
    }
    .tool-btn.btn-danger-hover:hover {
      background: var(--accent-danger);
      border-color: var(--accent-danger);
      color: #fff;
    }
    .zoom-badge {
      font-family: var(--font-mono);
      font-size: 0.67rem;
      color: var(--accent-cyan);
      min-width: 36px;
      text-align: center;
      background: #0d131f;
      padding: 1px 4px;
      border-radius: 3px;
      border: 1px solid var(--border-card);
    }

    /* 3. MAIN WORKSPACE LAYOUT (Fills 100% remaining vertical height, ZERO GAPS!) */
    .studio-layout {
      flex: 1 1 0 !important;
      min-height: 0 !important;
      height: auto !important;
      display: grid;
      grid-template-columns: 260px 1fr 280px;
      position: relative;
      overflow: hidden;
    }

    /* RIGHT: Nabataean Character Palette */
    .palette-panel {
      background: var(--bg-panel);
      border-left: 1px solid var(--border-subtle);
      display: flex;
      flex-direction: column;
      height: 100%;
      padding: 0.5rem;
      gap: 0.4rem;
      overflow: hidden;
    }
    .palette-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding-bottom: 0.25rem;
      border-bottom: 1px solid var(--border-subtle);
      gap: 4px;
    }
    .palette-title {
      font-size: 0.78rem;
      font-weight: 800;
      color: var(--accent-orange);
      white-space: nowrap;
    }
    .active-char-chip {
      font-size: 0.65rem;
      background: rgba(247, 127, 0, 0.12);
      border: 1px solid var(--accent-orange);
      color: var(--accent-orange);
      padding: 1px 6px;
      border-radius: 4px;
      font-weight: 700;
      font-family: var(--font-nabataean);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 140px;
    }
    .palette-search-box input {
      width: 100%;
      background: #080c14;
      border: 1px solid var(--border-card);
      border-radius: 5px;
      color: #fff;
      padding: 4px 6px;
      font-size: 0.68rem;
      font-family: inherit;
      outline: none;
      transition: border-color 0.15s;
    }
    .palette-search-box input:focus {
      border-color: var(--accent-orange);
    }

    /* Character Grid */
    .character-grid {
      flex: 1;
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      grid-template-rows: repeat(10, 1fr);
      gap: 3px;
      height: 100%;
      overflow: hidden;
    }
    .char-card {
      background: #121826;
      border: 1px solid #1a2436;
      border-radius: 5px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      position: relative;
      cursor: pointer;
      transition: all 0.12s ease;
      padding: 1px;
      min-height: 0;
    }
    .char-card:hover {
      background: #1a2336;
      border-color: var(--accent-orange);
      transform: scale(1.02);
      z-index: 5;
    }
    .char-card.active {
      background: #231a12;
      border-color: var(--accent-orange) !important;
      box-shadow: 0 0 8px rgba(247, 127, 0, 0.4);
      z-index: 6;
    }
    .char-card-glyph {
      font-family: var(--font-nabataean);
      font-size: 1.35rem;
      color: #fff;
      line-height: 1;
      transition: all 0.12s ease;
    }
    .char-card.active .char-card-glyph {
      color: var(--accent-orange);
      text-shadow: 0 0 8px rgba(247, 127, 0, 0.6);
    }
    .char-card-id {
      position: absolute;
      top: 1px;
      left: 2px;
      font-size: 0.50rem;
      font-family: var(--font-mono);
      color: var(--text-muted);
    }
    .char-card-count {
      position: absolute;
      bottom: 1px;
      right: 2px;
      font-size: 0.52rem;
      font-family: var(--font-mono);
      font-weight: bold;
      color: var(--text-muted);
    }
    .char-card.has-count .char-card-count {
      color: var(--accent-cyan);
    }

    /* CENTER: Unobstructed Canvas Workspace */
    .canvas-container {
      flex: 1;
      position: relative;
      background: #06090e;
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    #mainCanvas {
      width: 100%;
      height: 100%;
      display: block;
      cursor: crosshair;
    }

    /* LEFT: Tools Panel */
    .tools-panel {
      background: var(--bg-panel);
      border-right: 1px solid var(--border-subtle);
      display: flex;
      flex-direction: column;
      height: 100%;
      overflow: hidden !important;
      padding: 0.5rem;
      gap: 0.4rem;
    }
    .panel-tabs {
      display: flex;
      gap: 2px;
      background: #080c14;
      border: 1px solid var(--border-card);
      border-radius: 6px;
      padding: 2px;
      flex-shrink: 0;
    }
    .panel-tab-btn {
      flex: 1;
      background: transparent;
      border: none;
      color: var(--text-secondary);
      font-size: 0.66rem;
      font-weight: 700;
      padding: 4px 2px;
      border-radius: 4px;
      cursor: pointer;
      transition: all 0.12s ease;
      white-space: nowrap;
      text-align: center;
      font-family: inherit;
    }
    .panel-tab-btn:hover {
      color: #fff;
      background: #141c2b;
    }
    .panel-tab-btn.active {
      background: var(--accent-orange);
      color: #fff;
      box-shadow: 0 0 8px rgba(247, 127, 0, 0.3);
    }
    .tools-tab-content {
      display: flex;
      flex-direction: column;
      gap: 0.4rem;
      flex: 1;
      overflow-y: auto;
      padding-right: 2px;
    }

    .panel-card {
      background: var(--bg-card);
      border: 1px solid var(--border-card);
      border-radius: 6px;
      padding: 0.5rem;
      display: flex;
      flex-direction: column;
      gap: 0.35rem;
    }
    .card-title {
      font-size: 0.72rem;
      font-weight: 700;
      color: var(--accent-cyan);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .chip-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 3px;
    }
    .chip-btn {
      background: #101624;
      border: 1px solid #1a2438;
      color: var(--text-secondary);
      border-radius: 4px;
      padding: 4px 4px;
      font-size: 0.65rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.12s ease;
      font-family: inherit;
      text-align: center;
    }
    .chip-btn:hover {
      background: #182235;
      border-color: var(--accent-cyan);
      color: #fff;
    }

    .ctrl-group {
      display: flex;
      flex-direction: column;
      gap: 0.15rem;
    }
    .ctrl-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.68rem;
      color: var(--text-secondary);
    }
    .ctrl-val {
      font-family: var(--font-mono);
      color: var(--accent-orange);
      font-size: 0.68rem;
    }
    input[type="range"] {
      -webkit-appearance: none;
      appearance: none;
      width: 100%;
      height: 4px;
      border-radius: 4px;
      background: rgba(255, 255, 255, 0.12);
      outline: none;
    }
    input[type="range"]::-webkit-slider-thumb {
      -webkit-appearance: none;
      appearance: none;
      width: 11px;
      height: 11px;
      border-radius: 50%;
      background: var(--accent-orange);
      cursor: pointer;
      box-shadow: 0 0 5px rgba(247, 127, 0, 0.6);
    }
    .select-input {
      width: 100%;
      background: #090e17;
      border: 1px solid var(--border-card);
      border-radius: 4px;
      color: #fff;
      padding: 3px 6px;
      font-size: 0.67rem;
      font-family: inherit;
      outline: none;
    }

    /* 4. BOTTOM THUMBNAIL GALLERY (46px) */
    .bottom-gallery {
      flex: 0 0 46px;
      height: 46px;
      min-height: 46px;
      background: #080c14;
      border-top: 1px solid var(--border-subtle);
      display: flex;
      align-items: center;
      padding: 0 0.6rem;
      gap: 0.4rem;
      overflow-x: auto;
      overflow-y: hidden;
    }
    .thumb-card {
      flex-shrink: 0;
      width: 52px;
      height: 32px;
      border-radius: 4px;
      border: 2px solid var(--border-card);
      overflow: hidden;
      position: relative;
      cursor: pointer;
      background: #000;
      transition: all 0.12s ease;
    }
    .thumb-card:hover {
      transform: scale(1.04);
      border-color: var(--accent-cyan);
    }
    .thumb-card.active {
      border-color: var(--accent-orange) !important;
      box-shadow: 0 0 8px rgba(247, 127, 0, 0.5);
    }
    .thumb-badge {
      position: absolute;
      bottom: 1px;
      right: 1px;
      font-size: 0.50rem;
      font-family: var(--font-mono);
      font-weight: bold;
      padding: 0 2px;
      border-radius: 2px;
      display: flex;
      align-items: center;
    }
    .thumb-badge.labeled {
      background: rgba(0, 245, 212, 0.9);
      color: #05070a;
    }
    .thumb-badge.unlabeled {
      background: rgba(20, 28, 42, 0.85);
      color: #8fa3c0;
    }
    .thumb-add {
      flex-shrink: 0;
      width: 32px;
      height: 32px;
      border-radius: 4px;
      border: 1px dashed var(--border-card);
      background: #111826;
      color: var(--text-secondary);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1rem;
      cursor: pointer;
      transition: all 0.12s;
    }
    .thumb-add:hover {
      border-color: var(--accent-orange);
      color: var(--accent-orange);
    }

    /* Modals & D-Pad */
    .modal-backdrop {
      position: fixed; inset: 0;
      background: rgba(0, 0, 0, 0.85);
      backdrop-filter: blur(8px);
      display: flex; align-items: center; justify-content: center;
      z-index: 1000; opacity: 0; pointer-events: none; transition: opacity 0.2s;
    }
    .modal-backdrop.show { opacity: 1; pointer-events: auto; }
    .modal-box {
      background: #101624; border: 1px solid var(--border-card);
      border-radius: 10px; width: 90%; max-width: 520px;
      padding: 1rem; display: flex; flex-direction: column; gap: 0.8rem;
    }
    .modal-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-subtle); padding-bottom: 0.4rem; }
    .modal-opt {
      background: #151e2e; border: 1px solid var(--border-card);
      border-radius: 6px; padding: 0.7rem; display: flex;
      align-items: center; justify-content: space-between; cursor: pointer;
    }
    .modal-opt:hover { border-color: var(--accent-orange); }

    .dpad-wrapper {
      display: flex; flex-direction: column; align-items: center; gap: 4px; padding: 4px;
      background: #080c14; border: 1px solid #182234; border-radius: 6px;
    }
    .dpad-step-bar {
      width: 100%; display: flex; align-items: center; justify-content: space-between;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05); padding-bottom: 3px;
    }
    .dpad-steps { display: flex; gap: 2px; }
    .step-btn {
      background: #121826; border: 1px solid #1f2b3e; color: var(--text-secondary);
      border-radius: 3px; font-size: 0.58rem; padding: 1px 4px; cursor: pointer;
    }
    .step-btn.active { background: var(--accent-orange); color: #fff; border-color: var(--accent-orange); }
    .dpad-cross { display: flex; flex-direction: column; align-items: center; gap: 2px; }
    .dpad-middle-row { display: flex; align-items: center; gap: 2px; }
    .dpad-arm { display: flex; flex-direction: column; align-items: center; gap: 2px; }
    .dpad-btn-pair { display: flex; gap: 2px; }
    .dpad-btn {
      background: #141c2c; border: 1px solid #222f44; color: #fff; border-radius: 3px;
      padding: 2px 5px; font-size: 0.62rem; cursor: pointer; font-weight: bold;
    }
    .dpad-btn:hover { border-color: var(--accent-cyan); color: var(--accent-cyan); }
    .dpad-center-hub {
      background: #0f1624; border: 1px solid #222f44; border-radius: 5px; padding: 3px 5px; text-align: center;
    }
    .hub-title { font-size: 0.65rem; font-family: var(--font-mono); color: var(--accent-orange); }
    .hub-actions { display: flex; gap: 2px; margin-top: 1px; }
    .hub-btn { background: #172235; border: 1px solid #222f44; color: #fff; font-size: 0.58rem; padding: 1px 3px; border-radius: 2px; cursor: pointer; }
    
    .toast-container {
      position: fixed; bottom: 55px; left: 50%; transform: translateX(-50%);
      display: flex; flex-direction: column; gap: 6px; z-index: 9999; pointer-events: none;
    }
    .toast {
      background: #151e2e; border: 1px solid var(--border-card); color: #fff;
      padding: 6px 14px; border-radius: 6px; font-size: 0.74rem; font-weight: 700;
      box-shadow: 0 6px 18px rgba(0,0,0,0.5); pointer-events: auto; animation: toastIn 0.2s ease;
    }
    @keyframes toastIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
  </style>
</head>
<body>

  <!-- LEVEL 1: APPLICATION HEADER -->
  <header class="app-header">
    <!-- Brand -->
    <div class="brand-section">
      <div class="brand-icon">𐢀</div>
      <div class="brand-text">
        <span class="brand-title">النقوش النبطية والآرامية</span>
        <span class="brand-model-badge"><span class="status-dot-pulse"></span> YOLO (62c)</span>
      </div>
    </div>

    <!-- Center: Image Navigator -->
    <div class="image-navigator">
      <button class="nav-btn" id="btnPrevImg" title="الصورة السابقة (◀)">◀</button>
      <div class="image-status-card is-unlabeled" id="imgStatusCard" title="حالة الصورة الحالية">
        <span class="status-img-name" id="statusImgName">🖼️ لا توجد صورة</span>
        <span class="status-indicator-badge is-unlabeled" id="statusIndicatorBadge">
          <span id="statusIndicatorText">غير موسمة</span>
        </span>
      </div>
      <button class="nav-btn" id="btnNextImg" title="الصورة التالية (▶)">▶</button>
      <span class="counter-badge" id="imgCounter">0 / 0</span>
    </div>

    <!-- Left: Core Project Controls -->
    <div class="header-actions">
      <div class="labels-dir-box" title="حدد مجلد ملفات التوسيم (.txt)">
        <span style="font-size: 0.70rem;">📁</span>
        <input type="text" id="txtLabelsDirPath" placeholder="مجلد..." readonly onclick="document.getElementById('fileLabelsFolderInput').click()">
        <button class="btn-browse" onclick="document.getElementById('fileLabelsFolderInput').click()">استعراض</button>
      </div>
      <input type="file" id="fileLabelsFolderInput" webkitdirectory directory multiple style="display: none;">
      <input type="file" id="fileLabelsInput" accept=".txt" multiple style="display: none;">

      <button class="btn btn-primary" id="btnDirectSaveTxt" title="حفظ ملف الليبل والتوسيمات بتنسيق TXT (Ctrl+S)">
        <span>💾</span>
        <span>حفظ</span>
      </button>

      <button class="btn" id="btnOpenExport" title="خيارات التصدير">
        <span>📦</span>
        <span>تصدير</span>
      </button>

      <!-- UI Scale Controller -->
      <div class="ui-scale-group" title="ضبط حجم الواجهة">
        <button class="scale-btn" onclick="window.setUiZoom(1.0)">100%</button>
        <button class="scale-btn active" onclick="window.setUiZoom(0.85)">85%</button>
        <button class="scale-btn" onclick="window.setUiZoom(0.75)">75%</button>
      </div>
    </div>
  </header>

  <!-- LEVEL 2: DEDICATED WORKFLOW & TOOLS BAR -->
  <div class="workflow-bar">
    <!-- AI Auto-Detection -->
    <div class="workflow-group">
      <button class="btn btn-ai-magic" id="btnAiAutoDetect" title="فحص واكتشاف النص والحروف بالذكاء الاصطناعي">
        <span>✨</span>
        <span id="aiBtnText">كشف ذكي (AI)</span>
      </button>
      <div class="ai-conf-box" title="حساسية الذكاء الاصطناعي">
        <span style="color: #c77dff; font-weight: 800;">حساسية:</span>
        <input type="range" id="aiConfSlider" min="1" max="30" value="4" oninput="document.getElementById('aiConfVal').innerText = this.value + '%'">
        <span id="aiConfVal" style="font-family: var(--font-mono); color: #00f5d4; min-width: 20px; font-weight: 800;">4%</span>
      </div>
    </div>

    <div class="workflow-sep"></div>

    <!-- Canvas Editing Tools -->
    <div class="workflow-group">
      <button class="tool-btn" id="toolSelect" title="تحديد وتحريك (V)">👆</button>
      <button class="tool-btn active" id="toolRect" title="رسم صندوق YOLO (R)">🔲 صندوق</button>
      <button class="tool-btn" id="toolPan" title="سحب وتنقل (Space)">✋</button>
      <div class="workflow-sep"></div>
      <button class="tool-btn" id="btnUndo" title="تراجع (Ctrl+Z)">↩️</button>
      <button class="tool-btn" id="btnRedo" title="إعادة (Ctrl+Y)">↪️</button>
      <button class="tool-btn btn-danger-hover" id="btnDelete" title="حذف الصندوق المحدد (Delete)">🗑️</button>
      <div class="workflow-sep"></div>
      <button class="tool-btn" id="toggleSplitBtn" title="مقارنة قبل/بعد">⬌</button>
      <div class="workflow-sep"></div>
      <button class="tool-btn" id="btnZoomOut">🔍-</button>
      <span class="zoom-badge" id="zoomDisplay">100%</span>
      <button class="tool-btn" id="btnZoomIn">🔍+</button>
      <button class="tool-btn" id="btnFit" title="ملاءمة الشاشة">⛶</button>
    </div>

    <div class="workflow-sep"></div>

    <!-- Quick Import / Export Actions -->
    <div class="workflow-group">
      <button class="btn btn-sm" onclick="document.getElementById('fileImgInput').click()" title="رفع صور النقوش">
        <span>🖼️</span>
        <span>رفع</span>
      </button>
      <input type="file" id="fileImgInput" accept="image/*" multiple style="display: none;">

      <button class="btn btn-sm" id="btnExportCrops" title="قص وتصدير جميع الحروف المحددة">
        <span>✂️</span>
        <span>قص</span>
      </button>

      <button class="btn btn-sm" onclick="document.getElementById('fileClassesInput').click()" title="استيراد ملف حروف">
        <span>📂</span>
        <span>حروف</span>
      </button>
      <input type="file" id="fileClassesInput" accept=".txt,.json,.yaml,.csv" style="display: none;">
    </div>
  </div>

  <!-- LEVEL 3: STUDIO WORKSPACE -->
  <main class="studio-layout">

    <!-- RIGHT PANEL: Nabataean Alphabet Palette -->
    <aside class="palette-panel">
      <div class="palette-header">
        <span class="palette-title">الأبجدية النبطية</span>
        <span class="active-char-chip" id="activeCharLabel">𐢀 (#0) ألف</span>
      </div>

      <!-- Live Search Box -->
      <div class="palette-search-box">
        <input type="text" id="charSearchInput" placeholder="🔍 بحث عن حرف (ألف، باء، ميم...)" oninput="window.filterCharGrid(this.value)">
      </div>
      
      <!-- Character Grid -->
      <div class="character-grid" id="charGrid"></div>
    </aside>

    <!-- CENTER: 100% Clear Canvas Area -->
    <section class="canvas-container" id="canvasContainer">
      <canvas id="mainCanvas"></canvas>
    </section>

    <!-- LEFT: Image Enhancement & Box Shaper Panel -->
    <aside class="tools-panel">
      <!-- Modern Pill Tabs -->
      <div class="panel-tabs">
        <button class="panel-tab-btn active" id="tabBtnFilters" onclick="window.switchToolsTab('tab_filters')">🎨 الحفر</button>
        <button class="panel-tab-btn" id="tabBtnGeom" onclick="window.switchToolsTab('tab_geom')">☀️ الإضاءة</button>
        <button class="panel-tab-btn" id="tabBtnBoxes" onclick="window.switchToolsTab('tab_boxes')">📐 التوسيم</button>
      </div>

      <!-- Tab 1: Rock Enhancement & Presets -->
      <div class="tools-tab-content" id="tab_filters">
        <div class="panel-card">
          <div class="card-title"><span>✨ قوالب تحسين الحفر</span></div>
          <div class="chip-grid">
            <button class="chip-btn" data-preset="stone_boost">حفر حجري بارز</button>
            <button class="chip-btn" data-preset="dark_invert">عكس الصخور</button>
            <button class="chip-btn" data-preset="deep_contrast">تباين الأخاديد</button>
            <button class="chip-btn" data-preset="otsu_clean">عتبة أوتسو</button>
            <button class="chip-btn" data-preset="sobel_edges">كشف الحواف</button>
            <button class="chip-btn" data-preset="sandstone_map">خريطة صخرية</button>
          </div>
        </div>

        <div class="panel-card">
          <div class="card-title"><span>⚡ فلاتر كشف الحواف والأخاديد</span></div>
          <select class="select-input" id="selEdge">
            <option value="none">بدون كشف حواف</option>
            <option value="sobel">فلتر سوبل (Sobel - إبراز الحفر)</option>
            <option value="laplacian">فلتر لابلاسيان (Laplacian)</option>
          </select>
          <select class="select-input" id="selBinarize" style="margin-top: 4px;">
            <option value="none">ألوان كاملة (بدون عتبة)</option>
            <option value="otsu">عتبة أوتسو الثنائية (Otsu)</option>
          </select>
        </div>
      </div>

      <!-- Tab 2: Geometry & Adjustments -->
      <div class="tools-tab-content" id="tab_geom" style="display: none;">
        <div class="panel-card">
          <div class="card-title">
            <span>🔄 تدوير وهندسة الصورة</span>
            <button class="btn btn-sm" id="btnResetRot" style="padding: 1px 4px;">0°</button>
          </div>
          <div class="ctrl-group">
            <div class="ctrl-row"><span>الزاوية</span><span class="ctrl-val" id="valRot">0°</span></div>
            <input type="range" id="sliderRot" min="-180" max="180" value="0" step="1">
          </div>
          <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.2rem;">
            <button class="btn btn-sm" id="btnCCW">↺ 90°</button>
            <button class="btn btn-sm" id="btnCW">↻ 90°</button>
            <button class="btn btn-sm" id="btnFlH">↔ أفقي</button>
            <button class="btn btn-sm" id="btnFlV">↕ رأسي</button>
          </div>
        </div>

        <div class="panel-card">
          <div class="card-title"><span>☀️ الإضاءة والتباين</span><button class="btn btn-sm" id="btnResetFilters" style="padding: 1px 4px;">إعادة ضبط</button></div>
          <div class="ctrl-group">
            <div class="ctrl-row"><span>السطوع</span><span class="ctrl-val" id="valBright">0</span></div>
            <input type="range" id="sliderBright" min="-1" max="1" value="0" step="0.02">
          </div>
          <div class="ctrl-group">
            <div class="ctrl-row"><span>التباين</span><span class="ctrl-val" id="valContrast">0</span></div>
            <input type="range" id="sliderContrast" min="-1" max="1" value="0" step="0.02">
          </div>
          <div class="ctrl-group">
            <div class="ctrl-row"><span>غاما</span><span class="ctrl-val" id="valGamma">1.0</span></div>
            <input type="range" id="sliderGamma" min="0.2" max="3" value="1.0" step="0.05">
          </div>
          <div class="ctrl-group">
            <div class="ctrl-row"><span>الشحذ</span><span class="ctrl-val" id="valSharpen">0</span></div>
            <input type="range" id="sliderSharpen" min="0" max="3" value="0" step="0.1">
          </div>
          <div style="display: flex; justify-content: space-between; font-size: 0.70rem;">
            <label style="cursor: pointer;"><input type="checkbox" id="chkInvert"> عكس الألوان</label>
            <label style="cursor: pointer;"><input type="checkbox" id="chkEqualize"> موازنة التباين</label>
          </div>
        </div>
      </div>

      <!-- Tab 3: Box Shaper & Annotations List -->
      <div class="tools-tab-content" id="tab_boxes" style="display: none;">
        <!-- PlayStation-Style Box Shaper -->
        <div class="panel-card" id="boxShaperCard" style="display: none; border-color: var(--accent-orange);">
          <div class="card-title">
            <span style="color: var(--accent-orange);">🎮 تشكيل الصندوق (D-Pad)</span>
            <span class="ctrl-val" id="boxShaperId">#0</span>
          </div>

          <div class="dpad-wrapper">
            <div class="dpad-step-bar">
              <span style="font-size: 0.62rem; color: var(--text-muted);">الخطوة:</span>
              <div class="dpad-steps" id="dpadStepsContainer">
                <button class="step-btn" data-step="1">1px</button>
                <button class="step-btn active" data-step="2">2px</button>
                <button class="step-btn" data-step="5">5px</button>
                <button class="step-btn" data-step="10">10px</button>
              </div>
            </div>

            <div class="dpad-cross">
              <div class="dpad-arm dpad-top">
                <div class="dpad-btn-pair">
                  <button class="dpad-btn btn-shrink" id="btnTopShrink">▼ تصغير</button>
                  <button class="dpad-btn btn-expand" id="btnTopExpand">▲ تكبير</button>
                </div>
              </div>

              <div class="dpad-middle-row">
                <div class="dpad-arm dpad-left">
                  <div class="dpad-btn-pair">
                    <button class="dpad-btn btn-expand" id="btnLeftExpand">◀</button>
                    <button class="dpad-btn btn-shrink" id="btnLeftShrink">▶</button>
                  </div>
                </div>

                <div class="dpad-center-hub">
                  <div class="hub-title" id="dpadDims">0×0</div>
                  <div class="hub-actions">
                    <button class="hub-btn" id="btnAllShrink">− الكل</button>
                    <button class="hub-btn" id="btnAllExpand">+ الكل</button>
                  </div>
                </div>

                <div class="dpad-arm dpad-right">
                  <div class="dpad-btn-pair">
                    <button class="dpad-btn btn-shrink" id="btnRightShrink">◀</button>
                    <button class="dpad-btn btn-expand" id="btnRightExpand">▶</button>
                  </div>
                </div>
              </div>

              <div class="dpad-arm dpad-bottom">
                <div class="dpad-btn-pair">
                  <button class="dpad-btn btn-shrink" id="btnBottomShrink">▲ تصغير</button>
                  <button class="dpad-btn btn-expand" id="btnBottomExpand">▼ تكبير</button>
                </div>
              </div>
            </div>
          </div>

          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 3px; font-size: 0.68rem; margin-top: 2px;">
            <div><span style="color: var(--text-muted);">X:</span> <input type="number" id="inpBoxX" style="width: 100%; background: #0b101a; border: 1px solid var(--border-card); color: #fff; border-radius: 3px; padding: 1px 3px;"></div>
            <div><span style="color: var(--text-muted);">Y:</span> <input type="number" id="inpBoxY" style="width: 100%; background: #0b101a; border: 1px solid var(--border-card); color: #fff; border-radius: 3px; padding: 1px 3px;"></div>
            <div><span style="color: var(--text-muted);">W:</span> <input type="number" id="inpBoxW" style="width: 100%; background: #0b101a; border: 1px solid var(--border-card); color: #fff; border-radius: 3px; padding: 1px 3px;"></div>
            <div><span style="color: var(--text-muted);">H:</span> <input type="number" id="inpBoxH" style="width: 100%; background: #0b101a; border: 1px solid var(--border-card); color: #fff; border-radius: 3px; padding: 1px 3px;"></div>
          </div>
        </div>

        <!-- Annotations Summary -->
        <div class="panel-card" style="flex: 1; overflow-y: auto; max-height: 280px;">
          <div class="card-title">
            <span>التوسيمات الحالية</span>
            <span class="ctrl-val" id="annTotalBadge">0 عناصر</span>
          </div>
          <div id="annList" style="display: flex; flex-direction: column; gap: 3px;"></div>
        </div>
      </div>
    </aside>

  </main>

  <!-- LEVEL 4: BOTTOM IMAGE CAROUSEL STRIP -->
  <footer class="bottom-gallery" id="thumbStrip">
    <div class="thumb-add" onclick="document.getElementById('fileImgInput').click()" title="إضافة صور">+</div>
  </footer>

  <!-- MODALS -->
  <div class="modal-backdrop" id="exportModal">
    <div class="modal-box">
      <div class="modal-header">
        <h3 style="font-size: 0.95rem; color: #fff;">💾 تصدير التوسيمات والصور</h3>
        <button class="btn btn-sm" id="btnCloseExport">✕</button>
      </div>
      <div class="modal-opt" id="btnDoExportYOLO">
        <div>
          <div style="font-weight: bold; font-size: 0.85rem; color: #fff;">🚀 تصدير ملفات YOLO (.txt + classes.txt + data.yaml)</div>
          <div style="font-size: 0.70rem; color: var(--text-secondary);">إحداثيات معيارية جاهزة لتدريب نماذج YOLO</div>
        </div>
        <button class="btn btn-primary btn-sm">تنزيل YOLO</button>
      </div>
      <div class="modal-opt" id="btnDoExportCrops">
        <div>
          <div style="font-weight: bold; font-size: 0.85rem; color: #fff;">✂️ قص مقتطفات الحروف المفردة (Cropped Patches ZIP)</div>
          <div style="font-size: 0.70rem; color: var(--text-secondary);">قص كل حرف موسوم كصورة منفصلة مع مجلد لكل فئة</div>
        </div>
        <button class="btn btn-sm" style="border-color: var(--accent-orange); color: var(--accent-orange);">تنزيل المقتطفات</button>
      </div>
      <div class="modal-opt" id="btnDoExportImage">
        <div>
          <div style="font-weight: bold; font-size: 0.85rem; color: #fff;">🖼️ تصدير الصورة المعالجة (PNG عالية الدقة)</div>
          <div style="font-size: 0.70rem; color: var(--text-secondary);">تصدير الصورة الحالية مع التعديلات اللونية</div>
        </div>
        <button class="btn btn-sm">تنزيل الصورة</button>
      </div>
    </div>
  </div>

  <div class="modal-backdrop" id="aiResultsModal">
    <div class="modal-box" style="max-width: 600px; border-color: #9d4edd; box-shadow: 0 0 25px rgba(157, 78, 221, 0.35);">
      <div class="modal-header" style="border-bottom-color: rgba(157, 78, 221, 0.3);">
        <div style="display: flex; align-items: center; gap: 8px;">
          <span style="font-size: 1.2rem;">🤖</span>
          <div>
            <h3 style="font-size: 0.95rem; color: #fff; margin: 0;">تقرير فحص الحروف بالذكاء الاصطناعي (AI Inspection)</h3>
            <span style="font-size: 0.68rem; color: #c77dff;">نتائج كشف النقوش ونسب الدقة والمطابقة</span>
          </div>
        </div>
        <button class="btn btn-sm" id="btnCloseAiModal" style="padding: 1px 6px;">✕</button>
      </div>
      <div style="background: #080c14; border: 1px solid rgba(157, 78, 221, 0.4); border-radius: 6px; padding: 10px; text-align: center;">
        <div style="font-size: 0.70rem; color: #94a3b8; margin-bottom: 4px;">🔤 الحروف والنص المكتشف على الصخرة:</div>
        <div id="aiDetectedGlyphs" style="font-family: var(--font-nabataean); font-size: 2rem; color: #00f5d4; letter-spacing: 5px; min-height: 40px; text-shadow: 0 0 10px rgba(0, 245, 212, 0.5);"></div>
        <div id="aiDetectedArabic" style="font-size: 0.82rem; color: #ffbe0b; font-weight: 700; margin-top: 3px;"></div>
      </div>
      <div style="max-height: 240px; overflow-y: auto; display: flex; flex-direction: column; gap: 5px; padding-right: 4px;" id="aiDetectionsList"></div>
      <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 8px; margin-top: 4px;">
        <span id="aiSummaryCount" style="font-size: 0.72rem; color: #94a3b8; font-family: var(--font-mono);"></span>
        <div style="display: flex; gap: 6px;">
          <button class="btn btn-sm" id="btnDismissAiModal">إغلاق التقرير</button>
          <button class="btn btn-primary btn-sm" id="btnApplyAiBoxes">
            <span>📥</span>
            <span>رسم الصناديق على الكانفاس</span>
          </button>
        </div>
      </div>
    </div>
  </div>

  <div class="toast-container" id="toastContainer"></div>

"""

final_html = new_head_and_body + script_part

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(final_html)

print("Applied responsive compact layout successfully to index.html!")
