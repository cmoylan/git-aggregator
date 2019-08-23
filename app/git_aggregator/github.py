import os
import re
import requests
import urllib


class Github:
    def __init__(self, org_name, base_url="https://api.github.com/orgs/{}"):
        self.org_name = org_name
        self.base_url = base_url


    def organization(self):
        """
        Return the metadata for an organization
        """
        response = requests.get(self.base_url.format(self.org_name),
                                auth=self._auth())
        if self._request_error(response):
            return {}
        return response.json()


    def repositories(self):
        """
        Return all repositories for an organization
        """
        repos = []
        url = self.organization()["repos_url"]
        query = {"per_page": 100}
        response = requests.get(url,
                                auth=self._auth(),
                                params=query)

        if self._request_error(response):
            return []

        [repos.append(repo) for repo in response.json()]

        for i in range(1, int(self._last_page_for(response))):
            params = {"page": i}
            response = requests.get(self.base_url.format(self.org_name),
                                    params=params,
                                    auth=self._auth())
            if self._request_error(response):
                return []

            [repos.append(repo) for repo in response.json()]
        return repos


    def original_repos(self):
        """
        Return all repositories that ARE NOT forked
        """
        return list(filter(lambda x: not x["fork"] , self.repositories()))


    def forked_repos(self):
        """
        Return all repositories that ARE forked
        """
        return list(filter(lambda x: x["fork"] , self.repositories()))


    def followers(self):
        """
        Return the count of followers for an organization
        """
        org = self.organization()
        return org["followers"]


    def labels(self):
        """
        Return unique labels for all repositories across an organization as JSON
        """
        labels = set()
        for repo in self.repositories():
            # match up to the first {
            match = re.search('[^{]*', repo["labels_url"])
            label_url = match[0]
            response = requests.get(label_url)
            if self._request_error(response):
                return []
            for label in response.json():
                labels.add(label["name"])
        return list(labels)


    def languages(self):
        """
        Return all languages across all repositories for an organization
        """
        languages = set()
        for repo in self.repositories():
            languages.add(repo["language"])
        return list(languages)


    def watchers(self):
        """
        Return the count of watchers across all repositories of an organization
        """
        watchers = 0
        for repo in self.repositories():
            watchers += repo["watchers"]
        return watchers


    def _auth(self):
        print(os.environ['HOME'])
        if "GITHUB_USER" in os.environ.keys() and \
           "GITHUB_PASSWORD" in os.environ.keys():
           return (os.environ["GITHUB_USER"],
                   os.environ["GITHUB_PASSWORD"])


    @staticmethod
    def _last_page_for(request):
        if "Link" not in request.headers.keys():
            return 1

        links = request.headers["Link"].split(",")

        for link in links:
            parts = link.split(";")
            if parts[1].strip() == 'rel="last"':
                last_url = re.sub('[<>]', '', parts[0])
                url_parts = urllib.parse.urlparse(last_url)
                query_params = urllib.parse.parse_qs(url_parts.query)
                return query_params['page'][0]
        return 1


    @staticmethod
    def _request_error(response):
        success = response.status_code == requests.codes.ok
        if not success:
            # TODO: log an error here
            pass
        return not success
