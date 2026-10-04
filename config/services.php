<?php

return [

    /*
    |--------------------------------------------------------------------------
    | Third Party Services
    |--------------------------------------------------------------------------
    |
    | This file is for storing the credentials for third party services such
    | as Resend, Postmark, AWS, and more. This file provides the de facto
    | location for this type of information, allowing packages to have
    | a conventional file to locate these values.
    |
    */

    'musicbrainz' => [
        'live_enabled' => env('MUSICBRAINZ_LIVE_ENABLED', false),
        'base_url' => env('MUSICBRAINZ_BASE_URL', 'https://musicbrainz.org/ws/2'),
        'user_agent' => env('MUSICBRAINZ_USER_AGENT', 'SongChartNext/0.1 (+https://github.com/fusumivietnam/SongChart-Next)'),
        'timeout_seconds' => 8,
        'max_attempts' => 3,
        'success_retention_days' => 30,
        'error_retention_days' => 7,
    ],

    'postmark' => [
        'key' => env('POSTMARK_API_KEY'),
    ],

    'resend' => [
        'key' => env('RESEND_API_KEY'),
    ],

    'ses' => [
        'key' => env('AWS_ACCESS_KEY_ID'),
        'secret' => env('AWS_SECRET_ACCESS_KEY'),
        'region' => env('AWS_DEFAULT_REGION', 'us-east-1'),
    ],

    'slack' => [
        'notifications' => [
            'bot_user_oauth_token' => env('SLACK_BOT_USER_OAUTH_TOKEN'),
            'channel' => env('SLACK_BOT_USER_DEFAULT_CHANNEL'),
        ],
    ],

];
