import requests
from bs4 import BeautifulSoup

url = 'https://www.daraz.pk/catalog/?page=1&q=laptop'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print("Testing Daraz scraper...")
print(f"URL: {url}\n")

try:
    r = requests.get(url, headers=headers, timeout=15)
    print(f"Status Code: {r.status_code}")

    soup = BeautifulSoup(r.content, 'html.parser')
    print(f"Page Title: {soup.title.string if soup.title else 'No title'}\n")

    # Test different selectors
    selectors = [
        ('div', {'data-qa-locator': 'product-item'}),
        ('div', {'class': 'gridItem--Yd0sa'}),
        ('div', {'class': 'Bm3ON'}),
        ('a', {'class': 'mainLink'}),
    ]

    for tag, attrs in selectors:
        items = soup.find_all(tag, attrs)
        print(f"Selector: {tag} {attrs}")
        print(f"Items found: {len(items)}")
        if items:
            print(f"First item preview: {str(items[0])[:200]}...")
        print()

    # Check if page has anti-bot protection
    if 'captcha' in r.text.lower() or 'robot' in r.text.lower():
        print("⚠️ WARNING: Page may have anti-bot protection!")

    # Save HTML for inspection
    with open('page_source.html', 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    print("✅ Page source saved to page_source.html")

except Exception as e:
    print(f"❌ Error: {e}")
