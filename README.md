# sumFSA

`sumFSA` is SUM's filesystem/storage abstraction layer. Applications use stable logical paths while the backend translates them to the host filesystem.

## a1 scope

- SUM logical paths always use `/`.
- Native POSIX paths map directly to logical paths.
- Windows drives map to `/mnt/c`, `/mnt/d`, ... and `/mnt` is a virtual directory.
- Linux mounts are discovered from `/proc/self/mountinfo`.
- Common `Mount`, `Volume`, `Location`, `Entry` and `ResolvedPath` models are provided.
- The API exposes path translation, directory enumeration, stat/existence checks, mounts, volumes and user-facing locations.

Android currently uses the native POSIX-visible filesystem when available. **Android SAF is not implemented in this alpha**; the abstraction boundary is intentionally ready for a future provider without exposing `content://` URIs to SUM applications.

```python
from sumfsa import FileSystem;

fs=FileSystem();
print(fs.cwd);
print(fs.resolve(".").native);
for location in fs.locations():
    print(location.name, location.logical_path);
```

CLI inspection:

```text
sumfsa path .
sumfsa mounts
sumfsa volumes
sumfsa locations
sumfsa ls .
```

<p align=center><b>- oOo -</b></p>
