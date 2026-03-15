D-Alert — Disaster Response System
D-Alert is a real-time disaster alert and response web application designed to help emergency responders and the public track, classify, and prioritize disaster events as they happen.

What it does:

📡 Ingests alerts from two sources — social media reports and official weather feeds — and stores them in a database
🤖 Automatically classifies each alert by disaster type (flood, fire, earthquake, etc.), severity, and confidence level using AI
📍 Geocodes locations — converts location names into GPS coordinates so alerts can be mapped
🗺️ Clusters nearby alerts together on an interactive map to identify hotspots and high-risk zones
⚠️ Prioritizes alerts by risk score so responders know where to act first
✅ Tracks alert status — responders can acknowledge or resolve alerts in real time
🔁 Deduplicates reports — prevents the same incident from being reported 3+ times in an hour


Tech stack:
LayerTechnologyBackend APIPython + FastAPIDatabaseSQLite via SQLModelMappingFolium + StreamlitAI ClassificationOpenAI APIFrontendHTML + CSS + JavaScriptHostingRender

In short — D-Alert is a smart triage system for disasters, turning raw reports into actionable, prioritized intelligence for emergency teams.

🐍 Python — 52.9% (the backbone)
Python is doing the heavy lifting — it's the backend/server-side logic. In a disaster response app this typically means:

Running the web server (likely Flask or Django)
Handling API routes (e.g., receiving alert data, processing requests)
Any data processing, notification logic, or integration with external services (SMS alerts, maps, etc.)


🌐 JavaScript — 18.7% (interactivity)
JavaScript powers the dynamic, interactive parts of the frontend:

Real-time updates (e.g., refreshing alert feeds without reloading the page)
Handling button clicks, form submissions, and user interactions
Possibly fetching data from the Python backend via API calls (fetch/AJAX)


🎨 CSS — 16.0% (visual styling)
CSS is responsible for the look and feel of the app:

Layout, colors, fonts, and spacing
Making the UI readable and usable — especially important in an emergency/disaster context where clarity matters
Possibly responsive design so it works on mobile devices


🏗️ HTML — 12.4% (structure)
HTML defines the skeleton/structure of every page:

The forms users fill out (e.g., reporting an emergency)
Page layout elements like headers, navbars, and alert cards
The templates that Python renders and sends to the browser
