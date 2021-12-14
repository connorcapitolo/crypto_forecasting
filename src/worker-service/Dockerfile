# Use the official Debian-hosted Python image
FROM python:3.8-slim-buster

ARG DEBIAN_PACKAGES="build-essential git"

# Prevent apt from showing prompts
ENV DEBIAN_FRONTEND=noninteractive

# Python wants UTF-8 locale
ENV LANG=C.UTF-8

# Tell pipenv where the shell is. This allows us to use "pipenv shell" as a
# container entry point.
ENV PYENV_SHELL=/bin/bash

# Tell Python to disable buffering so we don't lose any logs.
ENV PYTHONUNBUFFERED=1

# Ensure we have an up to date baseline, install dependencies and
# create a user so we don't run the app as root
RUN set -ex; \
    apt-get update && \
    apt-get -y install sudo &&\
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends $DEBIAN_PACKAGES && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir --upgrade pip && \
    pip install pipenv && \
    useradd -ms /bin/bash app -d /home/app -u 1000 -p "$(openssl passwd -1 Passw0rd)" && \
    mkdir -p /app && \
    chown app:app /app



#USER root
#RUN sudo chown -R celery:celery celerybeat-schedule

#RUN ln -s /run/shm /dev/shm

#RUN chown nobody:nogroup "celerybeat-schedule"
#USER nobody
#CMD ["celery", "-A", "your_project.celery_app", "-E", "-B"]

#RUN chown nobody:nogroup "celerybeat-schedule"
#USER nobody
#CMD ["celery", "-A", "your_project.celery_app", "-E", "-B"]
# Switch to the new user
#RUN echo 'root:Docker!' | chpasswd

#RUN chown -R app:app /app
#RUN chmod 777 /app


USER app
WORKDIR /app

# Install python packages
ADD Pipfile Pipfile.lock /app/

RUN pipenv sync

# Add the rest of the source code. This is done last so we don't invalidate all
# layers when we change a line of code.
# we need this for the production mode; it was commented out and fine in dev mode since we were already mounting
ADD --chown=app:app . /app

# adding the Binance API secrets+key (should eventually move to .env.dev file)
ENV BINANCE_API_KEY="RLis1zPSdrqFz1uP28k9aJlhElR9lJnynaCldpSNeob2PrnhnoMiGAA7drlZdpC4"
ENV BINANCE_SECRETS_KEY="hplmjruPIXcHAQSC6F4OUPwoJvXfwjTeAeqJQiKAh7xAQC9QbZSo0y3yCI4gtbOH"

# Entry point
ENTRYPOINT ["/bin/bash","./docker-entrypoint.sh"]