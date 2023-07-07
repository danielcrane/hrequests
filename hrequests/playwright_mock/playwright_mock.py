from async_class import AsyncObject
from playwright.async_api import async_playwright
from hrequests.playwright_mock import context, ProxyManager, Faker



class PlaywrightMock(AsyncObject):
    # patch of botright to use webkit instead of ff
    async def __ainit__(self, headless=False, scroll_into_view=True):
        # setting values
        self.scroll_into_view = scroll_into_view
        # starting Playwright
        self.playwright = await async_playwright().start()
        # launching chromium
        self.main_browser = await self.launch_browser(
            client=self.playwright,
            headless=headless
        )
    
    args = [
        '--disable-blink-features=AutomationControlled',
        '--disable-web-security',
        '--disable-site-isolation-trials',
        '--disable-features=CrossSiteDocumentBlockingIfIsolating,'
            'CrossSiteDocumentBlockingAlways,'
            'IsolateOrigins,'
            'site-per-process,'
            'SharedArrayBuffer',
    ]
    
    @staticmethod
    async def launch_browser(client, headless=False):
        return await client.chromium.launch(
            headless=headless,
            args=PlaywrightMock.args + (['--headless=new'] if headless else []),
        )
    
    async def stop(self):
        await self.main_browser.close()
        await self.playwright.stop()

    async def new_context(self, browser_name: str, proxy=None, **launch_args):
        # calling proxyManager and faker
        _proxy = await ProxyManager(self, proxy)
        _faker = await Faker(self, _proxy, browser_name)
        # create context with human emulation
        _browser = await context.new_context(
            self,
            _proxy,
            _faker,
            bypass_csp=True,
            **launch_args
        )
        _browser.proxy = _proxy
        _browser.faker = _faker

        return _browser