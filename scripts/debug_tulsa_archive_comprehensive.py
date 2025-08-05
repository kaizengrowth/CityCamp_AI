#!/usr/bin/env python3
"""
Comprehensive debug script to analyze Tulsa Archive date filtering and form mechanisms
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta

def debug_comprehensive_archive():
    print("🔍 Comprehensive Tulsa Archive Analysis")
    print("=" * 60)

    archive_url = "https://www.cityoftulsa.org/apps/TulsaCouncilArchive"

    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        print(f"📡 Fetching main page: {archive_url}")
        response = session.get(archive_url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # 1. Analyze the form structure
        print("\n🔍 1. FORM ANALYSIS")
        print("-" * 40)

        forms = soup.find_all('form')
        for i, form in enumerate(forms):
            print(f"\nForm {i+1}:")
            print(f"  Action: {form.get('action', 'None')}")
            print(f"  Method: {form.get('method', 'GET')}")

            # Find all form inputs
            inputs = form.find_all(['input', 'select', 'textarea'])
            for inp in inputs:
                inp_type = inp.get('type', inp.name)
                inp_name = inp.get('name', 'unnamed')
                inp_value = inp.get('value', '')
                print(f"    {inp_type}: {inp_name} = '{inp_value}'")

        # 2. Analyze meeting type dropdown
        print("\n🔍 2. MEETING TYPE DROPDOWN ANALYSIS")
        print("-" * 40)

        meeting_type_select = soup.find('select', {'name': 'Council_Meeting_Type'})
        if meeting_type_select:
            options = meeting_type_select.find_all('option')
            print(f"Found {len(options)} meeting type options:")

            meeting_types = []
            for opt in options:
                value = opt.get('value', '')
                text = opt.get_text(strip=True)
                if value and value != '-- Select Meeting Type --':
                    meeting_types.append({'value': value, 'text': text})
                    print(f"  • '{text}' (value: '{value}')")

            print(f"\n📋 Total meeting types to scrape: {len(meeting_types)}")

        # 3. Analyze date inputs
        print("\n🔍 3. DATE INPUT ANALYSIS")
        print("-" * 40)

        date_inputs = soup.find_all('input', {'type': 'text', 'class': lambda x: x and 'date' in x.lower()})
        if not date_inputs:
            date_inputs = soup.find_all('input', {'name': lambda x: x and 'date' in x.lower()})

        print(f"Found {len(date_inputs)} date-related inputs:")
        for inp in date_inputs:
            print(f"  • Name: {inp.get('name')}, ID: {inp.get('id')}, Class: {inp.get('class')}")

        # 4. Look for JavaScript date pickers
        print("\n🔍 4. JAVASCRIPT ANALYSIS")
        print("-" * 40)

        scripts = soup.find_all('script')
        datepicker_scripts = []
        for script in scripts:
            script_text = script.get_text()
            if 'datepicker' in script_text.lower() or 'date' in script_text.lower():
                datepicker_scripts.append(script_text[:200] + "..." if len(script_text) > 200 else script_text)

        print(f"Found {len(datepicker_scripts)} date-related scripts:")
        for i, script in enumerate(datepicker_scripts[:3]):  # Show first 3
            print(f"  Script {i+1}: {script}")

        # 5. Test form submission with different parameters
        print("\n🔍 5. FORM SUBMISSION TEST")
        print("-" * 40)

        # Try to submit form with specific meeting type
        form = soup.find('form')
        if form:
            form_action = form.get('action')
            if not form_action or form_action.startswith('/'):
                form_action = archive_url

            print(f"Testing form submission to: {form_action}")

            # Test with Regular meetings
            test_data = {
                'Council_Meeting_Type': 'Regular'
            }

            print(f"Submitting with data: {test_data}")
            response = session.post(form_action, data=test_data, timeout=30)

            if response.status_code == 200:
                print(f"✅ Form submission successful")

                # Parse results
                result_soup = BeautifulSoup(response.content, 'html.parser')
                result_links = result_soup.find_all('a', href=lambda x: x and 'COTDisplayDocument' in x)
                print(f"Found {len(result_links)} documents in filtered results")

                # Show sample results
                for i, link in enumerate(result_links[:3]):
                    print(f"  {i+1}. {link.get_text(strip=True)} - {link.get('href')}")
            else:
                print(f"❌ Form submission failed: {response.status_code}")

        # 6. Identify all form fields for comprehensive scraping
        print("\n🔍 6. COMPREHENSIVE FORM FIELDS")
        print("-" * 40)

        all_form_fields = {}
        for form in forms:
            inputs = form.find_all(['input', 'select', 'textarea'])
            for inp in inputs:
                name = inp.get('name')
                if name:
                    if inp.name == 'select':
                        # For select elements, get all options
                        options = [opt.get('value') for opt in inp.find_all('option') if opt.get('value')]
                        all_form_fields[name] = options
                    else:
                        all_form_fields[name] = inp.get('value', '')

        print("Form fields for comprehensive scraping:")
        for field, value in all_form_fields.items():
            if isinstance(value, list):
                print(f"  • {field}: {len(value)} options - {value[:3]}{'...' if len(value) > 3 else ''}")
            else:
                print(f"  • {field}: '{value}'")

        print(f"\n🎯 SCRAPING STRATEGY:")
        print(f"  • Meeting Types: {len([v for v in all_form_fields.get('Council_Meeting_Type', []) if v])}")
        print(f"  • Date Range: 2020-2025 (need to determine date field names)")
        print(f"  • Form Method: POST to {form_action if 'form' in locals() else 'unknown'}")

        return all_form_fields

    except Exception as e:
        print(f"❌ Error debugging archive: {str(e)}")
        import traceback
        traceback.print_exc()
        return {}

if __name__ == "__main__":
    form_fields = debug_comprehensive_archive()

    if form_fields:
        print(f"\n💾 Saving form field analysis...")
        with open('tulsa_archive_form_fields.json', 'w') as f:
            json.dump(form_fields, f, indent=2)
        print(f"✅ Saved to tulsa_archive_form_fields.json")
