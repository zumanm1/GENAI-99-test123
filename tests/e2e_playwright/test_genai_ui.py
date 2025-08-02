#!/usr/bin/env python3
"""
Playwright E2E tests for GENAI automation functionality
"""

import pytest
from playwright.sync_api import sync_playwright, expect


class TestGenAIUI:
    """Test class for GENAI UI functionality"""
    
    def test_genai_page_loads(self):
        """Test that the GENAI page loads correctly"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                # Navigate to the frontend
                page.goto("http://localhost:8001")
                
                # Wait for page to load
                page.wait_for_load_state("networkidle")
                
                # Check for GENAI link
                genai_link = page.locator('a[href="/genai"]')
                expect(genai_link).to_be_visible()
                
                print("✓ GENAI page loads successfully")
                
            finally:
                browser.close()
    
    def test_genai_form_functionality(self):
        """Test GENAI form submission functionality"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                # Navigate to the frontend
                page.goto("http://localhost:8001")
                page.wait_for_load_state("networkidle")
                
                # Click on GENAI link
                page.click('a[href="/genai"]')
                
                # Wait for GENAI page to load
                page.wait_for_selector('#genai-form')
                
                # Fill out the form
                page.fill('#requirements', 'Configure a test VLAN.')
                page.select_option('#device_type', 'iosxr')
                
                # Submit the form
                page.click('#generate-btn')
                
                # Wait for results (with longer timeout for API call)
                page.wait_for_function(
                    'document.querySelector("#results-container").innerText.trim() !== "" && !document.querySelector(".error-message")',
                    timeout=60000
                )
                
                # Verify results
                results_text = page.locator('#results-container').inner_text()
                assert 'Error:' not in results_text, f"API returned error: {results_text}"
                
                print("✓ GENAI form functionality test passed")
                
            except Exception as e:
                # Take screenshot on failure
                page.screenshot(path="test-failure-screenshot-playwright.png")
                raise e
            finally:
                browser.close()

    def test_accessibility_features(self):
        """Test basic accessibility features"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                # Navigate to the frontend
                page.goto("http://localhost:8001")
                page.wait_for_load_state("networkidle")
                
                # Check for proper heading structure
                h1_elements = page.locator('h1')
                expect(h1_elements).to_have_count(1)
                
                # Check for form labels
                page.click('a[href="/genai"]')
                page.wait_for_selector('#genai-form')
                
                # Check for proper form labeling
                requirements_label = page.locator('label[for="requirements"]')
                device_type_label = page.locator('label[for="device_type"]')
                
                # These should be visible for accessibility
                expect(requirements_label).to_be_visible()
                expect(device_type_label).to_be_visible()
                
                print("✓ Basic accessibility features confirmed")
                
            finally:
                browser.close()


if __name__ == "__main__":
    # Run the tests directly if called as script
    test_instance = TestGenAIUI()
    test_instance.test_genai_page_loads()
    test_instance.test_genai_form_functionality()
    test_instance.test_accessibility_features()
    print("All Playwright E2E tests passed!")
