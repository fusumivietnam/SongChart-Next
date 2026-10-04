<?php

namespace App\Music\Providers;

enum ProviderFetchStatus: string
{
    case Success = 'success';
    case NotFound = 'not_found';
    case Malformed = 'malformed';
    case Unavailable = 'unavailable';
    case Disabled = 'disabled';
}
