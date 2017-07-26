import socket

# Path to solr source
solr_url  = 'http://147.94.102.65:8983/solr/documents'


# Socket configuration
sock_config_analysis = {
    'net': {
        'fam': socket.AF_INET,
        'type': socket.SOCK_STREAM,
        'addr': 'localhost',
        'port': 1338,
        },
    'END_CHR': '\0', # EOT character
}



#Settings to acces Sent-analysis on application server
analysis_path = 'echo/' #Local machine


