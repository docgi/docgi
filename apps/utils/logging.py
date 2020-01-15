import logging

from .middlewares import _thread_locals


class DocgiLoggingFormatter(logging.Formatter):
    def format(self, record):
        import sqlparse
        from pygments import highlight, lexers, formatters

        query_count = 1
        if hasattr(_thread_locals, "query_count"):
            _thread_locals.query_count += 1
            query_count = _thread_locals.query_count

        raw_sql = record.sql.strip()
        raw_sql = sqlparse.format(raw_sql, reindent_aligned=True, truncate_strings=500)
        raw_sql = highlight(
            raw_sql,
            lexers.get_lexer_by_name("sql"),
            formatters.TerminalFormatter()
        )
        statement = \
            f"====================== Query {query_count} ======================\n" \
            f"{raw_sql}" \
            f"======================  End {query_count}  =======================\n" \
            f"Duration: {record.duration:.3f}\n"

        return statement
