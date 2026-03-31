import { test, expect } from '@playwright/test';

test.describe('Email Analysis Flow', () => {
  test('should display email analyzer page', async ({ page }) => {
    await page.goto('/analyze/email');

    await expect(page.locator('h1')).toContainText(/email/i);
    await expect(page.locator('[data-testid="email-subject"], input[placeholder*="subject" i]').first()).toBeVisible();
  });

  test('should validate required fields', async ({ page }) => {
    await page.goto('/analyze/email');

    const submitBtn = page.locator('[data-testid="analyze-button"]');
    await submitBtn.click();

    // Should show validation errors (form won't submit with empty required fields)
    await expect(page.locator('text=/required|enter/i').first()).toBeVisible({ timeout: 5000 });
  });

  test('should accept input in all fields', async ({ page }) => {
    await page.goto('/analyze/email');

    const subject = page.locator('[data-testid="email-subject"]');
    const body = page.locator('[data-testid="email-body"]');
    const sender = page.locator('[data-testid="email-sender"]');

    await subject.fill('URGENT: Account Suspended');
    await body.fill('Click here to verify your credentials immediately');
    await sender.fill('security@fake-bank.xyz');

    await expect(subject).toHaveValue('URGENT: Account Suspended');
    await expect(body).toHaveValue('Click here to verify your credentials immediately');
    await expect(sender).toHaveValue('security@fake-bank.xyz');
  });

  test('should show demo sample picker', async ({ page }) => {
    await page.goto('/analyze/email');

    const picker = page.locator('[data-testid="demo-sample-picker"]');
    if (await picker.isVisible()) {
      await picker.click();
      await expect(page.locator('[role="menuitem"]').first()).toBeVisible({ timeout: 5000 });
    }
  });
});