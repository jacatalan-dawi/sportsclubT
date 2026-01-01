# docker/nginx/Dockerfile
FROM nginx:stable-trixie
EXPOSE 80

# COPY is relative to the context defined in the `docker-compose.yml` file,
# i.e., the project root, not the Dockerfile location.
COPY docker/nginx/nginx.conf /etc/nginx/nginx.conf
