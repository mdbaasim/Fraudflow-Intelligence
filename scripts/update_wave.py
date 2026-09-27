import re

with open('app/static/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update finnovaLineGrad with animated stops
old_grad = re.search(r'<linearGradient id="finnovaLineGrad"[^>]*>.*?</linearGradient>', html, re.DOTALL)
if old_grad:
    new_grad = '''<linearGradient id="finnovaLineGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stop-color="#818cf8" />
                  <stop offset="50%" stop-color="#5256e8">
                    <animate attributeName="stop-color" values="#5256e8;#a855f7;#38bdf8;#5256e8" dur="3.5s" repeatCount="indefinite" />
                  </stop>
                  <stop offset="100%" stop-color="#a855f7">
                    <animate attributeName="stop-color" values="#a855f7;#ec4899;#6366f1;#a855f7" dur="3.5s" repeatCount="indefinite" />
                  </stop>
                </linearGradient>'''
    html = html[:old_grad.start()] + new_grad + html[old_grad.end():]
    print('Grad updated')

# 2. Update pulse ring with SMIL animations
old_ring = re.search(r'<circle id="dash-sparkwave-pulse-ring"[^>]*/>', html)
if old_ring:
    new_ring = '''<circle id="dash-sparkwave-pulse-ring" cx="510" cy="30" r="4.5" fill="none" stroke="#6366f1" stroke-width="2" class="dash-sparkwave-pulse-ring">
                <animate attributeName="r" values="4.5;24;4.5" dur="1.8s" repeatCount="indefinite" />
                <animate attributeName="opacity" values="1;0.05;1" dur="1.8s" repeatCount="indefinite" />
                <animate attributeName="stroke-width" values="2.5;0.6;2.5" dur="1.8s" repeatCount="indefinite" />
              </circle>'''
    html = html[:old_ring.start()] + new_ring + html[old_ring.end():]
    print('Ring updated')

# 3. Update marker dot with subtle breathing pulse
old_dot = re.search(r'<circle id="dash-sparkwave-marker-dot"[^>]*/>', html)
if old_dot:
    new_dot = '''<circle id="dash-sparkwave-marker-dot" cx="510" cy="30" r="5" fill="#ffffff" stroke="#5256e8" stroke-width="2.5">
                <animate attributeName="r" values="4.5;6.2;4.5" dur="1.4s" repeatCount="indefinite" />
              </circle>'''
    html = html[:old_dot.start()] + new_dot + html[old_dot.end():]
    print('Dot updated')

with open('app/static/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('index.html wave animations applied!')
