FROM python:3.7-slim
RUN mkdir /app
WORKDIR /app
COPY ./libs /app/libs
ADD requirements.txt /app/
RUN pip install -r requirements.txt
COPY ./src /app
ENTRYPOINT ["python", "-m"]
CMD ["la_proj.api.main"]