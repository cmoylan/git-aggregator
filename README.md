# Git Aggregator

A Flask app to aggregate git data from Github and Bitbucket

## Install:

You can use a virtual environment (conda, venv, etc):
```
conda env create -f environment.yml
source activate user-profiles
```

Or just pip install from the requirements file
``` 
pip install -r requirements.txt
```

## Running the code

### Spin up the service

```
# start up local server
python -m run 
```

### Rate limiting

For smaller organizations anonymous access to both APIs should be fine. If you
get rate-limited by Github you can set a username and password through the
environment which will authenticate and increase the Github API limits
substantially. In the real world, this would take an OAuth token rather than
a username/password.

```
source config.sh
python -m run
```


### Making Requests

Make sure the server is runnin
```
curl -i "http://127.0.0.1:5000/health-check"

```

Links to the organzation resources
```
curl -i "http://127.0.0.1:5000/organizations/<name>"
```

Repositories in the organization
```
curl -i "http://127.0.0.1:5000/organizations/<name>/repositories"
```

Watchers across all repositories in the organization
```
curl -i "http://127.0.0.1:5000/organizations/<name>/watchers"
```

Languages across all repositories in the organization.
```
curl -i "http://127.0.0.1:5000/organizations/<name>/languages"

```

Topics/labels across all repositories in the organization
```
curl -i "http://127.0.0.1:5000/organizations/<name>/labels"
```


## What'd I'd like to improve on...

### Tests

app.git_aggregator.Github and app.git_aggregator.Bitbucket need unit tests. I
would save successful API requests as JSON and use this to stub the responses of
the Github and Bitbucket APIs.

I would test that if a request came back with a non-200 status an error was
logged and an empty response was returned. I would want to be sure one
unsuccessful request did not cause the entire aggregation process to halt.

I would test the API paging to make sure the entire result set was being
aggregated.

### Caching

None of the API requests are cached. I would cache the list of repositories.
From my interaction with both APIs, it is unclear if there is a way to determine
if organization data has been updated without fetching the entire resource. But
if something like a hash of the organization existed, it would be easy to
determine when to break and update the cache.

The instances of the Github and Bitbucket classes can be cached between web
requests because they probably won't change that often. I would want some way
for the cache to expire after a certain amount of time had passed.
