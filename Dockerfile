FROM python:3.12-slim

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

CMD ["python", "-m", "refiner"]
