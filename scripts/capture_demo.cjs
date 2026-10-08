// Run against an isolated synthetic demo. See docs/demo/README.md.
const path = require('node:path');
const fs = require('node:fs/promises');
const { chromium } = require(process.env.SHIFTNOTES_PLAYWRIGHT_MODULE || 'playwright');

const root = path.resolve(__dirname, '..');
const baseUrl = process.env.SHIFTNOTES_DEMO_URL || 'http://localhost:8503';
const output = path.join(root, 'docs', 'demo');
const videoDir = path.join(root, 'dist', 'demo-video');

async function main() {
  await fs.mkdir(output, { recursive: true });
  await fs.mkdir(videoDir, { recursive: true });
  const browser = await chromium.launch({
    channel: process.env.SHIFTNOTES_BROWSER_CHANNEL || 'msedge',
    headless: true,
  });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1000 },
    recordVideo: { dir: videoDir, size: { width: 1440, height: 1000 } },
    reducedMotion: 'reduce',
  });
  const page = await context.newPage();
  page.setDefaultTimeout(30000);
  const errors = [];
  const stages = [];
  page.on('pageerror', error => errors.push(error.message));

  async function shot(name, description, focus = null) {
    // Pause for chart rendering and give the recording a readable cadence.
    await page.waitForTimeout(1200);
    if (focus) {
      await focus.scrollIntoViewIfNeeded();
    } else {
      await page.evaluate(() => {
        const main = document.querySelector('[data-testid="stMain"]');
        if (main) main.scrollTop = 0;
      });
    }
    await page.screenshot({ path: path.join(output, `${name}.png`) });
    stages.push({ image: `${name}.png`, description });
    await page.waitForTimeout(1600);
    console.log(description);
  }

  async function choose(label, option) {
    const select = page.locator('[data-testid="stSelectbox"]:visible').filter({ hasText: label }).first();
    await select.getByRole('combobox').click();
    await page.getByRole('option', { name: option, exact: true }).click();
  }

  try {
    await page.goto(`${baseUrl}/?view=briefings`);
    await page.getByRole('heading', { name: 'Briefing Preview', exact: true }).waitFor();
    await page.locator('iframe').first().waitFor();
    await shot('briefing', '1. Read the weekly briefing email preview.');

    await page.getByRole('tab', { name: 'Dashboard', exact: true }).click();
    await page.getByRole('heading', { name: 'Operations overview', exact: true }).waitFor();
    await page.getByText('Data quality and metric definitions', { exact: true }).waitFor();
    await page.locator('canvas').first().waitFor();
    await shot('dashboard', '2. Review the latest week: metrics, priorities, and trends.');

    await choose('Date range', 'Last 3 months');
    await page.locator('.sn-kpi-received strong').filter({ hasText: '270' }).waitFor();
    await shot('trends', '3. Expand to all 12 weeks of synthetic reports.');

    await page.getByRole('tab', { name: 'Kiosk Compare', exact: true }).click();
    await page.getByRole('heading', { name: 'Kiosk comparison', exact: true }).waitFor();
    await choose('Date range', 'Last 3 months');
    await page.locator('[data-testid="stDownloadButton"]:visible').waitFor();
    await shot('comparison', '4. Compare kiosks using ratings, missing reports, and unclaimed lunches per report.');

    await page.getByRole('tab', { name: 'Dashboard', exact: true }).click();
    await choose('Kiosk', 'Bowls & Buns');
    await page.locator('.sn-kpi-received strong').filter({ hasText: '45' }).waitFor();
    await shot('kiosk', '5. Narrow the reporting window to one kiosk.');
    const sourceDrawer = page.locator('[data-testid="stExpander"]:visible').filter({ hasText: 'Inspect sources:' }).first();
    await sourceDrawer.locator('summary').click();
    const reviewLink = sourceDrawer.getByRole('link', { name: /Review \/ challenge/ }).first();
    await reviewLink.waitFor();
    const reviewHref = await reviewLink.getAttribute('href');
    const claimUrl = new URL(reviewHref, baseUrl);
    const claimId = claimUrl.searchParams.get('claim');
    if (!claimId) throw Error('Source drawer has no claim link.');
    await shot('sources', '6. Inspect the original report fields supporting a finding.', sourceDrawer);

    // Use the real claim link, preserving its identity for correction review.
    await page.goto(claimUrl.toString());
    await page.getByRole('heading', { name: 'Challenge Review', exact: true }).waitFor();
    const claims = JSON.parse(await fs.readFile(path.join(root, 'demo/data/final_mock/claims.json'), 'utf8'));
    const claim = claims.find(item => item.claim_id === claimId);
    if (!claim?.source_submission_ids.length) throw Error('Recorded claim has no source.');
    const sourceId = claim.source_submission_ids[0];
    const challenge = page.getByRole('textbox', { name: 'Explain what is wrong in ordinary English' });
    await challenge.fill(`For this demo, remove ${sourceId} from this claim so I can review the proposed change.`);
    await challenge.press('Tab');
    await page.getByRole('button', { name: 'Review challenge', exact: true }).click();
    await page.getByRole('heading', { name: 'Proposed Correction', exact: true }).waitFor();
    await page.getByRole('button', { name: 'Confirm correction', exact: true }).waitFor();
    await shot('correction', '7. Review the proposal at the human confirmation checkpoint.');
    await page.getByRole('button', { name: 'Cancel', exact: true }).click();
    await page.getByRole('tab', { name: 'Correction History', exact: true }).click();
    await page.getByRole('heading', { name: 'Correction History', exact: true }).waitFor();
    await shot('history', '8. Cancel the proposed change and inspect the recorded decision.');

    if (errors.length) throw Error(errors.join('\n'));
    const video = page.video();
    await context.close();
    await video.saveAs(path.join(output, 'workflow.webm'));
    await fs.writeFile(path.join(output, 'capture-manifest.json'), JSON.stringify({
      dataset: 'Bundled synthetic reports; isolated local run',
      viewport: { width: 1440, height: 1000 },
      claim_id: claimId,
      challenged_source: sourceId,
      decision: 'cancel',
      note: 'Source removal is a scripted demo action, not a claim that the original analysis was incorrect.',
      stages,
      browser_errors: errors,
    }, null, 2) + '\n');
  } finally {
    await context.close().catch(() => {});
    await browser.close();
  }
}

main().catch(error => { console.error(error); process.exitCode = 1; });
