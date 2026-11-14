import { test, expect } from "@playwright/test";

test.describe("Booking Smoke & Lifecycle - Playwright Parity", () => {
  let token: string;
  let bookingId: number;

  test.beforeAll(async ({ request }) => {
    // Authenticate and acquire token
    const authResp = await request.post("/auth", {
      data: {
        username: process.env.API_AUTH_USERNAME || "admin",
        password: process.env.API_AUTH_PASSWORD || "password123",
      },
    });
    expect(authResp.status()).toBe(200);
    const authData = await authResp.json();
    expect(authData).toHaveProperty("token");
    token = authData.token;
  });

  test("should execute full booking lifecycle: Create -> Read -> Update -> Delete", async ({ request, page }) => {
    // Render a live visual status console for headed mode monitoring
    await page.setContent(`
      <!DOCTYPE html>
      <html>
      <head>
        <title>API Automation Live Monitor</title>
        <style>
          body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0b0f19; color: #e2e8f0; margin: 0; padding: 28px; }
          .card { background: #1e293b; border-radius: 12px; padding: 24px; max-width: 800px; margin: 0 auto; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
          h1 { color: #38bdf8; font-size: 22px; margin-top: 0; display: flex; align-items: center; gap: 10px; }
          .badge { background: #0369a1; color: #e0f2fe; padding: 4px 10px; border-radius: 9999px; font-size: 12px; font-weight: 600; }
          .step { margin: 12px 0; padding: 12px 16px; border-radius: 8px; background: #0f172a; border-left: 4px solid #38bdf8; font-family: monospace; font-size: 13px; }
          .step.success { border-left-color: #22c55e; }
          .step-title { font-weight: bold; color: #f1f5f9; margin-bottom: 4px; }
          .step-detail { color: #94a3b8; }
          .status { color: #22c55e; font-weight: bold; }
        </style>
      </head>
      <body>
        <div class="card">
          <h1><span>⚡</span> API Quality Engineering - Live Test Monitor <span class="badge">HEADED MODE</span></h1>
          <p style="color: #94a3b8; margin-bottom: 20px;">Target API: <code>https://restful-booker.herokuapp.com</code></p>
          <div id="steps"></div>
        </div>
      </body>
      </html>
    `);

    async function logStep(title: string, detail: string, success: boolean = true) {
      await page.evaluate(({ title, detail, success }) => {
        const container = document.getElementById("steps");
        if (container) {
          const div = document.createElement("div");
          div.className = "step" + (success ? " success" : "");
          div.innerHTML = `<div class="step-title">${title}</div><div class="step-detail">${detail}</div>`;
          container.appendChild(div);
        }
      }, { title, detail, success });
      await page.waitForTimeout(400); // Visual pacing for headed observer
    }

    await logStep("1. Authentication Verified", `Acquired session token: <code>${token.slice(0, 4)}***${token.slice(-4)}</code>`);

    // 1. Create
    const newBooking = {
      firstname: "Playwright",
      lastname: "Automation",
      totalprice: 299,
      depositpaid: true,
      bookingdates: {
        checkin: "2026-12-01",
        checkout: "2026-12-10",
      },
      additionalneeds: "TypeScript Support",
    };

    const createResp = await request.post("/booking", {
      data: newBooking,
    });
    expect(createResp.status()).toBe(200);
    const createData = await createResp.json();
    expect(createData).toHaveProperty("bookingid");
    bookingId = createData.bookingid;
    expect(createData.booking.firstname).toBe("Playwright");

    await logStep(
      "2. POST /booking (Create)",
      `Status <span class="status">200 OK</span> | Created Booking ID: <strong>${bookingId}</strong> for <em>Playwright Automation</em> ($299)`
    );

    // 2. Read
    const getResp = await request.get(`/booking/${bookingId}`);
    expect(getResp.status()).toBe(200);
    const getData = await getResp.json();
    expect(getData.firstname).toBe("Playwright");
    expect(getData.totalprice).toBe(299);

    await logStep(
      `3. GET /booking/${bookingId} (Read-after-Write)`,
      `Status <span class="status">200 OK</span> | Verified record persistence & attribute parity`
    );

    // 3. Update (PUT)
    const updatedBooking = {
      ...newBooking,
      firstname: "PlaywrightUpdated",
      totalprice: 350,
    };

    const putResp = await request.put(`/booking/${bookingId}`, {
      headers: {
        "Cookie": `token=${token}`,
      },
      data: updatedBooking,
    });
    expect(putResp.status()).toBe(200);
    const putData = await putResp.json();
    expect(putData.firstname).toBe("PlaywrightUpdated");
    expect(putData.totalprice).toBe(350);

    await logStep(
      `4. PUT /booking/${bookingId} (Full Update with Auth Cookie)`,
      `Status <span class="status">200 OK</span> | Updated name to <em>PlaywrightUpdated</em> and price to $350`
    );

    // 4. Delete
    const deleteResp = await request.delete(`/booking/${bookingId}`, {
      headers: {
        "Cookie": `token=${token}`,
      },
    });
    expect(deleteResp.status()).toBe(201);

    await logStep(
      `5. DELETE /booking/${bookingId} (Teardown Cleanup)`,
      `Status <span class="status">201 Created</span> | Deleted resource successfully`
    );

    // 5. Post-deletion Read (404)
    const verifyResp = await request.get(`/booking/${bookingId}`);
    expect(verifyResp.status()).toBe(404);

    await logStep(
      `6. Post-Deletion Verification (GET /booking/${bookingId})`,
      `Status <span class="status">404 Not Found</span> | Resource confirmed purged. Complete lifecycle validated!`
    );

    await page.waitForTimeout(1000); // Allow final view in headed mode
  });
});
