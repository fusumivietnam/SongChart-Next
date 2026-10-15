<?php

http_response_code(503);
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
header('Retry-After: 2');

echo json_encode([
    'status' => 'bootstrapping',
], JSON_UNESCAPED_SLASHES) . PHP_EOL;
