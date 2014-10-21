#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import sys
from vat import VATchecker

sys.path.append('../..')

logging.basicConfig(level=logging.DEBUG)

# cancel some noisy loggers
logging.getLogger('suds.xsd').setLevel(logging.INFO)
logging.getLogger('suds.resolver').setLevel(logging.INFO)

if __name__ == '__main__':

    vc = VATchecker('<your-username>', '<your-password>')

    ver = vc.getVersion()
    print "version:", ver

    #vc._client.set_options(nosend=True)

    try:
        res = vc.getAFMinfo('<afm>', '<your-afm>')
        print res
    except Exception, e:
        logging.getLogger('main').exception("Failed: %s", e)


#eof
