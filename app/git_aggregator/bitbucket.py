import requests


class Bitbucket:
    def __init__(self, org_name, url="https://api.bitbucket.org/2.0/teams/{}"):
        self.org_name = org_name
        self.url = url


    def organization(self):
        """
        Return metadata for an organization
        """
        response = requests.get(self.url.format(self.org_name))
        if self._request_error(response):
            return []
        return response.json()


    def repositories(self):
        """
        Return all repositories for a bitbucket organization
        """
        url = self.organization()["links"]["repositories"]["href"]
        response = requests.get(url)
        if self._request_error(response):
            return []
        return response.json()["values"]


    def watchers(self):
        """
        Return the count of watchers across all repositories for an organization
        """
        total = 0
        for repo in self.repositories():
            url = repo["links"]["watchers"]["href"]
            response = requests.get(url)
            if self._request_error(response):
                return total
            total += response.json()["size"]
            return total


    def languages(self):
        """
        Return all unique languages across all repositories for an organization
        """
        languages = set()
        for repo in self.repositories():
            if repo["language"]:
                languages.add(repo["language"])
        return list(languages)


    def labels(self):
        # NOTE: does not seem to exist
        return ["not yet mplemented"]


    @staticmethod
    def _request_error(response):
        success = response.status_code == requests.codes.ok
        if not success:
            # TODO: log an error here
            pass
        return not success
