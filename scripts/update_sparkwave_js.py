import re

with open('app/static/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

old_engine_pattern = r'function startSparkwaveEngine\(\) \{.*?requestAnimationFrame\(renderSparkwaveFrame\);\s*\}'

new_engine = '''function startSparkwaveEngine() {
    if (sparkwaveAnimRunning) return;
    sparkwaveAnimRunning = true;

    function renderSparkwaveFrame(now) {
      // Smoothly interpolate towards target risk (spring physics)
      sparkwaveCurrentRisk += (sparkwaveTargetRisk - sparkwaveCurrentRisk) * 0.08;
      const fRisk = sparkwaveCurrentRisk;

      // Base peak Y (inverted coordinate: smaller Y = higher on card)
      const basePeakY = Math.max(16, Math.min(92, 105 - (fRisk / 100) * 85));

      // Pronounced, clearly visible fluid wave harmonics
      const t = now * 0.0032;
      const waveOsc1 = Math.sin(t * 1.8) * 6.5;
      const waveOsc2 = Math.sin(t * 2.2 - 1.2) * 8.5;
      const waveOsc3 = Math.cos(t * 1.9 - 2.5) * 7.5;
      const waveOsc4 = Math.sin(t * 2.4 - 3.8) * 5.5;
      const peakOsc = Math.sin(t * 2.0) * 3.5;

      const peakY = basePeakY + peakOsc;
      const y1 = 110 - (110 - basePeakY) * 0.16 + waveOsc1;
      const y2 = 110 - (110 - basePeakY) * 0.38 + waveOsc2;
      const y3 = 110 - (110 - basePeakY) * 0.62 + waveOsc3;
      const y4 = 110 - (110 - basePeakY) * 0.82 + waveOsc4;
      const yEnd = Math.max(10, peakY - 3 + waveOsc2 * 0.3);

      // Smooth multi-segment cubic Bezier path for fluid ripple
      const p1x = 130, p1y = y2;
      const p2x = 280, p2y = y3;
      const p3x = 410, p3y = y4;
      const p4x = 510, p4y = peakY;

      const areaD = `M 0 ${y1.toFixed(1)} ` +
                    `C 60 ${(y1 - 8 + waveOsc2 * 0.5).toFixed(1)}, 90 ${(p1y + 6).toFixed(1)}, ${p1x} ${p1y.toFixed(1)} ` +
                    `C 180 ${(p1y - 10).toFixed(1)}, 230 ${(p2y + 8).toFixed(1)}, ${p2x} ${p2y.toFixed(1)} ` +
                    `C 330 ${(p2y - 8).toFixed(1)}, 370 ${(p3y + 6).toFixed(1)}, ${p3x} ${p3y.toFixed(1)} ` +
                    `C 450 ${(p3y - 6).toFixed(1)}, 480 ${(p4y + 4).toFixed(1)}, ${p4x} ${p4y.toFixed(1)} ` +
                    `L 510 120 L 0 120 Z`;

      const lineD = `M 0 ${y1.toFixed(1)} ` +
                    `C 60 ${(y1 - 8 + waveOsc2 * 0.5).toFixed(1)}, 90 ${(p1y + 6).toFixed(1)}, ${p1x} ${p1y.toFixed(1)} ` +
                    `C 180 ${(p1y - 10).toFixed(1)}, 230 ${(p2y + 8).toFixed(1)}, ${p2x} ${p2y.toFixed(1)} ` +
                    `C 330 ${(p2y - 8).toFixed(1)}, 370 ${(p3y + 6).toFixed(1)}, ${p3x} ${p3y.toFixed(1)} ` +
                    `C 450 ${(p3y - 6).toFixed(1)}, 480 ${(p4y + 4).toFixed(1)}, ${p4x} ${p4y.toFixed(1)} ` +
                    `L 600 ${yEnd.toFixed(1)}`;

      const pathArea = elements.dashSparkwavePathArea || document.getElementById('dash-sparkwave-path-area');
      const pathLine = elements.dashSparkwavePathLine || document.getElementById('dash-sparkwave-path-line');
      const markerLine = elements.dashSparkwaveMarkerLine || document.getElementById('dash-sparkwave-marker-line');
      const markerDot = elements.dashSparkwaveMarkerDot || document.getElementById('dash-sparkwave-marker-dot');
      const pulseRing = elements.dashSparkwavePulseRing || document.getElementById('dash-sparkwave-pulse-ring');

      if (pathArea) pathArea.setAttribute('d', areaD);
      if (pathLine) pathLine.setAttribute('d', lineD);
      if (markerLine) markerLine.setAttribute('y1', peakY.toFixed(1));
      if (markerDot) markerDot.setAttribute('cy', peakY.toFixed(1));
      if (pulseRing) pulseRing.setAttribute('cy', peakY.toFixed(1));

      requestAnimationFrame(renderSparkwaveFrame);
    }

    requestAnimationFrame(renderSparkwaveFrame);
  }'''

match = re.search(old_engine_pattern, js, re.DOTALL)
if match:
    js = js[:match.start()] + new_engine + js[match.end():]
    print('startSparkwaveEngine regex matched and replaced!')
else:
    print('Regex failed to match old startSparkwaveEngine')

with open('app/static/app.js', 'w', encoding='utf-8') as f:
    f.write(js)
