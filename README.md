# studymate-backend-

Django REST backend for StudyMate, an AI-powered study planner.

Required AI environment on Railway:
- `OPENAI_API_KEY`
- `OPENAI_MODEL`

Planner generation now depends on a live OpenAI Responses API call. If the key is missing or the request fails, the API returns an error instead of falling back to a mock plan.
