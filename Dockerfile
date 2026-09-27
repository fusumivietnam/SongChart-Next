# syntax=docker/dockerfile:1
# Development stays ergonomic; production is deliberately minimal and is not yet a deployable web stack.
FROM php:8.4-fpm-bookworm AS php-extension-builder
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev libicu-dev libonig-dev libzip-dev libsqlite3-dev \
    && docker-php-ext-install -j"$(nproc)" pdo_pgsql pdo_sqlite intl mbstring zip opcache \
    && rm -rf /var/lib/apt/lists/*

FROM php:8.4-fpm-bookworm AS php-runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates libpq5 libicu72 libonig5 libzip4 libsqlite3-0 \
    && rm -rf /var/lib/apt/lists/*
COPY --from=php-extension-builder /usr/local/lib/php/extensions/ /usr/local/lib/php/extensions/
COPY --from=php-extension-builder /usr/local/etc/php/conf.d/ /usr/local/etc/php/conf.d/
WORKDIR /var/www/html
RUN php -r 'foreach (["pdo_pgsql","pdo_sqlite","intl","mbstring","zip","Zend OPcache"] as $ext) { if (!extension_loaded($ext)) {fwrite(STDERR, "Missing PHP extension: $ext\n"); exit(1);}}'

FROM composer:2 AS composer-bin
FROM node:22-bookworm AS node-bin

FROM php-runtime AS php-toolchain
COPY --from=composer-bin /usr/bin/composer /usr/local/bin/composer
COPY --from=node-bin /usr/local/bin/node /usr/local/bin/node
COPY --from=node-bin /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && npm install --global --ignore-scripts pnpm@10.17.1
ENV COMPOSER_ALLOW_SUPERUSER=1
RUN composer --version && node --version && pnpm --version

FROM php-toolchain AS app-source
COPY . .
RUN mkdir -p bootstrap/cache storage/framework/cache storage/framework/sessions storage/framework/views storage/logs \
    && test -s composer.lock && test -s pnpm-lock.yaml

FROM app-source AS development
EXPOSE 8000 5173
CMD ["php", "artisan", "serve", "--host=0.0.0.0", "--port=8000"]

FROM app-source AS build-deps
RUN composer install --prefer-dist --no-interaction --no-progress \
    && pnpm install --frozen-lockfile

FROM build-deps AS frontend-build
RUN pnpm run build && pnpm run types:check

FROM php-runtime AS production-deps
COPY --from=composer-bin /usr/bin/composer /usr/local/bin/composer
COPY composer.json composer.lock artisan ./
COPY app ./app
COPY bootstrap ./bootstrap
COPY config ./config
COPY database ./database
COPY routes ./routes
RUN mkdir -p bootstrap/cache storage/framework/cache storage/framework/sessions storage/framework/views storage/logs \
    && composer install --no-dev --prefer-dist --no-interaction --no-progress --optimize-autoloader \
    && composer check-platform-reqs \
    && rm -rf /root/.composer/cache

FROM php-runtime AS production
COPY --from=production-deps /var/www/html/vendor ./vendor
COPY --from=production-deps /var/www/html/bootstrap ./bootstrap
COPY app ./app
COPY config ./config
COPY database ./database
COPY public ./public
COPY resources/views ./resources/views
COPY routes ./routes
COPY artisan composer.json composer.lock ./
COPY --from=frontend-build /var/www/html/public/build ./public/build
RUN mkdir -p storage/framework/cache storage/framework/sessions storage/framework/views storage/logs bootstrap/cache \
    && chown -R www-data:www-data storage bootstrap/cache
USER www-data
EXPOSE 9000
CMD ["php-fpm"]
