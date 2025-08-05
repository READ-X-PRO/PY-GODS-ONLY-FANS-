import PyInstaller.__main__

PyInstaller.__main__.run([
    'digital_library.py',
    '--onefile',
    '--windowed',
    '--name=Unwritten_Library',
    '--add-data=library_content.json;.',
    '--icon=book_icon.ico'  # Optional: add an icon
])