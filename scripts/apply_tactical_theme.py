with open('app/static/styles.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Add Tactical Law Enforcement Command Theme Override at the end of styles.css
tactical_override = """

/* =========================================================================
   OFFICIAL MHA / I4C TACTICAL LAW ENFORCEMENT COMMAND THEME OVERRIDE
   Transforming from consumer glassmorphic UI to authentic Defense / Police Console
   ========================================================================= */

/* 1. Global Tactical Dark Palette */
body {
  background: #090d16 !important;
  color: #e2e8f0 !important;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
}

/* 2. Top Header - Official Government Cyber Command Bar */
.top-header {
  background: #0c121e !important;
  border-bottom: 1px solid #1e293b !important;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.4) !important;
  padding: 0.65rem 1.5rem !important;
}

.brand-emblem-fi {
  background: linear-gradient(135deg, #0369a1 0%, #0284c7 100%) !important;
  border: 1px solid #38bdf8 !important;
  border-radius: 4px !important;
  box-shadow: none !important;
}

.brand-emblem-fi span {
  font-weight: 800 !important;
  font-size: 0.75rem !important;
  letter-spacing: 0.5px !important;
}

.brand-titles h1 {
  font-size: 1.15rem !important;
  font-weight: 700 !important;
  color: #f8fafc !important;
  letter-spacing: -0.2px !important;
}

.brand-subtitle {
  color: #94a3b8 !important;
  font-size: 0.72rem !important;
  font-family: 'JetBrains Mono', monospace !important;
}

/* Official Government Node Pill in Header */
.official-node-tag {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: rgba(2, 132, 199, 0.12);
  border: 1px solid rgba(56, 189, 248, 0.35);
  color: #38bdf8;
  padding: 2px 7px;
  border-radius: 3px;
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.4px;
  text-transform: uppercase;
}

/* 3. Header Search & Feed Selectors - Tactical Form Controls */
.header-search-bar {
  background: #111827 !important;
  border: 1px solid #334155 !important;
  border-radius: 4px !important;
  box-shadow: none !important;
}

.header-search-bar input {
  color: #f1f5f9 !important;
  font-size: 0.78rem !important;
}

.header-feed-pill {
  background: #111827 !important;
  border: 1px solid #334155 !important;
  border-radius: 4px !important;
}

.header-select-inline {
  color: #e2e8f0 !important;
  background: transparent !important;
}

/* 4. Navigation Bar - Segmented Tactical Switch */
.finnova-nav-capsule {
  background: #0f172a !important;
  border: 1px solid #334155 !important;
  border-radius: 6px !important;
  padding: 3px !important;
  box-shadow: none !important;
}

.nav-tab-btn {
  border-radius: 4px !important;
  font-size: 0.75rem !important;
  font-weight: 600 !important;
  color: #94a3b8 !important;
  padding: 6px 14px !important;
  transition: all 0.15s ease !important;
}

.nav-tab-btn.active {
  background: #0284c7 !important;
  color: #ffffff !important;
  box-shadow: 0 1px 4px rgba(2, 132, 199, 0.4) !important;
}

/* 5. Statutory Advisory Notice */
.statutory-notice-banner, .finnova-notice-banner {
  background: #0f172a !important;
  border: 1px solid #1e293b !important;
  border-left: 4px solid #0284c7 !important;
  border-radius: 4px !important;
  box-shadow: none !important;
}

/* 6. Tactical Cards - Sharp 6px to 8px Edges & 1px Borders */
.finnova-stat-card,
.stat-card,
.tactical-card,
.account-detail-card,
.case-sidebar-panel,
.dashboard-card,
.dossier-card {
  background: #0f172a !important;
  border: 1px solid #1e293b !important;
  border-radius: 6px !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
}

.finnova-stat-card:hover {
  border-color: #334155 !important;
  transform: none !important;
}

/* Hero Risk Score Card */
.finnova-card-hero {
  background: #0f172a !important;
  border: 1px solid #1e293b !important;
}

/* Metric Values - High Legibility Crisp Fonts */
.finnova-card-val {
  color: #f8fafc !important;
  font-family: 'Inter', -apple-system, sans-serif !important;
  font-weight: 800 !important;
  letter-spacing: -0.5px !important;
}

.finnova-card-tag {
  color: #94a3b8 !important;
  font-size: 0.72rem !important;
  font-weight: 700 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.5px !important;
}

.finnova-badge-pill {
  border-radius: 3px !important;
  font-size: 0.68rem !important;
  font-weight: 700 !important;
}

/* 7. Left Sidebar Case Docket */
.case-sidebar-panel {
  background: #0f172a !important;
  border: 1px solid #1e293b !important;
  border-radius: 6px !important;
}

.sidebar-title-bar {
  border-bottom: 1px solid #1e293b !important;
}

/* Golden Hour Widget - High-Visibility Alert Terminal */
.golden-hour-widget {
  background: #111827 !important;
  border: 1px solid #374151 !important;
  border-left: 3px solid #ef4444 !important;
  border-radius: 4px !important;
  box-shadow: none !important;
}

.btn-emergency-blast {
  background: #dc2626 !important;
  border: 1px solid #ef4444 !important;
  border-radius: 4px !important;
  font-weight: 700 !important;
  font-size: 0.76rem !important;
  letter-spacing: 0.3px !important;
  box-shadow: none !important;
  transition: background 0.15s ease !important;
}

.btn-emergency-blast:hover {
  background: #b91c1c !important;
  transform: none !important;
}

/* Form Inputs in Sidebar */
.form-input, .form-select, select.header-select-inline {
  background: #111827 !important;
  border: 1px solid #334155 !important;
  border-radius: 4px !important;
  color: #f1f5f9 !important;
  font-size: 0.78rem !important;
}

.form-input:focus, .form-select:focus {
  border-color: #0284c7 !important;
  outline: none !important;
  box-shadow: 0 0 0 1px #0284c7 !important;
}

/* 8. Multi-Hop Incident Stream Table */
.finnova-stream-section {
  background: #0c121e !important;
  border: 1px solid #1e293b !important;
  border-radius: 6px !important;
}

.stream-tab-btn {
  border-radius: 3px !important;
  font-size: 0.72rem !important;
  font-weight: 600 !important;
}

.stream-tab-btn.active {
  background: #1e293b !important;
  color: #38bdf8 !important;
}

/* Stream Items */
.stream-item {
  background: #0f172a !important;
  border: 1px solid #1e293b !important;
  border-radius: 4px !important;
  box-shadow: none !important;
}

.stream-item:hover {
  border-color: #334155 !important;
  background: #131b2e !important;
}

.stream-item-title {
  color: #f8fafc !important;
  font-weight: 600 !important;
  font-size: 0.8rem !important;
}

.stream-item-sub {
  color: #94a3b8 !important;
  font-size: 0.72rem !important;
  font-family: 'JetBrains Mono', monospace !important;
}

.stream-item-amount {
  font-family: 'JetBrains Mono', monospace !important;
  font-weight: 700 !important;
}

/* 9. Directed Graph View */
.graph-canvas-container {
  background: #090d16 !important;
  border: 1px solid #1e293b !important;
  border-radius: 6px !important;
}

/* 10. Modals - Clean Law Enforcement Briefing Dialogs */
.modal-box {
  background: #0f172a !important;
  border: 1px solid #334155 !important;
  border-radius: 6px !important;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.7) !important;
  color: #e2e8f0 !important;
}

.modal-header {
  border-bottom: 1px solid #1e293b !important;
}

.modal-header h2 {
  color: #f8fafc !important;
  font-size: 0.95rem !important;
  font-weight: 700 !important;
}

/* 11. Remove blurry purple drop-shadows on SVG wave */
#dash-sparkwave-path-line {
  filter: drop-shadow(0 1px 4px rgba(2, 132, 199, 0.4)) !important;
  stroke-width: 2.2px !important;
}

/* Wave container styling */
.dash-sparkwave-container {
  background: #090d16 !important;
  border: 1px solid #1e293b !important;
  border-radius: 4px !important;
  padding: 4px !important;
}
"""

if 'OFFICIAL MHA / I4C TACTICAL LAW ENFORCEMENT COMMAND THEME' not in css:
    css = css + tactical_override
    with open('app/static/styles.css', 'w', encoding='utf-8') as f:
        f.write(css)
    print('styles.css updated with tactical theme!')
else:
    print('styles.css already has tactical theme override')
