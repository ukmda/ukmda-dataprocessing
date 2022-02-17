README for UKMON Archive

```mermaid
    flowchart TD
    A[camera 1] -- realtime --> C[livestream];
    B[camera 2] -- realtime --> C;
    A -- next day --> D[cloud storage];
    B -- next day --> D;
    D --> E[matching engine];
    E --> F[reports generator];
    F --> G[opt-in email of matches];
    F --> I[bad-data alerts];
    F --> H[website];
    H -- on demand -->J[other networks];
    H --> M[public];
    C --> M[public];
    C --> N{bright event?};
    N -- |yes| K[social media];
    K -- manual -->H;
```