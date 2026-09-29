"""Virtual Cursor Controller for Realistic Human-like Mouse Interactions."""

import math
import time

class VirtualCursor:
    """Animates realistic cursor movement, hovers, and clicks."""

    def __init__(self, page):
        self.page = page
        self.current_x = 100
        self.current_y = 100

    def move_to(self, selector: str, steps: int = 25, delay_ms: int = 15):
        """Moves virtual cursor to element using smooth curved interpolation."""
        box = self.page.locator(selector).bounding_box()
        if not box:
            return
        target_x = box["x"] + box["width"] / 2
        target_y = box["y"] + box["height"] / 2

        # Show cursor
        self.page.evaluate("document.getElementById('virtualCursor').style.display = 'block'")

        start_x, start_y = self.current_x, self.current_y
        for i in range(1, steps + 1):
            t = i / steps
            # Smooth ease-in-out
            ease = t * t * (3.0 - 2.0 * t)
            x = start_x + (target_x - start_x) * ease
            y = start_y + (target_y - start_y) * ease
            self.page.evaluate(f"""
                document.getElementById('virtualCursor').style.left = '{x}px';
                document.getElementById('virtualCursor').style.top = '{y}px';
            """)
            self.page.wait_for_timeout(delay_ms)

        self.current_x, self.current_y = target_x, target_y

    def click(self, selector: str):
        """Performs a visual click with a subtle scale ripple effect."""
        self.move_to(selector)
        # Click animation
        self.page.evaluate("""
            const c = document.getElementById('virtualCursor');
            c.style.transform = 'translate(-4px, -4px) scale(0.85)';
            setTimeout(() => { c.style.transform = 'translate(-4px, -4px) scale(1.0)'; }, 150);
        """)
        self.page.wait_for_timeout(150)
        self.page.locator(selector).click()
        self.page.wait_for_timeout(300)
