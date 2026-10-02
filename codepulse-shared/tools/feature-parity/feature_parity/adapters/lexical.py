from pygments.token import Comment, String


def mask_non_code(source, lexer):
    masked = list(source)
    for offset, token_type, value in lexer.get_tokens_unprocessed(source):
        if token_type in Comment or token_type in String:
            for position in range(offset, offset + len(value)):
                if masked[position] not in "\r\n":
                    masked[position] = " "
    return "".join(masked)