### Curseforge-Profile-Code-Downloader
Downloads a Modpack using the profile code, using curseforge's public api.
</br>\- Used Clade to make the python, simple stuff.
- `cf_profile_code_importer.py`
  -  profilecode -> curseforge zip. Saves in same dirrectory as the script.
- `cf_code_to_prism.py`
  - Only used if you are using Prism Launcher, Downloads the zip to your windows TEMP dir, then uses cmd arguments to send it to prism launcher

### Dependancies
- `pip install requests`

### Extra
- Supports calling the python with `cf_code_to_prism.py <profile_code>`
