# Changelog

This file is based on the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format

## [1.0.1] - 2023-07-30

### Changed

- 5deb569 - Pressing enter key while focused in the upload url field now uploads instead of submitting the post
- 5b8603e - Source field gets automatically filled if url uploaded and source field is empty
- 113027a - Tumblr tokens were moved to settings page
- 0cf4013 - Direct media links were given more priority over social media links

### Deprecated

- 113027a - Setting Tumblr tokens over environment variables is now deprecated and will be removed in 2.0.0. To set them you now have to go to settings (don't worry, your Tumblr tokens will be moved to the new system when you upgrade)

### Fixed

- cc56e64 - Fixes issue where some Reddit posts could be loaded out of order
- 9fae424 - Fixes issue where opening a non existent post would give a 5xx internal server error
- f628ec8 - Fixes issue where all instagram posts were downloaded as squares (when a non-square version existed)

## [1.0.0] - 2023-07-27

### Added

Initial release with all the base functionality
