# 🛡️ CyberShield AI

> India-first, multi-modal AI platform for deepfake detection, phishing analysis, and cyber-awareness training.

## Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/your-org/cybershield-ai.git
cd cybershield-ai
make setup

# 2. Start development
make dev

# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```



```
cybershield-ai
├─ apps
│  ├─ api-gateway
│  │  ├─ alembic.ini
│  │  ├─ config.py
│  │  ├─ crash.log
│  │  ├─ database.py
│  │  ├─ dependencies.py
│  │  ├─ Dockerfile
│  │  ├─ main.py
│  │  ├─ migrations
│  │  │  ├─ env.py
│  │  │  ├─ script.py.mako
│  │  │  └─ versions
│  │  │     └─ 001_initial_schema.py
│  │  ├─ ml
│  │  │  ├─ audio_model.py
│  │  │  ├─ llm_client.py
│  │  │  ├─ model_loader.py
│  │  │  ├─ phish_model.py
│  │  │  ├─ qr_decoder.py
│  │  │  ├─ url_heuristics.py
│  │  │  ├─ video_model.py
│  │  │  └─ __init__.py
│  │  ├─ requirements.txt
│  │  ├─ routes
│  │  │  ├─ admin.py
│  │  │  ├─ analyze.py
│  │  │  ├─ auth.py
│  │  │  ├─ awareness.py
│  │  │  ├─ chatbot.py
│  │  │  ├─ demo.py
│  │  │  ├─ reports.py
│  │  │  └─ __init__.py
│  │  ├─ schemas
│  │  │  ├─ admin.py
│  │  │  ├─ analysis.py
│  │  │  ├─ auth.py
│  │  │  ├─ chat.py
│  │  │  ├─ common.py
│  │  │  ├─ demo.py
│  │  │  ├─ quiz.py
│  │  │  └─ __init__.py
│  │  ├─ services
│  │  │  ├─ audio_analyzer.py
│  │  │  ├─ auth_service.py
│  │  │  ├─ chatbot_service.py
│  │  │  ├─ demo_service.py
│  │  │  ├─ email_analyzer.py
│  │  │  ├─ email_service.py
│  │  │  ├─ explainability.py
│  │  │  ├─ image_analyzer.py
│  │  │  ├─ news_service.py
│  │  │  ├─ qr_analyzer.py
│  │  │  ├─ quiz_service.py
│  │  │  ├─ scoring_engine.py
│  │  │  ├─ url_analyzer.py
│  │  │  ├─ video_analyzer.py
│  │  │  └─ __init__.py
│  │  ├─ tests
│  │  │  ├─ conftest.py
│  │  │  ├─ test_analyze_routes.py
│  │  │  ├─ test_api_endpoints.py
│  │  │  ├─ test_audio_analyzer.py
│  │  │  ├─ test_auth.py
│  │  │  ├─ test_awareness.py
│  │  │  ├─ test_chatbot.py
│  │  │  ├─ test_database.py
│  │  │  ├─ test_email_analyzer.py
│  │  │  ├─ test_file_validation.py
│  │  │  ├─ test_hashing.py
│  │  │  ├─ test_main.py
│  │  │  ├─ test_phishing.py
│  │  │  ├─ test_quiz_service.py
│  │  │  ├─ test_reports_admin_demo.py
│  │  │  ├─ test_schemas.py
│  │  │  ├─ test_scoring_engine.py
│  │  │  ├─ test_url_analyzer.py
│  │  │  ├─ test_video.py
│  │  │  ├─ test_video_analyzer.py
│  │  │  └─ verify_video_pipeline.py
│  │  ├─ train_models.py
│  │  └─ utils
│  │     ├─ audio_preprocessing.py
│  │     ├─ exceptions.py
│  │     ├─ file_validation.py
│  │     ├─ hashing.py
│  │     ├─ image_preprocessing.py
│  │     ├─ security.py
│  │     ├─ text_preprocessing.py
│  │     ├─ video_preprocessing.py
│  │     └─ __init__.py
│  └─ web
│     ├─ AGENTS.md
│     ├─ CLAUDE.md
│     ├─ components.json
│     ├─ Dockerfile
│     ├─ eslint.config.mjs
│     ├─ next-env.d.ts
│     ├─ next.config.ts
│     ├─ package-lock.json
│     ├─ package.json
│     ├─ postcss.config.mjs
│     ├─ public
│     │  ├─ favicon.ico
│     │  ├─ fonts
│     │  ├─ images
│     │  │  ├─ demo-samples
│     │  │  ├─ logo-icon.svg
│     │  │  ├─ logo.svg
│     │  │  ├─ logo_cybershield.png
│     │  │  └─ og-image.png
│     │  └─ publiccybershieldai
│     │     ├─ apple-icon.png
│     │     ├─ favicon.ico
│     │     ├─ icon0.svg
│     │     ├─ icon1.png
│     │     └─ manifest.json
│     ├─ README.md
│     ├─ src
│     │  ├─ (app)
│     │  │  ├─ admin
│     │  │  │  ├─ content
│     │  │  │  │  └─ page.tsx
│     │  │  │  └─ metrics
│     │  │  │     └─ page.tsx
│     │  │  ├─ analyze
│     │  │  │  ├─ audio
│     │  │  │  │  └─ page.tsx
│     │  │  │  ├─ email
│     │  │  │  │  └─ page.tsx
│     │  │  │  ├─ image
│     │  │  │  │  └─ page.tsx
│     │  │  │  ├─ layout.tsx
│     │  │  │  ├─ url
│     │  │  │  │  └─ page.tsx
│     │  │  │  └─ video
│     │  │  │     └─ page.tsx
│     │  │  ├─ app-shell.tsx
│     │  │  ├─ assistant
│     │  │  │  └─ page.tsx
│     │  │  ├─ awareness
│     │  │  │  ├─ layout.tsx
│     │  │  │  ├─ quizzes
│     │  │  │  │  ├─ page.tsx
│     │  │  │  │  └─ [category]
│     │  │  │  │     └─ page.tsx
│     │  │  │  ├─ resources
│     │  │  │  │  └─ page.tsx
│     │  │  │  └─ scenarios
│     │  │  │     ├─ page.tsx
│     │  │  │     └─ [id]
│     │  │  │        └─ page.tsx
│     │  │  ├─ dashboard
│     │  │  │  └─ page.tsx
│     │  │  ├─ help
│     │  │  │  └─ page.tsx
│     │  │  ├─ layout.tsx
│     │  │  ├─ reports
│     │  │  │  ├─ analyses
│     │  │  │  │  └─ page.tsx
│     │  │  │  └─ quizzes
│     │  │  │     └─ page.tsx
│     │  │  └─ sidebar-aware-client.tsx
│     │  ├─ (auth)
│     │  │  ├─ layout.tsx
│     │  │  ├─ signin
│     │  │  │  └─ page.tsx
│     │  │  └─ signup
│     │  │     └─ page.tsx
│     │  ├─ (marketing)
│     │  │  ├─ layout.tsx
│     │  │  └─ page.tsx
│     │  ├─ app
│     │  │  ├─ (app)
│     │  │  │  ├─ admin
│     │  │  │  │  ├─ content
│     │  │  │  │  │  └─ page.tsx
│     │  │  │  │  └─ metrics
│     │  │  │  │     └─ page.tsx
│     │  │  │  ├─ analyze
│     │  │  │  │  ├─ audio
│     │  │  │  │  │  └─ page.tsx
│     │  │  │  │  ├─ email
│     │  │  │  │  │  └─ page.tsx
│     │  │  │  │  ├─ image
│     │  │  │  │  │  └─ page.tsx
│     │  │  │  │  ├─ layout.tsx
│     │  │  │  │  ├─ url
│     │  │  │  │  │  └─ page.tsx
│     │  │  │  │  └─ video
│     │  │  │  │     └─ page.tsx
│     │  │  │  ├─ app-shell.tsx
│     │  │  │  ├─ assistant
│     │  │  │  │  └─ page.tsx
│     │  │  │  ├─ awareness
│     │  │  │  │  ├─ layout.tsx
│     │  │  │  │  ├─ quizzes
│     │  │  │  │  │  ├─ page.tsx
│     │  │  │  │  │  └─ [category]
│     │  │  │  │  │     └─ page.tsx
│     │  │  │  │  ├─ resources
│     │  │  │  │  │  └─ page.tsx
│     │  │  │  │  └─ scenarios
│     │  │  │  │     ├─ page.tsx
│     │  │  │  │     └─ [id]
│     │  │  │  │        └─ page.tsx
│     │  │  │  ├─ dashboard
│     │  │  │  │  └─ page.tsx
│     │  │  │  ├─ help
│     │  │  │  │  └─ page.tsx
│     │  │  │  ├─ layout.tsx
│     │  │  │  ├─ reports
│     │  │  │  │  ├─ analyses
│     │  │  │  │  │  └─ page.tsx
│     │  │  │  │  └─ quizzes
│     │  │  │  │     └─ page.tsx
│     │  │  │  └─ sidebar-aware-client.tsx
│     │  │  ├─ (auth)
│     │  │  │  ├─ layout.tsx
│     │  │  │  ├─ signin
│     │  │  │  │  └─ page.tsx
│     │  │  │  └─ signup
│     │  │  │     └─ page.tsx
│     │  │  ├─ (marketing)
│     │  │  │  ├─ layout.tsx
│     │  │  │  └─ page.tsx
│     │  │  ├─ globals.css
│     │  │  ├─ layout.tsx
│     │  │  └─ not-found.tsx
│     │  ├─ components
│     │  │  ├─ analyze
│     │  │  │  ├─ audio-upload.tsx
│     │  │  │  ├─ awareness-tip.tsx
│     │  │  │  ├─ demo-sample-picker.tsx
│     │  │  │  ├─ email-form.tsx
│     │  │  │  ├─ explanation-panel.tsx
│     │  │  │  ├─ file-dropzone.tsx
│     │  │  │  ├─ highlight-text.tsx
│     │  │  │  ├─ image-upload.tsx
│     │  │  │  ├─ qr-upload.tsx
│     │  │  │  ├─ result-card.tsx
│     │  │  │  ├─ risk-gauge.tsx
│     │  │  │  ├─ url-form.tsx
│     │  │  │  └─ video-upload.tsx
│     │  │  ├─ assistant
│     │  │  │  ├─ chat-message.tsx
│     │  │  │  ├─ chat-panel.tsx
│     │  │  │  └─ mode-toggle.tsx
│     │  │  ├─ auth
│     │  │  │  ├─ auth-card.tsx
│     │  │  │  ├─ countdown-timer.tsx
│     │  │  │  ├─ otp-input.tsx
│     │  │  │  ├─ sign-in-form.tsx
│     │  │  │  └─ sign-up-form.tsx
│     │  │  ├─ awareness
│     │  │  │  ├─ badge-display.tsx
│     │  │  │  ├─ quiz-card.tsx
│     │  │  │  ├─ quiz-progress.tsx
│     │  │  │  ├─ quiz-result.tsx
│     │  │  │  ├─ resource-card.tsx
│     │  │  │  └─ scenario-chat.tsx
│     │  │  ├─ dashboard
│     │  │  │  ├─ quick-access-tiles.tsx
│     │  │  │  ├─ recent-analyses.tsx
│     │  │  │  ├─ stats-cards.tsx
│     │  │  │  └─ threat-chart.tsx
│     │  │  ├─ landing
│     │  │  │  ├─ animated-counter.tsx
│     │  │  │  ├─ awareness-preview.tsx
│     │  │  │  ├─ cta-section.tsx
│     │  │  │  ├─ download-section.tsx
│     │  │  │  ├─ features-section.tsx
│     │  │  │  ├─ footer.tsx
│     │  │  │  ├─ globe-section.tsx
│     │  │  │  ├─ header.tsx
│     │  │  │  ├─ hero-section.tsx
│     │  │  │  ├─ how-it-works.tsx
│     │  │  │  ├─ matrix-rain.tsx
│     │  │  │  ├─ section-wrapper.tsx
│     │  │  │  └─ stats-section.tsx
│     │  │  ├─ shared
│     │  │  │  ├─ empty-state.tsx
│     │  │  │  ├─ error-boundary.tsx
│     │  │  │  ├─ loading-spinner.tsx
│     │  │  │  └─ page-header.tsx
│     │  │  └─ ui
│     │  │     ├─ app-store-button.tsx
│     │  │     ├─ avatar.tsx
│     │  │     ├─ badge.tsx
│     │  │     ├─ border-glow.tsx
│     │  │     ├─ breadcrumb.tsx
│     │  │     ├─ button.tsx
│     │  │     ├─ card.tsx
│     │  │     ├─ chatgpt-prompt-input.tsx
│     │  │     ├─ chrome-extension-button.tsx
│     │  │     ├─ cyber-matrix-bg.tsx
│     │  │     ├─ decrypted-text.tsx
│     │  │     ├─ dialog.tsx
│     │  │     ├─ dropdown-menu.tsx
│     │  │     ├─ flickering-grid.tsx
│     │  │     ├─ form.tsx
│     │  │     ├─ glare-hover.tsx
│     │  │     ├─ glitchy-404.tsx
│     │  │     ├─ globe-attack.tsx
│     │  │     ├─ globe-cdn.tsx
│     │  │     ├─ input.tsx
│     │  │     ├─ label.tsx
│     │  │     ├─ letter-glitch.tsx
│     │  │     ├─ liquid-metal-button.tsx
│     │  │     ├─ menu-toggle-icon.tsx
│     │  │     ├─ noise.tsx
│     │  │     ├─ play-store-button.tsx
│     │  │     ├─ progress.tsx
│     │  │     ├─ select.tsx
│     │  │     ├─ separator.tsx
│     │  │     ├─ sheet.tsx
│     │  │     ├─ sidebar.tsx
│     │  │     ├─ skeleton.tsx
│     │  │     ├─ sonner.tsx
│     │  │     ├─ tabs.tsx
│     │  │     ├─ textarea.tsx
│     │  │     ├─ tooltip.tsx
│     │  │     └─ use-scroll.ts
│     │  ├─ hooks
│     │  │  ├─ use-analysis.ts
│     │  │  ├─ use-auth.ts
│     │  │  ├─ use-chat.ts
│     │  │  ├─ use-media-upload.ts
│     │  │  ├─ use-mobile.ts
│     │  │  └─ use-quiz.ts
│     │  ├─ lib
│     │  │  ├─ api.ts
│     │  │  ├─ auth.ts
│     │  │  ├─ constants.ts
│     │  │  ├─ scenarios-data.ts
│     │  │  ├─ types.ts
│     │  │  ├─ utils.ts
│     │  │  └─ validators.ts
│     │  └─ providers
│     │     ├─ auth-provider.tsx
│     │     ├─ query-provider.tsx
│     │     ├─ sidebar-provider.tsx
│     │     └─ theme-provider.tsx
│     ├─ tailwind.config.ts
│     └─ tsconfig.json
├─ docs
│  ├─ API_REFERENCE.md
│  ├─ DEMO_GUIDE.md
│  ├─ DEPLOYMENT.md
│  ├─ MODEL_TRAINING.md
│  └─ TDD.md
├─ infra
│  ├─ docker-compose.prod.yml
│  ├─ docker-compose.yml
│  ├─ nginx
│  │  └─ nginx.conf
│  └─ scripts
│     ├─ download_models.sh
│     ├─ generate_demo_weights.py
│     ├─ seed_db.py
│     ├─ setup_dev.sh
│     └─ setup_ml.sh
├─ LICENSE
├─ Makefile
├─ notebooks
│  ├─ 01_phishing_model_training.ipynb
│  ├─ 02_audio_deepfake_training.ipynb
│  ├─ 03_video_deepfake_training.ipynb
│  └─ 04_model_evaluation.ipynb
├─ README.md
├─ tests
│  ├─ e2e
│  │  ├─ auth-flow.spec.ts
│  │  ├─ email-analysis.spec.ts
│  │  ├─ package.json
│  │  ├─ playwright.config.ts
│  │  └─ quiz-flow.spec.ts
│  └─ integration
│     └─ full-pipeline.test.py
├─ test_model.py
├─ tmp_crash.log
└─ tmp_test_audio.py

```