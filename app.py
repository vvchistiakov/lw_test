#!/usr/bin/env python

import argparse
import logging
import logging.config
import os
import io
import yaml
from flask import Flask, request, render_template, flash, redirect, send_file
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config

app = Flask(__name__)
app.secret_key = 'super secret key'


def parse_init():
    parser = argparse.ArgumentParser(description="lw_test")
    parser.add_argument("-p", "--port", dest="port", help="listen port", default=8080)
    parser.add_argument("--s3_region", dest="s3_region", help="s3 region name", default=None)
    parser.add_argument("--s3_bucket", dest="s3_bucket", help="s3 bucket name", required=True)
    return parser.parse_args()


def parse_yaml(filename='settings.yaml'):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return yaml.safe_load(stream=f)
    return None


def logger_init(name="root", config_path="logging.yaml"):
    if os.path.exists(path=config_path):
        config = parse_yaml(filename="logging.yaml")
        logging.config.dictConfig(config)
    else:
        logging.basicConfig()
    return logging.getLogger(name=name)


def init_s3(bucket_name: str, logger: logging.Logger, region: str = None):
    if region is None:
        logger.error(msg="s3 region is not defined")
        raise Exception("s3 region error")
    try:
        s3 = boto3.resource('s3', region_name=region)
        b = s3.Bucket(bucket_name)
        b.load()
        logger.debug(msg="S3 bucket {name} was created at {date}.".format(name=b.name, date=b.creation_date))
    except ClientError as e:
        logger.error(e)
        return None
    return b


def upload_file(bucket, file, logger: logging.Logger):
    filename = file.filename

    if filename in bucket.objects.all():
        logger.error(msg="File {file} already exists into the bucket".format(file=filename))
        return 1
    try:
        bucket.upload_fileobj(Fileobj=file, Key=filename)
    except ClientError as e:
        logger.error(e)
        return 2
    return 0


def download_file(bucket, filename, logger: logging.Logger):
    file_obj = io.BytesIO()
    bucket.download_fileobj(filename, file_obj)
    return file_obj


def list_files(bucket, logger: logging.Logger):
    return bucket.objects.all()


@app.route("/", methods=["GET"])
def index():
    objects = list_files(bucket=bucket, logger=logger)
    return render_template("index.html", files=objects)


@app.route("/upload", methods=["POST"])
def upload():
    if request.method == "POST":
        if "f" not in request.files:
            flash('No file was provided')
            logger.error("No file was provided")
            return redirect(request.url)
        file = request.files["f"]
        if file.filename == "":
            flash('No selected file')
            logger.error("No selected file")
            return redirect(request.url)
        logger.debug(msg="Upload file {file}".format(file=file.filename))
        upload_file(bucket=bucket, file=file, logger=logger)
        #todo add processing error
    return redirect("/")


@app.route("/download/<name>", methods=["GET"])
def download(name):
    if request.method == "GET":
        file = download_file(bucket=bucket, filename=name, logger=logger)
        return send_file(file, attachment_filename=name, as_attachment=True)


@app.route("/hello", methods=["GET"])
def hello():
    return "Hello"


if __name__ == "__main__":
    # connect logger
    logger = logger_init()

    logger.debug("==Start==")
    # connect args
    args = parse_init()
    logger.debug("S3 region is: {region}".format(region=args.s3_region))
    logger.debug("S3 bucket is: {bucket}".format(bucket=args.s3_bucket))
    bucket = init_s3(bucket_name=args.s3_bucket, logger=logger, region=args.s3_region)

    # run app
    app.run(host="0.0.0.0", port=args.port)
