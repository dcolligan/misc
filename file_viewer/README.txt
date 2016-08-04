A simple web.py-based file viewer.

Lots of extraneous files are included only for the sake of viewing.

Features:
- puts the viewer in chroot-jail-like restrictions based on where the script is launched
- downloads non-directory files on click 
- doesn't show symlinks

Improvements:
- make os-independent with os.path functions
- modularize some of the os.path code
- extensions that you can view directly in browser
- sorting option in UI
- hide hidden files option in UI
- show symlinks if they don't break out of the jail
- more info about files: access times, permissions, size, etc.
- grey out home and back buttons if at dir root
