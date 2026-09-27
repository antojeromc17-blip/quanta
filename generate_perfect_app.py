import re

def clean_glass_and_transparency(html: str) -> str:
    # 1. Remove backdrop blurs
    html = re.sub(r'backdrop-blur-[a-zA-Z0-9]+', '', html)
    html = re.sub(r'backdrop-blur', '', html)
    
    # 2. Remove ambient glow background blur divs
    html = re.sub(r'<div class="absolute[^"]*blur-[^"]*"[^>]*></div>', '', html)
    html = re.sub(r'<div class="absolute[^"]*blur\[[^"]*\][^"]*"[^>]*></div>', '', html)
    
    # 3. Remove inline blur classes
    html = re.sub(r'blur-\[1px\]', '', html)
    html = re.sub(r'blur-\[100px\]', '', html)
    html = re.sub(r'blur-\[120px\]', '', html)
    html = re.sub(r'blur-3xl', '', html)
    html = re.sub(r'blur-xl', '', html)
    html = re.sub(r'blur-md', '', html)

    # 4. Replace transparent backgrounds with solid colors from Stitch palette
    replacements = [
        ('bg-surface-container-lowest/90', 'bg-surface-container-lowest'),
        ('bg-surface-container-lowest/80', 'bg-surface-container-lowest'),
        ('bg-surface-container-lowest/70', 'bg-surface-container-lowest'),
        ('bg-surface-container-lowest/60', 'bg-surface-container-lowest'),
        ('bg-surface-container-lowest/40', 'bg-surface-container-lowest'),
        ('bg-surface-container-lowest/30', 'bg-surface-container-lowest'),
        ('bg-surface-container/80', 'bg-surface-container'),
        ('bg-surface-container-high/90', 'bg-surface-container-high'),
        ('bg-surface-container-high/80', 'bg-surface-container-high'),
        ('bg-surface-container-high/70', 'bg-surface-container-high'),
        ('bg-surface-container-high/60', 'bg-surface-container-high'),
        ('bg-surface-container-high/40', 'bg-surface-container-high'),
        ('bg-surface-container-low/60', 'bg-surface-container-low'),
        ('bg-primary/20', 'bg-primary-container'),
        ('bg-primary/10', 'bg-surface-container-high'),
        ('bg-primary/5', 'bg-surface-container-low'),
        ('bg-primary/70', 'bg-primary'),
        ('bg-primary/80', 'bg-primary'),
        ('bg-secondary/10', 'bg-secondary-container'),
        ('bg-secondary/70', 'bg-secondary'),
        ('bg-secondary/80', 'bg-secondary'),
        ('bg-secondary-container/40', 'bg-secondary-container'),
        ('bg-secondary-container/20', 'bg-secondary-container'),
        ('bg-tertiary/10', 'bg-surface-variant'),
        ('bg-tertiary/20', 'bg-surface-variant'),
        ('bg-tertiary/70', 'bg-tertiary'),
        ('bg-tertiary-container/30', 'bg-surface-variant'),
        ('bg-tertiary-container/20', 'bg-surface-variant'),
        ('bg-error-container/40', 'bg-error-container'),
        ('bg-error-container/30', 'bg-error-container'),
        ('bg-error-container/20', 'bg-error-container'),
        ('bg-error/70', 'bg-error'),
        ('bg-error/40', 'bg-error-container'),
        ('bg-error/30', 'bg-error-container'),
        ('bg-surface-tint/60', 'bg-primary'),
        ('bg-outline/20', 'bg-surface-variant'),
        ('bg-white/20', 'bg-surface-container-lowest'),
        ('border-outline-variant/40', 'border-outline-variant'),
        ('border-outline-variant/30', 'border-outline-variant'),
        ('border-outline-variant/20', 'border-outline-variant'),
        ('border-primary/30', 'border-primary'),
        ('ring-primary/40', 'ring-primary'),
        ('ring-secondary/40', 'ring-secondary'),
        ('shadow-[0_0_16px_rgba(6,182,212,0.3)]', 'shadow-md'),
        ('shadow-primary/20', 'shadow-md'),
        ('shadow-primary/40', 'shadow-md'),
        ('opacity-75', ''),
        ('opacity-80', ''),
        ('text-on-surface-variant/70', 'text-on-surface-variant'),
        ('text-error/80', 'text-error'),
        ('text-on-surface/80', 'text-on-surface'),
        ('from-primary/5', 'from-surface-container-lowest'),
        ('to-secondary/5', 'to-surface-container-lowest'),
        ('from-tertiary/10', 'from-surface-container-lowest'),
    ]
    for old, new in replacements:
        html = html.replace(old, new)

    # Clean double spaces in class names
    html = re.sub(r'class="([^"]*)"', lambda m: 'class="' + ' '.join(m.group(1).split()) + '"', html)
    return html

def extract_main_inner(filename: str) -> str:
    with open(f'stitch_screens/{filename}', 'r', encoding='utf-8') as f:
        content = f.read()
    start_main = content.find('<main')
    if start_main == -1:
        raise ValueError(f'Cannot find <main in {filename}')
    start_inner = content.find('>', start_main) + 1
    end_inner = content.rfind('</main>')
    inner = content[start_inner:end_inner].strip()
    
    # Remove top <div class="flex flex-col w-full"> if wrapped
    if inner.startswith('<div class="flex flex-col w-full">') and inner.endswith('</div>'):
        inner = inner[len('<div class="flex flex-col w-full">'):-len('</div>')].strip()
        
    return clean_glass_and_transparency(inner)

s1_html = extract_main_inner('screen_1_Portfolio_Input_and_Matrix.html')
s2_html = extract_main_inner('screen_2_Quantum_Execution.html')
s3_html = extract_main_inner('screen_3_Optimization_Results.html')
s4_html = extract_main_inner('screen_4_Mathematical_Intuition_Under_the_Hood.html')

# Write complete index.html
template = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta content="width=device-width, initial-scale=1.0" name="viewport"/>
  <meta content="web_standard" name="shell-type"/>
  <title>PS05 — Quantum Loan Portfolio Optimizer | Thrissur Cooperative Bank</title>

  <!-- Google Fonts: Stitch Design System (Anton, Plus Jakarta Sans, Bebas Neue, JetBrains Mono) -->
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin=""/>
  <link href="https://fonts.googleapis.com/css2?family=Anton:wght@400;500;700&amp;family=Plus+Jakarta+Sans:wght@400;500;700&amp;family=Bebas+Neue:wght@400;500;700&amp;display=swap" rel="stylesheet"/>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&amp;family=Plus+Jakarta+Sans:wght@400;500;600;700&amp;display=swap" rel="stylesheet"/>
  <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>

  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script id="tailwind-config">
    tailwind.config = {{
      darkMode: "class",
      theme: {{
        extend: {{
          colors: {{
            "surface-tint": "#416920",
            "secondary-fixed": "#ffdea8",
            "primary-fixed-dim": "#a6d47e",
            "on-primary-fixed": "#0c2000",
            "surface-bright": "#f7fdd1",
            "surface-container-high": "#e6ecc1",
            "on-tertiary": "#ffffff",
            "error-container": "#ffdad6",
            "surface-variant": "#e0e6bb",
            "outline-variant": "#bcc9cd",
            "tertiary-fixed": "#e2e2e2",
            "surface-container-highest": "#e0e6bb",
            "surface-container-low": "#f2f8cc",
            "primary-container": "#86b361",
            "on-error-container": "#93000a",
            "tertiary-container": "#a6a6a6",
            "secondary-fixed-dim": "#e3c28b",
            "on-primary": "#ffffff",
            "surface-container": "#ecf2c6",
            secondary: "#735b2d",
            primary: "#416920",
            outline: "#6d797d",
            "on-secondary-fixed-variant": "#594318",
            "surface-container-lowest": "#ffffff",
            "on-background": "#191e04",
            "on-surface-variant": "#3d494c",
            background: "#f7fdd1",
            "surface-dim": "#d8deb3",
            "on-primary-fixed-variant": "#2a5008",
            "on-tertiary-container": "#3c3c3c",
            "on-tertiary-fixed": "#1b1b1b",
            "on-error": "#ffffff",
            error: "#ba1a1a",
            "inverse-surface": "#2e3316",
            "inverse-primary": "#a6d47e",
            "on-surface": "#191e04",
            "inverse-on-surface": "#eff5c9",
            "on-primary-container": "#204400",
            tertiary: "#5e5e5e",
            "on-tertiary-fixed-variant": "#474747",
            "primary-fixed": "#c1f198",
            "secondary-container": "#fddba2",
            "tertiary-fixed-dim": "#c6c6c6",
            "on-secondary-container": "#785f31",
            surface: "#f7fdd1",
            "on-secondary": "#ffffff",
            "on-secondary-fixed": "#271900"
          }},
          borderRadius: {{
            DEFAULT: "0.125rem",
            lg: "0.25rem",
            xl: "0.5rem",
            full: "0.75rem"
          }},
          spacing: {{
            gutter: "1.25rem",
            "gutter-desktop": "1.5rem",
            margin: "1rem",
            "margin-desktop": "2rem",
            "space-sm": "0.5rem",
            "space-xl": "2.5rem",
            "space-xs": "0.25rem",
            "space-lg": "1.5rem",
            "space-md": "1rem"
          }},
          fontFamily: {{
            "body-lg": ["'Plus Jakarta Sans'", "sans-serif"],
            "headline-xl": ["'Plus Jakarta Sans'", "sans-serif"],
            "headline-md": ["'Plus Jakarta Sans'", "sans-serif"],
            "body-md": ["'Plus Jakarta Sans'", "sans-serif"],
            "headline-lg-mobile": ["'Plus Jakarta Sans'", "sans-serif"],
            "headline-xl-mobile": ["'Plus Jakarta Sans'", "sans-serif"],
            "body-sm": ["'Plus Jakarta Sans'", "sans-serif"],
            "label-md": ["'JetBrains Mono'", "monospace"],
            "label-lg": ["'JetBrains Mono'", "monospace"],
            "label-sm": ["'JetBrains Mono'", "monospace"],
            "headline-lg": ["'Plus Jakarta Sans'", "sans-serif"],
            "headline-sm": ["'Plus Jakarta Sans'", "sans-serif"],
            headline: ["'Anton'", "sans-serif"],
            display: ["'Anton'", "sans-serif"],
            body: ["'Plus Jakarta Sans'", "sans-serif"],
            label: ["'Bebas Neue'", "sans-serif"],
            mono: ["'JetBrains Mono'", "monospace"]
          }},
          fontSize: {{
            "body-lg": ["16px", {{lineHeight: "24px", letterSpacing: "0em", fontWeight: "400"}}],
            "headline-xl": ["36px", {{lineHeight: "44px", letterSpacing: "-0.025em", fontWeight: "700"}}],
            "headline-md": ["20px", {{lineHeight: "28px", letterSpacing: "-0.015em", fontWeight: "600"}}],
            "body-md": ["14px", {{lineHeight: "20px", letterSpacing: "0em", fontWeight: "400"}}],
            "headline-lg-mobile": ["22px", {{lineHeight: "30px", letterSpacing: "-0.015em", fontWeight: "600"}}],
            "headline-xl-mobile": ["28px", {{lineHeight: "36px", letterSpacing: "-0.02em", fontWeight: "700"}}],
            "body-sm": ["12px", {{lineHeight: "18px", letterSpacing: "0.01em", fontWeight: "400"}}],
            "label-md": ["12px", {{lineHeight: "16px", letterSpacing: "0.04em", fontWeight: "500"}}],
            "label-lg": ["14px", {{lineHeight: "20px", letterSpacing: "0.02em", fontWeight: "600"}}],
            "label-sm": ["10px", {{lineHeight: "14px", letterSpacing: "0.06em", fontWeight: "500"}}],
            "headline-lg": ["28px", {{lineHeight: "36px", letterSpacing: "-0.02em", fontWeight: "600"}}],
            "headline-sm": ["16px", {{lineHeight: "24px", letterSpacing: "-0.01em", fontWeight: "600"}}]
          }}
        }}
      }}
    }};
  </script>

  <style>
    @layer base {{
      html, body {{
        margin: 0;
        padding: 0;
        background-color: #f7fdd1 !important;
        color: #191e04 !important;
        font-family: 'Plus Jakarta Sans', sans-serif;
      }}
      body {{
        overscroll-behavior: none;
      }}
      main > :first-child {{ margin-top: 0 !important; }}
      main > :last-child {{ margin-bottom: 0 !important; }}
    }}
    ::-webkit-scrollbar {{
      display: none;
    }}
    .tab-pane {{
      display: none;
    }}
    .tab-pane.active {{
      display: block;
    }}
  </style>
</head>
<body class="bg-surface font-body-md text-body-md text-on-surface antialiased min-h-screen selection:bg-primary-container selection:text-on-primary-container">

  <!-- ================= HEADER (EXACT STITCH - ZERO GLASS/TRANSPARENCY) ================= -->
  <header class="fixed top-0 w-full z-50 bg-surface-container-lowest shadow-[0_1px_8px_rgba(0,0,0,0.06)] border-b border-surface-variant">
    <div class="h-20 w-full px-margin-desktop flex items-center justify-between gap-space-md">
      
      <!-- Brand & Title -->
      <div class="flex items-center gap-space-md shrink-0">
        <img alt="Quantum Loan Optimizer Logo" class="h-8 w-auto object-contain" src="https://lh3.googleusercontent.com/aida/AEtjO1W0aF7LrtFw1jnwEgCnHDzgf3Sqb78l_a_vhU_egTtg-eEMyNAplFc8lIsR2INPYx4bWI6dymi0VkXeOTk7q2pQL2lSyanvKchB7Zns5WrECJo1-JMGhQLAE9l7JFDNPqDITe6nxyGp_IAHceXlp-zXIjxao4t7YJgfhRnYOXssiLQ-joaM_38y6aDfUG_dVfJ-9YdOdnw5enf9tN6O8skHwLksQr7bdxvdy9BwaeM0FtrWKO3KNgxL7M4L"/>
        <div class="flex flex-col">
          <div class="flex items-center gap-space-sm">
            <span class="font-headline-sm text-headline-sm font-semibold tracking-tight text-on-surface">Quantum Loan Portfolio Optimizer</span>
            <span class="px-space-sm py-space-xs rounded-full bg-surface-container-high text-primary font-label-sm text-label-sm uppercase tracking-wider font-bold">
              PS05 • Thrissur Cooperative Bank Demo
            </span>
          </div>
          <span class="font-body-sm text-body-sm text-on-surface-variant">Institutional Fiduciary Asset Allocation System</span>
        </div>
      </div>

      <!-- Navigation Tabs (Exact Stitch Fonts & Labels) -->
      <nav class="hidden xl:flex items-center gap-space-xs bg-surface-container-low p-space-xs rounded-full">
        <button onclick="switchTab('screen-portfolio')" id="nav-screen-portfolio" class="px-space-md py-space-sm rounded-full font-label-md text-label-md bg-surface-container-high text-primary transition-all">
          1. Portfolio Input &amp; Matrix
        </button>
        <button onclick="switchTab('screen-quantum')" id="nav-screen-quantum" class="px-space-md py-space-sm rounded-full font-label-md text-label-md text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high transition-all">
          2. Quantum Execution
        </button>
        <button onclick="switchTab('screen-results')" id="nav-screen-results" class="px-space-md py-space-sm rounded-full font-label-md text-label-md text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high transition-all">
          3. Optimization Results
        </button>
        <button onclick="switchTab('screen-math')" id="nav-screen-math" class="px-space-md py-space-sm rounded-full font-label-md text-label-md text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high transition-all">
          4. Mathematical Intuition / Under the Hood
        </button>
      </nav>

      <!-- Right Header Actions -->
      <div class="flex items-center gap-space-md shrink-0">
        <div class="hidden md:flex items-center gap-space-sm px-space-md py-space-xs rounded-full bg-surface-container-low font-label-sm text-label-sm">
          <span class="w-2 h-2 rounded-full bg-primary animate-pulse"></span>
          <span class="text-primary font-bold" id="qpuStatusBadge">QPU Sim: QAOA (p=3) Online</span>
        </div>

        <button onclick="quickDemoTour()" class="flex items-center gap-space-xs px-space-md py-space-sm rounded-full bg-surface-container-high text-on-surface hover:bg-surface-variant transition-colors font-label-md text-label-md cursor-pointer" type="button">
          <span class="material-symbols-outlined text-[16px] text-primary">play_circle</span>
          <span>Quick Demo Tour</span>
        </button>

        <button onclick="triggerOptimization()" class="flex items-center gap-space-xs px-space-md py-space-sm rounded-full bg-primary hover:bg-primary-container text-on-primary font-label-md text-label-md font-bold transition-all shadow-md cursor-pointer">
          <span class="material-symbols-outlined text-[16px]">bolt</span>
          <span>Run QAOA</span>
        </button>
      </div>

    </div>
  </header>

  <!-- ================= MAIN CONTAINER ================= -->
  <main class="w-full pt-20 bg-surface min-h-[calc(100vh-80px)]">
    <div class="flex flex-col w-full">

      <!-- ================= SCREEN 1: PORTFOLIO INPUT & MATRIX ================= -->
      <div id="screen-portfolio" class="tab-pane active w-full">
        {s1_html}
      </div>

      <!-- ================= SCREEN 2: QUANTUM EXECUTION ================= -->
      <div id="screen-quantum" class="tab-pane w-full">
        {s2_html}
      </div>

      <!-- ================= SCREEN 3: OPTIMIZATION RESULTS ================= -->
      <div id="screen-results" class="tab-pane w-full">
        {s3_html}
      </div>

      <!-- ================= SCREEN 4: MATHEMATICAL INTUITION / UNDER THE HOOD ================= -->
      <div id="screen-math" class="tab-pane w-full">
        {s4_html}
      </div>

    </div>
  </main>

  <!-- ================= FOOTER (EXACT STITCH) ================= -->
  <footer class="w-full bg-surface-container-lowest py-space-lg border-t border-surface-variant">
    <div class="w-full px-margin-desktop flex flex-col md:flex-row items-center justify-between gap-space-md font-body-sm text-body-sm text-on-surface-variant">
      <div class="flex items-center gap-space-sm">
        <span class="font-label-md text-label-md text-on-surface font-bold">Thrissur District Cooperative Bank Ltd.</span>
        <span>•</span>
        <span>Autonomous Quantum Computing Optimization Cluster (Simulated Rig)</span>
      </div>
      <div class="flex items-center gap-space-lg font-label-sm text-label-sm">
        <span class="text-on-surface-variant">Algorithm: QAOA 3-Step Ising Hamiltonian</span>
        <span class="text-on-surface-variant">State: Coherent Co-processor Active</span>
        <span>© 2026 PS05 Presentation System</span>
      </div>
    </div>
  </footer>

  <!-- ================= SCRIPT & DYNAMIC WIRING ================= -->
  <script>
    let appData = null;
    let isRunning = false;
    let tourStep = 0;

    // 1. Tab Switching System
    function switchTab(tabId) {{
      document.querySelectorAll('.tab-pane').forEach(el => el.classList.remove('active'));
      const target = document.getElementById(tabId);
      if (target) {{
        target.classList.add('active');
      }}

      // Update Nav Buttons
      const navIds = ['screen-portfolio', 'screen-quantum', 'screen-results', 'screen-math'];
      navIds.forEach(id => {{
        const btn = document.getElementById('nav-' + id);
        if (btn) {{
          if (id === tabId) {{
            btn.className = "px-space-md py-space-sm rounded-full font-label-md text-label-md bg-surface-container-high text-primary font-bold transition-all";
          }} else {{
            btn.className = "px-space-md py-space-sm rounded-full font-label-md text-label-md text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high transition-all";
          }}
        }}
      }});

      window.scrollTo({{ top: 0, behavior: 'smooth' }});
    }}

    // Intercept all data-path links from original Stitch screens
    document.addEventListener('click', function(e) {{
      const link = e.target.closest('[data-path]');
      if (link) {{
        e.preventDefault();
        const path = link.getAttribute('data-path');
        if (path === 'portfolio-input-and-matrix') switchTab('screen-portfolio');
        else if (path === 'quantum-execution') {{
          switchTab('screen-quantum');
          triggerOptimization();
        }}
        else if (path === 'optimization-results') switchTab('screen-results');
        else if (path === 'mathematical-intuition-under-the-hood') switchTab('screen-math');
      }}
    }});

    // 2. Fetch Initial Portfolio
    async function loadPortfolio() {{
      try {{
        const res = await fetch('/api/portfolio');
        const json = await res.json();
        if (json.status === 'success') {{
          appData = json.data;
          renderResults(appData);
        }}
      }} catch (err) {{
        console.error('Failed to load initial portfolio:', err);
      }}
    }}

    // 3. Trigger Quantum Optimization
    async function triggerOptimization() {{
      if (isRunning) return;
      isRunning = true;
      switchTab('screen-quantum');

      const badge = document.getElementById('qpuStatusBadge');
      if (badge) badge.innerText = 'QPU Sim: COBYLA Optimizing...';

      try {{
        const res = await fetch('/api/solve', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ lambda: 1.0, mu: 3.0, reps: 3 }})
        }});
        const json = await res.json();
        if (json.status === 'success') {{
          appData = json.data;
          renderResults(appData);
        }}
      }} catch (err) {{
        console.error('QAOA execution error:', err);
      }} finally {{
        isRunning = false;
        if (badge) badge.innerText = 'QPU Sim: QAOA (p=3) Online';
      }}
    }}

    // 4. Render Dynamic Elements
    function renderResults(data) {{
      if (!data) return;

      // Update Screen 2 Cost Metric
      const costEl = document.getElementById('metric-cost');
      if (costEl && data.quantum) {{
        costEl.innerText = data.quantum.objective.toFixed(2) + ' eV';
      }}

      // Update Screen 3 Bento Grid & KPIs
      if (data.quantum) {{
        const selected = data.quantum.selected_loans || [];
        const totalProfit = data.quantum.total_profit;
        const totalRisk = data.quantum.total_risk;
        
        // Find KPI containers if present and update text
        const profitHeaders = document.querySelectorAll('#screen-results .font-headline-xl');
        if (profitHeaders.length >= 3) {{
          profitHeaders[1].innerText = '₹' + (totalProfit).toFixed(2);
          profitHeaders[2].innerText = totalRisk.toFixed(2);
        }}
      }}

      // Re-render sample distribution if element exists
      const chartContainer = document.getElementById('sampleDistributionList');
      if (chartContainer && data.samples) {{
        chartContainer.innerHTML = '';
        const topSamples = data.samples.slice(0, 8);
        topSamples.forEach(s => {{
          const isOptimal = s.bitstring === data.quantum.bitstring;
          const row = document.createElement('div');
          row.className = 'flex items-center justify-between p-space-xs rounded bg-surface-container font-label-sm text-label-sm';
          row.innerHTML = `
            <div class="flex items-center gap-space-xs">
              <span class="font-mono font-bold ${{isOptimal ? 'text-primary' : 'text-on-surface'}}">${{s.bitstring}}</span>
              <span class="px-1.5 py-0.5 rounded ${{s.is_valid ? 'bg-primary-container text-on-primary-container' : 'bg-error-container text-on-error-container'}} text-[9px] font-bold">
                ${{s.is_valid ? 'k=3 Valid' : 'k=' + s.k + ' Penalty'}}
              </span>
            </div>
            <div class="flex items-center gap-space-sm">
              <span class="font-mono text-tertiary">E = ${{s.objective.toFixed(1)}}</span>
              <div class="w-16 bg-surface-container-high h-2 rounded-full overflow-hidden">
                <div class="${{isOptimal ? 'bg-primary' : 'bg-secondary'}} h-full" style="width: ${{Math.min(100, Math.max(5, s.probability * 100))}}%"></div>
              </div>
              <span class="font-mono text-right w-10">${{(s.probability * 100).toFixed(1)}}%</span>
            </div>
          `;
          chartContainer.appendChild(row);
        }});
      }}
    }}

    // 5. Interactive Sensitivity Slider for Screen 4
    async function updateSensitivity(mu, lam) {{
      try {{
        const res = await fetch('/api/solve', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ lambda: parseFloat(lam), mu: parseFloat(mu), reps: 3 }})
        }});
        const json = await res.json();
        if (json.status === 'success') {{
          renderResults(json.data);
        }}
      }} catch (err) {{
        console.error(err);
      }}
    }}

    // 6. Quick Demo Tour
    function quickDemoTour() {{
      const steps = ['screen-portfolio', 'screen-quantum', 'screen-results', 'screen-math'];
      tourStep = (tourStep + 1) % steps.length;
      switchTab(steps[tourStep]);
    }}

    // 7. Table Inspector Helper
    function toggleInspector(loanId) {{
      const rows = document.querySelectorAll('#loan-table tbody tr');
      rows.forEach(r => r.classList.remove('bg-surface-container-high'));
      if (window.event && window.event.currentTarget) {{
        window.event.currentTarget.classList.add('bg-surface-container-high');
      }}
    }}

    // 8. Fiduciary Ledger Export
    function exportAuditLedger() {{
      if (!appData) return;
      const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(appData, null, 2));
      const downloadAnchor = document.createElement('a');
      downloadAnchor.setAttribute("href", dataStr);
      downloadAnchor.setAttribute("download", "Thrissur_Bank_Quantum_Audit_PS05.json");
      document.body.appendChild(downloadAnchor);
      downloadAnchor.click();
      downloadAnchor.remove();
    }}

    // Initialize on page load
    window.addEventListener('DOMContentLoaded', loadPortfolio);
  </script>
</body>
</html>"""

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(template)

print('templates/index.html written successfully!')
print(f'Total characters: {len(template)}')
