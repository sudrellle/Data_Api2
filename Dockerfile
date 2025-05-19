FROM python:3.9-alpine3.13

ENV PYTHONUNBUFFERED=1



COPY ./requirements.txt  /tmp/requirements.txt
COPY ./requirement.dev.txt /tmp/requirement.dev.txt
COPY ./app /app
WORKDIR /app
EXPOSE 8080
ARG DEV=false
##Commande d'execution
#la premiere commande est celle qui fait les mises à jours:/py/bin/pip install --upgrade py
##la second va lire dans le fichier requirements et install ce qui s'y trouve:/py/bin/pip install -r /tmp/requirementstxt
##creation d'un environnement virtuel:python -m venv en rajoutant les "&&" cela permet de surcharger notre systeme avec plusieurs couches
##D'où ici il se passe qu'il s'agit d'une seule commande
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \ 
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
       then /py/bin/pip install -r requirement.dev.txt  ; \
    fi && \    
    rm -rf /tmp/requirements.txt && \
    adduser \
       --disabled-password  \
       --no-create-home \
       django-user

ENV PATH="/py/bin:$PATH" 

USER django-user      
