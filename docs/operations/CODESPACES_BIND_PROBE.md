# Codespaces Docker bind-mount probe

Use this only when the Compose `app` container reports that `/var/www/html` does not contain SongChart source.

```bash
docker inspect songchart-next-app-1 \
  --format '{{range .Mounts}}{{println .Type .Source "->" .Destination}}{{end}}'
```

In a healthy Codespace the mount targeting `/var/www/html` must resolve to the host workspace path supplied by `LOCAL_WORKSPACE_FOLDER`, not merely the `/workspaces/...` path visible inside the devcontainer.

The authoritative fix is the devcontainer/Compose host-workspace contract in ADR-0010. Do not hard-code `/var/lib/docker/codespacemount/...` into `compose.yaml`, and do not delete named volumes to repair a source-bind problem.
