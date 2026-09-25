# Local development and build targets; production serving requires a separate release decision.
FROM php:8.4-fpm-bookworm AS php-base
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates git unzip libpq-dev libicu-dev libonig-dev libzip-dev libsqlite3-dev \
    && docker-php-ext-install -j"$(nproc)" pdo_pgsql pdo_sqlite intl mbstring zip opcache \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /var/www/html
RUN php -r 'foreach (["pdo_pgsql","pdo_sqlite","intl","mbstring","zip","Zend OPcache"] as $ext) { if (!extension_loaded($ext)) {fwrite(STDERR, "Missing PHP extension: $ext\n"); exit(1);}}'

FROM composer:2 AS composer-bin
FROM node:22-bookworm AS node-bin

FROM php-base AS php-toolchain
COPY --from=composer-bin /usr/bin/composer /usr/local/bin/composer
COPY --from=node-bin /usr/local/bin/node /usr/local/bin/node
COPY --from=node-bin /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && npm install --global --ignore-scripts pnpm@10.17.1
ENV COMPOSER_ALLOW_SUPERUSER=1
RUN composer --version && node --version && pnpm --version

FROM php-toolchain AS development
COPY . .
RUN mkdir -p bootstrap/cache storage/framework/cache storage/framework/sessions storage/framework/views storage/logs
RUN test -s composer.lock && test -s pnpm-lock.yaml \
    && composer install --prefer-dist --no-interaction --no-progress \
    && pnpm install --frozen-lockfile
EXPOSE 8000 5173
CMD ["php", "artisan", "serve", "--host=0.0.0.0", "--port=8000"]

FROM development AS frontend-build
RUN pnpm run build && pnpm run types:check

FROM php-base AS production
COPY --from=composer-bin /usr/bin/composer /usr/local/bin/composer
COPY . .
RUN mkdir -p bootstrap/cache storage/framework/cache storage/framework/sessions storage/framework/views storage/logs
RUN test -s composer.lock && composer install --no-dev --prefer-dist --no-interaction --no-progress --optimize-autoloader \
    && rm /usr/local/bin/composer \
    && mkdir -p storage/framework/cache storage/framework/sessions storage/framework/views storage/logs bootstrap/cache \
    && chown -R www-data:www-data storage bootstrap/cache
COPY --from=frontend-build /var/www/html/public/build /var/www/html/public/build
USER www-data
EXPOSE 9000
CMD ["php-fpm"]
