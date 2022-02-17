README for UKMON Archive

```mermaid
    flowchart TD
    A[camera 1] --> C[livestream];
    B[camera 2] --> C[livestream];
    A[camera 1] --> D[cloud storage];
    B[camera 2] --> D[cloud storage];
    D[cloud storage] --> E[matching engine];
    E[matching engine] --> F[reports generator];
    F[reports generator] --> G[opt-in email of matches];
    F[reports generator] --> H[website];
    F[reports generator] --> I[bad-data alerts];
```