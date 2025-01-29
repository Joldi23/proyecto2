FROM httpd:2.4.33-alpine

RUN apk update && apk upgrade

RUN apk add --no-cache apache2-utils apache2-proxy apache2-http2 curl

COPY demo.apache.conf /usr/local/apache2/conf/demo.apache.conf

RUN echo "Include /usr/local/apache2/conf/demo.apache.conf" \
    >> /usr/local/apache2/conf/httpd.conf
    
COPY ./static /var/www/html

RUN mkdir -p /var/www/html/fotos

RUN chown -R www-data:www-data /var/www/html/fotos && chmod -R 755 /var/www/html/fotos

EXPOSE 80