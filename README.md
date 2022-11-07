# stockapp
A simple stock analysis application.

### Compiling
#### MacOS
Open terminal in source file. First download Python if not already downloaded
```
pip3 install python
```
Install required packages with the following line
```
pip3 install -r requirements.txt
```
Install pyinstaller, the compiler for the application
```
pip3 install pyinstaller
```
Then, compile the application with
```
python -m PyInstaller --windowed --add-data="Resources/symbols.json:Resources" --hidden-import="scipy" --hidden-import="yfinance" stockapp_v0.py
```
