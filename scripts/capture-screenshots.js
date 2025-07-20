#!/usr/bin/env node

/**
 * Automated Screenshot Capture Script for CityCamp AI
 *
 * This script uses Playwright to automatically capture screenshots
 * of the live application for documentation purposes.
 *
 * Usage:
 *   npm install playwright
 *   node scripts/capture-screenshots.js
 */

const { chromium, devices } = require('playwright');
const fs = require('fs').promises;
const path = require('path');

// Configuration
const CONFIG = {
  baseUrl: process.env.SCREENSHOT_URL || 'https://d1s9nkkr0t3pmn.cloudfront.net',
  outputDir: 'docs/screenshots',
  viewports: {
    desktop: { width: 1920, height: 1080 },
    tablet: devices['iPad Pro'],
    mobile: devices['iPhone 12']
  },
  delay: 2000, // Wait time after page load
  quality: 80   // Image quality (0-100)
};

// Screenshot definitions
const SCREENSHOTS = [
  {
    name: 'homepage/landing-page',
    url: '/',
    selector: 'body',
    description: 'Main landing page with hero section',
    wait: '.hero-section, [data-testid="landing-hero"]' // Wait for specific elements
  },
  {
    name: 'homepage/dashboard-overview',
    url: '/dashboard',
    selector: 'body',
    description: 'User dashboard with notifications overview',
    wait: '.dashboard-container, [data-testid="dashboard"]'
  },
  {
    name: 'meetings/meeting-list',
    url: '/meetings',
    selector: 'body',
    description: 'AI-categorized meeting list with filters',
    wait: '.meetings-list, [data-testid="meetings-list"]'
  },
  {
    name: 'meetings/meeting-details',
    url: '/meetings',
    selector: 'body',
    description: 'Individual meeting details with agenda',
    wait: '.meeting-details, [data-testid="meeting-details"]',
    actions: [
      { type: 'click', selector: '.meeting-item:first-child, [data-testid="meeting-item"]:first-child' },
      { type: 'wait', timeout: 3000 }
    ]
  },
  {
    name: 'chatbot/chatbot-interface',
    url: '/',
    selector: 'body',
    description: 'AI chatbot interface and conversation',
    actions: [
      { type: 'click', selector: '.chatbot-trigger, [data-testid="chatbot-button"]' },
      { type: 'wait', timeout: 2000 },
      { type: 'type', selector: '.chatbot-input, [data-testid="chatbot-input"]', text: 'What meetings are happening this week?' },
      { type: 'press', key: 'Enter' },
      { type: 'wait', timeout: 3000 }
    ]
  },
  {
    name: 'notifications/signup-form',
    url: '/notifications',
    selector: 'body',
    description: 'Notification signup with topic preferences',
    wait: '.notification-form, [data-testid="notification-signup"]'
  }
];

/**
 * Create directories for screenshots
 */
async function createDirectories() {
  const dirs = [
    'homepage', 'meetings', 'chatbot',
    'notifications', 'admin'
  ].map(dir => path.join(CONFIG.outputDir, dir));

  for (const dir of dirs) {
    await fs.mkdir(dir, { recursive: true });
    console.log(`📁 Created directory: ${dir}`);
  }
}

/**
 * Take a screenshot for a specific configuration
 */
async function takeScreenshot(browser, screenshot, viewport, viewportName) {
  const page = await browser.newPage();

  try {
    // Set viewport
    if (viewport.width && viewport.height) {
      await page.setViewportSize(viewport);
    }

    console.log(`📸 Capturing ${screenshot.name}-${viewportName}...`);

    // Navigate to page
    const fullUrl = CONFIG.baseUrl + screenshot.url;
    console.log(`   → Navigating to: ${fullUrl}`);

    await page.goto(fullUrl, {
      waitUntil: 'networkidle',
      timeout: 30000
    });

    // Wait for specific elements if specified
    if (screenshot.wait) {
      try {
        await page.waitForSelector(screenshot.wait, { timeout: 10000 });
        console.log(`   → Element found: ${screenshot.wait}`);
      } catch (error) {
        console.log(`   ⚠️  Element not found: ${screenshot.wait}, continuing anyway`);
      }
    }

    // Perform actions if specified
    if (screenshot.actions) {
      console.log(`   → Performing ${screenshot.actions.length} action(s)`);
      for (const action of screenshot.actions) {
        try {
          switch (action.type) {
            case 'click':
              await page.click(action.selector);
              break;
            case 'type':
              await page.type(action.selector, action.text);
              break;
            case 'press':
              await page.keyboard.press(action.key);
              break;
            case 'wait':
              await page.waitForTimeout(action.timeout);
              break;
          }
        } catch (error) {
          console.log(`   ⚠️  Action failed: ${action.type}, continuing anyway`);
        }
      }
    }

    // Additional delay for page stability
    await page.waitForTimeout(CONFIG.delay);

    // Take screenshot
    const filename = `${screenshot.name}-${viewportName}.png`;
    const filepath = path.join(CONFIG.outputDir, filename);

    await page.screenshot({
      path: filepath,
      fullPage: false, // Capture viewport only
      type: 'png',
      quality: CONFIG.quality
    });

    console.log(`   ✅ Saved: ${filepath}`);

    return { success: true, filepath };

  } catch (error) {
    console.error(`   ❌ Error capturing ${screenshot.name}-${viewportName}:`, error.message);
    return { success: false, error: error.message };
  } finally {
    await page.close();
  }
}

/**
 * Generate screenshot report
 */
async function generateReport(results) {
  const report = {
    timestamp: new Date().toISOString(),
    total: results.length,
    successful: results.filter(r => r.success).length,
    failed: results.filter(r => !r.success).length,
    results: results
  };

  const reportPath = path.join(CONFIG.outputDir, 'screenshot-report.json');
  await fs.writeFile(reportPath, JSON.stringify(report, null, 2));

  console.log(`📊 Report saved: ${reportPath}`);
  return report;
}

/**
 * Main execution function
 */
async function main() {
  console.log('🚀 Starting CityCamp AI Screenshot Capture');
  console.log(`📍 Target URL: ${CONFIG.baseUrl}`);
  console.log(`📁 Output Directory: ${CONFIG.outputDir}`);

  // Create output directories
  await createDirectories();

  // Launch browser
  console.log('🌐 Launching browser...');
  const browser = await chromium.launch({
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-dev-shm-usage',
      '--disable-web-security'
    ]
  });

  const results = [];

  try {
    // Take screenshots for each configuration
    for (const screenshot of SCREENSHOTS) {
      console.log(`\n📋 Processing: ${screenshot.description}`);

      // Take screenshots for each viewport
      for (const [viewportName, viewport] of Object.entries(CONFIG.viewports)) {
        const result = await takeScreenshot(browser, screenshot, viewport, viewportName);
        results.push({
          name: screenshot.name,
          viewport: viewportName,
          description: screenshot.description,
          ...result
        });
      }
    }

    // Generate report
    const report = await generateReport(results);

    console.log('\n🎉 Screenshot capture complete!');
    console.log(`✅ Successful: ${report.successful}/${report.total}`);
    console.log(`❌ Failed: ${report.failed}/${report.total}`);

    if (report.failed > 0) {
      console.log('\n❌ Failed screenshots:');
      results.filter(r => !r.success).forEach(r => {
        console.log(`   • ${r.name}-${r.viewport}: ${r.error}`);
      });
    }

  } finally {
    await browser.close();
  }
}

/**
 * Help text
 */
function showHelp() {
  console.log(`
🏛️ CityCamp AI Screenshot Capture Tool

Usage:
  node scripts/capture-screenshots.js [options]

Environment Variables:
  SCREENSHOT_URL    Target URL (default: https://d1s9nkkr0t3pmn.cloudfront.net)

Examples:
  # Capture from production
  node scripts/capture-screenshots.js

  # Capture from local development
  SCREENSHOT_URL=http://localhost:3007 node scripts/capture-screenshots.js

Prerequisites:
  npm install playwright

Output:
  Screenshots saved to: docs/screenshots/
  Report saved to: docs/screenshots/screenshot-report.json
`);
}

// Check for help flag
if (process.argv.includes('--help') || process.argv.includes('-h')) {
  showHelp();
  process.exit(0);
}

// Run main function
main().catch(error => {
  console.error('💥 Script failed:', error);
  process.exit(1);
});
