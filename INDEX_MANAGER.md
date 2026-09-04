# Runtime Index Channel Manager

Admin commands:
- `/addindex -1001234567890`
- `/addindex @channelusername`
- `/delindex -1001234567890`
- `/indexlist`
- `/clearindex`
- `/indexhelp`
- `/config` (safe configuration view; secrets are never displayed)

The bot must be an administrator in every index channel/group.

Runtime index channels are stored in MongoDB (`admin_database.index_channels` inside the existing configuration collection) so adding a channel does not require a Koyeb redeploy.

The original `CHANNELS` environment variable is used to seed the runtime list the first time. Removing runtime entries does not edit Koyeb environment variables.
