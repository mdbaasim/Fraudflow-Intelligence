with open('app/static/styles.css', 'r', encoding='utf-8') as f:
    css = f.read()

unify_rules = """

/* =========================================================================
   100% UNIFIED SEAMLESS TACTICAL CYBER COMMAND CENTER (PALANTIR / NCRP)
   ========================================================================= */

/* Global Canvas */
html, body {
  background-color: #090d16 !important;
  color: #f8fafc !important;
}

.app-layout-wrapper {
  background-color: #090d16 !important;
}

/* Left Sidebar Container */
.left-sidebar {
  background: #0c121e !important;
  border-right: 1px solid #1e293b !important;
}

/* Sidebar Cards */
.sidebar-case-intake-card,
.sidebar-case-card,
.case-filing-card,
.sidebar-footer-brand {
  background: #0f172a !important;
  border: 1px solid #1e293b !important;
  border-radius: 6px !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4) !important;
  color: #f8fafc !important;
}

/* Sidebar Headings & Labels */
.sidebar-case-card h3,
.sidebar-case-card h4,
.cmd-case-intake-sidebar h3,
.case-details-header,
.case-form-group label,
.sidebar-case-card label,
.cmd-case-intake-sidebar label {
  color: #94a3b8 !important;
  font-weight: 600 !important;
  font-size: 0.72rem !important;
}

/* Sidebar Form Inputs & Selects */
.cmd-case-intake-sidebar .cmd-case-select,
.sidebar-case-card input,
.sidebar-case-card select,
.case-form-input,
.form-input,
.form-select {
  background: #111827 !important;
  border: 1px solid #334155 !important;
  color: #f8fafc !important;
  border-radius: 4px !important;
  font-size: 0.78rem !important;
}

.cmd-case-intake-sidebar .cmd-case-select:focus,
.sidebar-case-card input:focus,
.sidebar-case-card select:focus,
.form-input:focus,
.form-select:focus {
  border-color: #0284c7 !important;
  outline: none !important;
  box-shadow: 0 0 0 1px #0284c7 !important;
}

/* Brand Header Title */
.brand-titles h1,
.brand-titles h1 span {
  color: #ffffff !important;
  font-size: 1.2rem !important;
  font-weight: 700 !important;
}

.brand-subtitle span {
  color: #94a3b8 !important;
}

/* Main Dashboard Page Headings */
.finnova-page-title,
.main-page-title,
h1, h2, h3, h4 {
  color: #f8fafc !important;
}

.finnova-page-subtitle,
.main-page-subtitle,
.page-subtitle {
  color: #94a3b8 !important;
}

/* Top Navigation Tabs */
.finnova-nav-capsule {
  background: #0f172a !important;
  border: 1px solid #1e293b !important;
  border-radius: 6px !important;
}

.nav-tab-btn {
  color: #94a3b8 !important;
  border-radius: 4px !important;
}

.nav-tab-btn.active {
  background: #0284c7 !important;
  color: #ffffff !important;
}

/* Footer Brand */
.sidebar-footer-brand {
  color: #94a3b8 !important;
}

.sidebar-footer-brand span {
  color: #38bdf8 !important;
}

.sidebar-footer-brand a {
  color: #0ea5e9 !important;
}
"""

with open('app/static/styles.css', 'w', encoding='utf-8') as f:
    f.write(css + unify_rules)

print('Unify dark theme rules appended successfully!')
