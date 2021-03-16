FROM python:3.9-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ./app.py --s3_bucket=${S3_BUCKET} --s3_region=${S3_REGION}

