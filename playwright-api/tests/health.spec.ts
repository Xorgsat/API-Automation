import { test, expect } from "@playwright/test";

test.describe("Health Check API - Playwright Parity", () => {
  test("GET /ping should return HTTP 201 Created and text 'Created'", async ({ request }) => {
    const startTime = Date.now();
    const response = await request.get("/ping");
    const duration = Date.now() - startTime;

    expect(response.status()).toBe(201);
    const text = await response.text();
    expect(text.trim()).toBe("Created");
    expect(duration).toBeLessThan(5000);
  });
});
