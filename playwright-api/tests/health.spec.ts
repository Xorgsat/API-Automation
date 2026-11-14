import { test, expect } from "@playwright/test";

test.describe("Health Check API - Playwright Parity", () => {
  test("GET /ping should return HTTP 201 Created and text 'Created'", async ({ request, page }) => {
    await page.setContent(`
      <div style="font-family: -apple-system, sans-serif; background: #0f172a; color: #f8fafc; padding: 24px; min-height: 100vh;">
        <h2 style="color: #38bdf8;">⚡ Health Check - Live Monitor</h2>
        <p>Probing <code>GET https://restful-booker.herokuapp.com/ping</code>...</p>
        <div id="result" style="padding: 16px; background: #1e293b; border-radius: 8px; font-family: monospace;">Awaiting response...</div>
      </div>
    `);

    const startTime = Date.now();
    const response = await request.get("/ping");
    const duration = Date.now() - startTime;

    expect(response.status()).toBe(201);
    const text = await response.text();
    expect(text.trim()).toBe("Created");
    expect(duration).toBeLessThan(5000);

    await page.evaluate(({ status, text, duration }) => {
      const el = document.getElementById("result");
      if (el) {
        el.innerHTML = `<span style="color: #22c55e; font-weight: bold;">[HTTP ${status} Created]</span> Body: "${text.trim()}" | Latency: ${duration}ms`;
      }
    }, { status: response.status(), text, duration });

    await page.waitForTimeout(1000);
  });
});
