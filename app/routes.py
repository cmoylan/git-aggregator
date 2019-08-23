import logging

import flask
from flask import Response, jsonify, url_for
from app.git_aggregator.bitbucket import Bitbucket
from app.git_aggregator.github import Github


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
    """
    Endpoint to get RESTful links for organization
    """
    response = {
        "repositories_url": url_for("repositories", name=name, _external=True),
        "watchers_url": url_for("watchers", name=name, _external=True),
        "languages_url": url_for("languages", name=name, _external=True),
        "labels_url": url_for("labels", name=name, _external=True) }

    return jsonify(response)


@app.route("/organizations/<name>/repositories", methods=["GET"])
def repositories(name):
    """
    Endpoint to get repositories for given organization
    """
    github = Github(name)
    bitbucket = Bitbucket(name)
    response = {
         "github": {
             "original": len(github.original_repos()),
             "forked": len(github.forked_repos()) },
        "bitbucket": {
            "original": len(bitbucket.repositories()) } }
    return jsonify(response)


@app.route("/organizations/<name>/watchers")
def watchers(name):
    """
    Endpoing to get watchers for all repositories of a given organization
    """
    github = Github(name)
    bitbucket = Bitbucket(name)
    response = {
        "github": {
            "count": github.watchers() },
        "bitbucket": {
            "count": bitbucket.watchers() } }
    return jsonify(response)


@app.route("/organizations/<name>/languages")
def languages(name):
    """
    Endpoint to get unique languages for a given organization
    """
    github = Github(name)
    bitbucket = Bitbucket(name)

    github_languages = github.languages()
    bitbucket_languages = bitbucket.languages()

    response = {
        "github": {
            "count": len(github_languages),
            "values": github_languages },
        "bitbucket": {
            "count": len(bitbucket_languages),
            "values": bitbucket_languages } }
    return jsonify(response)


@app.route("/organizations/<name>/labels")
def labels(name):
    """
    Endoint to get labels from all repositories of a given organization
    """
    github = Github(name)
    bitbucket = Bitbucket(name)

    github_labels = github.labels()
    bitbucket_labels = bitbucket.labels()

    response = {
        "github": {
            "count": len(github_labels),
            "values": github_labels } }
    return jsonify(response)
