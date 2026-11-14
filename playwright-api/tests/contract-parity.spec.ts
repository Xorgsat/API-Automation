import { test, expect } from "@playwright/test";

test.describe("Contract Parity - Playwright Parity", () => {
  let createdId: number;
  let token: string;

  test.beforeAll(async ({ request }) => {
    const authResp = await request.post("/auth", {
      data: {
        username: process.env.API_AUTH_USERNAME || "admin",
        password: process.env.API_AUTH_PASSWORD || "password123",
      },
    });
    const authData = await authResp.json();
    token = authData.token;
  });

  test("response contract parity for Booking Creation and Schema properties", async ({ request, page }) => {
    await page.setContent(`
      <div style="font-family: -apple-system, sans-serif; background: #0f172a; color: #f8fafc; padding: 24px; min-height: 100vh;">
        <h2 style="color: #38bdf8;">⚡ API Contract Parity - Live Monitor</h2>
        <p>Validating POST /booking against JSON Schema properties...</p>
        <div id="contract-log" style="padding: 16px; background: #1e293b; border-radius: 8px; font-family: monospace; font-size: 13px;">Executing request...</div>
      </div>
    `);

    const payload = {
      firstname: "ContractTest",
      lastname: "ParityUser",
      totalprice: 180,
      depositpaid: false,
      bookingdates: {
        checkin: "2027-01-15",
        checkout: "2027-01-20",
      },
      additionalneeds: "Strict Types",
    };

    const response = await request.post("/booking", { data: payload });
    expect(response.status()).toBe(200);

    const body = await response.json();
    // Validate schema contract structure
    expect(typeof body.bookingid).toBe("number");
    expect(body.bookingid).toBeGreaterThan(0);
    expect(typeof body.booking).toBe("object");

    const b = body.booking;
    expect(typeof b.firstname).toBe("string");
    expect(typeof b.lastname).toBe("string");
    expect(typeof b.totalprice).toBe("number");
    expect(typeof b.depositpaid).toBe("boolean");
    expect(typeof b.bookingdates).toBe("object");
    expect(typeof b.bookingdates.checkin).toBe("string");
    expect(typeof b.bookingdates.checkout).toBe("string");

    createdId = body.bookingid;

    await page.evaluate(({ id }) => {
      const el = document.getElementById("contract-log");
      if (el) {
        el.innerHTML = `
          <div style="color: #22c55e; font-weight: bold; margin-bottom: 8px;">✓ Contract Schema Validated Successfully</div>
          <div>• bookingid: <span style="color: #38bdf8;">${id} (integer)</span></div>
          <div>• booking.firstname: <span style="color: #38bdf8;">ContractTest (string)</span></div>
          <div>• booking.totalprice: <span style="color: #38bdf8;">180 (integer)</span></div>
          <div>• booking.depositpaid: <span style="color: #38bdf8;">false (boolean)</span></div>
          <div>• booking.bookingdates: <span style="color: #38bdf8;">{"checkin", "checkout"} (object)</span></div>
        `;
      }
    }, { id: createdId });

    await page.waitForTimeout(1000);

    // Cleanup
    await request.delete(`/booking/${createdId}`, {
      headers: { "Cookie": `token=${token}` },
    });
  });
});
