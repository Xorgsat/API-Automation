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

  test("should execute full booking lifecycle: Create -> Read -> Update -> Delete", async ({ request }) => {
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

    // 2. Read
    const getResp = await request.get(`/booking/${bookingId}`);
    expect(getResp.status()).toBe(200);
    const getData = await getResp.json();
    expect(getData.firstname).toBe("Playwright");
    expect(getData.totalprice).toBe(299);

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

    // 4. Delete
    const deleteResp = await request.delete(`/booking/${bookingId}`, {
      headers: {
        "Cookie": `token=${token}`,
      },
    });
    expect(deleteResp.status()).toBe(201);

    // 5. Post-deletion Read (404)
    const verifyResp = await request.get(`/booking/${bookingId}`);
    expect(verifyResp.status()).toBe(404);
  });
});
