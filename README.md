# Family Promise of Spokane - DS API
See deployed API at [http://fam-prom-the-end.eba-jknbh7ge.us-east-1.elasticbeanstalk.com](http://fam-prom-the-end.eba-jknbh7ge.us-east-1.elasticbeanstalk.com)

# About Family Promise
Family Promise of Spokane is a US nonprofit organization based in Spokane, WA. They are an organization that helps homeless families as well as preventing families from becoming homeless. They provide shelter for families as well as rental assitance. For the full description visit their website [Family Promise of Spokane](https://www.familypromiseofspokane.org/)

# Current State of DS API (Yes, Actually Read Me)

###### DISCUSS
CORS
Prediction interpretations


## Database
The API currently accesses a development database which contains historical data from August 2020 and earlier. It only partially corresponds with the structure of the database used by the web backend, which will eventually be the official database which this API needs to access. The reason for creating this development database was that we foresaw imminent changes to the web database and saw no sense in building an API on shifting ground.

Looking forward, DS must work _**very**_ closely with Web in order to build an official database which suits all intents and purposes. 

See scripts in the 'migration' folder to understand how the current development database is structured. 

## Exit Predictions
One function of the API is to predict where guests at the shelter will exit to, out of five possible destination categories:
- Permanent Exit
- Temporary Exit
- Emergency Shelter
- Transitional Housing
- Unknown/Other

We in Labs31 were told there was a model already trained for this purpose. However, it quickly became clear that those who created this model had fallen (understandably) into some very treacherous pits. These pits are:
- The historical data provided for training had quite a different feature set from the database used by the web backend. Training on the whole dataset results in a model which can't actually be implemented.
- Guests usually exit _as families_, so a random train-test-split which separates family members will cause leakage. The model will make predictions in the validation set based off where their family member (in the training set) is already known to have exited. This is made terribly clear when you do a time-based split, or a random split which keeps families together. The validation accuracy drops by about 20%.

The solution to these dangers is **caution**. Unfortunately, caution sometimes produces poor metrics. The model currently implemented in the API boasts 45% cross-validation accuracy, and **one** feature (length_of_stay) has 100% of the feature importance. Of course, length_of_stay hardly exists as a feature when a guest first enrolls, so the already-scanty merits of this model are actually worthless until the guest is around for a few weeks. 

The model needs improvement, but without caution any improvements will be useless. I strongly recommend following the below steps as you work on creating a new model. 
1. **Start with Database Structure** - Don't even be tempted to throw an XGBClassifier on the whole historical dataset. Don't do it! Start by looking closely at _migration.py_, seeing what features you have available. If you've worked with Web to add more features to the database, by all means use those!
2. **Make Clean DataFrame with Correct Column Names** - Chisel down the historical dataset and rename the columns so that they match up _exactly_ with the features in the database. Don't leave it to the API to rename every feature, every single call. Try to help FastAPI live up to its name.
3. **Put All Feature Engineering in a Function** - Use this exact function in your API endpoint.
4. **Sort Columns** - This can go in the feature engineering function. It will make it super easy to line up features in the database exactly as they were in the training data.
5. **Train Model Inside Pipenv** - Using Colab, even if it trains faster, could easily destroy hours if you're not careful about package versions. Easier just to train within the actual environment your API is using.

## Visualizations




# Contributors

| [Ben Somerville](https://github.com/bsmrvl) |
| :---: |
| [<img src="https://avatars.githubusercontent.com/u/70228881?s=400&u=05b1dfcb97cd62deaf5f2afacbd6c2372d945530&v=4" width='200' />](https://github.com/bsmrvl) |
| Data Scientist |
| [<img src="https://github.com/favicon.ico" width="15"> ](https://github.com/bsmrvl) |
| [<img src="https://static.licdn.com/sc/h/al2o9zrvru7aqj8e1x2rzsrca" width="15"> ](https://www.linkedin.com/in/ben-somerville/) |

| [Kristine Wang](https://github.com/KristineYW) | [Tyler Etheridge](https://github.com/tyleretheridge) | [Santiago Berniz](https://github.com/sberniz/) | [Leslie Rodriguez](https://github.com/thereactgirl) |
| :---: | :---: | :---: | :---: | 
| [<img src="https://avatars0.githubusercontent.com/u/63246056?s=400&u=a10524916b756eb26132d0803bec3cbe62ede1ef&v=4" width = "200" />](https://github.com/KristineYW) | [<img src="https://avatars3.githubusercontent.com/u/61953470?s=400&u=8f8538f4d10dcb45b9179eb6990d1ef9c1aadc8d&v=4" width = "200" />](https://github.com/tyleretheridge) | [<img src="https://avatars3.githubusercontent.com/u/6207914?s=460&u=8bfaa068f7942170423371ff10e8f04f09f41e81&v=4" width = "200" />](https://github.com/sberniz/) | [<img src="https://avatars3.githubusercontent.com/u/46256764?s=400&u=337301ad07625f6977ed520ff7092ae54bb0852f&v=4" width = "200" />](https://github.com/thereactgirl) |
| TPL | Data Scientist | Data Scientist | Web Developer | Web Developer | 
|[<img src="https://github.com/favicon.ico" width="15"> ](https://github.com/KristineYW) | [<img src="https://github.com/favicon.ico" width="15"> ](https://github.com/tyleretheridge) | [<img src="https://github.com/favicon.ico" width="15"> ](https://github.com/sberniz/) | [<img src="https://github.com/favicon.ico" width="15"> ](https://github.com/thereactgirl) |
| [ <img src="https://static.licdn.com/sc/h/al2o9zrvru7aqj8e1x2rzsrca" width="15"> ](https://www.linkedin.com/in/kristine-wang-ds/) | [ <img src="https://static.licdn.com/sc/h/al2o9zrvru7aqj8e1x2rzsrca" width="15"> ](https://www.linkedin.com/in/tylerjetheridge/) | [ <img src="https://static.licdn.com/sc/h/al2o9zrvru7aqj8e1x2rzsrca" width="15"> ](https://www.linkedin.com/in/santiago-berniz/) | [ <img src="https://static.licdn.com/sc/h/al2o9zrvru7aqj8e1x2rzsrca" width="15"> ](https://www.linkedin.com/in/thereactgirl/) |          

| [Emily Huntwork](https://github.com/Ehuntwork) | [Abdi Mo](https://github.com/abdimohamud) | [Isaiah Fowler](https://github.com/idongessien) |
| :---: | :---: | :---: |  
| [<img src="https://avatars1.githubusercontent.com/u/27293120?s=400&u=e6c0fc75189b75dea5233e02562784ed1cfa2faf&v=4" width = "200" />](https://github.com/Ehuntwork) | [<img src="https://avatars1.githubusercontent.com/u/65041807?s=400&u=2ff3514545d906fe2b734fed79c7f8d640b58ae6&v=4" width = "200" />](https://github.com/abdimohamud) | [<img src="https://avatars1.githubusercontent.com/u/66272034?s=400&u=db133631ead14125bb0d5e9515932985c6293448&v=4" width = "200" />](https://github.com/isaiah-j) | 
| Web Developer | Web Developer | Web Developer | 
|[<img src="https://github.com/favicon.ico" width="15"> ](https://github.com/Ehuntwork) | [<img src="https://github.com/favicon.ico" width="15"> ](https://github.com/abdimohamud) | [<img src="https://github.com/favicon.ico" width="15"> ](https://github.com/isaiah-j) | 
| [ <img src="https://static.licdn.com/sc/h/al2o9zrvru7aqj8e1x2rzsrca" width="15"> ](https://www.linkedin.com/in/emily-huntwork/) | [ <img src="https://static.licdn.com/sc/h/al2o9zrvru7aqj8e1x2rzsrca" width="15"> ](https://www.linkedin.com/in/abdinajib-mohamud/) | [ <img src="https://static.licdn.com/sc/h/al2o9zrvru7aqj8e1x2rzsrca" width="15"> ](https://www.linkedin.com/in/isaiah-fowler/) |              

<br>          
<br>
<br> 

![fastapi](https://img.shields.io/badge/fastapi-0.62.0-blue)
![pandas](https://img.shields.io/badge/pandas-1.1.5-blueviolet)

![uvicorn](https://img.shields.io/badge/uvicorn-0.13.1-ff69b4)
![psycopg2](https://img.shields.io/badge/psycopg2-2.8.6-informational)
![sqlalchemy](https://img.shields.io/badge/sqlalchemy-1.3.21-green)

![scikit-learn](https://img.shields.io/badge/scikit--learn-0.23.2-yellow)
![plotly-express](https://img.shields.io/badge/plotly--express-0.4.1-informational)


# Deployed Product
[Front End Dashboard](https://a.familypromisesofspokane.dev/) |
[Back End API](https://family-promise-a-be.herokuapp.com/) |
[Data Science API](http://fam-prom-the-end.eba-jknbh7ge.us-east-1.elasticbeanstalk.com)

# Repositories
[Front End](https://github.com/Lambda-School-Labs/family-promise-spokane-fe-a) |
[Back End](https://github.com/Lambda-School-Labs/family-promise-spokane-be-a) |
[Data Science](https://github.com/Lambda-School-Labs/family-promise-spokane-ds-a)

# Installing Locally

Simply clone this repo, enter its directory, and...
```
pipenv install
```
**If you're on Windows**, it is not recommended to mess with the Pipfile or Pipfile.lock, as this gave us issues while deploying to AWS. If you have to install new packages, either test locally in Docker to make sure the deploy will work, OR reinstall the pipenv in WSL and use that from there on out.


## Environment Variables

The only required environment variable is DATABASE_URL. Create a new '.env' file in your local repo and add the below.

    DATABASE_URL="YOUR-POSTGRES-DATABASE-URL"


# Deploying to AWS

First get your AWS credentials and access keys. Then follow the [Lambda instructions here](https://docs.labs.lambdaschool.com/data-science/tech/aws-elastic-beanstalk).

Note that at the time of this writing, Lambda has recommended you delete the Dockerfile and use the Elastic Beanstalk 'Python' option instead. Personally, I preferred Docker, and would continue to recommend it, as it allows you to perform _exact_ tests locally.

In the Lambda instructions, when you get to **Deploy the first time** step **7**, simply put `--platform docker` instead of the recommended `--platform python-3.7`. That's the only thing you have to do differently.

Of course, don't forget to add your database url to the Elastic Beanstalk environment variables!!


# Architecture / Endpoints

The DS API has a handful of endpoints which can be called by the Web frontend or backend through simple GET requests. Visit [the API homepage](http://fam-prom-the-end.eba-jknbh7ge.us-east-1.elasticbeanstalk.com) to understand these endpoints via the interactive docs. 


# Bugs

- Check first to see if your issue has already been reported.
- Check to see if the issue has recently been fixed by attempting to reproduce the issue using the latest master branch in the repository.
- Create a live example of the problem.
- Submit a detailed bug report including your environment & browser, steps to reproduce the issue, actual and expected outcomes, where you believe the issue is originating from, and any potential solutions you have considered.


# Support
Reach out to [Ben](https://github.com/bsmrvl).

# Contributing

When contributing to this repository, please first discuss the change you wish to make via issue, email, or any other method with the owners of this repository before making a change.

Describe what you have changed in this repo as a team
Provide examples and descriptions of components, how props are handled, where to find these changes, database tables, models, etc.

## Feature Requests

We would love to hear from you about new features which would improve this app and further the aims of our project. Please provide as much detail and information as possible to show us why you think your new feature should be implemented.

## Pull Requests

If you have developed a patch, bug fix, or new feature that would improve this app, please submit a pull request. It is best to communicate your ideas with the developers first before investing a great deal of time into a pull request to ensure that it will mesh smoothly with the project.

Remember that this project is licensed under the MIT license, and by submitting a pull request, you agree that your work will be, too.

## Pull Request Guidelines

- Ensure any install or build dependencies are removed before the end of the layer when doing a build.
- Update the README.md with details of changes to the interface, including new plist variables, exposed ports, useful file locations and container parameters.
- Ensure that your code conforms to our existing code conventions and test coverage.
- Include the relevant issue number, if applicable.
- You may merge the Pull Request in once you have the sign-off of two other developers, or if you do not have permission to do that, you may request the second reviewer to merge it for you.

## Attribution

These contribution guidelines have been adapted from [this good-Contributing.md-template](https://gist.github.com/PurpleBooth/b24679402957c63ec426).

# Documentation
[Front End](https://github.com/Lambda-School-Labs/family-promise-spokane-fe-a/blob/main/README.md)

[Back End](https://github.com/Lambda-School-Labs/family-promise-spokane-be-a/blob/main/README.md)

[Data Science](https://github.com/Lambda-School-Labs/family-promise-spokane-ds-a/blob/main/README.md)
