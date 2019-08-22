import logging

import flask
from flask import Response, jsonify

app = flask.Flask("user_profiles_api")
logger = flask.logging.create_logger(app)
logger.setLevel(logging.INFO)


@app.route("/health-check", methods=["GET"])
def health_check():
    """
    Endpoint to health check API
    """
    app.logger.info("Health Check!")
    return Response("All Good!", status=200)


@app.route("/organizations/<name>", methods=["GET"])
def organizations(name):
    github = Github(name)
    response = {
        "repo_count": {
            "original": len(github.original_repos()),
            "forked": len(github.forked_repos()) },
        "followers": github.followers(),
        "watchers": github.watchers(),
        "languages": github.languages()
    }
    return Response("{}".format(response), status=200)
    #return jsonify(github.repositories())


@app.route("/organizations/<name>/repositories", methods=["GET"])
def repositories(name):
    github = Github(name)
    bitbucket = Bitbucket(name)
    response = {
        "github": {

        },
        "bitbucket": {
            "original": len(bitbucket.repositories())
        }

    }
    return Response("{}".format(response), status=200)


# TODO: probably want a few restful endpoints like
#       /org/<name>/repos
#       /org/<name>/watchers
#       etc


# Total number of public repos (seperate by original repos vs forked repos)
# ○ Total watcher/follower count
# ○ A list/count of languages used across all public repos
# ○ A list/count of repo topics
#class Cache:
#    def __init__(self):
#        pass

#def cached(func):
#    " Used on methods to convert them to methods that replace themselves\
#        with their return value once they are called. "
#
#    def cache(*args):
#        self = args[0] # Reference to the class who owns the method
#        funcname = func.__name__
#        ret_value = func(self)
#        setattr(self, funcname, ret_value) # Replace the function with its value
#        return ret_value # Return the result of the function
#
#    return property(cache)

def cached(should_cache):
    def wrap(func):
        def wrapper(*args):
            if should_cache:
                pass
            else:
                func(*args)
        return wrapper
    return wrap



class Bitbucket:
    def __init__(self, org_name, cached=False):
        self._adapter = BitbucketAdapter(org_name)


    def repositories(self):
        return self._adapter.repositories()


    def followers(self):
        # can come from size for each repo
        pass

    def languages(self):
        languages = set()
        for repo in self.repositories():
            langauges.add(repo["language"])
        return list(languages)


    def topics(self):
        # FIXME: figure this out
        pass


class Github:
    _all_repos = None

    def __init__(self, org_name, cached=False):
        self._adapter = GithubAdapter(org_name)


    def repos(self):
        # TODO: should use caching layer
        if self._all_repos is None:
            self._all_repos = self._adapter.repositories()
        return self._all_repos


    def original_repos(self):
        # TODO: convert to list comprehension
        result = []
        for repo in self.repos():
            if repo["fork"] is False:
                result.append(repo)
        return result


    def forked_repos(self):
        # FIXME: should use a list comprehension
        # use a set...whatever is in original_repos but not repositories is a fork
        #return [(lambda repo: repo["fork"])(repo) for repo in self.repos()]
        return list(filter(lambda x: x["fork"] , self.repos()))


    def followers(self):
        # available in the org response itself
        org = self._adapter.organization()
        return org["followers"]


    def labels(self):
        # TODO: need to hit another URL to get these...
        pass


    def languages(self):
        languages = set()
        for repo in self.repos():
            languages.add(repo["language"])
        return list(languages)


    def watchers(self):
        # have to crawl every repo and count up followers
        watchers = 0
        for repo in self.repos():
            watchers += repo["watchers"]
        return watchers


import requests
import urllib

# class GithubAdapter(Adapter)
class GithubAdapter:
    # FIXME: should limit this to code that interacts with the api
    # FIXME: make a second class for the logicy bits
    def __init__(self, org_name):
        self.org_name = org_name

    # FIXME: should use the hypermedia api and get the endpoints from there
    # FIXME: only pull org if it has changed
    # FIXME: should store all this stuff...


    def organization(self):
        response = requests.get("https://api.github.com/orgs/{}".format(self.org_name),
                                auth=self._auth())
        return response.json()


    def repositories(self):
        # TODO: handle failure
        # TODO: get link from hypermedia api
        #print("$$$$$$$$$$$$$$$$$$$$$$$$$ making a request $$$$$$$$$$$$$$$$$$$$$$$$$$$$4444")
        repos = []
        query = {"per_page": 100}
        response = requests.get("https://api.github.com/orgs/{}/repos".format(self.org_name),
                                auth=self._auth(),
                                params=query)

        last = GithubAdapter.last_page_for(response)
        print("got last", last)
        for repo in response.json():
            repos.append(repo)

        # get this working
        #for i in range(1, int(last)):
        #    params = {"page": i}
        #    response = requests.get("https://api.github.com/orgs/{}/repos".format(self.org_name),
        #                            params=params,
        #                            auth=self._auth())
        #    for repo in response.json():
        #        repos.append(repo)

        return repos

    def _auth(self):
        #return requests.auth.HTTPBasicAuth
        return ('cmoylan-test', 'passwordcandle123')


    def _authorized_request(self, url, params):
        pass

    @staticmethod
    def last_page_for(request):
        import re
        print("HEADERS--------------------------------------")
        print(request.headers)
        links = request.headers["Link"].split(",")

        for link in links:
            parts = link.split(";")
            if parts[1].strip() == 'rel="last"':
                last_url = re.sub('[<>]', '', parts[0])
                print(last_url)
                url_parts = urllib.parse.urlparse(last_url)
                query_params = urllib.parse.parse_qs(url_parts.query)
                return query_params['page'][0]




class BitbucketAdapter:
    def __init__(self, org_name):
        self.org_name = org_name


    def organization(self):
        response = requests.get("https://api.bitbucket.org/2.0/teams/{}".format(self.org_name))
        return response.json()

    def repositories(self):
       # https://api.bitbucket.org/2.0/teams/mailchimp
       url = self.organization()["links"]["repositories"]["href"]
       response = requests.get(url)
       return response.json()["values"]
