"""Main app file."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from . import predict, records, visualize

description = """
An API for accessing predictive data and visualizations for [Family Promise of Spokane]\
(https://a.familypromisesofspokane.dev/).

To use these interactive docs:
- Click on an endpoint below
- Click the **Try it out** button
- Edit the Request body or any parameters
- Click the **Execute** button
- Scroll down to see the Server response Code & Details
"""

app = FastAPI(
    title='Family Promise - DS API',
    description=description,
    docs_url='/',
)

app.include_router(predict.router, tags=['Predictions'])
app.include_router(visualize.router, tags=['Visualizations'])
app.include_router(records.router, tags=['Records'])


# TODO - Incorporate this! API should not be publicly accessible.
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

if __name__ == '__main__':
    uvicorn.run(app)