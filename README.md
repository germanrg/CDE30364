# CDE30364

A simple python script to get active IPs on LAN managed with a Hitron CDE-30364 router model. This script has been optimizated to firmware PSPU-Boot 1.0.16.22-H2.8.3 therefore using a different firmware version can cause errors.

The script can use a text file called KnownMACs stored in the script dir (if you want) to compare the MAC addresses given by the router. Very useful if you want detect possible intrussions in your LAN.

CDE30364.py uses two external libs: BeautifulSoup & Selenium To install the libs try the next commands:

$> pip beautifulsoup4
$> pip selenium

Bug report & Suggestions

gNrg(at)tuta.io
