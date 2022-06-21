# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.1] - 25 May 2021

### Fixed

- `Project.get_dataset()` is now able to return a dataset by using the most recent import job

## [1.2.0] - 6 Apr 2021

### Added

- `forecast_dimensions` as a `Predictor` parameter

## [1.1.0] - 9 Feb 2021

### Added

- `Predictor.info` property that updates predictor information and returns an info dict.

- `Predictor.wait_for_training()` so that users are able to time the training duration.

## [1.0.0] - 9 Feb 2021

### Changed

- `Project` now requires LDAP user for authentication.

## [0.1.1] - 4 Feb 2021

### Changed

- The predictor now waits for all datasets to be `ACTIVE` before creating a forecast.


## [0.1.0] - 28 Jan 2021

### Added

- `supplementary_features` as an optional parameter in `train_new_predictor()`


<!-- Safe to delete, just as example -->
## [0.0.1] - example - 04 Nov 2020

### Added

- New feature added

### Changed

- Fixed bug
- Enhanced feature
- Refactored code

### Removed

- Unnecessary file
