from fastapi import FastAPI

from slr_app.routers import activity, begin, feature_extraction

app = FastAPI(
    debug=True,
    title='SignLingoDetectorApp',
    summary='FastAPI app to detect russian sign language from video.',
    version='0.1.0'
)

app.include_router(activity.router)
app.include_router(begin.router)
app.include_router(feature_extraction.router)
