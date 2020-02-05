import logging
from threading import local

import sqlparse
from pygments import highlight, lexers, formatters

_thread_locals = local()


class DocgiLoggingFormatter(logging.Formatter):
    def format(self, record):
        if not hasattr(_thread_locals, "query_count"):
            setattr(_thread_locals, "query_count", 0)

        _thread_locals.query_count += 1

        raw_sql = record.sql.strip()
        raw_sql = sqlparse.format(raw_sql, reindent_aligned=True, truncate_strings=500)
        raw_sql = highlight(
            raw_sql,
            lexers.get_lexer_by_name("sql"),
            formatters.TerminalFormatter()
        )
        statement = \
            f"====================== Query {_thread_locals.query_count} ======================\n\n" \
            f"{raw_sql}\n" \
            f"======================  End {_thread_locals.query_count}  =======================\n" \
            f"Duration: {record.duration:.3f}\n"

        return statement
