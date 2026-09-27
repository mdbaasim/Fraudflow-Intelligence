with open('app/static/styles.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Fix -webkit-text-fill-color on brand titles
css = css.replace(
    '-webkit-text-fill-color: var(--text-heading);',
    '-webkit-text-fill-color: #ffffff;'
)

extra_contrast_rules = """
/* Maximum Contrast for Headings and Brand Titles */
.brand-titles h1,
.brand-titles h1 span,
header h1,
header h1 span {
  color: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
  font-weight: 800 !important;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5) !important;
}

.main-page-title,
.finnova-page-title,
.dashboard-title-area h1,
.dashboard-title-area h2 {
  color: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
  font-weight: 800 !important;
}

.notice-text,
.statutory-notice-banner,
.statutory-notice-banner strong {
  color: #e2e8f0 !important;
}
"""

with open('app/static/styles.css', 'w', encoding='utf-8') as f:
    f.write(css + extra_contrast_rules)

print('Heading contrast rules applied successfully!')
