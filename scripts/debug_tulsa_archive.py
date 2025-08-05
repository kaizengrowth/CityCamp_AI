#!/usr/bin/env python3
"""
Debug script to analyze the Tulsa Archive website structure
"""

import requests
from bs4 import BeautifulSoup

def debug_tulsa_archive():
    print("🔍 Debugging Tulsa Archive Website Structure")
    print("=" * 60)

    archive_url = "https://www.cityoftulsa.org/apps/TulsaCouncilArchive"

    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        print(f"📡 Fetching: {archive_url}")
        response = session.get(archive_url, timeout=30)
        response.raise_for_status()

        print(f"✅ Response received: {response.status_code}")
        print(f"📄 Content length: {len(response.content)} bytes")
        print(f"🔤 Content type: {response.headers.get('content-type', 'unknown')}")

        soup = BeautifulSoup(response.content, 'html.parser')

        # Check for various table structures
        print("\n🔍 Analyzing page structure...")

        # Look for tables
        tables = soup.find_all('table')
        print(f"📊 Found {len(tables)} tables")

        for i, table in enumerate(tables):
            print(f"\n📋 Table {i+1}:")
            rows = table.find_all('tr')
            print(f"  - Rows: {len(rows)}")

            if rows:
                # Show first few rows
                for j, row in enumerate(rows[:3]):
                    cells = row.find_all(['td', 'th'])
                    cell_texts = [cell.get_text(strip=True)[:50] for cell in cells]
                    print(f"    Row {j+1}: {cell_texts}")

        # Look for divs that might contain meetings
        meeting_divs = soup.find_all('div', {'class': lambda x: x and any(word in x.lower() for word in ['meeting', 'agenda', 'council'])})
        print(f"\n📋 Found {len(meeting_divs)} potential meeting divs")

        # Look for links
        links = soup.find_all('a', href=True)
        document_links = [link for link in links if 'COTDisplayDocument' in link.get('href', '')]
        print(f"🔗 Found {len(document_links)} document links")

        if document_links:
            print("\n📋 Sample document links:")
            for i, link in enumerate(document_links[:5]):
                print(f"  {i+1}. Text: {link.get_text(strip=True)[:50]}")
                print(f"     URL: {link.get('href')}")
                print()

        # Look for scripts that might load data dynamically
        scripts = soup.find_all('script')
        print(f"📜 Found {len(scripts)} script tags")

        # Check for forms or search interfaces
        forms = soup.find_all('form')
        print(f"📝 Found {len(forms)} forms")

        # Look for select dropdowns
        selects = soup.find_all('select')
        print(f"📋 Found {len(selects)} select dropdowns")

        for i, select in enumerate(selects):
            print(f"\nSelect {i+1}: {select.get('name', 'unnamed')}")
            options = select.find_all('option')
            print(f"  Options: {[opt.get_text(strip=True) for opt in options[:5]]}")

        # Show raw HTML sample for debugging
        print(f"\n📝 HTML Sample (first 1000 chars):")
        print("-" * 40)
        print(response.text[:1000])
        print("-" * 40)

        # Check if there's an error message
        error_divs = soup.find_all('div', {'class': lambda x: x and 'error' in x.lower()})
        if error_divs:
            print(f"\n❌ Found error messages:")
            for error in error_divs:
                print(f"  - {error.get_text(strip=True)}")

        print(f"\n🎉 Debug analysis complete!")

    except Exception as e:
        print(f"❌ Error debugging archive: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_tulsa_archive()
