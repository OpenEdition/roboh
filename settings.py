import socket

# Path to solr source
solr_url  = 'http://147.94.102.65:8983/solr/documents'


nerd_api_key = '4hmuhq425psqnl69la3glv8tu2vdu68q'
allgo_key = '2d1edf7391684877a5b011fe0278806a'
allgo_url = 'https://allgo.inria.fr/api/v1/jobs'

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
analysis_path = '../../../../echoVE/echo/' #Local machine


