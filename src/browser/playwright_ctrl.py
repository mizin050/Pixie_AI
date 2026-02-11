"""
Browser Control - Playwright automation for precise web interactions
"""
from playwright.sync_api import sync_playwright, Browser, Page, BrowserContext
from typing import Optional, List, Dict
import time


class BrowserController:
    """Control browser using Playwright"""
    
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        print("✓ Browser controller initialized")
    
    def launch(self, headless: bool = False) -> bool:
        """
        Launch browser
        
        Args:
            headless: Run in headless mode
        
        Returns:
            True if successful
        """
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=headless)
            self.context = self.browser.new_context()
            self.page = self.context.new_page()
            
            print(f"✓ Browser launched (headless={headless})")
            return True
        except Exception as e:
            print(f"❌ Failed to launch browser: {e}")
            return False
    
    def navigate(self, url: str) -> bool:
        """
        Navigate to URL
        
        Args:
            url: URL to navigate to
        
        Returns:
            True if successful
        """
        if not self.page:
            print("⚠ Browser not launched")
            return False
        
        try:
            # Add https:// if missing
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            self.page.goto(url, wait_until='domcontentloaded', timeout=30000)
            print(f"✓ Navigated to: {url}")
            return True
        except Exception as e:
            print(f"❌ Navigation failed: {e}")
            return False
    
    def click(self, selector: str, timeout: int = 5000) -> bool:
        """
        Click an element
        
        Args:
            selector: CSS selector
            timeout: Wait timeout in ms
        
        Returns:
            True if successful
        """
        if not self.page:
            return False
        
        try:
            self.page.click(selector, timeout=timeout)
            print(f"✓ Clicked: {selector}")
            return True
        except Exception as e:
            print(f"❌ Click failed: {e}")
            return False
    
    def type_text(self, selector: str, text: str, timeout: int = 5000) -> bool:
        """
        Type text into an input
        
        Args:
            selector: CSS selector
            text: Text to type
            timeout: Wait timeout in ms
        
        Returns:
            True if successful
        """
        if not self.page:
            return False
        
        try:
            self.page.fill(selector, text, timeout=timeout)
            print(f"✓ Typed into {selector}: {text[:50]}")
            return True
        except Exception as e:
            print(f"❌ Type failed: {e}")
            return False
    
    def press_key(self, key: str) -> bool:
        """
        Press a keyboard key
        
        Args:
            key: Key name (e.g., 'Enter', 'Escape')
        
        Returns:
            True if successful
        """
        if not self.page:
            return False
        
        try:
            self.page.keyboard.press(key)
            print(f"✓ Pressed: {key}")
            return True
        except Exception as e:
            print(f"❌ Key press failed: {e}")
            return False
    
    def get_text(self, selector: str) -> Optional[str]:
        """
        Get text content of an element
        
        Args:
            selector: CSS selector
        
        Returns:
            Text content or None
        """
        if not self.page:
            return None
        
        try:
            text = self.page.text_content(selector)
            return text
        except Exception as e:
            print(f"⚠ Get text failed: {e}")
            return None
    
    def get_url(self) -> Optional[str]:
        """Get current URL"""
        if not self.page:
            return None
        return self.page.url
    
    def get_title(self) -> Optional[str]:
        """Get page title"""
        if not self.page:
            return None
        return self.page.title()
    
    def screenshot(self, path: str = "screenshot.png") -> bool:
        """
        Take a screenshot
        
        Args:
            path: Save path
        
        Returns:
            True if successful
        """
        if not self.page:
            return False
        
        try:
            self.page.screenshot(path=path)
            print(f"✓ Screenshot saved: {path}")
            return True
        except Exception as e:
            print(f"❌ Screenshot failed: {e}")
            return False
    
    def wait_for_selector(self, selector: str, timeout: int = 5000) -> bool:
        """
        Wait for an element to appear
        
        Args:
            selector: CSS selector
            timeout: Wait timeout in ms
        
        Returns:
            True if found
        """
        if not self.page:
            return False
        
        try:
            self.page.wait_for_selector(selector, timeout=timeout)
            print(f"✓ Found: {selector}")
            return True
        except Exception as e:
            print(f"⚠ Element not found: {selector}")
            return False
    
    def is_visible(self, selector: str) -> bool:
        """Check if element is visible"""
        if not self.page:
            return False
        
        try:
            return self.page.is_visible(selector)
        except:
            return False
    
    def close(self):
        """Close browser"""
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            
            print("✓ Browser closed")
        except Exception as e:
            print(f"⚠ Error closing browser: {e}")


# Global instance
_browser_controller = None

def get_browser_controller() -> BrowserController:
    """Get or create global browser controller"""
    global _browser_controller
    if _browser_controller is None:
        _browser_controller = BrowserController()
    return _browser_controller


# Convenience functions
def launch_browser(headless: bool = False) -> bool:
    """Launch browser"""
    return get_browser_controller().launch(headless)


def navigate(url: str) -> bool:
    """Navigate to URL"""
    return get_browser_controller().navigate(url)


def click(selector: str) -> bool:
    """Click element"""
    return get_browser_controller().click(selector)


def type_text(selector: str, text: str) -> bool:
    """Type text"""
    return get_browser_controller().type_text(selector, text)
