# Changelog

## [1.1.0](https://github.com/GoogleCloudPlatform/cxas-scrapi/compare/v1.0.0...v1.1.0) (2026-04-29)


### Features

* Add --modality flag to cxas_sim_eval run_evals script ([77bab91](https://github.com/GoogleCloudPlatform/cxas-scrapi/commit/77bab915551c88768059db7ba676bc86f698f870))
* Add --modality flag to cxas_sim_eval run_evals script ([4ea51ea](https://github.com/GoogleCloudPlatform/cxas-scrapi/commit/4ea51ea55789ddd2e1e26d464cc4f12b0b496758))
* add progress bar for eval runs ([3960546](https://github.com/GoogleCloudPlatform/cxas-scrapi/commit/3960546042bdb4cb71a7a37ca4c3451c1a85009a))
* add progress bar for eval runs ([f3d33d6](https://github.com/GoogleCloudPlatform/cxas-scrapi/commit/f3d33d643dcf07a3586ed237bf40cdf1f686e40b))
* Add support for providing environment.json file when branching app ([3170a40](https://github.com/GoogleCloudPlatform/cxas-scrapi/commit/3170a40aaba4c67f2f95712a4f046422fc9d81d8))
* complete refactor to Pydantic models, fix codebase porting bugs ([#26](https://github.com/GoogleCloudPlatform/cxas-scrapi/issues/26)) ([a38648c](https://github.com/GoogleCloudPlatform/cxas-scrapi/commit/a38648cc4cbd563cbdd5662d59edb2d261a2e35f))
* **evals:** capture and render agent transfers and custom payloads i… ([f33b6b3](https://github.com/GoogleCloudPlatform/cxas-scrapi/commit/f33b6b35dff436592da309e6a45d23929a2ce4d5))
* **evals:** capture and render agent transfers and custom payloads in sim reports ([46bf15e](https://github.com/GoogleCloudPlatform/cxas-scrapi/commit/46bf15e62ab831f3879cb08de511a26db0ad429a))
* implement colab dashboard and CLI dashboard modules, and refactor visualization components ([2d6f80b](https://github.com/GoogleCloudPlatform/cxas-scrapi/commit/2d6f80b09844b54a1b16f944366aae73666cffe6))
* implement colab dashboard and CLI interface modules, and refactor visualization components ([b0bd6f5](https://github.com/GoogleCloudPlatform/cxas-scrapi/commit/b0bd6f5dbf247ce08875d0bdbaf47aebbf01a47b))
* **linter:** add I014 rule to warn when current_date is missing from instructions ([68d6a3d](https://github.com/GoogleCloudPlatform/cxas-scrapi/commit/68d6a3d0c0cd4b05760c6bf186fcfe2920a39e8c))
* **linter:** add I014 rule to warn when current_date is missing from… ([97a7e53](https://github.com/GoogleCloudPlatform/cxas-scrapi/commit/97a7e536782fa662ee1cf8d970e3feafe3487f2b))


### Bug Fixes

* Fix bugs in init-github-action ([a94c019](https://github.com/GoogleCloudPlatform/cxas-scrapi/commit/a94c019a0c96196d09b6a245bac7b9f5ac1ed240))
* Fix bugs in init-github-action ([3d498bc](https://github.com/GoogleCloudPlatform/cxas-scrapi/commit/3d498bcdab66e35f7c091751d2f70e41d5c5ecdc))
* **linter:** accept display names in S004 child agent references ([0ca0727](https://github.com/GoogleCloudPlatform/cxas-scrapi/commit/0ca0727a155881a3021cac50e94bf7ca7f140376))
* **linter:** accept display names in S004 child agent references ([2313da9](https://github.com/GoogleCloudPlatform/cxas-scrapi/commit/2313da95c1544fb37fa94c5955a80c2591b94848)), closes [#16](https://github.com/GoogleCloudPlatform/cxas-scrapi/issues/16)
* linting ([50dc27e](https://github.com/GoogleCloudPlatform/cxas-scrapi/commit/50dc27ee78daea9bab45305a22e746925830301a))
* linting ([7983803](https://github.com/GoogleCloudPlatform/cxas-scrapi/commit/79838037d283873961bc8cdcd6968c1996a33396))
* **lint:** update ruff version and fix import sorting ([c006eb0](https://github.com/GoogleCloudPlatform/cxas-scrapi/commit/c006eb0dae67b6056ceaa5c0eb4aae5567879d7b))
* rename app_id to app_name; remove unused code ([59804b8](https://github.com/GoogleCloudPlatform/cxas-scrapi/commit/59804b88c337db2fe29432425d5d2ceac0965f2e))
* revert app_id for create_app method ([bc41156](https://github.com/GoogleCloudPlatform/cxas-scrapi/commit/bc4115672f030b0a1647e3cf52a2318821554b4f))
* update app_id to app_name in CLI ([aa65fdb](https://github.com/GoogleCloudPlatform/cxas-scrapi/commit/aa65fdbc79763725cfddfed1bf548ec152977193))
* update app_id to app_name in CLI ([057f853](https://github.com/GoogleCloudPlatform/cxas-scrapi/commit/057f8533fd68cc09e6e14cc17743a92b2c8c0e71))


### Documentation

* add Mercedes F1 fan agent PRD example ([42a7d64](https://github.com/GoogleCloudPlatform/cxas-scrapi/commit/42a7d642935bd5746b6e019c3450a19a4a18de88))
* add Mercedes F1 fan agent PRD example ([d35b056](https://github.com/GoogleCloudPlatform/cxas-scrapi/commit/d35b0568ddf843085a1ded38c7410dc731c9f3f1))
* fix mkdocs build warnings ([b178ec2](https://github.com/GoogleCloudPlatform/cxas-scrapi/commit/b178ec2b929b5d5704080ede562e2adcc72e2928))
* fix setup instructions across documentation ([4bd9cce](https://github.com/GoogleCloudPlatform/cxas-scrapi/commit/4bd9cce322503f7f943598a2314e539fff839066))
* fix setup instructions across documentation ([1b2e47c](https://github.com/GoogleCloudPlatform/cxas-scrapi/commit/1b2e47c31735508289f09da4e543161d67ef480a))

## 1.0.0 (2026-04-22)


### Features

* Init release of CXAS SCRAPI ([5f37dea](https://github.com/GoogleCloudPlatform/cxas-scrapi/commit/5f37deacf2f8b7cb16793bf071ffa076c8a1db75))


### Miscellaneous Chores

* release 1.0.0 ([3b9b0c2](https://github.com/GoogleCloudPlatform/cxas-scrapi/commit/3b9b0c2609f80646cbd312049569438f22b7290f))
