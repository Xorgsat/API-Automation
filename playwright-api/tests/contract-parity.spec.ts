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

  test("response contract parity for Booking Creation and Schema properties", async ({ request }) => {
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

    // Cleanup
    await request.delete(`/booking/${createdId}`, {
      headers: { "Cookie": `token=${token}` },
    });
  });
});
