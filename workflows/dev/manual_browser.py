#!/usr/bin/env python3
"""
Manual browser launcher for VNC inspection
"""
import asyncio
from playwright.async_api import async_playwright
import signal
import sys

class BrowserManager:
    def __init__(self):
        self.browser = None
        self.playwright = None
        
    async def start(self):
        print('🌐 VNCブラウザを起動中...')
        print('📍 http://localhost:6080/vnc.html を開いてブラウザを確認してください')
        
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=False,
            args=[
                '--disable-web-security', 
                '--allow-running-insecure-content',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        context = await self.browser.new_context(
            viewport={'width': 1280, 'height': 720}
        )
        page = await context.new_page()
        
        print('✅ ブラウザが起動しました')
        print('🔗 en-ambi.com に移動します...')
        
        await page.goto('https://en-ambi.com/company/')
        
        print('👆 VNCビューアーでログインし、サイト構造を確認してください')
        print('⏸️  ブラウザは起きっぱなしです。Ctrl+C で終了してください')
        
        return page
    
    async def stop(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        print('🛑 ブラウザを終了しました')

async def main():
    manager = BrowserManager()
    
    def signal_handler(signum, frame):
        print('\n🛑 終了シグナルを受信しました...')
        asyncio.create_task(manager.stop())
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        page = await manager.start()
        
        # Keep the browser running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print('\n🛑 キーボード割り込みで終了...')
    except Exception as e:
        print(f'❌ エラー: {e}')
    finally:
        await manager.stop()

if __name__ == '__main__':
    asyncio.run(main())