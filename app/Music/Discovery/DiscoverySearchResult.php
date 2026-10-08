<?php

namespace App\Music\Discovery;

final readonly class DiscoverySearchResult
{
    /** @param list<DiscoverySearchItem> $items */
    public function __construct(
        public string $query,
        public array $items,
    ) {}

    /** @return array{query:string,items:list<array{type:string,id:string,slug:string,name:string,detail:string,path:string}>} */
    public function toArray(): array
    {
        return [
            'query' => $this->query,
            'items' => array_map(
                static fn (DiscoverySearchItem $item): array => $item->toArray(),
                $this->items,
            ),
        ];
    }
}
