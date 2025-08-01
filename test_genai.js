const puppeteer = require('puppeteer');

(async () => {
    let browser;
    let page;
    try {
        console.log('Launching browser...');
        browser = await puppeteer.launch({ 
            headless: true, 
            args: ['--no-sandbox', '--disable-setuid-sandbox'] 
        });
        page = await browser.newPage();
        const url = 'http://localhost:8001';

        // Capture console logs from the page
        page.on('console', msg => console.log('PAGE LOG:', msg.text()));

        console.log(`Navigating to ${url}...`);
        await page.goto(url, { waitUntil: 'networkidle2' });

        console.log('Waiting for GENAI link to be visible...');
        await page.waitForSelector('a[href="/genai"]', { visible: true });

        console.log('Clicking on GENAI Automation link...');
        await page.click('a[href="/genai"]');
        
        console.log('Waiting for GENAI page to load...');
        await page.waitForSelector('#genai-form');

        console.log('Filling out the form...');
        await page.type('#requirements', 'Configure a test VLAN.');
        await page.select('#device_type', 'iosxr');

        console.log('Submitting the form...');
        await page.click('#generate-btn');

        console.log('Waiting for results...');
        // Wait for the results container to show something, and specifically not an error message.
        await page.waitForFunction(
            'document.querySelector("#results-container").innerText.trim() !== "" && !document.querySelector(".error-message")',
            { timeout: 60000 } // Increased timeout for live API call
        );

        console.log('Verifying results...');
        const resultsText = await page.$eval('#results-container', el => el.innerText);
        if (resultsText.includes('Error:')) {
            throw new Error(`Test Failed: API returned an error: ${resultsText}`);
        }

        console.log('✅ Test Passed: GENAI feature successfully generated a configuration.');
    } catch (error) {
        console.error('❌ Test execution failed:', error);
        if (page) {
            await page.screenshot({ path: 'test-failure-screenshot.png' });
            console.log('📸 Screenshot saved to test-failure-screenshot.png');
        }
        process.exit(1);
    } finally {
        if (browser) {
            await browser.close();
            console.log('Browser closed.');
        }
    }
})();
