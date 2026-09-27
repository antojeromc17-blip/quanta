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
    inner = content[start_inner:end_inner]
    
    # Strip any top-level <div class="flex flex-col w-full"> wrapper if present
    inner = inner.strip()
    if inner.startswith('<div class="flex flex-col w-full">') and inner.endswith('</div>'):
        inner = inner[len('<div class="flex flex-col w-full">'):-len('</div>')].strip()
    return inner

# Read all 4 screen mains
s1 = extract_main_inner('screen_1_Portfolio_Input_and_Matrix.html')
s2 = extract_main_inner('screen_2_Quantum_Execution.html')
s3 = extract_main_inner('screen_3_Optimization_Results.html')
s4 = extract_main_inner('screen_4_Mathematical_Intuition_Under_the_Hood.html')

# Clean glassmorphism & transparency
s1 = clean_glass_and_transparency(s1)
s2 = clean_glass_and_transparency(s2)
s3 = clean_glass_and_transparency(s3)
s4 = clean_glass_and_transparency(s4)

print('Extracted & cleaned successfully!')
print(f'S1: {len(s1)} chars, S2: {len(s2)} chars, S3: {len(s3)} chars, S4: {len(s4)} chars')
