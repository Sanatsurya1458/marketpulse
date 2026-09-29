"""Virtual Camera and Highlight Control for Product Demo Recording."""

from typing import Dict, Any, Optional

class VirtualCamera:
    """Manages viewport transforms, pan/zoom transitions, and spotlight overlays."""

    def __init__(self, page):
        self.page = page

    def focus(self, selector: str, zoom: float = 1.25, duration_ms: int = 800):
        """Smoothly pans and zooms the viewport to focus on a target UI component."""
        js_code = f"""
        (function() {{
            const el = document.querySelector("{selector}");
            if (!el) return;
            const rect = el.getBoundingClientRect();
            const centerX = rect.left + rect.width / 2;
            const centerY = rect.top + rect.height / 2;
            
            // Apply scale and transform origin smoothly
            document.body.style.transition = "transform {duration_ms}ms cubic-bezier(0.25, 1, 0.5, 1)";
            document.body.style.transformOrigin = `${{centerX}}px ${{centerY}}px`;
            document.body.style.transform = "scale({zoom})";
        }})();
        """
        self.page.evaluate(js_code)
        self.page.wait_for_timeout(duration_ms)

    def reset(self, duration_ms: int = 600):
        """Resets camera zoom to 1.0."""
        js_code = f"""
        (function() {{
            document.body.style.transition = "transform {duration_ms}ms cubic-bezier(0.25, 1, 0.5, 1)";
            document.body.style.transform = "scale(1.0)";
        }})();
        """
        self.page.evaluate(js_code)
        self.page.wait_for_timeout(duration_ms)

    def spotlight(self, selector: str):
        """Highlights the target element with a focused spotlight glow."""
        self.page.evaluate(f"highlightElement('{selector}')")

    def clear_spotlight(self):
        """Removes active spotlight effects."""
        self.page.evaluate("highlightElement(null)")
