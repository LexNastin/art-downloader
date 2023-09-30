# Changelog

This file is based on the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format

## [1.1.0] - 2023-09-30

### Added

- [`0263082`](https://github.com/ArchGryphon9362/art-downloader/commit/026308204b272bc0668eb386d71cfe7e930140a3) - Support for thumbnails from HEIF images was added
- [`4f84944`](https://github.com/ArchGryphon9362/art-downloader/commit/4f84944ba1287fd745c908b7f6fbcda29ff3583f) - Links from X are now supported (adding to previous Twitter support)
- [`147376c`](https://github.com/ArchGryphon9362/art-downloader/commit/147376cd12352cc4cd3096f0f038d404cfcb6e20) - Buttons to select all, none, or deselect all tags were added
- [`7b1ed78`](https://github.com/ArchGryphon9362/art-downloader/commit/7b1ed785d5bdfdcab2cc28515d9bc21522e74bc3) - Added meta tag to get previews on other websites and apps

### Changed

- [`6a0ed1b`](https://github.com/ArchGryphon9362/art-downloader/commit/6a0ed1b9131b23bd99702cf7ea1e86877468cdc1) - Links to source now open in a new tab instead of the current one

### Fixed

- [`4ebefad`](https://github.com/ArchGryphon9362/art-downloader/commit/4ebefad610ac3fdcff64a2db70ba5d9cde2ea00e) - Tumblr keys are now actually being taken from settings
- [`bcfb32b`](https://github.com/ArchGryphon9362/art-downloader/commit/bcfb32bb34e71a7d80bd1e33d202ff0549ced646) - Fixes an issue where posts from insta were square most (if not all) of the time
- [`2aab018`](https://github.com/ArchGryphon9362/art-downloader/commit/2aab0184ed3751b43b0bb9816d6a7ed2671f378b) - Fixes issue with timezones being taken into account in some places (I'm completely ignoring timezones for this project)
- [`3ae6fd8`](https://github.com/ArchGryphon9362/art-downloader/commit/3ae6fd8de02f5440127f3b4f34d0acb79b5ea0a2) - Prevents empty tags from being used
- [`3e0e3e1`](https://github.com/ArchGryphon9362/art-downloader/commit/3e0e3e17db2b9f671a9b89d6027b7f67651fdc2a) - Website now redirects to public posts when signing out (or login if the website is private)
- [`abeafa5`](https://github.com/ArchGryphon9362/art-downloader/commit/abeafa53ff766c0813319e0e4ea4663f4a4eb284) - A certain type of Tumblr post now works

## [1.0.1] - 2023-07-30

### Changed

- [`5deb569`](https://github.com/ArchGryphon9362/art-downloader/commit/5deb569fb9d5b12eb11d55701814bd04922eaaab) - Pressing enter key while focused in the upload url field now uploads instead of submitting the post
- [`5b8603e`](https://github.com/ArchGryphon9362/art-downloader/commit/5b8603ee4d62004a787fed71e8e8d6d449d47985) - Source field gets automatically filled if url uploaded and source field is empty
- [`113027a`](https://github.com/ArchGryphon9362/art-downloader/commit/113027a0f51409d76b09b730fceb09ebee4575ef) - Tumblr tokens were moved to settings page
- [`0cf4013`](https://github.com/ArchGryphon9362/art-downloader/commit/0cf40131bd75c45ff9c038d4c4ed4fd2fd07dffb) - Direct media links were given more priority over social media links

### Deprecated

- [`113027a`](https://github.com/ArchGryphon9362/art-downloader/commit/113027a0f51409d76b09b730fceb09ebee4575ef) - Setting Tumblr tokens over environment variables is now deprecated and will be removed in 2.0.0. To set them you now have to go to settings (don't worry, your Tumblr tokens will be moved to the new system when you upgrade)

### Fixed

- [`cc56e64`](https://github.com/ArchGryphon9362/art-downloader/commit/cc56e64b57d790bfd39d5df1ee7ec8874aac4d89) - Fixes issue where some Reddit posts could be loaded out of order
- [`9fae424`](https://github.com/ArchGryphon9362/art-downloader/commit/9fae424353bc475fd7a302f3564e1f1b36809a94) - Fixes issue where opening a non existent post would give a 5xx internal server error
- [`f628ec8`](https://github.com/ArchGryphon9362/art-downloader/commit/f628ec856e4d184e12be1c65a7f07189d9e26d7e) - Fixes issue where all instagram posts were downloaded as squares (when a non-square version existed)

## [1.0.0] - 2023-07-27

### Added

Initial release with all the base functionality
