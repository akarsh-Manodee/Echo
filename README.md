Echo - Your Private Journal App

Echo is a minimalistic and secure journal application designed to let you record your thoughts without distraction. With encryption, daily journal entries, and an intuitive interface, Echo ensures your private musings are for your eyes only.

 Features

- Pin Protected: Your journals are encrypted and protected with a 4-digit pin.
- Immutable Entries: Once saved, journal entries become read-only and cannot be edited, ensuring you capture your thoughts as they are in the moment.
- Smooth Animations: Enjoy a smooth transition when focusing on writing mode or reviewing your past entries.
- Dark Mode: A distraction-free dark mode with subtle design elements.
- Text Formatting: Customize your journal entries with bold, colored text, and text alignment options.

 Creating an Executable (EXE)

To create an executable file for the app, follow these steps:

1. Install `pyinstaller` if you haven’t already:
   ```
   pip install pyinstaller
   ```

2. Generate the executable using this command:
   ```
   pyinstaller --onefile --windowed Echo.py
   ```

   - The `--onefile` flag ensures that everything is bundled into a single executable file.
   - The `--windowed` flag prevents a terminal window from appearing when you run the app.

3. After running the above command, the executable will be created in the `dist` folder.

 Usage Instructions

- Start Writing: Open the app, enter your pin, and begin journaling. Your journal entry for the day will be saved as you write and will become read-only once saved.
- Read Past Entries: You can navigate through previous entries using the sidebar.
- Note: Once you enter writing mode for a day’s entry, you cannot edit or save it again. If you navigate away without saving, unsaved changes will be lost.


