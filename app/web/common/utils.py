from flask import request

def paginate(query):
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('limit', 20))
    return query.paginate(page=page, per_page=per_page, error_out=False)