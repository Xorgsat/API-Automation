import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",
  timeout: 30000,
  retries: 0,
  workers: 1,
  reporter: [
    ["list"],
    ["html", { outputFolder: "playwright-report", open: "never" }],
    ["json", { outputFile: "playwright-report/results.json" }],
  ],
  use: {
    baseURL: process.env.API_BASE_URL || "https://restful-booker.herokuapp.com",
    extraHTTPHeaders: {
      "Accept": "application/json",
      "User-Agent": "playwright-api-testing/1.0",
    },
  },
});
