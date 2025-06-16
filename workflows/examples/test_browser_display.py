#!/usr/bin/env python3
"""Test script to verify browser display functionality in devcontainer."""

import asyncio
import time
from browser_use import Browser
from playwright.async_api import async_playwright


async def test_browser_display():
    """Test browser display with a simple visual demo."""
    print("🧪 Testing browser display functionality...")
    print("📺 Make sure to open http://localhost:6080/vnc.html in your browser to see the action!")
    print()
    
    # Give user time to open the VNC viewer
    print("⏳ Waiting 5 seconds for you to open the VNC viewer...")
    await asyncio.sleep(5)
    
    async with async_playwright() as playwright:
        print("🚀 Launching browser...")
        browser_instance = await playwright.chromium.launch(
            headless=False,  # Show the browser
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security'
            ]
        )
        
        print("📄 Creating new page...")
        page = await browser_instance.new_page()
        
        # Visit a simple test page
        print("🌐 Navigating to example.com...")
        await page.goto("https://example.com")
        await asyncio.sleep(2)
        
        # Highlight the main heading
        print("✨ Highlighting the main heading...")
        await page.evaluate("""
            const heading = document.querySelector('h1');
            if (heading) {
                heading.style.border = '3px solid red';
                heading.style.backgroundColor = 'yellow';
                heading.style.padding = '10px';
                heading.style.animation = 'pulse 1s infinite';
                
                // Add pulsing animation
                const style = document.createElement('style');
                style.textContent = `
                    @keyframes pulse {
                        0% { transform: scale(1); }
                        50% { transform: scale(1.05); }
                        100% { transform: scale(1); }
                    }
                `;
                document.head.appendChild(style);
            }
        """)
        await asyncio.sleep(3)
        
        # Navigate to another page
        print("🔍 Navigating to Google...")
        await page.goto("https://www.google.com")
        await asyncio.sleep(2)
        
        # Type in search box with Japanese text
        print("⌨️  Typing in search box...")
        search_box = await page.wait_for_selector('textarea[name="q"], input[name="q"]')
        await search_box.click()
        await search_box.type("こんにちは！devcontainerから日本語テスト", delay=100)
        await asyncio.sleep(2)
        
        # Take a screenshot
        print("📸 Taking screenshot...")
        await page.screenshot(path="/workspace/workflows/examples/browser_test_screenshot.png")
        print("💾 Screenshot saved to: browser_test_screenshot.png")
        
        print("⏳ Keeping browser open for 5 more seconds...")
        await asyncio.sleep(5)
        
        print("🏁 Closing browser...")
        await browser_instance.close()
    
    print()
    print("✅ Browser display test completed successfully!")
    print("🎉 If you saw the browser in the VNC viewer, everything is working correctly!")


async def test_browser_use_agent():
    """Test browser-use agent functionality."""
    print("\n" + "="*60)
    print("🤖 Testing browser-use agent...")
    print("="*60 + "\n")
    
    print("⏳ Waiting 3 seconds...")
    await asyncio.sleep(3)
    
    browser = Browser()
    try:
        print("🚀 Launching browser agent...")
        result = await browser.run(
            "Go to example.com and tell me what the main heading says",
            headless=False  # Show the browser
        )
        print(f"\n📊 Agent result: {result}")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await browser.close()
    
    print("\n✅ Browser-use agent test completed!")


async def main():
    """Run all browser tests."""
    print("🎯 Browser Display Test Suite")
    print("="*60)
    print("This will test if the browser display is working properly in the devcontainer.")
    print("Make sure you have opened http://localhost:6080/vnc.html in your browser!")
    print("="*60 + "\n")
    
    # Run basic browser test
    await test_browser_display()
    
    # Skip interactive prompt in automated environment
    print("\n" + "="*60)
    print("Skipping browser-use agent test for now.")
    # response = input("Would you like to test the browser-use agent as well? (y/n): ")
    # if response.lower() == 'y':
    #     await test_browser_use_agent()
    
    print("\n🎉 All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())