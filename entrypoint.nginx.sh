#!/bin/sh

envsubst '${API_DOMAIN} ${GRAFANA_DOMAIN} ${ADMIN_IP} ${FLOWER_DOMAIN} ${ADMIN_DOMAIN} ${DJANGO_ADMIN_PATH}' < /etc/nginx/nginx.template.conf > /etc/nginx/nginx.conf

exec nginx -g "daemon off;"
