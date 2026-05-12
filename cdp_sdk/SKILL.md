---
name: cdp-browse
description: >
  Browse and interact with web pages using the local Chrome browser via CDP-Bridge.
  Use this skill whenever the user wants to open a URL, read a webpage, extract content,
  click elements, scroll pages, fill forms, scrape data, or perform any browser automation
  through their local Chrome. Trigger on phrases like "open this URL", "check this page",
  "what's on this website", "go to", "browse", "scrape", "extract from page", "click on",
  "scroll down", "看看这个网页", "帮我打开", "抓取", or anytime a URL is provided and
  the user wants to see or interact with its content.
---

# CDP Browse — Local Chrome Browser Control

Control the user's local Chrome browser through CDP-Bridge to browse web pages, extract
content, and interact with elements. The browser shares the user's login sessions and cookies,
so authenticated pages (GitLab, Jira, internal tools) work without extra auth.

**Follow the user's language** — Chinese prompt, Chinese response; English prompt, English response.

## Important: How to Run Python

**ALWAYS** run Python code via `uvx --from cdp-browse python`, NOT bare `python`. This ensures
`cdp_sdk` is available regardless of the agent's Python environment.

```bash
uvx --from cdp-browse python -c "
from cdp_sdk import CDPClient, Page
# your code here
"
```

If the code is long, write it to a temp file first:

```bash
uvx --from cdp-browse python /tmp/browse.py
```

## Core Workflow

**navigate -> wait -> interact -> extract**

### 1. Navigate

```python
# Simple navigation with fixed wait
page.navigate(url)

# Navigate + wait for element (preferred — no blind sleep)
page.navigate(url, wait_for_selector=".commit-row-message")

# Navigate + wait for JS condition
page.navigate(url, wait_for_js="document.querySelectorAll('.item').length > 0", timeout=10)
```

### 2. Wait

```python
page.wait_for_selector("h1", timeout=10)
page.wait_for_js("document.readyState === 'complete'", timeout=10)
```

### 3. Interact

```python
page.click("button.submit")
page.scroll_by(0, 3000)
page.scroll_to_bottom()
```

### 4. Extract

```python
page.extract_text()                    # full page (default: body)
page.extract_text("h1")                # specific element
page.extract_html(".content")          # innerHTML
page.query_all("a")                    # all matching elements' text
page.query_all("a", "a => a.href")     # custom transform
page.title                             # page title
page.url                               # current URL
```

### 5. Raw JS (escape hatch)

```python
client.execute_js("document.title")
client.execute_js("document.querySelectorAll('.row').length")
```

## Common Templates

### Read a page

```bash
uvx --from cdp-browse python -c "
from cdp_sdk import CDPClient, Page
import time

client = CDPClient()
client.find_session()
page = Page(client)
page.navigate('THE_URL', wait_for_js=\"document.readyState === 'complete'\", timeout=10)
time.sleep(2)
print(page.extract_text())
"
```

### Scrape a list

```python
items = page.query_all(".list-item", """el => ({
    title: el.querySelector('.title')?.textContent.trim(),
    link: el.querySelector('a')?.href,
    date: el.querySelector('.date')?.textContent.trim()
})""")
```

### Scroll-to-load

```python
for _ in range(5):
    page.scroll_to_bottom()
    time.sleep(1)
all_items = page.query_all(".item")
```

### Multi-step flow

```python
page.navigate(url, wait_for_selector="button.next")
page.click("button.next")
page.wait_for_selector(".results")
print(page.extract_text(".results"))
```

## Troubleshooting

1. `client.check_alive()` — True if CDP-Bridge service is running
2. `client.get_sessions()` — should return non-empty list
3. System proxy must bypass `localhost` and `127.0.0.1`
4. Chrome extension icon should show green "Connected"

## Constraints

- Never restart Chrome or use `--remote-debugging-port`
- Never kill browser processes
- Never create new Chrome profiles
- Uses `window.location.href` for navigation to preserve login state
- For long pages, use `scroll_to_bottom()` in a loop before extracting
