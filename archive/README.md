UKMON Archive and UKMON Live data flows
=======================================

```mermaid
    flowchart TD
    A[camera 1] -- realtime --> C[UKMON Live];
    B[camera 2] -- realtime --> C;
    P[camera 3] -- realtime --> C;
    A -- next day --> D[cloud storage];
    B -- next day --> D;
    P -- next day --> D;
    D --> E[matching engine];
    E --> F[reports generator];
    F --> G[opt-in email of matches];
    F --> I[bad-data alerts];
    F --> H[UKMON Archive];
    H -- on demand --> J[other networks];
    H --> M[public];
    C --> M[public];
    C --> N{bright event?};
    N -->|yes| K[social media];
    H -- manual --> K;
    I --> O[camera owners];
    G --> O;
```