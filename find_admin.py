
with open(r'e:\\picture\\app\\main\\routes.py', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        if "@bp.route('/admin')" in line or "def admin(" in line:
            print(f"{i}: {line.strip()}")
