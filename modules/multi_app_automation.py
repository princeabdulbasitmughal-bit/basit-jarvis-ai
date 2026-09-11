"""
============================================================
MODULE 7: MULTI-APP AUTOMATION (Browser & Office win32com)
============================================================
Automates:
1. Web Browsers (Playwright / webbrowser / Google / YouTube searches)
2. Microsoft Office Apps (Word, Excel, PowerPoint via win32com)
"""

import sys
import logging
import webbrowser
import urllib.parse
from typing import Optional, List, Dict, Any

logger = logging.getLogger("Jarvis.MultiApp")


class MultiAppAutomation:
    def __init__(self):
        self._has_win32com = False
        self._init_win32()

    def _init_win32(self):
        if sys.platform == "win32":
            try:
                import win32com.client
                self._has_win32com = True
                logger.info("win32com available for Office automation.")
            except ImportError:
                logger.warning("win32com not installed. Install pywin32 for Office automation.")

    # ---------------------------------------------------------
    # 1. BROWSER AUTOMATION
    # ---------------------------------------------------------
    def open_url(self, url: str) -> bool:
        """Opens URL in default web browser."""
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        logger.info(f"Opening URL: {url}")
        return webbrowser.open(url)

    def web_search(self, query: str, engine: str = "google") -> bool:
        """Searches query on chosen search engine."""
        encoded = urllib.parse.quote_plus(query)
        engines = {
            "google": f"https://www.google.com/search?q={encoded}",
            "youtube": f"https://www.youtube.com/results?search_query={encoded}",
            "github": f"https://github.com/search?q={encoded}",
            "bing": f"https://www.bing.com/search?q={encoded}",
            "wikipedia": f"https://en.wikipedia.org/wiki/Special:Search?search={encoded}"
        }
        target_url = engines.get(engine.lower(), engines["google"])
        logger.info(f"Web search ({engine}): '{query}' -> {target_url}")
        return webbrowser.open(target_url)

    def scrape_webpage(self, url: str) -> Optional[str]:
        """Scrapes text content of a page using Playwright or requests."""
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, timeout=10000)
                text = page.inner_text("body")
                browser.close()
                return text[:4000]  # Return first 4000 characters
        except Exception as e:
            logger.debug(f"Playwright scrape error: {e}. Falling back to requests.")
            try:
                import requests
                from bs4 import BeautifulSoup
                r = requests.get(url, timeout=5)
                soup = BeautifulSoup(r.text, "html.parser")
                return soup.get_text()[:4000]
            except Exception as e2:
                logger.error(f"Scrape fallback failed: {e2}")
                return None

    # ---------------------------------------------------------
    # 2. MICROSOFT OFFICE AUTOMATION (win32com)
    # ---------------------------------------------------------
    def create_word_document(self, content: str, title: str = "Document") -> bool:
        """Creates a new MS Word document and inserts content."""
        if not self._has_win32com:
            logger.warning("win32com not available. Cannot automate MS Word.")
            return False

        try:
            import win32com.client
            word = win32com.client.Dispatch("Word.Application")
            word.Visible = True
            doc = word.Documents.Add()
            selection = word.Selection
            selection.TypeText(f"{title}\n\n")
            selection.TypeText(content)
            logger.info("MS Word document created successfully.")
            return True
        except Exception as e:
            logger.error(f"Error creating Word document: {e}")
            return False

    def create_excel_sheet(self, headers: List[str], rows: List[List[Any]]) -> bool:
        """Creates an Excel spreadsheet and fills in rows."""
        if not self._has_win32com:
            logger.warning("win32com not available. Cannot automate Excel.")
            return False

        try:
            import win32com.client
            excel = win32com.client.Dispatch("Excel.Application")
            excel.Visible = True
            wb = excel.Workbooks.Add()
            ws = wb.Worksheets(1)

            # Write headers
            for col_idx, header in enumerate(headers, start=1):
                ws.Cells(1, col_idx).Value = str(header)

            # Write rows
            for row_idx, row in enumerate(rows, start=2):
                for col_idx, val in enumerate(row, start=1):
                    ws.Cells(row_idx, col_idx).Value = str(val)

            logger.info("MS Excel sheet created successfully.")
            return True
        except Exception as e:
            logger.error(f"Error creating Excel sheet: {e}")
            return False
