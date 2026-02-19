# Free Browser Automation Alternatives

## Overview

You have **3 completely FREE** options for browser automation (no Brave API needed):

| Tool           | Cost | Speed  | Ease   | Best For           |
| -------------- | ---- | ------ | ------ | ------------------ |
| **Selenium**   | FREE | Medium | Easy   | General automation |
| **Playwright** | FREE | Fast   | Medium | Modern web apps    |
| **Puppeteer**  | FREE | Fast   | Medium | Chrome-specific    |

## Option 1: Selenium (Already Using!)

### What You're Already Using

Pixie already uses Selenium for WhatsApp! Same tool works for ANY website.

### Pros

- ✅ **100% FREE**
- ✅ **Most popular** - Huge community
- ✅ **Works with all browsers** - Chrome, Firefox, Safari, Edge
- ✅ **Easy to learn**
- ✅ **Tons of tutorials**

### Cons

- ❌ Slower than Playwright/Puppeteer
- ❌ More verbose code

### What It Can Do

- Automate ANY website
- Fill forms
- Click buttons
- Scrape data
- Take screenshots
- Handle JavaScript
- Download files
- Upload files

### Already Installed!

```bash
# Already in requirements.txt
selenium>=4.15.0
webdriver-manager>=4.0.0
```

### Example - Automate Google Search

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

driver = webdriver.Chrome()
driver.get("https://google.com")

search_box = driver.find_element(By.NAME, "q")
search_box.send_keys("Python tutorials")
search_box.send_keys(Keys.ENTER)

# Get results
results = driver.find_elements(By.CSS_SELECTOR, "h3")
for result in results[:5]:
    print(result.text)

driver.quit()
```

---

## Option 2: Playwright (Recommended for Modern Apps)

### What Is It?

Microsoft's modern browser automation tool. Faster and more reliable than Selenium.

### Pros

- ✅ **100% FREE**
- ✅ **Faster** than Selenium
- ✅ **Better for modern web apps**
- ✅ **Auto-waits** for elements
- ✅ **Built-in screenshots/videos**
- ✅ **Network interception**

### Cons

- ❌ Newer (less tutorials)
- ❌ Slightly more complex

### Install

```bash
pip install playwright
playwright install chromium
```

### Example - Same Google Search

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://google.com")

    page.fill('input[name="q"]', "Python tutorials")
    page.press('input[name="q"]', "Enter")

    # Get results
    results = page.query_selector_all("h3")
    for result in results[:5]:
        print(result.text_content())

    browser.close()
```

### Why Playwright?

- **Faster** - 2-3x faster than Selenium
- **More reliable** - Auto-waits for elements
- **Better API** - Cleaner, more intuitive code
- **Modern** - Built for modern web apps

---

## Option 3: Puppeteer (Chrome-Specific)

### What Is It?

Google's official Chrome automation tool (Node.js, but has Python version).

### Pros

- ✅ **100% FREE**
- ✅ **Very fast**
- ✅ **Official Google tool**
- ✅ **Great for Chrome/Chromium**

### Cons

- ❌ Chrome/Chromium only
- ❌ Originally Node.js (Python version exists)

### Install (Python version)

```bash
pip install pyppeteer
```

### Example

```python
import asyncio
from pyppeteer import launch

async def main():
    browser = await launch()
    page = await browser.newPage()
    await page.goto('https://google.com')

    await page.type('input[name="q"]', 'Python tutorials')
    await page.keyboard.press('Enter')

    await page.waitForSelector('h3')
    results = await page.querySelectorAll('h3')

    for result in results[:5]:
        text = await page.evaluate('(element) => element.textContent', result)
        print(text)

    await browser.close()

asyncio.run(main())
```

---

## Comparison Table

| Feature              | Selenium | Playwright | Puppeteer   |
| -------------------- | -------- | ---------- | ----------- |
| **Cost**             | FREE     | FREE       | FREE        |
| **Speed**            | Medium   | Fast       | Fast        |
| **Browsers**         | All      | All        | Chrome only |
| **Learning Curve**   | Easy     | Medium     | Medium      |
| **Community**        | Huge     | Growing    | Large       |
| **Auto-wait**        | No       | Yes        | Yes         |
| **Screenshots**      | Yes      | Yes        | Yes         |
| **Network Control**  | Limited  | Yes        | Yes         |
| **Mobile Emulation** | Yes      | Yes        | Yes         |

---

## Which Should You Use?

### Use Selenium (Current) If:

- ✅ You want the easiest option
- ✅ You need maximum compatibility
- ✅ You want tons of tutorials
- ✅ You're already using it (WhatsApp)

### Use Playwright If:

- ✅ You need speed
- ✅ You're automating modern web apps
- ✅ You want better reliability
- ✅ You need network interception

### Use Puppeteer If:

- ✅ You only need Chrome
- ✅ You want Google's official tool
- ✅ You're comfortable with async code

---

## Real-World Examples

### 1. Automate LinkedIn

```python
# Selenium
driver.get("https://linkedin.com")
driver.find_element(By.ID, "username").send_keys("email")
driver.find_element(By.ID, "password").send_keys("pass")
driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
```

### 2. Scrape Amazon Prices

```python
# Playwright
page.goto("https://amazon.com/product")
price = page.text_content(".a-price-whole")
print(f"Price: ${price}")
```

### 3. Auto-Fill Forms

```python
# Selenium
driver.find_element(By.NAME, "name").send_keys("John Doe")
driver.find_element(By.NAME, "email").send_keys("john@email.com")
driver.find_element(By.NAME, "phone").send_keys("1234567890")
driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
```

### 4. Take Screenshots

```python
# Selenium
driver.get("https://example.com")
driver.save_screenshot("screenshot.png")

# Playwright
page.goto("https://example.com")
page.screenshot(path="screenshot.png")
```

---

## Pixie Integration

Pixie already uses Selenium! You can extend it to automate ANY website:

```
"Scrape product prices from Amazon"
"Auto-fill this job application"
"Take a screenshot of this website"
"Monitor this page and alert me if it changes"
"Auto-post to Facebook"
"Download all images from this page"
```

---

## Installation

### Selenium (Already Installed!)

```bash
pip install selenium webdriver-manager
```

### Playwright (Recommended Upgrade)

```bash
pip install playwright
playwright install chromium
```

### Puppeteer (Python version)

```bash
pip install pyppeteer
```

---

## Recommendation

**Stick with Selenium** for now - it's already working great for WhatsApp!

**Upgrade to Playwright** if you need:

- Faster automation
- Modern web apps
- Better reliability

Both are **100% FREE** and work without any API!

---

## No Brave API Needed!

All three options are:

- ✅ **Completely FREE**
- ✅ **No API keys**
- ✅ **No subscriptions**
- ✅ **Open source**
- ✅ **Work offline**

You already have everything you need with Selenium! 🚀
