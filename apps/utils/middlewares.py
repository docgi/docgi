import logging

import sqlparse
from django.db import connection
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class DocgiMiddleware(MiddlewareMixin):
    def process_request(self, request):
        print('\n\n')
        print('| Start')
        print('--------------------------------------------------------------------------')

    def process_response(self, request, response):
        from pygments import highlight, lexers, formatters
        for item in connection.queries:
            raw_sql = item['sql']
            raw_sql = sqlparse.format(raw_sql, reindent_aligned=True, truncate_strings=500)
            raw_sql = highlight(
                raw_sql,
                lexers.get_lexer_by_name("sql"),
                formatters.TerminalFormatter()
            )
            print(raw_sql)

        print('--------------------------------------------------------------------------')
        print('| ;; Total queries: %d' % (len(connection.queries)))
        return response
