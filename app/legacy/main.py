from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app import db, ml, viz

description = """
This is our FastAPI DS API. to use the current api send a post request to 
/getdata endpoint with the member_id. a predicted exit destination along with 
top features will show in a JSON format. Below is an example on how to use it 
interactively. 

To use these interactive docs:
- Click on an endpoint below
- Click the **Try it out** button
- Edit the Request body or any parameters
- Click the **Execute** button
- Scroll down to see the Server response Code & Details

To edit description after some endpoints has been added.
Edit your app's title and description. See [https://fastapi.tiangolo.com/tutorial/metadata/](https://fastapi.tiangolo.com/tutorial/metadata/)

"""

app = FastAPI(
    title='Family Promise of Spokane - Labs 29 ',
    description=description,
    docs_url='/',
)
# tags to show on FatsAPI 
# app.include_router(db.router, tags=['Database'])
app.include_router(ml.router, tags=['Machine Learning'])
app.include_router(viz.router, tags=['Visualization'])
#app.include_router(viz.router, tags=['Shapley'])

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

if __name__ == '__main__':
    uvicorn.run(app)