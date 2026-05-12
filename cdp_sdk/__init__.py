"""
cdp_sdk — Chrome browser control SDK via CDP-Bridge

通过 CDP-Bridge 控制 Chrome 浏览器，复用登录态，适用于 Web 爬虫、
自动化测试、数据采集等场景。

快速开始::

    from cdp_sdk import CDPClient, Page

    client = CDPClient()
    client.find_session()

    page = Page(client)
    page.navigate("https://example.com", wait_for_selector="h1")
    print(page.extract_text("h1"))
"""
from cdp_sdk.client import CDPClient, CDPError
from cdp_sdk.page import Page

__all__ = ["CDPClient", "CDPError", "Page"]
