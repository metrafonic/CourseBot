FROM python:3.7
RUN pip install virtualenv
ADD . /app
WORKDIR
RUN pip install -r requirements.txt
CMD [ "python", "./CourseBot" ]
