from loguru import logger as logger_

logger = logger_.bind(context='system')

FORMAT = "<g>{time:YYYY-MM-DD HH:mm:ss.SSS}</> | <y>{level}</> | <w>{extra[context]}</> | <c>{message}</>"
FILTER = lambda x: 'context' in x['extra']
