#!/bin/bash
# Generate demo model weights if models don't exist
python -c "
import os
if not os.path.exists('models/phishing_classifier.pkl'):
    print('Generating demo model weights...')
    exec(open('../infra/scripts/generate_demo_weights.py').read())
    print('Demo weights generated!')
else:
    print('Models already exist')
"

# Run migrations
alembic upgrade head

# Start the server
uvicorn main:app --host 0.0.0.0 --port $PORT