<?php

declare(strict_types=1);

use App\Music\Discovery\DiscoverySearch;
use Illuminate\Contracts\Console\Kernel;
use Illuminate\Support\Facades\DB;

require __DIR__.'/../vendor/autoload.php';

$app = require __DIR__.'/../bootstrap/app.php';
$app->make(Kernel::class)->bootstrap();

$search = $app->make(DiscoverySearch::class);
$query = 'signals at dawn';
$iterations = 25;
$durationsMs = [];

for ($i = 0; $i < $iterations; $i++) {
    $started = hrtime(true);
    $result = $search->search($query);
    $durationsMs[] = (hrtime(true) - $started) / 1_000_000;

    if ($result->items === []) {
        throw new RuntimeException('Benchmark fixture query returned no canonical search results.');
    }
}

sort($durationsMs);
$planRows = DB::select(
    "EXPLAIN (ANALYZE, FORMAT JSON) SELECT id, title FROM releases WHERE LOWER(title) LIKE ? ESCAPE '\\' LIMIT 20",
    ['%signals at dawn%'],
);

$plan = $planRows[0]->{'QUERY PLAN'} ?? null;
if (is_string($plan)) {
    $decoded = json_decode($plan, true, 512, JSON_THROW_ON_ERROR);
    $plan = $decoded;
}

$evidence = [
    'schema_version' => 1,
    'purpose' => 'bounded VS-03a CI evidence; not a production-scale benchmark',
    'database_driver' => DB::connection()->getDriverName(),
    'query' => $query,
    'iterations' => $iterations,
    'result_count' => count($search->search($query)->items),
    'latency_ms' => [
        'min' => round($durationsMs[0], 3),
        'median' => round($durationsMs[(int) floor($iterations / 2)], 3),
        'max' => round($durationsMs[$iterations - 1], 3),
        'mean' => round(array_sum($durationsMs) / $iterations, 3),
    ],
    'release_candidate_plan' => $plan,
];

echo json_encode($evidence, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_THROW_ON_ERROR).PHP_EOL;
