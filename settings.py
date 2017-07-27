import socket

# Path to solr source
solr_url  = path_to_solr/documents


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
analysis_path = '/data/echoVE/echo/' #Local machine


