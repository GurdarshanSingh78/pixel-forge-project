PixelForge forge 📸
PixelForge is a sophisticated, AI-powered web application that transforms a simple text query into a curated collection of high-quality, relevant images. Users can request a large batch of images, and the application's robust backend pipeline will fetch, filter, and deliver the final set directly to their email.

This project was built from the ground up, starting from a flowchart, and demonstrates a full-stack implementation of a modern, production-ready AI service.

✨ Key Features
Modern Frontend: A beautiful, fully responsive user interface built with Tailwind CSS, featuring a "glassmorphism" design and subtle animations.

Asynchronous Backend: Powered by FastAPI, the application handles long-running jobs in the background, providing an instant response to the user.

AI-Powered Curation: Utilizes OpenAI's CLIP model to intelligently filter images, ensuring that the final results are highly relevant to the user's text query.

Robust Image Pipeline: A multi-stage processing pipeline that:

Fetches high-quality images from the Pexels API.

Deduplicates images using perceptual hashing to eliminate visual clones.

Filters the set using AI for contextual relevance.

Email Notification System: Integrated with SendGrid to automatically notify users via email when their job is complete, providing a link to the results page.

Ad-Ready & Monetizable: The results page includes a dedicated ad slot, fulfilling a key business requirement.

Convenient Delivery: Users can download their entire curated image set as a single .zip file.

Scalable Architecture: Built with a professional structure that is ready for deployment on services like Render.

🛠️ Tech Stack
Backend: Python, FastAPI, Gunicorn

Frontend: HTML, Tailwind CSS, JavaScript

AI/ML: PyTorch, Transformers (CLIP)

Database: SQLAlchemy, SQLite

Image Processing: Pillow, ImageHash

APIs & Services: Pexels API (for image sourcing), SendGrid (for email)

Async & Scheduling: FastAPI BackgroundTasks, APScheduler
