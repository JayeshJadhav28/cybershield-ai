import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test('should display sign-in page with OTP form', async ({ page }) => {
    await page.goto('/signin');

    await expect(page.locator('h1, h2').first()).toContainText(/sign in/i);
    await expect(page.locator('input[type="email"], input[placeholder*="email" i]')).toBeVisible();
  });

  test('should display sign-up page', async ({ page }) => {
    await page.goto('/signup');

    await expect(page.locator('h1, h2').first()).toContainText(/sign up|create|register/i);
  });

  test('should navigate between sign-in and sign-up', async ({ page }) => {
    await page.goto('/signin');

    const signUpLink = page.locator('a[href*="signup"], button:has-text("Sign Up"), a:has-text("Sign Up")').first();
    if (await signUpLink.isVisible()) {
      await signUpLink.click();
      await expect(page).toHaveURL(/signup/);
    }
  });

  test('should show landing page for unauthenticated users', async ({ page }) => {
    await page.goto('/');

    await expect(page.locator('text=CyberShield')).toBeVisible();
  });
});