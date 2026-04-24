import re
import os

log_path = r'C:\Users\hp\.gemini\antigravity\brain\93322571-6d11-46e3-8ac4-95618fa707be\.system_generated\logs\overview.txt'
with open(log_path, 'r', encoding='utf-8') as f:
    text = f.read()

style_matches = re.findall(r'<style>(.*?)</style>', text, re.DOTALL)
if style_matches:
    css_content = style_matches[-1]
    auth_css = """
/* --- Forms & Auth --- */
.auth-container { display: flex; align-items: center; justify-content: center; min-height: 70vh; padding: 40px 20px; }
.auth-card { width: 100%; max-width: 400px; background: rgba(255, 255, 255, 0.8); backdrop-filter: blur(20px); padding: 40px; border-radius: 12px; box-shadow: var(--shadow-book); border: 1px solid rgba(255, 255, 255, 0.5); }
.form-group { margin-bottom: 20px; }
.form-group label { display: block; margin-bottom: 8px; font-weight: 500; font-family: var(--font-body); font-size: 14px; }
.form-group input:not([type="checkbox"]), .form-group select, .form-group textarea { width: 100%; padding: 12px 15px; border: 1px solid #E5E7EB; border-radius: 8px; font-family: var(--font-body); font-size: 15px; background: var(--ivory); }
"""
    with open(r'c:\Users\hp\.gemini\antigravity\scratch\static\css\style.css', 'w', encoding='utf-8') as f:
        f.write(css_content.strip() + '\n' + auth_css)

script_matches = re.findall(r'<script>(.*?)</script>', text, re.DOTALL)
if script_matches:
    js_content = script_matches[-1]
    with open(r'c:\Users\hp\.gemini\antigravity\scratch\static\js\main.js', 'w', encoding='utf-8') as f:
        f.write(js_content.strip())
