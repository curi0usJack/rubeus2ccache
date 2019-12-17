# rubeus2ccache
Extracts all base64 ticket data from a rubeus /dump file and converts the tickets to ccache files for easy use with other tools. 

1. Run rubeus to dump tickets (must be in an admin context): rubeus dump /service:krbtgt > output.txt
2. python3 rubeus2ccache.py -i output.txt
3. Load up tickets in Impacket. 
