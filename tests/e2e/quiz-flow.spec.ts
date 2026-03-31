import { test, expect } from '@playwright/test';

test.describe('Quiz Flow', () => {
  test('should display quiz category selection', async ({ page }) => {
    await page.goto('/awareness/quizzes');

    await expect(page.locator('h1')).toContainText(/quiz/i);

    // Should show at least one category card
    await expect(page.locator('text=/deepfake|phishing|upi/i').first()).toBeVisible();
  });

  test('should display start quiz buttons', async ({ page }) => {
    await page.goto('/awareness/quizzes');

    const startButtons = page.locator('a[href*="/awareness/quizzes/"], button:has-text("Start Quiz")');
    await expect(startButtons.first()).toBeVisible();
  });

  test('should navigate to scenario simulations', async ({ page }) => {
    await page.goto('/awareness/scenarios');

    await expect(page.locator('h1')).toContainText(/scenario/i);
  });

  test('should display learning resources', async ({ page }) => {
    await page.goto('/awareness/resources');

    await expect(page.locator('h1')).toContainText(/resource/i);
    await expect(page.locator('text=cybercrime.gov.in')).toBeVisible();
  });

  test('should show badge thresholds info', async ({ page }) => {
    await page.goto('/awareness/quizzes');

    await expect(page.locator('text=/bronze|silver|gold/i').first()).toBeVisible();
  });
});