<?php

namespace App\Music\Discovery;

final readonly class DiscoverySearchItem
{
    public function __construct(
        public string $type,
        public string $id,
        public string $slug,
        public string $name,
        public string $detail,
        public string $path,
        public int $score,
    ) {}

    /** @return array{type:string,id:string,slug:string,name:string,detail:string,path:string} */
    public function toArray(): array
    {
        return [
            'type' => $this->type,
            'id' => $this->id,
            'slug' => $this->slug,
            'name' => $this->name,
            'detail' => $this->detail,
            'path' => $this->path,
        ];
    }
}
