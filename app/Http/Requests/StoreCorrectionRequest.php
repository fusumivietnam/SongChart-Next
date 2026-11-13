<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

final class StoreCorrectionRequest extends FormRequest
{
    public function authorize(): bool
    {
        // Public intake is intentionally anonymous.
        return true;
    }

    /**
     * @return array<string, array<int, string>>
     */
    public function rules(): array
    {
        return [
            'subject_type' => ['required', 'string', 'in:artist,release,recording'],
            'subject_id' => ['required', 'string', 'ulid'],
            'claim' => ['required', 'string', 'max:4000'],
            'evidence_url' => ['nullable', 'string', 'max:2048', 'url:http,https'],
        ];
    }
}
