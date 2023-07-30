# Changelog

This file is based on the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format

## [1.0.1] - 2023-07-30

### Changed

- [5deb569](https://github.com/ArchGryphon9362/art-downloader/commit/5deb569fb9d5b12eb11d55701814bd04922eaaab) - Pressing enter key while focused in the upload url field now uploads instead of submitting the post
- [5b8603e](https://github.com/ArchGryphon9362/art-downloader/commit/5b8603ee4d62004a787fed71e8e8d6d449d47985) - Source field gets automatically filled if url uploaded and source field is empty
- [113027a](https://github.com/ArchGryphon9362/art-downloader/commit/113027a0f51409d76b09b730fceb09ebee4575ef) - Tumblr tokens were moved to settings page
- [0cf4013](https://github.com/ArchGryphon9362/art-downloader/commit/0cf40131bd75c45ff9c038d4c4ed4fd2fd07dffb) - Direct media links were given more priority over social media links

### Deprecated

- [113027a](https://github.com/ArchGryphon9362/art-downloader/commit/113027a0f51409d76b09b730fceb09ebee4575ef) - Setting Tumblr tokens over environment variables is now deprecated and will be removed in 2.0.0. To set them you now have to go to settings (don't worry, your Tumblr tokens will be moved to the new system when you upgrade)

### Fixed

- [cc56e64](https://github.com/ArchGryphon9362/art-downloader/commit/cc56e64b57d790bfd39d5df1ee7ec8874aac4d89) - Fixes issue where some Reddit posts could be loaded out of order
- [9fae424](https://github.com/ArchGryphon9362/art-downloader/commit/9fae424353bc475fd7a302f3564e1f1b36809a94) - Fixes issue where opening a non existent post would give a 5xx internal server error
- [f628ec8](https://github.com/ArchGryphon9362/art-downloader/commit/f628ec856e4d184e12be1c65a7f07189d9e26d7e) - Fixes issue where all instagram posts were downloaded as squares (when a non-square version existed)

## [1.0.0] - 2023-07-27

### Added

Initial release with all the base functionality
